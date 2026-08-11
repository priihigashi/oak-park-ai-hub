"""
Content Creator V2 — visual + text embedding module (Sprint 3, coding order step 4 of 10).

Uses OpenCLIP (ViT-B/32) to generate 512-dim embeddings for keyframe PNGs and
transcript text. Stores results in catalog.scenes.visual_embedding /
text_embedding as JSON arrays.

Run embed_all(catalog) before searching to ensure indexed scenes have embeddings.
Scenes without keyframes are skipped for visual embeddings; scenes without
transcripts are skipped for text embeddings.

Install dependency: pip install open_clip_torch torch Pillow

Master plan: https://docs.google.com/document/d/1DjLeV5Ba5jXM4eY-7D0EZSCzzhgCJU8i1u0JDE2lQXU/edit
"""

from __future__ import annotations

import json
import logging
from typing import Optional

from .catalog import Catalog
from .contracts import Scene

logger = logging.getLogger(__name__)

_MODEL_NAME = "ViT-B-32"
_PRETRAINED = "openai"

# Module-level lazy cache — model is loaded once per process (heavy init ~1-2s)
_clip_model = None
_clip_preprocess = None
_clip_tokenizer = None


def _load_clip():
    """Load OpenCLIP ViT-B/32 and cache. Raises RuntimeError if not installed."""
    global _clip_model, _clip_preprocess, _clip_tokenizer
    if _clip_model is not None:
        return _clip_model, _clip_preprocess, _clip_tokenizer

    try:
        import open_clip
    except ImportError:
        raise RuntimeError(
            "open_clip_torch is not installed. Run: pip install open_clip_torch torch"
        )

    model, _, preprocess = open_clip.create_model_and_transforms(
        _MODEL_NAME, pretrained=_PRETRAINED
    )
    model.eval()
    tokenizer = open_clip.get_tokenizer(_MODEL_NAME)
    _clip_model, _clip_preprocess, _clip_tokenizer = model, preprocess, tokenizer
    logger.info("OpenCLIP %s loaded", _MODEL_NAME)
    return model, preprocess, tokenizer


def embed_image(image_path: str) -> Optional[list[float]]:
    """
    Return a 512-dim L2-normalised visual embedding for a keyframe PNG.
    Returns None on any error (missing file, bad image, missing dependency).
    """
    try:
        import torch
        from PIL import Image

        model, preprocess, _ = _load_clip()
        img = preprocess(Image.open(image_path).convert("RGB")).unsqueeze(0)
        with torch.no_grad():
            feat = model.encode_image(img)
            feat = feat / feat.norm(dim=-1, keepdim=True)
        return feat[0].tolist()
    except Exception as exc:
        logger.warning("embed_image failed for %s: %s", image_path, exc)
        return None


def embed_text(text: str) -> Optional[list[float]]:
    """
    Return a 512-dim L2-normalised text embedding using the OpenCLIP text encoder.
    Lives in the same vector space as embed_image(), enabling cross-modal search.
    """
    try:
        import torch

        model, _, tokenizer = _load_clip()
        tokens = tokenizer([text])
        with torch.no_grad():
            feat = model.encode_text(tokens)
            feat = feat / feat.norm(dim=-1, keepdim=True)
        return feat[0].tolist()
    except Exception as exc:
        logger.warning("embed_text failed: %s", exc)
        return None


def _transcript_to_text(raw: str) -> str:
    """Extract plain text from Whisper JSON output, falling back to the raw string."""
    try:
        return json.loads(raw).get("text", "").strip()
    except (json.JSONDecodeError, TypeError):
        return str(raw).strip()


def embed_scene(scene: Scene, catalog: Catalog) -> bool:
    """
    Compute any missing embeddings for a scene and persist them to the catalog.
    Returns True if at least one embedding was added or updated.
    """
    updated = False

    if scene.visual_embedding is None and scene.keyframe_paths:
        vec = embed_image(scene.keyframe_paths[0])
        if vec is not None:
            scene.visual_embedding = vec
            updated = True

    if scene.text_embedding is None and scene.transcript:
        text = _transcript_to_text(scene.transcript)
        if text:
            vec = embed_text(text)
            if vec is not None:
                scene.text_embedding = vec
                updated = True

    if updated:
        catalog.upsert_scene(scene)

    return updated


def embed_all(catalog: Catalog) -> tuple[int, int]:
    """
    Generate and store embeddings for every scene in the catalog that is missing them.
    Skips scenes that already have both embeddings.

    Returns:
        (updated, skipped) counts.
    """
    updated = skipped = 0
    for asset in catalog.all_assets():
        for scene in catalog.scenes_for_asset(asset.asset_id):
            needs_visual = scene.visual_embedding is None and bool(scene.keyframe_paths)
            needs_text = scene.text_embedding is None and bool(scene.transcript)
            if not needs_visual and not needs_text:
                skipped += 1
                continue
            if embed_scene(scene, catalog):
                updated += 1
            else:
                skipped += 1
    logger.info("embed_all complete: updated=%d skipped=%d", updated, skipped)
    return updated, skipped


def main(argv: list[str] | None = None) -> None:
    import argparse
    from .catalog import DEFAULT_DB

    parser = argparse.ArgumentParser(
        description="Generate OpenCLIP embeddings for all indexed scenes.",
        epilog="Example: python -m scripts.content_creator_v2.embedder --embed-all",
    )
    parser.add_argument(
        "--embed-all", action="store_true",
        help="Embed all scenes in the catalog that are missing embeddings.",
    )
    parser.add_argument(
        "--db", default=str(DEFAULT_DB),
        help=f"Path to catalog DB (default: {DEFAULT_DB})",
    )
    args = parser.parse_args(argv)

    if not args.embed_all:
        parser.print_help()
        return

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    with Catalog(Path(args.db)) as catalog:
        stats = catalog.stats()
        print(f"Catalog: {stats['assets']} assets, {stats['scenes']} scenes")
        print("Embedding scenes (this may take a few minutes on first run)…")
        updated, skipped = embed_all(catalog)
        print(f"Done — updated: {updated}, already embedded: {skipped}")


if __name__ == "__main__":
    from pathlib import Path
    import logging
    main()
