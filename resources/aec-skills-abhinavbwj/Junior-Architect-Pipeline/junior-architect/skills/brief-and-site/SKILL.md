---
name: brief-and-site
description: Turning a client brief or site pack into traceable requirements, conflicts, gaps and design drivers. Covers the check_trace format. Use for brief-digest and site-dossier tasks.
---

# Brief and site

## Traceability
Every requirement in the digest carries a verbatim quote from the source and a page:

`- Lecture hall: "a 120-seat lecture hall with level access" (p.1)`

`check_trace` fails:
- any bullet in `## Requirements` without a quote;
- any quote that does not appear verbatim in the source text.

That makes invented requirements and changed numbers visible.

## Structure

| Section | What goes in it |
|---|---|
| `## Requirements` | One bullet per requirement, quoted. |
| `## Conflicts` | Requirements that contradict each other, the budget or the site, with both quotes. |
| `## Gaps` | What a designer needs that the brief omits: area standard, occupancy, budget basis, programme, sustainability targets, accessibility level. |
| `## Drivers` | The three requirements that shape the plan. Kept separate, so the junior can compare it with their own ranking. |

## Site dossier
Each figure names its source and date. Typical figures:
- parcel area and boundaries;
- zoning;
- heights and setbacks;
- heritage and environmental designations;
- flood risk;
- ground conditions;
- utilities;
- access;
- orientation and climate data.

Prefer official sources (cadastre, planning portal, national mapping agency). Flag any figure older than five years.
