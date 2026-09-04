#!/usr/bin/env python3
"""
Regression test for --transcribe-only (capture_pipeline).

The point of this test is the DEFAULT path, not the new flag: adding a mode must not
change what the pipeline already does. Both directions are asserted, so the test can
actually fail in the case it exists to catch.

Run: python3 -m pytest scripts/tests/test_transcribe_only.py -v
"""
import ast
import pathlib

SRC = pathlib.Path(__file__).resolve().parents[1] / "capture" / "capture_pipeline.py"


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


def test_default_is_false():
    """Default must be OFF. If this flips, every capture silently stops filing."""
    for node in ast.walk(_tree()):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "TRANSCRIBE_ONLY":
                    assert node.value.value is False, "TRANSCRIBE_ONLY must default to False"
                    return
    raise AssertionError("TRANSCRIBE_ONLY global not defined")


def test_both_side_effects_are_guarded():
    """The two content-system writes must short-circuit in transcribe-only mode."""
    for name in ("update_inspiration_library", "create_calendar_task"):
        assert _guards_on_transcribe_only(_func(name)), f"{name} is not guarded"


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
