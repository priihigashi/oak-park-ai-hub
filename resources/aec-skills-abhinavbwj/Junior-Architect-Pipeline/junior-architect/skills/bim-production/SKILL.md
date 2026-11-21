---
name: bim-production
description: Building the Revit model properly. Covers templates and project setup, levels and grids, wall location lines and joins, room bounding, type and instance parameters, families on reference planes, worksets, and Level of Information Need (ISO 7817-1). Use for bim-setup, building-model and families tasks.
---

# BIM production

## Setup
1. Start from the office template: units, view templates, line styles, title blocks, browser organisation.
2. **Levels:** names and elevations follow the office convention. Decide finished floor level against structural slab level and model to one consistently.
3. **Grids:** from the structural strategy, named in the office pattern (numbers one way, letters the other).
4. **Coordinates:** shared coordinates and survey point before linking anything.

## Walls
- **Location line.** Revit offers wall centreline, core centreline, finish face exterior and interior, and core face. Choose the one the plan is dimensioned to. A wall drawn to the wrong line shifts every room by half a wall.
- **Joins.** Walls must join, or rooms will not bound. After creating walls, read the model warnings and fix every "room not enclosed".
- **Types.** Real compound types with layers and materials. Never "Generic - 200mm" in a model past concept.

## Rooms
Place rooms only in enclosed spaces. Room bounding elements (walls, floors, separation lines) decide the area. Export rooms for `check_areas` after every change to walls.

## Families
- Build on reference planes, lock geometry to them, and flex every parameter before loading.
- **Category** decides scheduling and IFC export. Choose it deliberately.
- **Parameters:** type parameters for what varies by type, instance parameters for what varies by placement.
- Names follow the office convention (`required_fields.families`).

## Information
Model to the Level of Information Need the exchange requires (ISO 7817-1:2024): geometry, information and documentation per purpose. Do not over-model. Never under-model what someone downstream relies on.
