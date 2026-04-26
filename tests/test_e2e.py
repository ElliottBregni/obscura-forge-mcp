"""End-to-end tests that hit fal.ai for real.

Skipped automatically when FAL_KEY isn't set, so the default `pytest` run
stays free. Opt in with:

    FAL_KEY=<your-key> pytest tests/test_e2e.py -v

These tests cost real money — pennies, but real. They use the cheapest
default model in each modality (flux-schnell, stable-audio, cartesia).
Video is intentionally skipped by default because it's much more
expensive; pass `--run-video` to include it.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from obscura_forge_mcp import server

pytestmark = pytest.mark.skipif(
    not os.environ.get("FAL_KEY"),
    reason="FAL_KEY not set — skipping fal.ai end-to-end tests",
)


def _payload(result: object) -> dict:
    if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], dict):
        text = result[1].get("result")
        if isinstance(text, str):
            return json.loads(text)
    raise AssertionError(f"unexpected call_tool result: {type(result).__name__}")


def _assert_output_file(parsed: dict) -> None:
    assert "outputs" in parsed, f"no outputs in response: {parsed}"
    assert parsed["outputs"], "empty outputs list"
    first = parsed["outputs"][0]
    assert first.get("path"), f"no local path saved: {first}"
    p = Path(first["path"])
    assert p.exists(), f"file does not exist on disk: {p}"
    assert p.stat().st_size > 0, f"file is empty: {p}"


@pytest.mark.asyncio
async def test_e2e_generate_image_flux_schnell() -> None:
    mcp = server.build_server()
    result = await mcp.call_tool(
        "generate_image",
        {
            "prompt": "a single red apple on a white surface, studio lighting, photo",
            "model": "flux-schnell",
            "aspect_ratio": "1:1",
            "num_images": 1,
        },
    )
    parsed = _payload(result)
    _assert_output_file(parsed)
    assert parsed["model"] == "flux-schnell"


@pytest.mark.asyncio
async def test_e2e_generate_speech_cartesia() -> None:
    mcp = server.build_server()
    result = await mcp.call_tool(
        "generate_speech",
        {
            "text": "Hello from Obscura Forge.",
            "model": "cartesia",
        },
    )
    parsed = _payload(result)
    _assert_output_file(parsed)


@pytest.mark.asyncio
async def test_e2e_generate_music_short() -> None:
    mcp = server.build_server()
    result = await mcp.call_tool(
        "generate_music",
        {
            "prompt": "ambient pad, slow, calm",
            "duration_seconds": 5,
        },
    )
    parsed = _payload(result)
    _assert_output_file(parsed)


@pytest.mark.skipif(
    "--run-video" not in os.environ.get("PYTEST_ADDOPTS", ""),
    reason="video generation is expensive; opt in via PYTEST_ADDOPTS=--run-video",
)
@pytest.mark.asyncio
async def test_e2e_generate_video_kling() -> None:
    mcp = server.build_server()
    result = await mcp.call_tool(
        "generate_video",
        {
            "prompt": "a leaf falling slowly, soft natural light",
            "model": "kling",
            "duration_seconds": 5,
            "aspect_ratio": "16:9",
        },
    )
    parsed = _payload(result)
    _assert_output_file(parsed)
