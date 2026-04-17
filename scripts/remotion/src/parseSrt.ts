/**
 * parseSrt.ts — parse an SRT string into frame-indexed caption entries
 * Used by render-props-builder.py to convert Whisper SRT output to Remotion props.
 */

export interface CaptionEntry {
  startFrame: number;
  endFrame: number;
  text: string;
}

/** Convert SRT timestamp (HH:MM:SS,mmm) to seconds */
function srtTimeToSeconds(ts: string): number {
  const [hms, ms] = ts.split(",");
  const [h, m, s] = hms.split(":").map(Number);
  return h * 3600 + m * 60 + s + Number(ms) / 1000;
}

/** Parse SRT string to CaptionEntry array at given FPS */
export function parseSrt(srtContent: string, fps: number): CaptionEntry[] {
  const blocks = srtContent.trim().split(/\n\n+/);
  const entries: CaptionEntry[] = [];

  for (const block of blocks) {
    const lines = block.trim().split("\n");
    if (lines.length < 3) continue;
    const timeLine = lines[1];
    const match = timeLine.match(
      /(\d{2}:\d{2}:\d{2},\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2},\d{3})/
    );
    if (!match) continue;
    const startSec = srtTimeToSeconds(match[1]);
    const endSec = srtTimeToSeconds(match[2]);
    const text = lines.slice(2).join(" ").trim();
    entries.push({
      startFrame: Math.round(startSec * fps),
      endFrame: Math.round(endSec * fps),
      text,
    });
  }
  return entries;
}
