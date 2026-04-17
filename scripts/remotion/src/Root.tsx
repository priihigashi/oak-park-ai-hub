import React from "react";
import { Composition } from "remotion";
import { SovereignReel, SovereignReelProps } from "./SovereignReel";

// Default props for development previews — overridden by --props in CI render
const defaultProps: SovereignReelProps = {
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
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="SovereignReelEN"
        component={SovereignReel}
        durationInFrames={900}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ ...defaultProps, language: "en" }}
      />
      <Composition
        id="SovereignReelPT"
        component={SovereignReel}
        durationInFrames={900}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ ...defaultProps, language: "pt" }}
      />
    </>
  );
};
