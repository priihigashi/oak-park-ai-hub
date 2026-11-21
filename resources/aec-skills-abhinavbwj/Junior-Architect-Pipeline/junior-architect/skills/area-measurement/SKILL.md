---
name: area-measurement
description: Measuring building areas correctly for area schedules. Covers area standards (IPMS, RICS, DIN 277, ANSI/BOMA), internal versus centreline boundaries, units, arcs, nested rooms, and exporting room geometry from Rhino or Revit for the check_areas checker. Use for area-schedule tasks and any area figure.
---

# Area measurement

## Name the standard first
Areas are meaningless until the standard is named. The common ones differ:

| Standard | Scope | Main measures |
|---|---|---|
| **IPMS** (International Property Measurement Standards) | All buildings | IPMS 1 (external), IPMS 2 (to the internal dominant face), IPMS 3 (occupier's exclusive area) |
| **RICS Code of Measuring Practice** (UK and Commonwealth) | Property measurement | GEA, GIA, NIA. RICS adopts IPMS for offices and residential. |
| **DIN 277** (Germany) | Building areas | BGF (gross), NRF (net room area), NUF (usable), with TF (technical) and VF (circulation) |
| **ANSI/BOMA Z65 series** (North America) | Office and other building types | Building-type methods |

Record the standard and the boundary in `.jap/project.json` (`area_standard`, `area_definition`). Never mix standards in one schedule.

## Boundaries
- **Internal face:** the inside face of the enclosing walls. Typical for net and usable areas.
- **Centreline:** the middle of the wall. It overstates a room's area by half the wall thickness times the perimeter.
- A room drawn to the wrong boundary passes a naive check. That is why `check_areas` compares the boundary flag with the project definition.

## Export format for `check_areas`
`rooms.json` is a list, one object per room:
```json
{"name": "Studio A", "number": "0.01", "layer": "ROOMS", "closed": true, "units": "mm",
 "boundary": "internal", "has_arcs": false, "vertices": [[0,0],[6000,0],[6000,4500],[0,4500]]}
```
- **Rhino through MCP:** read the closed curves on the rooms layer, then the control points of each polyline in document units. Set `has_arcs` when any segment is an arc, or divide arcs into segments short enough to keep the error under 0.1%.
- **Revit through MCP:** read room boundary segments. Values arrive in **feet**, so set `units: "ft"`, or convert to mm in the export script and say so.
- `targets.csv` columns are `room,target_m2`, taken from the brief.

## What the checker catches
- open boundaries
- self-intersections
- duplicates
- nested rooms
- wrong layer
- wrong boundary definition
- arcs
- a reported area that differs from the recomputed one
- unit traps (ratios near 10.764, 92,903 and 1,000,000)
- name typos against the brief
- rooms missing from the brief
- deviations beyond the tolerance

## What it cannot catch
- Whether a space should count at all, such as a shaft, a void or a low-headroom zone. Rules for these differ by standard.
- Whether the brief's target was measured to the same standard. That is the junior's call; write it in the review.
