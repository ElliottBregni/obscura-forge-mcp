"""Music + SFX generation."""

from __future__ import annotations

from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .. import fal, models
from ._shared import format_result, merge_extras, resolve_model


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def generate_music(
        prompt: Annotated[
            str,
            Field(
                description="Describe the music: genre, mood, instruments, tempo. Or describe an SFX."
            ),
        ],
        model: Annotated[
            str,
            Field(
                description="Model alias from list_models (modality=music). Defaults to stable-audio."
            ),
        ] = "",
        duration_seconds: Annotated[
            int,
            Field(description="Clip length in seconds.", ge=1, le=120),
        ] = 30,
        seed: Annotated[
            int | None,
            Field(description="Optional integer seed."),
        ] = None,
        extra_params: Annotated[
            dict[str, Any] | None,
            Field(description="Model-specific overrides merged into the request."),
        ] = None,
    ) -> str:
        """Generate a music or SFX clip from a text prompt."""
        spec = resolve_model(model or models.DEFAULTS["music"], "music")
        # Different fal models use different keys for duration; send both.
        args: dict[str, Any] = {
            "prompt": prompt,
            "seconds_total": duration_seconds,
            "duration": duration_seconds,
        }
        if seed is not None:
            args["seed"] = seed
        result = await fal.run(spec.model, merge_extras(args, extra_params))
        return await format_result(result, spec)
