---
name: drafting-standards
description: 2D drafting to standard. Covers ISO 128 line types and widths, ISO 3098 lettering heights, CAD layer conventions (ISO 13567, AIA CAD Layer Guidelines), plot scales, model-space units, hatching of cut material, Make2D clean-up and DXF/DWG exchange. Use for rhino-2d-drawings, dwg-export and any CAD drawing.
---

# Drafting standards

## Lines (ISO 128)
- **Widths:** a √2 series: 0.13, 0.18, 0.25, 0.35, 0.5, 0.7, 1.0, 1.4 and 2 mm. A drawing uses two or three widths in a fixed ratio.
- **Meaning, not decoration:**
  - cut elements heaviest;
  - visible edges beyond medium;
  - hidden and overhead lines dashed;
  - centre lines and grids chain.
- **The junior's step:** set the cut, beyond and below weights first. It is the first judgement of drawing.

## Lettering (ISO 3098)
- **Paper heights:** 1.8, 2.5, 3.5, 5, 7, 10, 14 and 20 mm.
- **Model-space height** = paper height × plot scale. At 1:100, 2.5 mm text is 250 mm in the model.
- `check_dxf` flags heights off the series at the project's plot scale.

## Layers
- **ISO 13567:** structured fields: agent responsible, element (often classified by Uniclass or a national table), presentation, with optional fields.
- **AIA CAD Layer Guidelines (US National CAD Standard):** discipline-major group-minor group, for example `A-WALL-FULL`, `A-DOOR`, `A-ANNO-DIMS`.
- **Office standards** often adapt one of these. Write the office pattern as a regular expression in `project.json` `cad.layer_pattern`. The checker applies it to every layer.
- **Layer 0** holds nothing in model space. It belongs inside block definitions only.

## Units and exchange
- Model space in millimetres for metric projects (`$INSUNITS` = 4). Check it on every exported file: a DWG in metres or inches silently rescales everyone's work.
- Export ASCII DXF for checking. Never explode text or dimensions on export.
- **Make2D in Rhino** produces duplicates and hidden lines on separate layers. Delete or re-layer them before issue. Join and simplify curves.

## Hatching
Hatch cut material by material (concrete, masonry, insulation, timber), to a pattern scale tied to the plot scale. Uncut surfaces stay unhatched unless the drawing type calls for it.
