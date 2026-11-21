---
name: visualisation
description: Honest architectural visualisation. Covers eye-level cameras and lenses, aerials and parallel axonometrics, real sun positions for the site and date, verified views and photomontage, real materials, context, renders in Rhino, Revit and Blender, diagrams, and presentation boards. Use for viewport-captures, sun-shadow-study, materials, rendering, photo-match, diagrams and presentation-board tasks.
---

# Visualisation

An image is a claim about the future place. The checker tests the parts of that claim that can be measured.

## Cameras
- **Eye level:** 1.5 to 1.75 m above the viewer's ground.
- **Lens:** 24 to 50 mm full-frame equivalent. Below 24 mm, spaces look larger and deeper than they will feel.
- **Verified views:** for planning, follow the planning authority's methodology. In the UK, for example, the Landscape Institute's Technical Guidance Note 06/19 sets out visualisation types and photography standards.
- **Axonometrics:** parallel projection. Aerials state their height.
- **Record** every camera in `renders.json`.

## Sun
The sun is never set "where it looks good". Use:
- the site's latitude and longitude;
- the time zone, including daylight saving;
- the date and local time.

`check_render` computes the real azimuth and altitude (NOAA solar position equations) and fails any scene sun more than 2° away. Typical sun-study set: equinox and both solstices at 09:00, 12:00 and 15:00.

## Materials and context
- **Materials:** real products, with colours sampled from product images and textures at true scale.
- **Context:** from the site model. No invented neighbours, trees or weather.
- **People and cars** at true scale. Never fewer or more of them than the place will have.

## Diagrams
One diagram, one argument (circulation, structure, program, phasing, sun). Colour needs a legend. Show it on the real plan or a real section, never as an abstract graph.

## Boards
- Every image carries a caption and a source or credit.
- Every drawing carries a scale bar, and every plan a north point.
- Text is at least 3 mm at print size.
- Write `board.json`, run `check_board`, then compose with `board.js` (PDF and PNG through headless Chrome).
