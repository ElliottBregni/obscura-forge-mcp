"""Video generation."""

from __future__ import annotations

from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .. import fal, models
from ._shared import format_result, merge_extras, resolve_model


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def generate_video(
        prompt: Annotated[
            str,
            Field(description="What to film. Describe motion, subject, camera, style."),
        ],
        model: Annotated[
            str,
            Field(description="Model alias from list_models (modality=video). Defaults to kling."),
        ] = "",
        duration_seconds: Annotated[
            int,
            Field(description="Target clip length, capped by model.", ge=2, le=20),
        ] = 5,
        aspect_ratio: Annotated[
            str,
            Field(description="Aspect ratio: 16:9, 9:16, 1:1."),
        ] = "16:9",
        image_url: Annotated[
            str | None,
            Field(description="Optional image to animate (image-to-video). URL or local path."),
        ] = None,
        seed: Annotated[
            int | None,
            Field(description="Optional integer seed."),
        ] = None,
        extra_params: Annotated[
            dict[str, Any] | None,
            Field(description="Model-specific overrides merged into the request."),
        ] = None,
    ) -> str:
        """Generate a short video from a text prompt (and optional image).

        Video generation can take 30s–5min depending on model and length.
        """
        spec = resolve_model(model or models.DEFAULTS["video"], "video")
        args: dict[str, Any] = {
            "prompt": prompt,
            "duration": str(duration_seconds),
            "aspect_ratio": aspect_ratio,
        }
        if image_url:
            if not image_url.startswith(("http://", "https://")):
                image_url = await fal.upload(image_url)
            args["image_url"] = image_url
        if seed is not None:
            args["seed"] = seed
        result = await fal.run(spec.model, merge_extras(args, extra_params))
        return await format_result(result, spec)
