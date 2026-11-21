---
name: stairs-and-cores
description: Designing and checking stairs and cores. Covers the Blondel step rule (2R+G), riser and going limits from the code in force, flights and landings, headroom, uniform risers, widths for escape, and core planning. Use for stairs-and-cores tasks and any stair in a model.
---

# Stairs and cores

## Do the arithmetic by hand first
1. Floor-to-floor height ÷ the maximum riser = the minimum number of risers. Round up.
2. Riser = floor-to-floor ÷ risers, and every riser in a flight is equal.
3. Going from the step rule, checked against the code minimum.
4. Number of flights from the code's maximum risers per flight. Landings between flights.
5. Plan length = goings × (risers − 1 per flight) + landings.

## The step rule
François Blondel (*Cours d'architecture*, 1675) related riser and going to the human stride: **2R + G ≈ 600 to 650 mm**. Many codes and guides use a range around it. The project sets the range in `stair_rules`.

## Limits come from the code in force
Every code sets its own values for:
- maximum riser and minimum going;
- maximum pitch;
- minimum width (often driven by escape occupancy);
- minimum headroom;
- maximum risers per flight;
- handrail heights;
- landing lengths.

These differ by use (private, common or public) and by jurisdiction. Enter them per use in `.jap/project.json` `stair_rules`, each from a quoted clause in a checked `code-research` run. The checker's defaults are placeholders and say so.

## What `check_stairs` catches
- 2R+G outside the range;
- risers over the maximum, goings under the minimum, widths under the minimum;
- low headroom and steep pitch;
- flights with too many risers;
- total rise that does not equal floor to floor;
- uneven risers within a flight.

## Cores
A core carries:
- stairs and lifts;
- risers and shafts;
- toilets;
- fire-fighting provisions where required.

Check escape travel distances against the code, and keep the core stacked through every floor.
