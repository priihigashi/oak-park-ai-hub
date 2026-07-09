# Lead Capture AI Receptionist — Phase 1 Setup Brief
**Date:** 2026-07-09 | **Status:** Ready to execute | **Drafted by:** Daily Advancer

---

## Recommendation: GoodCall — Starter Plan ($59/mo)

**Why GoodCall over Rosie/Numa/Smith.ai:**
- Native Google Sheets integration — call logs write directly to your existing sheets (no Zapier)
- Construction-specific templates pre-built (contractor intake, estimate requests)
- $59/mo Starter covers unlimited minutes + 1 number (OPC only needs 1)
- Rosie ($41-49/mo) lacks Sheets-native; Smith.ai ($285+/mo) overkill for solo operation
- GoodCall handles job-seeker screening natively (filter "Are you calling about a job?" → different script branch)

**Phase 0 status:** DONE — vendor comparison completed, GoodCall selected.

---

## Phase 1: 10-Step Setup Checklist

1. **Sign up at goodcall.com** — Starter plan, use priscila@oakpark-construction.com
2. **Assign/port a phone number** — use a new local number or forward OPC main line
3. **Connect Google Sheets** — authorize GoodCall OAuth to write call logs to Ideas & Inbox sheet (`1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU`) → create tab `📞 Call Logs`
4. **Upload OPC call script** (see below)
5. **Configure business hours** — Mon–Fri 8AM–6PM CT; after-hours → voicemail + SMS confirmation
6. **Set job-seeker branch** — if caller says "job" or "work" → "We're not hiring right now but you can email your resume to priscila@oakpark-construction.com"
7. **Set estimate-request branch** — collect: name, address, project type (roof/siding/windows/gutters), timeline, best callback time
8. **Set emergency branch** — if caller says "emergency" or "urgent" → forward to Priscila's cell
9. **Test with 3 calls** — estimate request, job seeker, general inquiry — verify Sheets logging
10. **Go live** — update OPC Google Business Profile phone number to GoodCall number OR set call forward from existing number

---

## OPC Receptionist Call Script (load into GoodCall)

```
GREETING:
"Thank you for calling Oak Park Construction. This is the OPC assistant.
How can I help you today?"

[IF: estimate / quote / pricing / project]
→ "I'd love to get you connected with Priscila. Let me collect a few details."
→ "What's your name?" [collect]
→ "What's the project address?" [collect]
→ "What type of work are you looking to have done? 
   For example — roofing, siding, windows, gutters, or something else?" [collect]
→ "What's your timeline — are you looking to start in the next few weeks, 
   or is this a few months out?" [collect]
→ "What's the best number and time to reach you?" [collect]
→ "Perfect. I've logged your information and Priscila will reach out 
   within 1 business day. Is there anything else I can help with?"

[IF: job / hiring / work / application]
→ "Thanks for reaching out! Oak Park Construction isn't currently hiring,
   but you're welcome to send your resume to priscila@oakpark-construction.com
   and we'll keep it on file."

[IF: existing customer / project update / schedule]
→ "Let me take your name and project address and I'll make sure 
   Priscila's team follows up with you today."
→ [collect name + address + question]
→ "Got it — you'll hear back within a few hours. Thank you!"

[IF: emergency]
→ "I'm going to transfer you right now. One moment please."
→ [forward to Priscila's cell]

[DEFAULT / unclear]
→ "Let me take your name and number and Priscila will call you back 
   within 1 business day."
→ [collect name + number]
→ "You're all set. Thank you for calling Oak Park Construction!"
```

---

## Open Decisions (Only Priscila Can Resolve)

1. **Phone number strategy:** Forward existing OPC main line to GoodCall, OR get a new GoodCall number and update Google Business Profile? Forwarding = zero disruption. New number = cleaner tracking but requires GBP update.

2. **After-hours handling:** Voicemail-only (GoodCall records + transcribes), OR send Priscila an SMS summary for every after-hours call? SMS = more interruptions but zero missed leads.

3. **Estimate callback SLA:** The script says "1 business day" — is that accurate for OPC volume, or should it say "within a few hours" to set a stronger expectation?

---

## Phase 2 Preview (after Phase 1 is live)
- Connect GoodCall call log sheet to 4AM agent — agent auto-creates follow-up tasks for unanswered estimate requests
- Add SMS auto-reply via GoodCall when caller is sent to voicemail
- Review 30-day call log for patterns (peak hours, most common project type)

---
_Source doc: Lead Capture Master Plan `1KS_eJqE3PGrHyv87uwNU4xa8YkgOfakNybWDUD-oUH4`_
_Append this content to that doc once Composio googledocs connection is re-established._
