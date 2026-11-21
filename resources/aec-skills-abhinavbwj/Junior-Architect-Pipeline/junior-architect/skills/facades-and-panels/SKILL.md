---
name: facades-and-panels
description: Facade modules, curtain walls, panelisation and fabrication parts. Covers modules and grids, unitised versus stick systems, glass and transport size limits, panel type rationalisation, planarity and cold bending, unrolling and nesting on stock sheets. Use for facade-and-curtain-wall and fabrication-prep tasks.
---

# Facades and panels

## Module first
The facade module ties together:
- the structural grid;
- the room widths;
- the glass sizes;
- the panel's fabrication and transport limits.

The junior chooses it, and predicts how many panel types it produces, before anything is modelled.

## Limits to set in `project.json` `fabrication`

| Limit | What sets it |
|---|---|
| Maximum panel width and height | Glass plate (float glass is commonly made in plates of about 3.2 × 6 m), the IGU manufacturer's limit, the road transport envelope, crane capacity. Use the supplier's figures. |
| Minimum width | The smallest panel the system can make. Smaller panels are slivers. |
| Maximum number of types | The budget. Every new type costs tooling and checking. |
| Maximum planarity deviation | What a flat panel can take by cold bending in the chosen system. |

## Free-form surfaces
Double-curved glazing is expensive. Planar quad panels need a mesh whose faces are flat. Conical meshes (Liu, Pottmann and others, 2006) are one family that allows it.
- Measure each panel's deviation from its best-fit plane (the four-point twist for quads).
- Panels above the cold-bend limit need curved glass or re-meshing.

## Fabrication parts
- `unroll` developable surfaces. Doubly curved surfaces distort when unrolled; flag them.
- Label every part. A part without a label gets lost on site.
- Check every flat part against the stock sheet sizes (`fabrication.stock`). Rotation is allowed.
- `check_panels` reports oversize parts, slivers, non-planar panels, parts that fit no stock sheet, and type counts over the limit.
