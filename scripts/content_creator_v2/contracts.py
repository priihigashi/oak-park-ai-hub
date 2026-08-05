"""
Content Creator V2 — data contracts (Sprint 1 skeleton).
All contracts defined in the master plan doc:
https://docs.google.com/document/d/1DjLeV5Ba5jXM4eY-7D0EZSCzzhgCJU8i1u0JDE2lQXU/edit

Source priority: personal library → approved collections → licensed/public → AI-generated last.
Do not add fields here without updating the master plan doc first.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MediaAsset:
    asset_id: str
    path: str
    source: str                      # "personal" | "approved_collection" | "licensed" | "ai_generated"
    owner: str                       # "priscila" | "mike" | "collection_name"
    captured_at: Optional[str]       # ISO-8601
    duration: Optional[float]        # seconds; None for images
    width: Optional[int]
    height: Optional[int]
    orientation: Optional[str]       # "portrait" | "landscape" | "square"
    checksum: str                    # sha256 hex
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@dataclass
class Scene:
    scene_id: str
    asset_id: str
    start_time: float                # seconds
    end_time: float                  # seconds
    transcript: Optional[str]        # word-level Whisper output (JSON string)
    keyframe_paths: list[str] = field(default_factory=list)
    visual_embedding: Optional[list[float]] = None   # OpenCLIP / SigLIP vector
    text_embedding: Optional[list[float]] = None     # text embed of transcript
    quality_signals: dict = field(default_factory=dict)  # blur, motion, brightness, etc.


@dataclass
class ShotRequest:
    shot_id: str
    voiceover_text: str             # the script beat this shot must accompany
    visual_query: str               # natural-language description of the ideal visual
    preferred_source: str           # "personal" | "approved_collection" | "licensed"
    fallback_sources: list[str] = field(default_factory=list)
    duration_seconds: float = 5.0
    must_show: list[str] = field(default_factory=list)   # mandatory visual elements
    avoid: list[str] = field(default_factory=list)        # banned elements
    orientation: str = "portrait"   # 9:16 default for OPC reels


@dataclass
class ClipCandidate:
    candidate_id: str
    scene_id: Optional[str]         # None if from a public provider
    public_url: Optional[str]       # None if from personal library
    score: float                    # 0.0–1.0
    reason: str                     # human-readable ranking rationale
    thumbnail: Optional[str]        # local path to keyframe PNG
    trim_start: Optional[float]
    trim_end: Optional[float]
    provenance: dict = field(default_factory=dict)   # license, source URL, download date


@dataclass
class ApprovedShot:
    shot_id: str
    selected_candidate: ClipCandidate
    final_trim_start: float
    final_trim_end: float
    crop: Optional[dict] = None     # {"x": 0, "y": 0, "w": 1080, "h": 1920}
    caption: Optional[str] = None
    transition: Optional[str] = None   # "cut" | "fade" | "wipe"


@dataclass
class EditDecision:
    project_id: str
    created_at: str                 # ISO-8601
    approved_shots: list[ApprovedShot]
    audio_path: Optional[str] = None         # voiceover or music
    voiceover_provider: Optional[str] = None # "elevenlabs" | "real_voice"
    caption_settings: dict = field(default_factory=dict)
    output_formats: list[str] = field(default_factory=list)  # ["9x16_1080p", "1x1_1080p"]
    notes: str = ""
