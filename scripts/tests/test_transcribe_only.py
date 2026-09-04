#!/usr/bin/env python3
"""
Regression test for --transcribe-only (capture_pipeline).

The point of this test is the DEFAULT path, not the new flag: adding a mode must not
change what the pipeline already does. Both directions are asserted, so the test can
actually fail in the case it exists to catch.

Three layers, deliberately:
  1. SHAPE   — the guard exists and is the first statement (AST).
  2. ORDER   — the guard runs BEFORE the write it protects. A guard placed after a
               sheet append is decoration; these assertions go red on that.
  3. RUNTIME — the guarded functions are actually called with the flag on and must
               return None without touching a Sheets/Calendar client. AST tests pass
               on code that never runs; this layer runs it.

Run: python3 -m pytest scripts/tests/test_transcribe_only.py -v
"""
import ast
import os
import pathlib
import sys
import tempfile
import types

SRC = pathlib.Path(__file__).resolve().parents[1] / "capture" / "capture_pipeline.py"
WORKFLOW = pathlib.Path(__file__).resolve().parents[2] / ".github" / "workflows" / "capture_pipeline.yml"


def _tree():
    return ast.parse(SRC.read_text())


def _func(name):
    for node in ast.walk(_tree()):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"{name} not found in capture_pipeline.py")


def _guards_on_transcribe_only(fn):
    """True if the function's FIRST statement (after any docstring) is an
    `if TRANSCRIBE_ONLY:` block that returns."""
    body = fn.body
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
        body = body[1:]
    if not body or not isinstance(body[0], ast.If):
        return False
    test = body[0].test
    if not (isinstance(test, ast.Name) and test.id == "TRANSCRIBE_ONLY"):
        return False
    return any(isinstance(n, ast.Return) for n in ast.walk(body[0]))


def _live_guards(fn):
    """Every LIVE `if TRANSCRIBE_ONLY:` node inside fn.

    Live means the test is the name itself. `if False:` / `if 0:` around the same
    body is dead code that reads like a guard and stops nothing, so it is not
    counted — that mutation has to be able to turn these tests red.
    """
    return [n for n in ast.walk(fn)
            if isinstance(n, ast.If)
            and isinstance(n.test, ast.Name)
            and n.test.id == "TRANSCRIBE_ONLY"]


def test_default_is_false():
    """Default must be OFF. If this flips, every capture silently stops filing."""
    for node in ast.walk(_tree()):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "TRANSCRIBE_ONLY":
                    assert node.value.value is False, "TRANSCRIBE_ONLY must default to False"
                    return
    raise AssertionError("TRANSCRIBE_ONLY global not defined")


# Every function that files something into the content system. Audited 2026-09-04:
# the first two were the original PR; the rest were found by grepping for sheet
# appends, tracker writes and downstream workflow dispatches.
GUARDED_WRITERS = (
    "update_inspiration_library",     # 📥 Inspiration Library row (+ Content Queue promote)
    "create_calendar_task",           # Google Calendar content brief
    "update_book_tracker",            # Book Tracker "Stories" row
    "_write_manual_tasks_to_inbox",   # 📥 Inbox rows
    "_trigger_topic_scraper",         # dispatches topic_scraper.yml (~$0.50 + its own calendar tasks)
    "_mark_queue_processed",          # would silently consume a queued capture
)


def test_both_side_effects_are_guarded():
    """The two writes the PR was opened for. Kept as its own assertion so the
    original contract stays visible — the full list is the next test."""
    for name in ("update_inspiration_library", "create_calendar_task"):
        assert _guards_on_transcribe_only(_func(name)), f"{name} is not guarded"


def test_all_content_system_writes_are_guarded():
    """Not just the two the PR started with — every filing path."""
    for name in GUARDED_WRITERS:
        assert _guards_on_transcribe_only(_func(name)), f"{name} is not guarded"


def _funcs_containing(needle):
    src = SRC.read_text()
    lines = src.splitlines()
    out = []
    for node in ast.walk(_tree()):
        if isinstance(node, ast.FunctionDef):
            seg = "\n".join(lines[node.lineno - 1:node.end_lineno])
            if needle in seg:
                out.append((node.name, seg))
    return out


def test_ideas_queue_appends_are_guarded():
    """The 💡 Ideas Queue append hides inside two Drive-shaped functions
    (create_content_workspace, save_to_news_folder). Both must respect the flag.

    ORDER is asserted, not just presence: these two are guarded by `gc = None`
    rather than an early return, so a guard that lands BELOW the append would
    still contain the string and still write the row.
    """
    found = _funcs_containing("\\U0001f4a1 Ideas Queue")
    assert found, "Ideas Queue append not found — did the tab constant move?"
    for name, _seg in found:
        fn = _func(name)
        appends = [n.lineno for n in ast.walk(fn)
                   if isinstance(n, ast.Call)
                   and isinstance(n.func, ast.Attribute)
                   and n.func.attr == "append_row"]
        assert appends, f"{name}: no append_row found — did the write move?"
        guards = _live_guards(fn)
        assert guards, f"{name} appends to Ideas Queue without checking the flag"
        first_append = min(appends)
        assert any(g.lineno < first_append for g in guards), (
            f"{name}: the TRANSCRIBE_ONLY guard sits at or below the append_row on "
            f"line {first_append}. A guard cannot stop a write that already ran."
        )


def _encloses(node, lineno):
    return node.lineno <= lineno <= (node.end_lineno or node.lineno)


def _import_lines(fn, module):
    return [n.lineno for n in ast.walk(fn)
            if isinstance(n, ast.ImportFrom) and n.module == module]


def test_downstream_dispatch_hooks_are_guarded():
    """These two hooks run in SEPARATE processes where the module global cannot
    reach — they have to be stopped at the dispatch boundary, inside main().

    The dispatch must live in the ELSE branch of a live `if TRANSCRIBE_ONLY:`.
    Asserting that, rather than 'the string appears somewhere nearby', is what
    makes this test able to fail: a guard moved below the dispatch, or neutered
    to `if False:` with the skip message left behind, no longer satisfies it.
    """
    fn = _func("main")
    guards = _live_guards(fn)
    for module in ("person_evidence_dispatcher", "resource_router"):
        lines = _import_lines(fn, module)
        assert lines, f"{module} hook not found in main()"
        for lineno in lines:
            in_else = any(any(_encloses(n, lineno) for n in g.orelse) for g in guards)
            assert in_else, (
                f"{module} is dispatched on line {lineno}, outside the else branch of a "
                f"live `if TRANSCRIBE_ONLY:`. Transcribe-only would still fire it."
            )


def test_completion_emails_do_not_claim_unwritten_rows():
    """The completion email must not say a row was added when the flag skipped it."""
    src = SRC.read_text()
    for lie in ('f"Inspiration Library: row added',
                'f"Sheets: row added to Inspiration Library'):
        assert lie not in src, f"completion email still claims unconditionally: {lie}"


def test_transcription_is_NOT_guarded():
    """Falsifiability: the flag must skip FILING, never the transcription itself.
    If someone guards the transcript path, this goes red."""
    for name in ("transcribe_audio", "download_audio"):
        try:
            fn = _func(name)
        except AssertionError:
            continue  # function renamed upstream; not this test's job to police
        assert not _guards_on_transcribe_only(fn), (
            f"{name} must NOT be skipped — transcribe-only still transcribes"
        )


def test_flag_is_wired_to_argparse():
    src = SRC.read_text()
    assert '"--transcribe-only"' in src, "argparse flag missing"
    assert 'TRANSCRIBE_ONLY = bool(getattr(args, "transcribe_only", False))' in src, \
        "flag is declared but never read from args"


def test_workflow_passes_the_flag():
    """The flag is only reachable through the workflow. If the `choice` option and
    the shell comparison ever disagree on the literal, she picks transcribe_only
    in the UI and gets a full capture — the exact harm this PR exists to prevent.
    """
    txt = WORKFLOW.read_text()
    assert "- transcribe_only" in txt, "mode choice option missing from capture_pipeline.yml"
    assert "--transcribe-only" in txt, "workflow never passes --transcribe-only to the script"
    import re
    branch = re.search(r'inputs\.mode\s*\}\}"\s*=\s*"([a-z_]+)"', txt)
    assert branch, "no shell comparison on inputs.mode"
    assert branch.group(1) == "transcribe_only", (
        f'workflow compares inputs.mode to "{branch.group(1)}" but the choice option '
        f'is "transcribe_only" — the flag would never be passed'
    )


def _load_pipeline():
    """Import capture_pipeline for real.

    `requests` is stubbed so this needs no third-party packages, and the import
    runs in a temp cwd because the module does TRANSCRIPTS_DIR.mkdir() at import.
    """
    import importlib.util
    sys.modules.setdefault("requests", types.ModuleType("requests"))
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as tmp:
        os.chdir(tmp)
        try:
            spec = importlib.util.spec_from_file_location("capture_pipeline_under_test", SRC)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        finally:
            os.chdir(cwd)
    return mod


def test_guards_stop_the_write_at_RUNTIME():
    """AST tests pass on code that never runs. This one runs it.

    Every outbound door the guarded functions could use is replaced with a
    sentinel that raises. With the flag ON, none of them may be reached and every
    function must still return None — an early `return` where a caller expected a
    value would show up here. urlopen is sentinelled too, so a broken guard can
    never dispatch a real workflow from a test.
    """
    import urllib.request

    cp = _load_pipeline()

    class Fired(Exception):
        pass

    def boom(*_a, **_k):
        raise Fired("outbound call reached in transcribe-only mode")

    real_urlopen = urllib.request.urlopen
    cp.get_sheets_client = boom
    cp.get_calendar_service = boom
    cp._auto_promote_capture_to_content_queue = boom
    urllib.request.urlopen = boom
    try:
        cp.TRANSCRIBE_ONLY = True
        calls = {
            "update_inspiration_library":
                lambda: cp.update_inspiration_library("https://x", "transcript", {"niche": "opc"}),
            "create_calendar_task":
                lambda: cp.create_calendar_task("sid", "opc", "https://x", "doc", "preview", "notes"),
            "update_book_tracker":
                lambda: cp.update_book_tracker("sid", "https://x", "doc", {"summary": "s"}, "notes"),
            "_write_manual_tasks_to_inbox":
                lambda: cp._write_manual_tasks_to_inbox([{"task": "do a thing"}], "sid", "https://x"),
            "_trigger_topic_scraper":
                lambda: cp._trigger_topic_scraper({"niche": "Brazil"}, niche="Brazil"),
            "_mark_queue_processed":
                lambda: cp._mark_queue_processed("https://x"),
        }
        for name, call in calls.items():
            try:
                result = call()
            except Fired as exc:
                raise AssertionError(f"{name}: {exc} — the guard did not stop it") from None
            assert result is None, (
                f"{name} returned {result!r} in transcribe-only mode; every caller "
                f"treats these as None-returning and the guard must not change that"
            )

        # Falsifiability: with the flag OFF the same calls MUST reach the sentinel.
        # If they do not, the sentinels are in the wrong place and the half above
        # proves nothing. Only the four that open a client first are exercised —
        # the two token-gated ones would bail on a missing token, not on the guard.
        cp.TRANSCRIBE_ONLY = False
        for name in ("update_inspiration_library", "create_calendar_task",
                     "update_book_tracker", "_write_manual_tasks_to_inbox"):
            try:
                calls[name]()
            except Fired:
                continue
            raise AssertionError(
                f"{name} did not reach the sentinel with the flag OFF — this test "
                f"cannot prove the guard is what stopped it"
            )
    finally:
        urllib.request.urlopen = real_urlopen
        cp.TRANSCRIBE_ONLY = False
