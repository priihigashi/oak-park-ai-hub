---
name: schedules
description: Door, window and room schedules and room data sheets produced from the model and checked against it. Covers the required fields, marks, model exports and the check_schedule format. Use for door-schedule, window-schedule and room-data-sheets tasks.
---

# Schedules and room data sheets

## Principle
A schedule is a view of the model. It is never a separate document typed beside it. Export the elements, generate the schedule from the export, then check the schedule against a fresh export.

## Exports for `check_schedule`
- `model_doors.json`, `model_windows.json` or `model_rooms.json`: a list of objects, each with `mark` (or `number`) and the scheduled parameters as the model holds them.
- The schedule CSV: one row per element, with the columns in `.jap/project.json` under `required_fields`.

The checker reports:
- duplicate marks;
- elements in the model but missing from the schedule, and elements in the schedule but missing from the model (a stale schedule);
- empty required fields;
- every value that differs between the schedule and the model.

## What a junior should know about each schedule

**Doors**
- The fire rating follows the wall or compartment line it sits in, never the door type alone.
- The clear width differs from the leaf width, and accessibility rules govern the clear width.
- Ironmongery sets carry the escape, accessibility and security requirements.

**Windows**
- Thermal (U-value), solar (g-value) and acoustic performance come from the energy and acoustic strategy.
- Opening size is measured to a stated reference: structural opening or frame.

**Room data sheets**
- Finishes, ceiling height, services and environmental conditions per room, consistent with the room type.
- Fill one sheet by hand per room type before the agent fills the rest.
