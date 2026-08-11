# Remotion runtime

This is a nested npm package. Keep its dependency lifecycle separate from the repository-root pnpm quality tooling.

## Supported runtime

Use Node 24 LTS or newer. The project intentionally has no upper Node engine ceiling.

## Reproducible install

```bash
cd scripts/remotion
npm ci --include=dev
```

Do not regenerate `package-lock.json` casually. When dependencies intentionally change, update `package.json` and the lockfile together and run the typecheck before committing.

## Checks

```bash
npm run typecheck
```

## Render entry point

`remotion.config.ts` declares `src/Root.tsx` as the package entry point. CI may also pass `src/Root.tsx` explicitly to the Remotion CLI.

Example:

```bash
npx remotion render src/Root.tsx EvidenceCompilation out/evidence.mp4 --props=props.json
```
