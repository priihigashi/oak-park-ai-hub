#!/usr/bin/env python3
"""Static security regression tests for Capture Pipeline v2 workflow.

These tests guard three properties that are easy to regress during workflow edits:
1. workflow_dispatch string inputs never become shell source;
2. Actions are referenced immutably by full commit SHA;
3. GITHUB_TOKEN permissions stay explicitly constrained.
"""
import pathlib
import re

WORKFLOW = (
    pathlib.Path(__file__).resolve().parents[2]
    / ".github"
    / "workflows"
    / "capture_pipeline.yml"
)


def _text():
    return WORKFLOW.read_text()


def _capture_run_body(txt):
    match = re.search(
        r"- name: Run capture pipeline.*?\n\s+run:\s*\|\n(?P<body>.*?)(?=\n\s+- name:)",
        txt,
        re.DOTALL,
    )
    assert match, "Run capture pipeline shell block not found"
    return match.group("body")


def test_dispatch_inputs_are_not_interpolated_into_shell_source():
    """workflow_dispatch strings must reach Bash as data via env/argv, not `${{ }}`.

    Direct expression interpolation inside a `run:` block can turn crafted input
    into shell syntax. The capture step handles high-value secrets, so this is a
    hard security boundary rather than a style preference.
    """
    txt = _text()
    body = _capture_run_body(txt)

    assert "${{ inputs." not in body, (
        "workflow_dispatch input is interpolated directly into the capture shell block"
    )
    assert "eval " not in body, "capture shell block must never eval a constructed command"
    assert 'cmd=(python scripts/capture/capture_pipeline.py "$CAPTURE_URL"' in body
    assert '"${cmd[@]}"' in body

    for env_name, input_name in (
        ("CAPTURE_URL", "url"),
        ("CAPTURE_PROJECT", "project"),
        ("CAPTURE_STORY_ID", "story_id"),
        ("CAPTURE_NOTES", "notes"),
        ("CAPTURE_CREDITS", "credits"),
        ("CAPTURE_MODE", "mode"),
        ("CAPTURE_URL2", "url2"),
        ("CAPTURE_URL2_ROLE", "url2_role"),
        ("CAPTURE_PROJECTS", "projects"),
    ):
        expected = f"{env_name}:"
        expression = "${{ inputs." + input_name + " }}"
        assert expected in txt and expression in txt, (
            f"{input_name} is not passed through the environment as inert data"
        )


def test_all_actions_are_pinned_to_full_commit_sha():
    """A mutable tag can be retargeted; full 40-char SHAs are immutable refs."""
    refs = re.findall(r"^\s*uses:\s*([^\s#]+)", _text(), flags=re.MULTILINE)
    assert refs, "no uses: references found"

    unpinned = []
    for ref in refs:
        if ref.startswith("./"):
            continue
        if "@" not in ref:
            unpinned.append(ref)
            continue
        _action, revision = ref.rsplit("@", 1)
        if not re.fullmatch(r"[0-9a-fA-F]{40}", revision):
            unpinned.append(ref)

    assert not unpinned, f"mutable/non-SHA action refs: {unpinned}"


def test_github_token_permissions_are_explicitly_constrained():
    """Current architecture needs Actions write for downstream dispatches only."""
    txt = _text()
    match = re.search(
        r"\n\s{4}permissions:\s*\n(?P<body>(?:\s{6}.+\n)+)",
        txt,
    )
    assert match, "capture job has no explicit permissions block"

    permissions = {}
    for line in match.group("body").splitlines():
        key, value = [part.strip() for part in line.split(":", 1)]
        permissions[key] = value

    assert permissions == {"actions": "write", "contents": "read"}, (
        f"unexpected GITHUB_TOKEN permissions: {permissions}"
    )


def test_checkout_does_not_persist_credentials():
    txt = _text()
    checkout = re.search(
        r"- name: Checkout oak-park-ai-hub.*?(?=\n\s+- name:)",
        txt,
        re.DOTALL,
    )
    assert checkout, "checkout step not found"
    assert "persist-credentials: false" in checkout.group(0)
