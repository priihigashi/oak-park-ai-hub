---
name: grasshopper
description: Building Grasshopper definitions that others can read, rerun and trust. Covers dataflow design, naming, data trees (graft, flatten, simplify), referencing instead of internalising, clusters, baking to layers, and checking runtime state. Use for grasshopper-definition tasks and any parametric definition.
---

# Grasshopper

## Design the dataflow before the canvas
On paper, write:
- inputs: what is read from Rhino or set by sliders;
- operations: in order;
- outputs: what is baked or exported.

One definition does one job.

## Readability
- **Names.** Every slider and parameter says what it is, with units: "Floor height (mm)". The checker flags unnamed sliders.
- **Layout.** The canvas flows left to right, with groups labelled by stage.
- **Clusters** hold reusable parts, with named inputs and outputs.

## Data trees
Most wrong results are silent tree errors.
- Graft makes one branch per item, flatten collapses all branches, simplify removes redundant path levels.
- Write down the expected item count and path structure at each stage, and compare them with what the definition reports.
- A count that differs from the expectation is a bug even when nothing turns red.

## References
- **Reference** geometry from the Rhino model, so the definition follows the design.
- **Internalised** geometry is frozen at the moment it was internalised. The checker warns on it.
- Random components take a fixed seed, so results can be reproduced.

## Run and check
1. Solve the definition.
2. Read every component's runtime state. Each one should show no errors and no unexplained warnings.
3. Export `gh_export.json` and run `check_gh`.
4. Bake to named layers and save the definition next to the Rhino file.

Rhino.Compute and Hops can run definitions headless when the office needs it.
