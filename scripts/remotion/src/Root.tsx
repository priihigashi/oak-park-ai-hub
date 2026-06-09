import React from "react";
import { Composition, registerRoot } from "remotion";
import { NewsReel, NewsReelProps } from "./NewsReel";
import { CarouselMotion, CarouselMotionProps } from "./CarouselMotion";
import { CarouselReel, CarouselReelProps } from "./CarouselReel";
import {
  EvidenceCompilation,
  EvidenceCompilationProps,
  evidenceCompilationDefaultProps,
} from "./EvidenceCompilation";
import { BeforeTheCut, BeforeTheCutProps } from "./BeforeTheCut";

// Default props for development previews — overridden by --props in CI render
const defaultProps: NewsReelProps = {
  videoSrc: "./public/source_clip.mp4",
  videoStartFrame: 0,
  proofSlides: [
    {
      headline: "1953. CIA OVERTHREW IRAN'S DEMOCRACY.",
      fact: "Operation AJAX removed democratically elected PM Mossadegh.",
      source: "CIA declassified files, 2013",
      startFrame: 90,
      durationFrames: 150,
    },
  ],
  captions: [],
  language: "en",
  totalFrames: 900,
  speakerName: "Marianne Williamson",
  speakerRole: "Author & Activist",
  topicTitle: "REGIME CHANGE",
};

// CarouselMotion default props — overridden by --props in CI render.
// 1080x1350 matches Instagram carousel slide dimensions; 150 frames @ 30fps = 5s loop.
const carouselDefaultProps: CarouselMotionProps = {
  posterPng: "./public/poster_placeholder.png",
  clipSrc: undefined,
  hookText: undefined,
  accentColor: "#F4C430",
};

// FORMAT-025 BeforeTheCut default props — overridden by --props in CI render.
// Defaults render against placeholder clips for local preview only.
const beforeTheCutDefaultProps: BeforeTheCutProps = {
  manipulatedSrc: "./public/manipulated.mp4",
  originalSrc: "./public/original.mp4",
  originalStartFrame: 0,
  revealFrame: 150,
  totalFrames: 900,
  hook: "Cortaram o começo deste vídeo.",
  contextText: "",
  captions: [],
  language: "pt",
  sourceLabel: "",
};

const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="NewsReelEN"
        component={NewsReel}
        durationInFrames={900}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ ...defaultProps, language: "en" }}
      />
      <Composition
        id="NewsReelPT"
        component={NewsReel}
        durationInFrames={900}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ ...defaultProps, language: "pt" }}
      />
      <Composition
        id="CarouselMotion"
        component={CarouselMotion}
        durationInFrames={150}
        fps={30}
        width={1080}
        height={1350}
        defaultProps={carouselDefaultProps}
      />
      <Composition
        id="CarouselReel"
        component={CarouselReel}
        durationInFrames={150 * 7}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ slides: [], slideDurationFrames: 150 } as CarouselReelProps}
      />
      <Composition
        id="EvidenceCompilation"
        component={EvidenceCompilation}
        durationInFrames={Math.max(
          30,
          Math.round((evidenceCompilationDefaultProps.duration_seconds || 24) * 30)
        )}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={evidenceCompilationDefaultProps as EvidenceCompilationProps}
      />
      <Composition
        id="BeforeTheCutEN"
        component={BeforeTheCut}
        durationInFrames={900}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ ...beforeTheCutDefaultProps, language: "en", hook: "They cut the start of this video." }}
      />
      <Composition
        id="BeforeTheCutPT"
        component={BeforeTheCut}
        durationInFrames={900}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ ...beforeTheCutDefaultProps, language: "pt" }}
      />
    </>
  );
};

registerRoot(RemotionRoot);
