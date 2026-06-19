# Maya / Call Assistants — pilot software layer

McFolling voice agents (APPROVED — ACTIVE 2026-06-19). This package is the provider-agnostic
logic + safety controls. It is fully unit-tested **without** a live Retell/Twilio account.

## Modules
- `config.py` — locked decisions, secret NAMES, guardrail constants.
- `escalation.py` — call-until-answered (Priscila 3×@2min → Michael), voicemail≠answered, kill switch.
- `webhook_auth.py` — HMAC signature verification (fail closed).
- `notes.py` — guest note schema, urgency rubric, dedup.
- `safety.py` — consent, RE4 outbound compliance gate, errand authorization, rate/cost caps, retention/PII.
- `requirements.py` — RM/RE → test traceability map.
- `agent_prompts/` — guest prompt, errand prompt, property KB template.
- `retell_agent_config.json` — import once the Retell account/key exists.

## Run the tests
```
cd oak-park-ai-hub && python3 -m pytest tests/test_maya_*.py -q
```

## Going live — required external setup (true blockers; not code)
1. **MF_RETELL_API_KEY** — create Retell account + a Retell-managed US number; add the secret.
2. **MF_RETELL_WEBHOOK_SECRET**, **MF_PRISCILA_PHONE**, **MF_MICHAEL_PHONE** — add as secrets.
3. **Publish the OAuth app** (stops 7-day token death).
4. **Airbnb ingestion (RM-pipeline)** — validate notification emails first (what content/identity/
   reply capability exists), then wire the chosen route. Until validated, guest capture is gated.
5. **Fill one property KB** (`agent_prompts/property_kb_template.md`) and share with the SA.

## Acceptance + rollback (RM18)
Pilot passes when, on ONE property: routine Qs auto-answered from KB with no hallucination;
urgent → escalation reaches a human or fires fallback within policy; every inbound creates a
note; disclosure+consent on 100% of calls. **Rollback:** flip `MF_MAYA_KILL_SWITCH=1` to stop
all calls instantly; pause if any safety/compliance test regresses or cost cap is hit.

## Monitoring (RM13) & number distribution (RM17)
- Reuse the `mcfolling_token_healthcheck.yml` pattern for a Maya health check that emails on outage.
- Decide how guests receive the pilot number (listing message / check-in instructions) before launch.
