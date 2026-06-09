import React from "react";
import {
  AbsoluteFill,
  OffthreadVideo,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
} from "remotion";

/**
 * BeforeTheCut — FORMAT-025 "O Que Veio Antes / Before The Cut" reel.
 *
 * The deceptive-edit debunk: a viral clip was cut to flip its meaning.
 * We expose it by playing the manipulated cut against the UNCUT original —
 * including the seconds BEFORE the cut — so context is restored on screen.
 *
 * Three phases (driven by Sequence):
 *   1. [0 .. revealFrame)        manipulated cut plays alone (audio ON) + hook overlay.
 *   2. reveal card               brief "Agora o vídeo completo 👇" flash.
 *   3. [revealFrame .. end)      SPLIT — top = manipulated (MUTED), bottom = original
 *                                (audio ON — it IS the proof) + context band + captions.
 *
 * Why a separate composition from NewsReel:
 *   NewsReel = one video + TEXT proof cards in the bottom zone.
 *   BeforeTheCut = TWO videos stacked (cut vs uncut). Different mechanic, so a sibling
 *   composition. Layout constants / colors mirror NewsReel deliberately (shared look),
 *   re-declared locally to keep NewsReel.tsx 100% untouched (MVP — extract to _shared.tsx later).
 *
 * Render trigger: render-beforethecut.yml (BeforeTheCutEN + BeforeTheCutPT passes).
 * Props built by: build_beforethecut_props.py.
 */

// ─── LAYOUT (mirrors NewsReel.tsx) ──────────────────────────────────────────────
const W = 1080;
const H = 1920;
const HALF_Y = H / 2;          // 960px — equal top/bottom split for dual video
const DIVIDER_H = 4;
const PAD = 72;
const HOOK_FRAMES = 150;        // 5s at 30fps
const REVEAL_CARD_FRAMES = 24;  // ~0.8s flash at the reveal

const C = {
  obsidian: "#0E0D0B",
  paper: "#F2ECE0",
  accent: "#F4C430",   // canario gold — same as Rachadinha / NewsReel
  blood: "#8B1A1A",
  margin: "#6B6560",
};

export interface CaptionEntry {
  startFrame: number;   // PHASE-2-LOCAL frames (aligned to the original playing from frame 0)
  endFrame: number;
  text: string;
}

export interface BeforeTheCutProps {
  manipulatedSrc: string;       // local file in /public — the cut as posted
  originalSrc: string;          // local file in /public — uncut window (already starts a few sec early)
  originalStartFrame?: number;  // playback offset inside originalSrc (default 0 — preroll baked into the download)
  revealFrame: number;          // when the split appears
  totalFrames: number;
  hook: string;
  contextText: string;          // "what he was actually talking about"
  captions: CaptionEntry[];
  language: "en" | "pt";
  creatorHandle?: string;       // who posted the manipulated cut
  sourceLabel: string;          // "Fonte: TV Câmara — 14:32"
}

// ─── HOOK INTRO (phase 1 overlay) ───────────────────────────────────────────────
const HookIntro: React.FC<{ hook: string; frame: number }> = ({ hook, frame }) => {
  const opacity = interpolate(
    frame,
    [0, 8, HOOK_FRAMES - 12, HOOK_FRAMES],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: W,
        height: H,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "rgba(11,11,12,0.62)",
        opacity,
        padding: `0 ${PAD}px`,
        zIndex: 10,
      }}
    >
      <div
        style={{
          fontFamily: "Fraunces, serif",
          fontWeight: 700,
          fontSize: 104,
          color: C.paper,
          lineHeight: 1.05,
          textAlign: "center",
          textShadow: "0 4px 24px rgba(0,0,0,0.95)",
        }}
      >
        {hook}
      </div>
    </div>
  );
};

// ─── REVEAL CARD (between phase 1 and phase 2) ──────────────────────────────────
const RevealCard: React.FC<{ language: "en" | "pt"; localFrame: number }> = ({
  language,
  localFrame,
}) => {
  const opacity = interpolate(
    localFrame,
    [0, 6, REVEAL_CARD_FRAMES - 6, REVEAL_CARD_FRAMES],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const text = language === "pt" ? "Agora o vídeo completo 👇" : "Now watch the full video 👇";
  return (
    <AbsoluteFill
      style={{
        background: C.obsidian,
        opacity,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 20,
      }}
    >
      <div
        style={{
          fontFamily: "Fraunces, serif",
          fontWeight: 700,
          fontSize: 88,
          color: C.accent,
          textAlign: "center",
          padding: `0 ${PAD}px`,
          lineHeight: 1.1,
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};

// ─── CAPTION (burned-in, over original zone in phase 2) ─────────────────────────
const Caption: React.FC<{ captions: CaptionEntry[]; localFrame: number }> = ({
  captions,
  localFrame,
}) => {
  const active = captions.find((c) => localFrame >= c.startFrame && localFrame < c.endFrame);
  if (!active) return null;
  return (
    <div
      style={{
        position: "absolute",
        bottom: 120,
        left: PAD,
        right: PAD,
        background: "rgba(0,0,0,0.6)",
        padding: "12px 20px",
        color: C.paper,
        fontFamily: "Inter, sans-serif",
        fontWeight: 500,
        fontSize: 38,
        lineHeight: 1.4,
        textAlign: "center",
        textShadow: "0 2px 8px rgba(0,0,0,0.9)",
      }}
    >
      {active.text}
    </div>
  );
};

// ─── ZONE LABEL (small chip identifying each video) ─────────────────────────────
const ZoneLabel: React.FC<{ text: string; top: number; tone: "cut" | "real" }> = ({
  text,
  top,
  tone,
}) => (
  <div
    style={{
      position: "absolute",
      top: top + 20,
      left: PAD,
      background: tone === "cut" ? C.blood : C.accent,
      color: tone === "cut" ? C.paper : C.obsidian,
      fontFamily: "'JetBrains Mono', monospace",
      fontWeight: 700,
      fontSize: 24,
      letterSpacing: 1,
      padding: "6px 14px",
      borderRadius: 4,
      zIndex: 15,
    }}
  >
    {text}
  </div>
);

// ─── MAIN COMPOSITION ───────────────────────────────────────────────────────────
export const BeforeTheCut: React.FC<BeforeTheCutProps> = ({
  manipulatedSrc,
  originalSrc,
  originalStartFrame = 0,
  revealFrame,
  totalFrames,
  hook,
  contextText,
  captions,
  language,
  creatorHandle,
  sourceLabel,
}) => {
  const frame = useCurrentFrame();

  const cutLabel = language === "pt" ? "O CORTE" : "THE CUT";
  const realLabel = language === "pt" ? "O ORIGINAL" : "THE ORIGINAL";
  const splitStart = revealFrame + REVEAL_CARD_FRAMES;

  return (
    <AbsoluteFill style={{ background: C.obsidian }}>
      {/* ── PHASE 1: manipulated cut alone, audio ON ── */}
      <Sequence from={0} durationInFrames={revealFrame}>
        <OffthreadVideo
          src={manipulatedSrc}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
        {creatorHandle ? <ZoneLabel text={`@${creatorHandle}`} top={0} tone="cut" /> : null}
        {hook ? <HookIntro hook={hook} frame={frame} /> : null}
      </Sequence>

      {/* ── REVEAL CARD ── */}
      <Sequence from={revealFrame} durationInFrames={REVEAL_CARD_FRAMES}>
        <RevealCardWrapper language={language} />
      </Sequence>

      {/* ── PHASE 2: split — top muted cut, bottom uncut original (audio ON) ── */}
      <Sequence from={splitStart} durationInFrames={Math.max(1, totalFrames - splitStart)}>
        <SplitPhase
          manipulatedSrc={manipulatedSrc}
          originalSrc={originalSrc}
          originalStartFrame={originalStartFrame}
          captions={captions}
          contextText={contextText}
          sourceLabel={sourceLabel}
          cutLabel={cutLabel}
          realLabel={realLabel}
        />
      </Sequence>
    </AbsoluteFill>
  );
};

// RevealCard needs its own local frame (relative to its Sequence) → small wrapper.
const RevealCardWrapper: React.FC<{ language: "en" | "pt" }> = ({ language }) => {
  const localFrame = useCurrentFrame();
  return <RevealCard language={language} localFrame={localFrame} />;
};

// SplitPhase reads its own local frame (relative to the phase-2 Sequence) so
// caption timings + original playback line up regardless of revealFrame.
const SplitPhase: React.FC<{
  manipulatedSrc: string;
  originalSrc: string;
  originalStartFrame: number;
  captions: CaptionEntry[];
  contextText: string;
  sourceLabel: string;
  cutLabel: string;
  realLabel: string;
}> = ({
  manipulatedSrc,
  originalSrc,
  originalStartFrame,
  captions,
  contextText,
  sourceLabel,
  cutLabel,
  realLabel,
}) => {
  const localFrame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: C.obsidian }}>
      {/* TOP — the manipulated cut, MUTED + slightly desaturated to read as "the lie" */}
      <div
        style={{ position: "absolute", top: 0, left: 0, width: W, height: HALF_Y, overflow: "hidden" }}
      >
        <OffthreadVideo
          src={manipulatedSrc}
          muted
          style={{ width: "100%", height: "100%", objectFit: "cover", filter: "grayscale(0.4)" }}
        />
        <ZoneLabel text={cutLabel} top={0} tone="cut" />
      </div>

      {/* DIVIDER */}
      <div
        style={{ position: "absolute", top: HALF_Y - DIVIDER_H / 2, left: 0, width: W, height: DIVIDER_H, background: C.accent, zIndex: 12 }}
      />

      {/* BOTTOM — the uncut original, audio ON (the proof) */}
      <div
        style={{ position: "absolute", top: HALF_Y, left: 0, width: W, height: H - HALF_Y, overflow: "hidden" }}
      >
        <OffthreadVideo
          src={originalSrc}
          startFrom={originalStartFrame}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
        <ZoneLabel text={realLabel} top={HALF_Y} tone="real" />
        <Caption captions={captions} localFrame={localFrame} />
      </div>

      {/* CONTEXT BAND — what they were actually talking about */}
      {contextText ? (
        <div
          style={{
            position: "absolute",
            top: HALF_Y - 4,
            left: 0,
            width: W,
            transform: "translateY(-100%)",
            background: "rgba(14,13,11,0.82)",
            color: C.paper,
            fontFamily: "Inter, sans-serif",
            fontWeight: 600,
            fontSize: 32,
            lineHeight: 1.3,
            padding: `18px ${PAD}px`,
            zIndex: 11,
          }}
        >
          {contextText}
        </div>
      ) : null}

      {/* SOURCE LABEL — bottom strip */}
      {sourceLabel ? (
        <div
          style={{
            position: "absolute",
            bottom: 28,
            left: PAD,
            right: PAD,
            textAlign: "center",
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 24,
            color: C.margin,
            zIndex: 14,
          }}
        >
          {sourceLabel}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
