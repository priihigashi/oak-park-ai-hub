# Junior Architect Pipeline

A Claude Code plugin that runs a junior architect's production work as a gated pipeline. It has **45 tasks in eight families**:
- brief and site;
- regulation;
- 3D modelling, BIM and Grasshopper;
- drafting and documentation;
- schedules;
- visualisation;
- coordination;
- administration.

The tasks run across RIBA stages 0 to 7, with AIA and HOAI equivalents.

**How it works:**
- 17 specialist subagents drive Rhino, Grasshopper, Revit and Blender through whichever MCP servers you connect. Without one, they work from exported files.
- 20 deterministic checkers recompute every output: areas, stairs, panels, Grasshopper state, views, tags, DXF layers and units, IFC entities, quantities, sun positions, boards, clashes, regulations.
- Hooks keep every judgement step with the junior: they predict first, review the redline and build a learning record.

## Install

```
/plugin marketplace add abhinavbwj/Junior-Architect-Pipeline
/plugin install junior-architect@junior-architect-marketplace
```
To try it without installing: `claude --plugin-dir ./junior-architect`. Then, in a project folder: `/junior-architect:setup`.

## The 45 tasks

| Family | Tasks |
|---|---|
| Brief and site | brief-digest, site-dossier, site-model |
| Regulation and envelope | code-research, planning-constraints, buildable-envelope, regulation-check |
| 3D modelling, BIM and Grasshopper | massing-study, bim-setup, building-model, stairs-and-cores, facade-and-curtain-wall, families, grasshopper-definition, fabrication-prep |
| Drafting and documentation | view-set, annotation, detailing, sheet-production, rhino-2d-drawings, dwg-export, drawing-qa, sheet-register |
| Schedules and quantities | area-schedule, room-data-sheets, door-schedule, window-schedule, quantity-takeoff |
| Visualisation and presentation | viewport-captures, sun-shadow-study, materials, rendering, photo-match, diagrams, presentation-board |
| Analysis, coordination and exchange | daylight-and-sun, clash-detection, model-audit, apartment-mix, ifc-export |
| Specification and construction administration | spec-section, rfi-response, submittal-review, meeting-minutes, site-visit-report |

`pipeline.json` gives each task:
- its stages and autonomy ceiling;
- its agent, skill and checker;
- the hosts it works in and the capabilities it needs from them;
- the judgement the junior keeps;
- its failure modes.

Each task is a slash command, for example `/junior-architect:stairs-and-cores A2`. `/junior-architect:stage <n>` runs a whole stage.

## Seven layers

| Layer | Files | Job |
|---|---|---|
| Context | `CLAUDE.md`, `.jap/project.json` | Units, area standard, stair rules, fabrication limits, view and tag requirements, CAD standard, render rules, clash tolerance, IFC schema, naming, status codes |
| Procedure | `skills/` (24) | How each task is done, and the standard it rests on |
| Isolation | `agents/` (17) | Each subagent gets only the tools its job needs |
| Tools | Any connected MCP server | Rhino, Grasshopper, Revit, Archicad, SketchUp and Blender. The official vendor servers (McNeel, Autodesk, Graphisoft, Trimble, Blender Lab) and community ones are listed in `mcp/README.md`; each task states the capabilities it needs |
| Gates | `hooks/hooks.json`, `scripts/gate.js` | Five gates that hold whatever the model decides |
| Verification | `scripts/jap.js`, `scripts/checks/` | 20 checkers that recompute from raw exports |
| Judgement | `prediction.md`, `review.md`, `learning_log.csv` | The junior's record |

## The gates

| Gate | Rule |
|---|---|
| G1 | Claude cannot write the junior's prediction or review, by any tool, including the CLI through the shell |
| G2 | Only the checker writes the report, the run state and the learning log |
| G3 | At A1 and A2, no MCP call and no write into the run before the prediction |
| G4 | Claude cannot finish while a deliverable has no checker report |
| G5 | Checkers and gates are read-only during a run |

## Tested
`node junior-architect/tests/examples.test.js` runs all 20 checkers on seeded-fault examples and asserts exactly which faults each one reports. All 20 cases pass.

Examples of what the checkers report:
- **Stairs:** 2R+G out of range, uneven risers, a total rise that does not equal the floor-to-floor height.
- **DXF:** a drawing in metres instead of millimetres, entities on layer 0, text off the ISO 3098 series.
- **IFC:** an IFC4 file where IFC4X3 is required, proxies, a missing storey, an unnamed space.
- **Sun studies:** a sun at an impossible position for Oslo on 21 June, computed with the NOAA solar equations.

In use, an area-schedule run stays closed to the data until the junior has recorded a prediction, then returns the checker's redline for the junior to review.

## Requirements
- Claude Code.
- The scripts are Node only, with no packages to install.
- For modelling tasks: an MCP server for your host that provides the capabilities each task lists. `mcp/README.md` lists the official vendor servers (McNeel's Rhino MCP Platform, Autodesk's Revit Public MCP Server, Graphisoft's Public Archicad MCP Server, Trimble's SketchUp Connector, Blender Lab's MCP server) and community ones. Tasks also run on exported files.
- Chrome for board composition.

## Author

Created by **Abhinav Bhardwaj**, architect, urban designer and computational designer.
- GitHub: [abhinavbwj](https://github.com/abhinavbwj)
- Web: [abhinavbhardwaj.com](https://abhinavbhardwaj.com)

## Licence
MIT © 2026 Abhinav Bhardwaj. See [LICENSE](LICENSE).
