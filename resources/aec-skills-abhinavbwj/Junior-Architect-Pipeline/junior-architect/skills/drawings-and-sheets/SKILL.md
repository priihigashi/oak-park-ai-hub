---
name: drawings-and-sheets
description: Producing a drawing set in Revit. Covers the view set per stage, scales, where to cut sections, view templates and crops, dimensioning hierarchy, tags and keynotes, sheet layout, title blocks, revisions and PDF sets. Use for view-set, annotation and sheet-production tasks.
---

# Drawings and sheets

## The set follows the stage

| Stage | Drawings |
|---|---|
| Concept | Plans, sections and elevations at 1:200 or 1:100 |
| Spatial coordination | 1:100 and 1:50 general arrangements, with key sections through the parts that coordinate (cores, stairs, atria, roof) |
| Technical design | 1:50 general arrangements; 1:20, 1:10 and 1:5 details; schedules |

Write the office's list in `project.json` `view_requirements`.

## Sections explain
A section line is a decision. Cut through:
- the stair;
- the core;
- the change of level;
- the tallest space;
- the facade's typical bay.

Never cut where nothing happens. The junior draws the section lines.

## Views
- One template per view type and scale. A view without a template drifts.
- Crop to the drawing, and use scope boxes for repeated levels.
- Names follow the convention (`Level 01 - GA Plan - 1:100`), never "Section 1" or "Copy of".

## Dimensions
Set out in the order a builder works:
1. Grid.
2. Structure.
3. Openings.
4. Fit-out.

- Overall strings outside, then grid to grid, then openings.
- Strings close, so their parts add up to the overall.
- Spot levels on every floor, roof, threshold and external level.

## Tags and keynotes
- Every door, window and room is tagged. Coverage is set in `tag_coverage`.
- Keynotes need a legend on the sheet.
- Clean overlaps before issue.

## Sheets
- **Content:** the title block fields (project, number, title, scale, revision, status, drawn, checked, date) are complete, and number and status follow the naming convention.
- **Layout:** the drawing at the top left, notes and key plan at the right, the title block bottom right.
- **Revisions:** every change after first issue gets a revision and a cloud.
- **Issue:** the sheet set and the PDF export.
