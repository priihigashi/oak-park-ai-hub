---
name: analysis
description: Quick design analyses a junior runs. Covers daylight metrics (window-to-floor ratio, daylight factor, spatial daylight autonomy, EN 17037), sun hours on outdoor space, unit mix and minimum sizes, and writing metrics and rules files for check_metrics. Use for daylight-and-sun and apartment-mix tasks.
---

# Analysis

## Use the metric the code names
Daylight is regulated with different metrics in different places:

| Metric | What it is |
|---|---|
| Window or glass area to floor area ratio | A simple prescriptive check in some codes |
| Daylight factor | Interior illuminance as a percentage of an unobstructed overcast sky |
| Spatial daylight autonomy and annual sunlight exposure | Climate-based metrics in IES LM-83 |
| EN 17037 | European targets for daylight provision, view, sunlight exposure and glare |

Name the metric and the clause in `daylight_rules.json`. Never replace a climate-based requirement with a ratio silently.

## Include what blocks the light
Neighbouring buildings, balconies above, deep reveals. A daylight result without the context is optimistic by construction.

## Sun on outdoor space
Some codes and guides require a share of outdoor space to receive sun for a number of hours on a named date. Use the real site, true north and that date.

## Unit mix
- Count units by type and size against the brief.
- Measure to the brief's area standard.
- Check minimum sizes and dual aspect only where the plan truly gives two aspects.

## Files for `check_metrics`
- `*_metrics.json`: the measured values.
- `*_rules.json`: one rule per requirement, with an operator, a limit and a source.
