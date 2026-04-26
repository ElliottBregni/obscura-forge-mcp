"""Thin wrapper around fal_client with structured errors and logging."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import fal_client

log = logging.getLogger(__name__)


class FalError(Exception):
    """Raised when fal.ai returns an error or is misconfigured."""


def _ensure_key() -> None:
    if not os.environ.get("FAL_KEY"):
        raise FalError(
            "FAL_KEY is not set. Get a key at https://fal.ai/dashboard/keys "
            "and export FAL_KEY=<value> before launching the server."
        )


async def run(model: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Submit a job to fal.ai and wait for the result.

    Uses the queue API (`submit_async` + `get`) so long-running video / audio
    jobs don't time out.
    """
    _ensure_key()
    log.info("fal.run model=%s args_keys=%s", model, sorted(arguments.keys()))
    try:
        handler = await fal_client.submit_async(model, arguments=arguments)
        result = await handler.get()
    except Exception as exc:
        raise FalError(f"fal.ai call failed for {model}: {exc}") from exc
    if not isinstance(result, dict):
        raise FalError(f"unexpected fal response type: {type(result).__name__}")
    return result


async def upload(local_path: str) -> str:
    """Upload a local file to fal.ai's CDN, return the public URL."""
    _ensure_key()
    return await fal_client.upload_file_async(Path(local_path))
