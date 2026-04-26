"""Smoke tests that don't hit fal.ai."""

from __future__ import annotations

import json

import pytest

from obscura_forge_mcp import models, server, storage
from obscura_forge_mcp.tools._shared import (
    extract_urls,
    merge_extras,
    resolve_model,
)


def test_catalog_aliases_unique() -> None:
    aliases = [s.alias for s in models.CATALOG]
    assert len(aliases) == len(set(aliases)), "duplicate alias in CATALOG"


def test_defaults_resolve() -> None:
    for modality, alias in models.DEFAULTS.items():
        spec = models.by_alias(alias)
        assert spec is not None, f"default alias '{alias}' missing from CATALOG"
        assert spec.modality == modality


def test_resolve_model_modality_check() -> None:
    with pytest.raises(ValueError, match="modality"):
        resolve_model("kling", "image")


def test_resolve_model_unknown_alias() -> None:
    with pytest.raises(ValueError, match="unknown model alias"):
        resolve_model("nope-model-xyz", "image")


def test_extract_urls_image_response() -> None:
    result = {"images": [{"url": "https://x/y.png", "content_type": "image/png"}]}
    assert extract_urls(result) == [("https://x/y.png", "image/png")]


def test_extract_urls_video_response() -> None:
    result = {"video": {"url": "https://x/y.mp4", "content_type": "video/mp4"}}
    assert extract_urls(result) == [("https://x/y.mp4", "video/mp4")]


def test_extract_urls_audio_response() -> None:
    result = {"audio": {"url": "https://x/y.wav"}}
    assert extract_urls(result) == [("https://x/y.wav", "")]


def test_extract_urls_audio_url_string() -> None:
    result = {"audio_url": "https://x/y.mp3"}
    assert extract_urls(result) == [("https://x/y.mp3", "")]


def test_extract_urls_fallback() -> None:
    result = {"some_unknown_key": "https://x/y.bin"}
    assert extract_urls(result) == [("https://x/y.bin", "")]


def test_extract_urls_empty() -> None:
    assert extract_urls({"foo": "bar"}) == []


def test_extension_from_url() -> None:
    assert storage.extension_from_url("https://x/y.png", "jpg") == "png"
    assert storage.extension_from_url("https://x/y.PNG", "jpg") == "PNG"
    assert storage.extension_from_url("https://x/y.png?v=1", "jpg") == "png"
    assert storage.extension_from_url("https://x/y.png#frag", "jpg") == "png"
    assert storage.extension_from_url("https://x/y", "jpg") == "jpg"
    assert storage.extension_from_url("https://x/y.toolong", "jpg") == "jpg"


def test_merge_extras_none() -> None:
    base = {"a": 1}
    assert merge_extras(base, None) == {"a": 1}


def test_merge_extras_overrides() -> None:
    base = {"a": 1, "b": 2}
    extra = {"b": 99, "c": 3}
    assert merge_extras(base, extra) == {"a": 1, "b": 99, "c": 3}
    # Original must not be mutated.
    assert base == {"a": 1, "b": 2}


def test_build_server_registers_all_tools() -> None:
    """FastMCP should expose every tool we registered."""
    mcp = server.build_server()
    # FastMCP stores tools internally; this is a behavioral test via list_tools().
    import asyncio

    tool_list = asyncio.run(mcp.list_tools())
    names = {t.name for t in tool_list}
    expected = {
        "generate_image",
        "edit_image",
        "generate_video",
        "generate_music",
        "generate_speech",
        "list_models",
    }
    missing = expected - names
    assert not missing, f"missing tools: {missing}"


def _parse_tool_result(result: object) -> dict:
    """Pull the JSON payload out of a FastMCP call_tool() return value.

    FastMCP returns a tuple of (content_blocks, structured_content) — the
    structured form has the original return string under "result".
    """
    if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], dict):
        text = result[1].get("result")
        if isinstance(text, str):
            return json.loads(text)
    if isinstance(result, list) and result:
        first = result[0]
        text = getattr(first, "text", str(first))
        return json.loads(text)
    raise AssertionError(f"unexpected call_tool result shape: {type(result).__name__}")


@pytest.mark.asyncio
async def test_list_models_all() -> None:
    mcp = server.build_server()
    parsed = _parse_tool_result(await mcp.call_tool("list_models", {"modality": "all"}))
    assert len(parsed["models"]) == len(models.CATALOG)
    assert parsed["defaults"] == models.DEFAULTS


@pytest.mark.asyncio
async def test_list_models_filter() -> None:
    mcp = server.build_server()
    parsed = _parse_tool_result(await mcp.call_tool("list_models", {"modality": "video"}))
    assert all(m["modality"] == "video" for m in parsed["models"])
    assert len(parsed["models"]) == len(models.by_modality("video"))


@pytest.mark.asyncio
async def test_list_models_unknown_modality() -> None:
    mcp = server.build_server()
    parsed = _parse_tool_result(await mcp.call_tool("list_models", {"modality": "bogus"}))
    assert "error" in parsed
