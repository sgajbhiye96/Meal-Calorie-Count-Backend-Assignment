import os
import requests
from dotenv import load_dotenv
from difflib import get_close_matches

load_dotenv()
USDA_API_KEY = os.getenv("USDA_API_KEY")

SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
DETAIL_URL = "https://api.nal.usda.gov/fdc/v1/foods/{}"  # /{fdcId}

def search_foods(query: str, page_size: int = 10):
    if not USDA_API_KEY:
        raise RuntimeError("USDA_API_KEY not set in environment")
    params = {"query": query, "pageSize": page_size, "api_key": USDA_API_KEY}
    resp = requests.get(SEARCH_URL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

def choose_best_match(query: str, foods: list):
    # foods is list of dicts returned in 'foods'
    names = [f.get("description", "") for f in foods]
    # try exact contains
    lower_names = [n.lower() for n in names]
    qlow = query.lower()
    for i, n in enumerate(lower_names):
        if qlow in n:
            return foods[i]
    # fallback to difflib close match
    best = get_close_matches(query, names, n=1)
    if best:
        idx = names.index(best[0])
        return foods[idx]
    # else return first if exists
    return foods[0] if foods else None

def extract_calories_from_food_item(food_item: dict):
    """
    Extract calories per 100g or per serving.
    USDA response contains 'foodNutrients' list with nutrientId/name.
    We look for energy (kcal) - nutrientName may be 'Energy' or 'Energy (kcal)' etc.
    Also check 'labelNutrients' or 'foodPortions' if available.
    Return calories_per_serving (float), source string
    """
    # Check for 'foodNutrients' -> look for nutrientName containing 'Energy'
    nutrients = food_item.get("foodNutrients", []) or []
    cal = None
    for n in nutrients:
        name = n.get("nutrientName") or n.get("name") or ""
        if "energy" in name.lower() or "calories" in name.lower():
            # amount may be in 'value' or 'amount'
            amount = n.get("value") or n.get("amount")
            if amount is not None:
                cal = amount
                break

    # USDA often returns per 100g. We attempt to find serving size weight if available
    # Check for 'foodPortions' or 'servingSize' fields
    serving_multiplier = 1.0
    # if 'servingSize' exists in top-level
    if "servingSize" in food_item and food_item["servingSize"]:
        ss = food_item["servingSize"]
        # if calories are per 100g, adjust later. But many USDA items report nutrient values per 100g.
        # We'll assume extracted cal is per 100g if food_item.get('foodPortions') present with gram weight info
        pass

    # Try 'labelNutrients' (some branded foods)
    if cal is None:
        label_nutrients = food_item.get("labelNutrients") or {}
        energy = label_nutrients.get("calories") or label_nutrients.get("energy")
        if energy and isinstance(energy, dict):
            cal = energy.get("value")

    # If still None, attempt to fetch details endpoint for richer info (food_item may have fdcId)
    if cal is None and "fdcId" in food_item:
        # fetch full detail
        try:
            resp = requests.get(DETAIL_URL.format(food_item["fdcId"]), params={"api_key": USDA_API_KEY}, timeout=10)
            resp.raise_for_status()
            d = resp.json()
            nutrients = d.get("foodNutrients", []) or []
            for n in nutrients:
                name = n.get("nutrientName") or n.get("name") or ""
                if "energy" in name.lower() or "calories" in name.lower():
                    amount = n.get("value") or n.get("amount")
                    if amount is not None:
                        cal = amount
                        break
        except Exception:
            pass

    # As a last resort, try to find calories in food_item['description'] (not ideal)
    if cal is None:
        # cannot determine
        return None, "USDA FoodData Central"

    # Many nutrients in USDA are per 100g; we'll document that assumption in response.
    # We return calories per serving = calories_per_100g (user will provide servings; but serving weight isn't known).
    # So the API consumer should treat the "servings" as "number of standard servings" we assume 1 serving = 100g
    # To be explicit, we return calories_per_serving equal to cal (interpreted as per 100g).
    return float(cal), "USDA FoodData Central"