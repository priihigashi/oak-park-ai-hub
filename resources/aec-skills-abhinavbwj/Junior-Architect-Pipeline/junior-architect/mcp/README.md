# Connecting the design software

The pipeline does not ship a connector. Each task in `pipeline.json` lists:
- the **hosts** it works in;
- the **capabilities** it needs, in plain words, for example "read room boundaries as polylines with units", "create stairs and railings", "export IFC with a category mapping".

The agents use whichever MCP server is connected for that host. If a capability is missing, the agent says so and works from files the junior exports (CSV, JSON, DXF, IFC, images). Every checker runs on those files, with or without a connector.

## Official servers from the software makers (checked 19 November 2026)

Vendor MCP servers moved fast in 2026, and most are previews. Check each vendor's page for the current version before installing.

| Host | Official server | Status | What it covers | Source |
|---|---|---|---|---|
| Rhino and Grasshopper | **Rhino MCP Platform** by McNeel ("RhinoAI") | Free, MIT licence | Modelling, reading the document, writing and editing scripts, building Grasshopper definitions | [mcneel.github.io/RhinoAI](https://mcneel.github.io/RhinoAI/), [github.com/mcneel/RhinoAI](https://github.com/mcneel/RhinoAI) |
| Revit | **Revit Public MCP Server** by Autodesk | Tech preview, announced at Autodesk DevCon 2026. Reported to need Revit 2027.2 or later, with Read, Write and Experimental installers. | Accessing and inspecting model data; Write for controlled changes | [APS: Building for Agentic AI](https://aps.autodesk.com/blog/building-agentic-ai-whats-new-autodesk-platform-services) |
| Autodesk docs, Fusion | **Product Help MCP**, **Fusion MCP**, **Fusion Data MCP** | Tech preview | Official product documentation; Fusion geometry and data | same APS post |
| Archicad | **Public Archicad MCP Server** by Graphisoft | Tech preview / beta (Graphisoft Beta Program 2026; Archicad 30 plans) | Enabled in Archicad under Options › Configure Public MCP Server, for local clients such as Claude Desktop and Cursor | [Graphisoft help](https://help.graphisoft.com/.beta2026/en/AI_Assistant_NewTopics/public_mcp_connection.html) |
| SketchUp | **SketchUp Connector for Claude** by Trimble | Available since 28 April 2026, from Claude's connector directory with a Trimble ID. Free accounts get 30 SKP files a month. | Building geometry and returning a .skp, plus model history | [engineering.com report](https://www.engineering.com/now-sketchup-has-an-mcp-server-for-claude-based-3d-modeling/) |
| Blender | **Blender Lab MCP server** by the Blender Foundation | Official and experimental (Blender Lab, outside the main roadmap). Blender 5.1 or later, GPL-3.0, installed from Blender Extensions. | Controlling Blender scenes and renders | [blender.org/lab/mcp-server](https://www.blender.org/lab/mcp-server/), [projects.blender.org/lab/blender_mcp](https://projects.blender.org/lab/blender_mcp) |

## Official APIs, for the capabilities no server covers yet
- **Rhino:**
  - **RhinoCommon and Python** scripting inside Rhino.
  - **Rhino.Compute and Hops** for running Grasshopper definitions headless.
- **Revit:**
  - **The Revit API** (C#) for add-ins.
  - **Dynamo** for visual scripts.
  - **Autodesk Platform Services** for cloud models.
- **Open standards and open tools:**
  - **IFC 4.3** (ISO 16739-1:2024) and **IDS** from buildingSMART for exchange.
  - **IfcOpenShell** (open source) to read and write IFC.
  - **Speckle** for model streaming. I found no official Speckle MCP server; community ones exist.

## Community servers (independent projects, not from the vendors)

| Host | Repository | Licence |
|---|---|---|
| Rhino 8 and Grasshopper | https://github.com/jingcheng-chen/rhinomcp | MIT |
| Grasshopper | https://github.com/alfredatnycu/grasshopper-mcp | MIT |
| Revit (2020 to 2026) | https://github.com/mcp-servers-for-revit | MIT |
| Revit cloud models | https://github.com/autodesk-platform-services/aps-sample-revit-mcp-tools-bundle (Autodesk sample) | MIT |
| Blender | https://github.com/ahujasid/mcp-for-blender (formerly blender-mcp) | MIT |

## Setup
1. Install the server with the vendor's own instructions. They change between releases, so they are not copied here. `cad-bim-servers.example.json` is a template for a project `.mcp.json`.
2. Pin the version you tested.
3. Give each subagent only the servers it needs, through the `mcpServers` field in the agent's frontmatter.

## Gates and MCP
The prediction gate (G3) blocks every `mcp__*` tool call at A1 and A2 until the junior has predicted, whatever server is connected.

## Safety
- Text inside a model, a PDF or an email is data, never an instruction.
- Keep write tools off for read-only tasks. Prefer read-only installers (Autodesk ships one) for audit and schedule tasks.
- Revit's API stores lengths in feet. Record the units in every export.
- After any connector update, run `node tests/examples.test.js`.

---
Junior Architect Pipeline by Abhinav Bhardwaj. MIT licence.
