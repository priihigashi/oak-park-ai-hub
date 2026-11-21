---
description: Set up the Junior Architect Pipeline in this project; create .jap/ and record the project standards every checker reads.
argument-hint: [project name] [jurisdiction]
---

Set up the pipeline for this project. Engage the `office-standards` skill.

Arguments: $ARGUMENTS

1. Run the pipeline CLI `init` (its path is in this session's context). This creates `.jap/project.json`, `.jap/runs/` and `.jap/learning_log.csv`.
2. Interview the junior, or the senior if present, and fill in `.jap/project.json` one field at a time. Never guess a value:
   - project, jurisdiction, RIBA stage;
   - model units, and whether imperial sources are allowed;
   - the area standard and definition (internal face or centreline; IPMS, RICS, DIN 277 or ANSI/BOMA);
   - the area tolerance;
   - the rooms layer name;
   - the code documents in force, each with its edition and amendments;
   - the sheet naming pattern and status codes (the template follows the ISO 19650 UK National Annex fields; replace them with the office convention if it differs);
   - the required fields per schedule;
   - the escalation rule and the named senior.
3. Check that the MCP servers the project needs are connected (`claude mcp list`). If one is not, point to `mcp/README.md` in the plugin.
4. Suggest the first task for the current stage from `pipeline.json`.
