# obscura-forge-mcp

MCP server for AI media **generation** — image, video, music, and speech — powered by [fal.ai](https://fal.ai).

Sister project to [Obscura](https://github.com/elliottbregni/obscura). Designed to plug into Obscura's MCP integration, but works with any MCP client (Claude Desktop, Cursor, etc.).

`forge` *produces* media. Pair it with the ingest-side MCP if you also need to consume existing media.

## What it generates

| Modality   | Aliases                                              | Default       |
| ---------- | ---------------------------------------------------- | ------------- |
| Image      | `flux-schnell`, `flux-dev`, `flux-pro`, `sd3`, `recraft` | `flux-schnell` |
| Image edit | `flux-redux`, `flux-canny`                           | `flux-redux`  |
| Video      | `kling`, `luma`, `minimax`, `mochi`, `hunyuan`       | `kling`       |
| Music      | `stable-audio`, `musicgen`                           | `stable-audio` |
| Speech     | `elevenlabs`, `cartesia`, `playai`                   | `elevenlabs`  |

Aliases are short names — call `list_models` for the live catalog. Alias→fal.ai endpoint mapping lives in [`obscura_forge_mcp/models.py`](obscura_forge_mcp/models.py).

## Tools

| Tool              | Purpose                                       |
| ----------------- | --------------------------------------------- |
| `generate_image`  | Text → image (FLUX, SD3, Recraft, …)          |
| `edit_image`      | Image → image (variation, structure-aware)    |
| `generate_video`  | Text/image → short video clip                 |
| `generate_music`  | Text → music or SFX clip                      |
| `generate_speech` | Text → spoken audio (TTS)                     |
| `list_models`     | Inspect available aliases per modality        |

All generation tools return JSON:

```json
{
  "model": "flux-schnell",
  "outputs": [
    { "path": "/Users/you/.obscura/forge/2026-04-25/abc123.png", "url": "https://..." }
  ]
}
```

Files are saved to `~/.obscura/forge/<YYYY-MM-DD>/<uuid>.<ext>`. Override with `OBSCURA_FORGE_DIR`.

## Install

```bash
git clone https://github.com/ElliottBregni/obscura-forge-mcp.git && cd obscura-forge-mcp
uv tool install --editable .

# Get a key from https://fal.ai/dashboard/keys
export FAL_KEY=<your-fal-api-key>
```

## Run

```bash
obscura-forge-mcp                  # stdio MCP server (talks JSON-RPC over stdin/stdout)
```

Logs go to stderr; stdout is reserved for MCP protocol traffic.

### Wire into Obscura

Add to `~/.obscura/mcp/core.json`:

```json
{
  "servers": {
    "forge": {
      "command": "obscura-forge-mcp",
      "env": { "FAL_KEY": "${FAL_KEY}" }
    }
  }
}
```

### Wire into Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "forge": {
      "command": "obscura-forge-mcp",
      "env": { "FAL_KEY": "<your-key>" }
    }
  }
}
```

## Cost

Each generation hits fal.ai's paid API. Per-call cost varies — image is fractions of a cent, video is dollars per clip. Check [fal.ai pricing](https://fal.ai/pricing) before bulk-generating.

## Development

```bash
uv sync --group dev
uv run pytest             # smoke tests, no API key required
uv run ruff check .
uv run ruff format .
uv run pyright
```

## License

MIT
