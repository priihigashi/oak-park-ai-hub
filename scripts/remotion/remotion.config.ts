import { Config } from "@remotion/cli/config";

// Entry point must be declared here — Remotion 4 does NOT read the
// `remotion.entryPoint` field in package.json, so without this every
// `remotion studio` / `remotion render` invocation fails to resolve a root.
Config.setEntryPoint("src/Root.tsx");

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
