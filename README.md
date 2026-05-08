<div align="center">

# Recipe Finder Ai MCP

**MCP server for recipe finder ai mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-recipe-finder-ai-mcp)](https://pypi.org/project/meok-recipe-finder-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Recipe Finder Ai MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `find_recipe` | Find recipes matching available ingredients. Ingredients as comma-separated stri |
| `substitute_ingredient` | Get ingredient substitutions, optionally filtered by dietary preference. |
| `plan_weekly_meals` | Generate a weekly meal plan based on preferences. |
| `estimate_nutrition` | Estimate approximate nutritional content from ingredient list (comma-separated). |

## Installation

```bash
pip install meok-recipe-finder-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "recipe-finder-ai": {
      "command": "python",
      "args": ["-m", "meok_recipe_finder_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 4 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
