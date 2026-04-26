"""Helpers shared between tool modules."""

from __future__ import annotations

import json
import logging
from typing import Any

from .. import models, storage

log = logging.getLogger(__name__)


def resolve_model(alias: str, modality: models.Modality) -> models.ModelSpec:
    spec = models.by_alias(alias)
    if spec is None:
        available = ", ".join(m.alias for m in models.by_modality(modality))
        raise ValueError(
            f"unknown model alias '{alias}' for modality '{modality}'. Available: {available}"
        )
    if spec.modality != modality:
        raise ValueError(
            f"model '{alias}' is for modality '{spec.modality}', expected '{modality}'."
        )
    return spec


def extract_urls(result: dict[str, Any]) -> list[tuple[str, str]]:
    """Pull (url, content_type) pairs from a fal.ai response.

    fal returns wildly different shapes depending on the model — a list of
    images, a single video object, an audio object with various keys. Try
    the well-known shapes in order.
    """
    urls: list[tuple[str, str]] = []

    for img in result.get("images") or []:
        if isinstance(img, dict) and isinstance(img.get("url"), str):
            urls.append((img["url"], img.get("content_type", "")))

    vid = result.get("video")
    if isinstance(vid, dict) and isinstance(vid.get("url"), str):
        urls.append((vid["url"], vid.get("content_type", "")))

    for key in ("audio", "audio_file", "audio_url"):
        a = result.get(key)
        if isinstance(a, dict) and isinstance(a.get("url"), str):
            urls.append((a["url"], a.get("content_type", "")))
        elif isinstance(a, str) and a.startswith(("http://", "https://")):
            urls.append((a, ""))

    if not urls:
        # Last-ditch: any top-level string that looks like a URL.
        for value in result.values():
            if isinstance(value, str) and value.startswith(("http://", "https://")):
                urls.append((value, ""))
                break

    return urls


async def format_result(result: dict[str, Any], spec: models.ModelSpec) -> str:
    pairs = extract_urls(result)
    if not pairs:
        return json.dumps(
            {"error": "no media URL found in response", "raw": _trunc(result)},
            indent=2,
        )
    outputs = []
    for url, _ctype in pairs:
        ext = storage.extension_from_url(url, spec.output_ext)
        try:
            path = await storage.download(url, ext)
        except Exception as exc:
            log.warning("download failed for %s: %s", url, exc)
            outputs.append({"path": None, "url": url, "download_error": str(exc)})
            continue
        outputs.append({"path": str(path), "url": url})
    return json.dumps({"model": spec.alias, "outputs": outputs}, indent=2)


def _trunc(value: Any, depth: int = 0) -> Any:
    """Truncate long strings in nested structures for safe display."""
    if depth > 4:
        return "..."
    if isinstance(value, str):
        return value if len(value) < 200 else value[:200] + "..."
    if isinstance(value, dict):
        return {k: _trunc(v, depth + 1) for k, v in value.items()}
    if isinstance(value, list):
        return [_trunc(v, depth + 1) for v in value[:5]]
    return value


def merge_extras(args: dict[str, Any], extras: dict[str, Any] | None) -> dict[str, Any]:
    """Merge user-supplied extra params into the request, extras win."""
    if not extras:
        return args
    merged = dict(args)
    merged.update(extras)
    return merged
