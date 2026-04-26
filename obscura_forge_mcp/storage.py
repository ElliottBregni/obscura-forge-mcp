"""Output file management: where to put generated media on disk."""

from __future__ import annotations

import datetime as dt
import logging
import os
import uuid
from pathlib import Path

import httpx

log = logging.getLogger(__name__)

DEFAULT_BASE = Path.home() / ".obscura" / "forge"


def base_dir() -> Path:
    custom = os.environ.get("OBSCURA_FORGE_DIR")
    return Path(custom).expanduser() if custom else DEFAULT_BASE


def output_path(extension: str) -> Path:
    today = dt.datetime.now().strftime("%Y-%m-%d")
    folder = base_dir() / today
    folder.mkdir(parents=True, exist_ok=True)
    name = f"{uuid.uuid4().hex[:12]}.{extension.lstrip('.')}"
    return folder / name


async def download(url: str, extension: str) -> Path:
    """Stream a remote file to the local forge directory and return its path."""
    path = output_path(extension)
    async with (
        httpx.AsyncClient(timeout=600.0, follow_redirects=True) as client,
        client.stream("GET", url) as resp,
    ):
        resp.raise_for_status()
        with path.open("wb") as f:
            async for chunk in resp.aiter_bytes(chunk_size=64 * 1024):
                f.write(chunk)
    log.info("downloaded %s -> %s", url, path)
    return path


def extension_from_url(url: str, default: str) -> str:
    """Extract a file extension from a URL, falling back to a default."""
    head = url.split("?", 1)[0].split("#", 1)[0]
    tail = head.rsplit(".", 1)
    if len(tail) == 2 and 1 <= len(tail[1]) <= 5 and tail[1].isalnum():
        return tail[1]
    return default
