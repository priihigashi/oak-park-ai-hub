---
name: bim-coordination
description: Federated models, clash detection and IFC exchange. Covers clash types and matrices, tolerances, ownership and approval, BCF, IFC 4.3 (ISO 16739-1:2024), exchange requirements and IDS, proxies, storeys, spaces and units. Use for clash-detection and ifc-export tasks.
---

# BIM coordination

## Clashes
- **Types:**
  - hard: elements occupy the same space;
  - clearance: maintenance or insulation space is infringed;
  - workflow: sequence or time conflicts.
- **Clash matrix:** which discipline and category is tested against which. Testing everything against everything produces noise.
- **Tolerance:** small overlaps below the tolerance (`clash_tolerance_mm`) are usually modelling noise. Agree the value with the team.
- **Ownership:** every open clash beyond the tolerance has an owner. Every approved clash has a named approver. Issues travel between tools as BCF.

## IFC exchange
- **IFC 4.3** is published as ISO 16739-1:2024. Use the schema the exchange requirements name.
- **IDS** (Information Delivery Specification, buildingSMART) states what an exchange must contain and can be checked automatically.
- **`check_ifc`** reads the STEP file and reports:
  - the schema;
  - element counts against the model;
  - the share of `IfcBuildingElementProxy`;
  - storeys;
  - unnamed spaces;
  - the length unit.
- **Proxies** mean elements lost their category on export. Fix the category mapping; never accept a model full of proxies.
- **Viewer check:** the junior opens the IFC in a free viewer and checks one storey and one door by hand. A file that passes the checker can still carry wrong properties.
