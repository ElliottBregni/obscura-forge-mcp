"""MCP tool registration for forge."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import catalog, image, music, speech, video


def register(mcp: FastMCP) -> None:
    """Register every forge tool on the given FastMCP instance."""
    image.register(mcp)
    video.register(mcp)
    music.register(mcp)
    speech.register(mcp)
    catalog.register(mcp)
