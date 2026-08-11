# JS/TS quality-gate enforcement

Effective 2026-08-11. `docs/QUALITY_BASELINE.md` remains the historical debt inventory captured on 2026-08-05; this document defines what CI actually enforces.

## Complexity gate

- ESLint complexity threshold: 10.
- Existing JS/TS debt is recorded in `eslint-suppressions.json` using ESLint's native bulk-suppression format.
- CI runs plain `pnpm quality:js`; no suppression-generation flag is used in CI.
- A new file with an above-threshold function fails immediately.
- A baselined file fails when its number of `complexity` violations rises above the stored count.
- When legacy violations are removed, CI reports stale suppressions; run `pnpm quality:js:prune` and commit the smaller suppression file.

### Important limitation

ESLint bulk suppressions are keyed by file + rule + violation count. They do **not** preserve the identity or numeric complexity of each historical function. Therefore the gate does not guarantee that an already-suppressed function cannot move, for example, from complexity 12 to 20 while the file still has the same number of complexity violations.

That is an intentional simplification for the first enforcement phase. If per-function non-regression becomes a requirement, add a value-aware differential check rather than describing native suppressions as providing that guarantee.

## Recorded JS/TS suppression counts

| File | Existing complexity violations |
|---|---:|
| `scripts/blog-generator.js` | 7 |
| `scripts/research.js` | 4 |
| `scripts/fill-missing.js` | 1 |
| `scripts/gsc-sync.js` | 1 |
| `scripts/remotion/export_slides.js` | 1 |
| `scripts/remotion/src/EvidenceCompilation.tsx` | 1 |
| `scripts/remotion/src/NewsReel.tsx` | 1 |
| **Total** | **16** |

The WordPress credential pre-flight added to `scripts/blog-generator.js` on 2026-08-10 has only three decision branches and does not add an above-threshold complexity violation, so the historical count of seven remains valid when the August 5 baseline is reconciled with current `main`.

## Runtime policy

- Supported project baseline: Node 24 LTS.
- `package.json` and `scripts/remotion/package.json` intentionally use `engines.node: >=24` with no artificial upper ceiling.
- Root quality tooling stays on pnpm and `pnpm-lock.yaml`.
- Remotion stays a nested npm package with its own committed `package-lock.json`.
- Dedicated Remotion CI installs with `npm ci --include=dev`.

Python/Ruff enforcement is not enabled by this workflow. The Python inventory in `QUALITY_BASELINE.md` remains debt data until its own no-regression rollout is defined.
