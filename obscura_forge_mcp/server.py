"""MCP server entry point for obscura-forge-mcp."""

from __future__ import annotations

import logging
import sys

from mcp.server.fastmcp import FastMCP

from . import tools


def build_server() -> FastMCP:
    mcp = FastMCP("obscura-forge")
    tools.register(mcp)
    return mcp


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,  # stdout is reserved for MCP protocol traffic
    )
    server = build_server()
    server.run()


if __name__ == "__main__":
    main()
