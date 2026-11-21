---
name: construction-admin
description: Construction-stage junior work. Covers RFI responses, submittal and shop-drawing reviews, and site visit reports, with the check_refs and check_minutes formats. Use for rfi-response, submittal-review and site-visit-report tasks.
---

# Construction administration

## RFI responses
- The junior writes the intent of the answer in one sentence first.
- Cite the **current** revision of every drawing referenced. `check_refs` compares each reference against `sheets.csv`. It flags references to sheets that do not exist and to superseded revisions.
- An answer that changes scope, cost or programme says so plainly and goes to the senior.
- Wording that commits the architect contractually ("we will pay", "the architect will accept liability", "guarantee", "warrant") is flagged by the checker, because the contract decides those questions.

## Submittal reviews
- Compare the submittal with the specification section and the drawings in force.
- List every deviation and substitution, naming the clause it departs from.
- Recommend one status from the office's stamps, for example "no exceptions taken", "make corrections noted", "revise and resubmit" or "rejected".
- Never accept a substitution silently.
- Reviewing against a superseded specification is a common, costly failure. Confirm the issue being used.

## Site visit reports
Use an `## Observations` or `## Defects` table: Item | Owner | Due | Location.

`check_minutes` flags rows without an owner, rows without a YYYY-MM-DD date, and defects without a location. Reference photos by file name. The junior writes their three observations before reading the agent's report.
