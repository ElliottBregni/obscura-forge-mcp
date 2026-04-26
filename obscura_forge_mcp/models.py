"""Curated catalog of fal.ai endpoints, grouped by modality.

Aliases are short stable names users (and the agent) pass to tools. The
underlying fal.ai endpoint slugs change occasionally — update them here in
one place when fal renames or retires a model.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Modality = Literal["image", "image_edit", "video", "music", "speech"]


@dataclass(frozen=True)
class ModelSpec:
    alias: str
    model: str
    modality: Modality
    description: str
    output_ext: str


CATALOG: tuple[ModelSpec, ...] = (
    # ---------- image: text-to-image ----------
    ModelSpec(
        "flux-schnell",
        "fal-ai/flux/schnell",
        "image",
        "FLUX.1 [schnell] — fast 4-step diffusion, cheap and good default.",
        "png",
    ),
    ModelSpec(
        "flux-dev",
        "fal-ai/flux/dev",
        "image",
        "FLUX.1 [dev] — higher quality than schnell, ~2× slower.",
        "png",
    ),
    ModelSpec(
        "flux-pro",
        "fal-ai/flux-pro/v1.1-ultra",
        "image",
        "FLUX.1.1 [pro] ultra — top-tier quality, paid tier.",
        "png",
    ),
    ModelSpec(
        "sd3",
        "fal-ai/stable-diffusion-v3-medium",
        "image",
        "Stable Diffusion 3 medium.",
        "png",
    ),
    ModelSpec(
        "recraft",
        "fal-ai/recraft-v3",
        "image",
        "Recraft v3 — strong on text rendering and vector style.",
        "png",
    ),
    # ---------- image: edit / image-to-image ----------
    ModelSpec(
        "flux-redux",
        "fal-ai/flux-pro/v1.1-ultra/redux",
        "image_edit",
        "FLUX redux — variation conditioned on an input image.",
        "png",
    ),
    ModelSpec(
        "flux-canny",
        "fal-ai/flux-pro/v1/canny",
        "image_edit",
        "FLUX canny — structure-preserving edit using edge map.",
        "png",
    ),
    # ---------- video ----------
    ModelSpec(
        "kling",
        "fal-ai/kling-video/v1.6/standard/text-to-video",
        "video",
        "Kling 1.6 — strong physics & motion, 5–10s clips.",
        "mp4",
    ),
    ModelSpec(
        "luma",
        "fal-ai/luma-dream-machine",
        "video",
        "Luma Dream Machine — cinematic style.",
        "mp4",
    ),
    ModelSpec(
        "minimax",
        "fal-ai/minimax-video",
        "video",
        "Hailuo Minimax video — broad capability text→video.",
        "mp4",
    ),
    ModelSpec(
        "mochi",
        "fal-ai/mochi-v1",
        "video",
        "Genmo Mochi 1 — open-weights, expressive motion.",
        "mp4",
    ),
    ModelSpec(
        "hunyuan",
        "fal-ai/hunyuan-video",
        "video",
        "Tencent HunyuanVideo — open-weights, longer clips.",
        "mp4",
    ),
    # ---------- music + sfx ----------
    ModelSpec(
        "stable-audio",
        "fal-ai/stable-audio",
        "music",
        "Stability Stable Audio — text→music + SFX, up to 47s.",
        "wav",
    ),
    ModelSpec(
        "musicgen",
        "cassetteai/music-generator",
        "music",
        "Cassette MusicGen — fast text-to-music.",
        "wav",
    ),
    # ---------- speech / TTS ----------
    ModelSpec(
        "elevenlabs",
        "fal-ai/elevenlabs/tts/multilingual-v2",
        "speech",
        "ElevenLabs Multilingual v2 — top-tier TTS, voice cloning.",
        "mp3",
    ),
    ModelSpec(
        "cartesia",
        "fal-ai/cartesia/tts",
        "speech",
        "Cartesia Sonic — low-latency TTS.",
        "mp3",
    ),
    ModelSpec(
        "playai",
        "fal-ai/playai/tts/v3",
        "speech",
        "PlayAI TTS v3 — natural voices, voice cloning.",
        "mp3",
    ),
)


DEFAULTS: dict[Modality, str] = {
    "image": "flux-schnell",
    "image_edit": "flux-redux",
    "video": "kling",
    "music": "stable-audio",
    "speech": "elevenlabs",
}


def by_alias(alias: str) -> ModelSpec | None:
    return next((m for m in CATALOG if m.alias == alias), None)


def by_modality(modality: Modality) -> tuple[ModelSpec, ...]:
    return tuple(m for m in CATALOG if m.modality == modality)
