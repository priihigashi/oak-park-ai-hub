"""
Requirement -> delivery/test traceability map (RM1-18, RE1-4).

coverage type:
  unit  -> covered by a unit test (test_file named).
  spec  -> covered by a written spec in a prompt/template/config (no pure code path).
  ops   -> an operational decision/runbook step (human-owned), documented.

The test_maya_requirements suite asserts: no requirement is missing, and every `unit`
item points at a test file that actually exists.
"""
from __future__ import annotations

REQUIREMENTS: dict[str, dict] = {
    # ---- Maya (guest line) ----
    "RM1":  {"desc": "Capture guest note", "type": "unit", "ref": "test_maya_notes.py"},
    "RM2":  {"desc": "Auto-answer common Q", "type": "spec", "ref": "agent_prompts/guest_agent_prompt.md"},
    "RM3":  {"desc": "Urgent escalation (call until answered)", "type": "unit", "ref": "test_maya_escalation.py"},
    "RM4":  {"desc": "Human-sounding voice (measured)", "type": "spec", "ref": "retell_agent_config.json"},
    "RM5":  {"desc": "Definition of urgent (rubric)", "type": "unit", "ref": "test_maya_notes.py"},
    "RM6":  {"desc": "AI + recording disclosure & consent", "type": "unit", "ref": "test_maya_safety.py"},
    "RM7":  {"desc": "Note destination + schema", "type": "unit", "ref": "test_maya_notes.py"},
    "RM8":  {"desc": "Duplicate-message handling", "type": "unit", "ref": "test_maya_notes.py"},
    "RM9":  {"desc": "Webhook authentication", "type": "unit", "ref": "test_maya_webhook_auth.py"},
    "RM10": {"desc": "Voicemail detection (!= answered)", "type": "unit", "ref": "test_maya_escalation.py"},
    "RM11": {"desc": "Kill switch", "type": "unit", "ref": "test_maya_safety.py"},
    "RM12": {"desc": "Cost / rate limits", "type": "unit", "ref": "test_maya_safety.py"},
    "RM13": {"desc": "Failure monitoring", "type": "ops", "ref": "README.md (reuse health-check pattern)"},
    "RM14": {"desc": "Data retention / deletion", "type": "unit", "ref": "test_maya_safety.py"},
    "RM15": {"desc": "Language behavior", "type": "spec", "ref": "agent_prompts/guest_agent_prompt.md"},
    "RM16": {"desc": "Transfer / fallback", "type": "spec", "ref": "agent_prompts/guest_agent_prompt.md"},
    "RM17": {"desc": "Guest gets the number", "type": "ops", "ref": "README.md (distribution)"},
    "RM18": {"desc": "Pilot rollback conditions", "type": "spec", "ref": "README.md"},
    # ---- Errand agent ----
    "RE1":  {"desc": "Call authorization (no booking/payment)", "type": "unit", "ref": "test_maya_safety.py"},
    "RE2":  {"desc": "Disclosure & recording consent", "type": "unit", "ref": "test_maya_safety.py"},
    "RE3":  {"desc": "Structured report-back", "type": "spec", "ref": "agent_prompts/errand_agent_prompt.md"},
    "RE4":  {"desc": "Outbound AI-call compliance gate", "type": "unit", "ref": "test_maya_safety.py"},
}


def missing_ids() -> list[str]:
    """Return any expected RM/RE id not present in the map (gap detector)."""
    expected = [f"RM{i}" for i in range(1, 19)] + [f"RE{i}" for i in range(1, 5)]
    return [rid for rid in expected if rid not in REQUIREMENTS]
