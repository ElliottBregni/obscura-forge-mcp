"""Model catalog tool: introspect available aliases per modality."""

from __future__ import annotations

import json
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .. import models


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def list_models(
        modality: Annotated[
            str,
            Field(description="Filter: image, image_edit, video, music, speech, or 'all'."),
        ] = "all",
    ) -> str:
        """List available model aliases. Pass an alias to any generate_* tool's `model` param."""
        if modality == "all":
            specs = models.CATALOG
        elif modality in {"image", "image_edit", "video", "music", "speech"}:
            specs = models.by_modality(modality)  # type: ignore[arg-type]
        else:
            return json.dumps(
                {
                    "error": f"unknown modality '{modality}'",
                    "valid": ["image", "image_edit", "video", "music", "speech", "all"],
                },
                indent=2,
            )
        return json.dumps(
            {
                "models": [
                    {
                        "alias": s.alias,
                        "modality": s.modality,
                        "fal_model": s.model,
                        "description": s.description,
                        "output_ext": s.output_ext,
                    }
                    for s in specs
                ],
                "defaults": models.DEFAULTS,
            },
            indent=2,
        )
