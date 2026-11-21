---
name: site-modelling
description: Building a site model that can be trusted. Covers georeferencing, true north and project north, datums, survey versus open data (OpenStreetMap, terrain datasets), context buildings, and site metrics for check_metrics. Use for site-model tasks.
---

# Site modelling

## Sources, in order of trust
1. A measured topographical survey: always primary.
2. Official cadastre and national mapping (parcel boundaries, building footprints).
3. Open data:
   - OpenStreetMap for streets and buildings: completeness and accuracy vary by place, so check coverage;
   - terrain models such as the Copernicus DEM (about 30 m) or EU-DEM (25 m), for context only.

Label every element of the model with its source. A 25 m terrain model is never presented as a survey.

## Position and orientation
- **Georeferencing.** Record the coordinate system (national grid, or UTM zone) and a survey point.
- **North.** True north differs from project north. Record the angle. Sun studies and solar access use true north.
- **Datum.** Every height is measured from a stated datum: national datum or site datum. Planning heights often use a specific datum, so read the planning constraints.

## Site metrics for `check_metrics`
Export `site_metrics.json`:
- parcel area;
- elevation minimum and maximum;
- north angle;
- context buildings imported.

Write `site_rules.json` from the survey and cadastre, for example "parcel area within 1% of 4,102 m², source: cadastre extract 2026-10".

The junior writes the parcel area, the level difference and true north before the model is built. Each one is then checked.
