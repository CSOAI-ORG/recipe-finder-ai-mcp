#!/usr/bin/env python3

import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

from mcp.server.fastmcp import FastMCP
import json
mcp = FastMCP("recipe-finder-ai-mcp")
RECIPES = {
    "pasta": {"ingredients": ["pasta", "tomato", "garlic"], "time_min": 20},
    "salad": {"ingredients": ["lettuce", "cucumber", "olive oil"], "time_min": 10},
    "curry": {"ingredients": ["rice", "coconut milk", "spices"], "time_min": 35},
}
@mcp.tool(name="find_recipe")
async def find_recipe(ingredients: list, max_time_min: int = 60, api_key: str = "") -> str:
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    matches = []
    for name, r in RECIPES.items():
        overlap = set(ingredients) & set(r["ingredients"])
        if overlap and r["time_min"] <= max_time_min:
            matches.append({"name": name, "overlap": list(overlap), "time_min": r["time_min"]})
    return {"matches": matches}
@mcp.tool(name="substitute_ingredient")
async def substitute_ingredient(ingredient: str, api_key: str = "") -> str:
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    subs = {"butter": "olive oil", "sugar": "honey", "cream": "coconut milk"}
    return {"original": ingredient, "substitute": subs.get(ingredient.lower(), "no substitute known")}
if __name__ == "__main__":
    mcp.run()
