"""Text-to-speech."""

from __future__ import annotations

from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .. import fal, models
from ._shared import format_result, merge_extras, resolve_model


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def generate_speech(
        text: Annotated[
            str,
            Field(description="Text to speak. Punctuation affects pacing."),
        ],
        model: Annotated[
            str,
            Field(
                description="Model alias from list_models (modality=speech). Defaults to elevenlabs."
            ),
        ] = "",
        voice: Annotated[
            str,
            Field(
                description="Voice ID or preset name. Model-specific; leave empty for model default."
            ),
        ] = "",
        speed: Annotated[
            float,
            Field(description="Speech speed multiplier.", ge=0.5, le=2.0),
        ] = 1.0,
        extra_params: Annotated[
            dict[str, Any] | None,
            Field(description="Model-specific overrides merged into the request."),
        ] = None,
    ) -> str:
        """Synthesize speech audio from text."""
        spec = resolve_model(model or models.DEFAULTS["speech"], "speech")
        args: dict[str, Any] = {"text": text, "speed": speed}
        if voice:
            args["voice"] = voice
        result = await fal.run(spec.model, merge_extras(args, extra_params))
        return await format_result(result, spec)
