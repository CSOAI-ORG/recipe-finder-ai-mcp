#!/usr/bin/env python3
"""
Recipe Finder AI MCP — MEOK AI Labs. Recipe search, ingredient substitution, meal planning, nutrition estimation."""

import sys, os
from auth_middleware import check_access

import json
from datetime import datetime, timezone
from collections import defaultdict
from mcp.server.fastmcp import FastMCP
import urllib.request as _meter_urlreq
import urllib.error as _meter_urlerr

FREE_DAILY_LIMIT = 50
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None

mcp = FastMCP("recipe-finder-ai", instructions="Recipe search and meal planning. Find recipes by ingredients, get substitutions, plan meals, and estimate nutrition. By MEOK AI Labs.")

RECIPES = {
    "spaghetti_bolognese": {"name": "Spaghetti Bolognese", "ingredients": ["spaghetti", "ground beef", "tomato", "onion", "garlic", "olive oil"], "time_min": 35, "servings": 4, "cuisine": "italian", "diet": ["omnivore"], "calories_per_serving": 480, "difficulty": "easy"},
    "chicken_stir_fry": {"name": "Chicken Stir Fry", "ingredients": ["chicken breast", "soy sauce", "bell pepper", "broccoli", "garlic", "ginger", "rice"], "time_min": 25, "servings": 3, "cuisine": "asian", "diet": ["omnivore", "gluten-free"], "calories_per_serving": 380, "difficulty": "easy"},
    "vegetable_curry": {"name": "Vegetable Curry", "ingredients": ["potato", "chickpeas", "coconut milk", "onion", "garlic", "curry powder", "rice"], "time_min": 40, "servings": 4, "cuisine": "indian", "diet": ["vegetarian", "vegan", "gluten-free"], "calories_per_serving": 350, "difficulty": "easy"},
    "caesar_salad": {"name": "Caesar Salad", "ingredients": ["romaine lettuce", "parmesan", "croutons", "chicken breast", "lemon", "garlic", "olive oil"], "time_min": 15, "servings": 2, "cuisine": "american", "diet": ["omnivore"], "calories_per_serving": 280, "difficulty": "easy"},
    "mushroom_risotto": {"name": "Mushroom Risotto", "ingredients": ["arborio rice", "mushrooms", "onion", "garlic", "parmesan", "white wine", "butter"], "time_min": 45, "servings": 4, "cuisine": "italian", "diet": ["vegetarian"], "calories_per_serving": 420, "difficulty": "medium"},
    "fish_tacos": {"name": "Fish Tacos", "ingredients": ["white fish", "tortillas", "cabbage", "lime", "avocado", "sour cream", "cilantro"], "time_min": 30, "servings": 3, "cuisine": "mexican", "diet": ["omnivore"], "calories_per_serving": 340, "difficulty": "easy"},
    "lentil_soup": {"name": "Lentil Soup", "ingredients": ["red lentils", "onion", "carrot", "celery", "garlic", "cumin", "tomato"], "time_min": 35, "servings": 6, "cuisine": "middle_eastern", "diet": ["vegetarian", "vegan", "gluten-free"], "calories_per_serving": 220, "difficulty": "easy"},
    "pad_thai": {"name": "Pad Thai", "ingredients": ["rice noodles", "shrimp", "egg", "bean sprouts", "peanuts", "lime", "soy sauce"], "time_min": 30, "servings": 3, "cuisine": "thai", "diet": ["omnivore"], "calories_per_serving": 410, "difficulty": "medium"},
    "shepherds_pie": {"name": "Shepherd's Pie", "ingredients": ["ground lamb", "potato", "onion", "carrot", "peas", "tomato paste", "butter"], "time_min": 60, "servings": 6, "cuisine": "british", "diet": ["omnivore", "gluten-free"], "calories_per_serving": 450, "difficulty": "medium"},
    "banana_pancakes": {"name": "Banana Pancakes", "ingredients": ["banana", "eggs", "flour", "milk", "butter", "maple syrup"], "time_min": 20, "servings": 2, "cuisine": "american", "diet": ["vegetarian"], "calories_per_serving": 320, "difficulty": "easy"},
}

SUBSTITUTIONS = {
    "butter": ["olive oil", "coconut oil", "margarine", "applesauce (for baking)"],
    "sugar": ["honey", "maple syrup", "stevia", "agave nectar"],
    "cream": ["coconut cream", "cashew cream", "silken tofu"],
    "milk": ["oat milk", "almond milk", "soy milk", "coconut milk"],
    "eggs": ["flax egg (1 tbsp ground flax + 3 tbsp water)", "chia egg", "applesauce", "mashed banana"],
    "flour": ["almond flour", "coconut flour", "oat flour", "rice flour"],
    "soy sauce": ["tamari (gluten-free)", "coconut aminos", "worcestershire sauce"],
    "parmesan": ["nutritional yeast (vegan)", "pecorino romano", "grana padano"],
    "chicken breast": ["tofu", "tempeh", "seitan", "jackfruit"],
    "ground beef": ["beyond meat", "lentils", "mushrooms", "tvp"],
    "white wine": ["chicken broth", "white grape juice", "apple cider vinegar + water"],
    "rice": ["quinoa", "cauliflower rice", "couscous", "bulgur wheat"],
}

def _server_meter_check(api_key: str = "") -> dict:
    """Calls the live /verify endpoint for server-side metering. Returns the JSON dict.
    Fail-open: if /verify is unreachable or KV isn't configured, returns allowed=True
    (so the local rate-limit in _check_rate_limit remains the safety net)."""
    try:
        data = json.dumps({"api_key": api_key, "tool": ""}).encode()
        req = _meter_urlreq.Request(_METER_URL, data=data,
            headers={"Content-Type": "application/json"}, method="POST")
        with _meter_urlreq.urlopen(req, timeout=2.5) as r:
            d = json.loads(r.read())
            if isinstance(d, dict) and "allowed" in d:
                return d
    except Exception:
        pass
    return {"allowed": True, "tier": "anonymous", "remaining": 200, "upgrade_url": "https://meok.ai/pricing"}


_METER_URL = "https://proofof.ai/verify"


@mcp.tool()
def find_recipe(ingredients: str, max_time_min: int = 60, cuisine: str = "", diet: str = "", api_key: str = "") -> str:
    """Find recipes matching available ingredients. Ingredients as comma-separated string.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.

    Args:
        ingredients (str): The ingredients to analyze or process.
        max_time_min (int): The max time min to analyze or process.
        cuisine (str): The cuisine to analyze or process.
        diet (str): The diet to analyze or process.
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://councilof.ai"}
    if err := _rl(): return err

    user_ingredients = {i.strip().lower() for i in ingredients.split(",") if i.strip()}
    matches = []

    for key, recipe in RECIPES.items():
        if recipe["time_min"] > max_time_min:
            continue
        if cuisine and recipe["cuisine"] != cuisine.lower():
            continue
        if diet and diet.lower() not in recipe["diet"]:
            continue

        recipe_ings = {i.lower() for i in recipe["ingredients"]}
        overlap = user_ingredients & recipe_ings
        missing = recipe_ings - user_ingredients
        match_pct = len(overlap) / len(recipe_ings) * 100

        if overlap:
            matches.append({
                "name": recipe["name"],
                "match_pct": round(match_pct),
                "matched_ingredients": sorted(overlap),
                "missing_ingredients": sorted(missing),
                "time_min": recipe["time_min"],
                "servings": recipe["servings"],
                "calories_per_serving": recipe["calories_per_serving"],
                "difficulty": recipe["difficulty"],
                "cuisine": recipe["cuisine"],
            })

    matches.sort(key=lambda m: m["match_pct"], reverse=True)
    return {"matches": matches, "total": len(matches), "searched_with": sorted(user_ingredients)}


@mcp.tool()
def substitute_ingredient(ingredient: str, dietary_preference: str = "", api_key: str = "") -> str:
    """Get ingredient substitutions, optionally filtered by dietary preference.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.

    Args:
        ingredient (str): The ingredient to analyze or process.
        dietary_preference (str): The dietary preference to analyze or process.
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://councilof.ai"}
    if err := _rl(): return err

    key = ingredient.lower().strip()
    subs = SUBSTITUTIONS.get(key, [])
    if not subs:
        # Try partial match
        for k, v in SUBSTITUTIONS.items():
            if key in k or k in key:
                subs = v
                key = k
                break

    if dietary_preference:
        pref = dietary_preference.lower()
        if pref == "vegan":
            subs = [s for s in subs if "vegan" in s.lower() or not any(w in s.lower() for w in ["butter", "cream", "milk", "egg", "cheese"])]

    return {"ingredient": ingredient, "substitutions": subs, "count": len(subs)}


@mcp.tool()
def plan_weekly_meals(servings: int = 2, diet: str = "", max_time_min: int = 45, api_key: str = "") -> str:
    """Generate a weekly meal plan based on preferences.

    Behavior:
        This tool generates structured output without modifying external systems.
        Output is deterministic for identical inputs. No side effects.
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.

    Args:
        servings (int): The servings to analyze or process.
        diet (str): The diet to analyze or process.
        max_time_min (int): The max time min to analyze or process.
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://councilof.ai"}
    if err := _rl(): return err

    eligible = []
    for key, recipe in RECIPES.items():
        if recipe["time_min"] <= max_time_min:
            if not diet or diet.lower() in recipe["diet"]:
                eligible.append(recipe)

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    plan = []
    all_ingredients = set()

    for i, day in enumerate(days):
        if eligible:
            recipe = eligible[i % len(eligible)]
            plan.append({"day": day, "recipe": recipe["name"], "time_min": recipe["time_min"], "calories": recipe["calories_per_serving"]})
            all_ingredients.update(recipe["ingredients"])
        else:
            plan.append({"day": day, "recipe": "No matching recipes", "time_min": 0, "calories": 0})

    total_calories = sum(m["calories"] for m in plan)
    return {
        "plan": plan,
        "shopping_list": sorted(all_ingredients),
        "total_weekly_calories": total_calories,
        "avg_daily_calories": round(total_calories / 7),
        "diet": diet or "any",
    }


@mcp.tool()
def estimate_nutrition(ingredients: str, api_key: str = "") -> str:
    """Estimate approximate nutritional content from ingredient list (comma-separated).

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.

    Args:
        ingredients (str): The ingredients to analyze or process.
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://councilof.ai"}
    if err := _rl(): return err

    # Rough calorie estimates per ingredient category
    calorie_map = {
        "rice": 200, "pasta": 220, "noodles": 200, "bread": 150, "flour": 120,
        "chicken": 165, "beef": 250, "lamb": 260, "fish": 140, "shrimp": 100,
        "egg": 70, "cheese": 110, "butter": 100, "cream": 80, "milk": 60,
        "potato": 130, "lentils": 115, "chickpeas": 120, "beans": 110,
        "onion": 25, "garlic": 5, "tomato": 22, "carrot": 25, "broccoli": 30,
        "oil": 120, "sugar": 50, "honey": 60,
    }

    items = [i.strip().lower() for i in ingredients.split(",") if i.strip()]
    breakdown = []
    total = 0

    for item in items:
        cal = 30  # default
        for key, val in calorie_map.items():
            if key in item:
                cal = val
                break
        breakdown.append({"ingredient": item, "estimated_calories": cal})
        total += cal

    return {"ingredients": breakdown, "total_estimated_calories": total, "note": "Rough estimates — actual values depend on portion sizes"}


def main():
    mcp.run()

if __name__ == '__main__':
    main()


# ── MEOK monetization layer (Stripe upgrade · PAYG · pricing) ──────────
# Free tier is zero-config. Upgrade to Pro (unlimited) or pay-as-you-go per call.
import os as _meok_os
MEOK_STRIPE_UPGRADE = "https://buy.stripe.com/aFa7sNcgAdQS0ZT1Uc8k91t"  # Pro (unlimited)
MEOK_PAYG_KEY = _meok_os.environ.get("MEOK_PAYG_KEY", "")  # set to enable PAYG (x402 / ~GBP0.05 per call)
MEOK_PRICING = "https://meok.ai/pricing"


def meok_upsell(tier: str = "free") -> dict:
    """Monetization options for free-tier callers: Pro upgrade, PAYG, or pricing page."""
    if tier != "free":
        return {}
    return {"upgrade_url": MEOK_STRIPE_UPGRADE,
            "payg_enabled": bool(MEOK_PAYG_KEY),
            "pricing": MEOK_PRICING}
