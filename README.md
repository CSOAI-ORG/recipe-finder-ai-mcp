# Recipe Finder Ai

> By [MEOK AI Labs](https://meok.ai) — Recipe search and meal planning. Find recipes by ingredients, get substitutions, plan meals, and estimate nutrition. By MEOK AI Labs.

Recipe Finder AI MCP — MEOK AI Labs. Recipe search, ingredient substitution, meal planning, nutrition estimation.

## Installation

```bash
pip install recipe-finder-ai-mcp
```

## Usage

```bash
# Run standalone
python server.py

# Or via MCP
mcp install recipe-finder-ai-mcp
```

## Tools

### `find_recipe`
Find recipes matching available ingredients. Ingredients as comma-separated string.

**Parameters:**
- `ingredients` (str)
- `max_time_min` (int)
- `cuisine` (str)
- `diet` (str)

### `substitute_ingredient`
Get ingredient substitutions, optionally filtered by dietary preference.

**Parameters:**
- `ingredient` (str)
- `dietary_preference` (str)

### `plan_weekly_meals`
Generate a weekly meal plan based on preferences.

**Parameters:**
- `servings` (int)
- `diet` (str)
- `max_time_min` (int)

### `estimate_nutrition`
Estimate approximate nutritional content from ingredient list (comma-separated).

**Parameters:**
- `ingredients` (str)


## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## Links

- **Website**: [meok.ai](https://meok.ai)
- **GitHub**: [CSOAI-ORG/recipe-finder-ai-mcp](https://github.com/CSOAI-ORG/recipe-finder-ai-mcp)
- **PyPI**: [pypi.org/project/recipe-finder-ai-mcp](https://pypi.org/project/recipe-finder-ai-mcp/)

## License

MIT — MEOK AI Labs
