from mcp.server.fastmcp import FastMCP

mcp = FastMCP("recipe-finder")

RECIPES = {
    "Avocado Toast": {
        "ingredients": ["bread", "avocado", "salt", "lemon"],
        "diet": ["vegetarian", "vegan"],
        "steps": ["Toast the bread.", "Mash avocado with lemon and salt.", "Spread on toast and serve."],
    },
    "Chicken Stir Fry": {
        "ingredients": ["chicken", "soy sauce", "vegetables", "rice"],
        "diet": ["gluten_free_option"],
        "steps": ["Cook rice.", "Stir fry chicken and vegetables.", "Add soy sauce and serve over rice."],
    },
    "Greek Salad": {
        "ingredients": ["tomato", "cucumber", "olives", "feta", "olive oil"],
        "diet": ["vegetarian", "gluten_free"],
        "steps": ["Chop vegetables.", "Toss with olives and feta.", "Drizzle olive oil and serve."],
    },
    "Pasta Aglio e Olio": {
        "ingredients": ["pasta", "garlic", "olive oil", "chili flakes"],
        "diet": ["vegetarian", "vegan"],
        "steps": ["Boil pasta.", "Sauté garlic in olive oil.", "Toss pasta with oil and chili flakes."],
    },
}

@mcp.tool()
def search_by_ingredients(ingredients: list) -> dict:
    """Search recipes by ingredients."""
    user_set = set(i.lower() for i in ingredients)
    matches = []
    for name, data in RECIPES.items():
        recipe_set = set(i.lower() for i in data["ingredients"])
        overlap = user_set & recipe_set
        if overlap:
            matches.append({"name": name, "matched_ingredients": list(overlap), "total_ingredients": data["ingredients"]})
    return {"matches": matches}

@mcp.tool()
def get_recipe_details(name: str) -> dict:
    """Get recipe details."""
    data = RECIPES.get(name)
    if not data:
        return {"error": "Recipe not found", "available": list(RECIPES.keys())}
    return {"name": name, **data}

@mcp.tool()
def filter_by_diet(diet: str) -> dict:
    """Filter recipes by diet."""
    results = []
    for name, data in RECIPES.items():
        if diet.lower() in [d.lower() for d in data["diet"]]:
            results.append(name)
    return {"diet": diet, "recipes": results}

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
