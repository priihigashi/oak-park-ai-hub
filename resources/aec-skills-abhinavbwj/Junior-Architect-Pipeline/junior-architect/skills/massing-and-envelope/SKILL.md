---
name: massing-and-envelope
description: Buildable envelopes, massing studies and regulation checks. Covers GFA and FAR definitions, height limits and datums, setbacks, angle and sky-exposure planes, coverage, strategies versus shapes, and the rules file for check_metrics. Use for buildable-envelope, massing-study and regulation-check tasks.
---

# Massing and envelope

## The envelope comes from the rules
Build the envelope from the planning constraints of a checked `planning-constraints` run:
- the height limit and its datum;
- setbacks from named boundaries;
- angle or sky-exposure planes;
- the coverage limit;
- floor area ratio or gross floor area caps;
- protected views and corridors.

Every rule in `envelope_rules.json` names its source clause. A rule without a source cannot be defended.

## Definitions differ
- Gross floor area, floor area ratio and site coverage are defined differently by each jurisdiction: what counts (basements, balconies, shafts, plant), and where it is measured (external or internal face).
- Measure to the rule's own definition, and say which one.

## Massing alternatives are strategies
Alternatives differ in strategy, never only in shape. Strategies include:
- perimeter block;
- court;
- slab;
- point towers;
- terrace.

Each argues access, circulation, daylight, outdoor space and use. Triangles and arbitrary forms without that reasoning are not options.

## Metrics
Export metrics for `check_metrics` against the envelope and the brief:
- GFA, FAR, coverage and height;
- the number of storeys;
- sun hours on the outdoor space.

The junior predicts the maximum GFA the envelope allows before the model computes it. The gap between the two is the lesson.
