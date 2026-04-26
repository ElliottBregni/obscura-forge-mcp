"""Image generation + edit tools."""

from __future__ import annotations

from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .. import fal, models
from ._shared import format_result, merge_extras, resolve_model


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def generate_image(
        prompt: Annotated[
            str,
            Field(
                description="What to generate. Be specific about subject, style, lighting, composition."
            ),
        ],
        model: Annotated[
            str,
            Field(
                description="Model alias from list_models (modality=image). Defaults to flux-schnell."
            ),
        ] = "",
        aspect_ratio: Annotated[
            str,
            Field(description="Aspect ratio: 1:1, 16:9, 9:16, 4:3, 3:4, 21:9."),
        ] = "1:1",
        num_images: Annotated[
            int,
            Field(description="How many images to generate.", ge=1, le=4),
        ] = 1,
        seed: Annotated[
            int | None,
            Field(description="Optional integer seed for reproducibility."),
        ] = None,
        extra_params: Annotated[
            dict[str, Any] | None,
            Field(description="Model-specific overrides merged into the request."),
        ] = None,
    ) -> str:
        """Generate one or more images from a text prompt.

        Returns JSON: {"model": ..., "outputs": [{"path": ..., "url": ...}, ...]}.
        Files are saved under ~/.obscura/forge/<date>/.
        """
        spec = resolve_model(model or models.DEFAULTS["image"], "image")
        args: dict[str, Any] = {
            "prompt": prompt,
            "num_images": num_images,
            "aspect_ratio": aspect_ratio,
        }
        if seed is not None:
            args["seed"] = seed
        result = await fal.run(spec.model, merge_extras(args, extra_params))
        return await format_result(result, spec)

    @mcp.tool()
    async def edit_image(
        image_url: Annotated[
            str,
            Field(description="HTTPS URL or local file path of source image."),
        ],
        prompt: Annotated[
            str,
            Field(description="What to change. Empty for variation."),
        ] = "",
        model: Annotated[
            str,
            Field(description="Model alias from list_models (modality=image_edit)."),
        ] = "",
        strength: Annotated[
            float,
            Field(description="Deviation from source. 0=identical, 1=ignore source.", ge=0, le=1),
        ] = 0.6,
        extra_params: Annotated[
            dict[str, Any] | None,
            Field(description="Model-specific overrides merged into the request."),
        ] = None,
    ) -> str:
        """Edit an image or generate a variation conditioned on it.

        If `image_url` is a local path, it is uploaded to fal.ai's CDN first.
        """
        spec = resolve_model(model or models.DEFAULTS["image_edit"], "image_edit")
        if not image_url.startswith(("http://", "https://")):
            image_url = await fal.upload(image_url)
        args: dict[str, Any] = {
            "image_url": image_url,
            "strength": strength,
        }
        if prompt:
            args["prompt"] = prompt
        result = await fal.run(spec.model, merge_extras(args, extra_params))
        return await format_result(result, spec)
