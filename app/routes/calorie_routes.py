from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, models
from ..deps import get_db, get_current_user
from ..utils.usda_client import search_foods, choose_best_match, extract_calories_from_food_item
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from fastapi import Form

router = APIRouter(tags=["calories"])

def normalize_name(name: str) -> str:
    return " ".join(name.lower().strip().split())

@router.post("/get-calories")
def get_calories(
    dish_name: str = Form(...),
    servings: int = Form(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    dish_norm = dish_name.strip().lower()

    # Check cached calories first
    cached = (
        db.query(models.MealCache)
        .filter(models.MealCache.dish_name == dish_norm)
        .first()
    )
    if cached:
        age = datetime.utcnow() - cached.created_at
        if age < timedelta(hours=24):
            cal_per_serving = cached.calories_per_serving
            total = cal_per_serving * servings
            return {
                "dish_name": dish_name,
                "servings": servings,
                "calories_per_serving": round(cal_per_serving, 2),
                "total_calories": round(total, 2),
                "source": "Cache"
            }

    # Otherwise call USDA API
    try:
        food_item = search_foods(dish_name)
        cal_per_serving = extract_calories_from_food_item(food_item)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling USDA API: {e}")

    # Cache result
    new_cache = models.MealCache(
        dish_name=dish_norm,
        calories_per_serving=cal_per_serving,
        source="USDA FoodData Central",
    )
    db.add(new_cache)
    db.commit()

    total = cal_per_serving * servings
    return {
        "dish_name": dish_name,
        "servings": servings,
        "calories_per_serving": round(cal_per_serving, 2),
        "total_calories": round(total, 2),
        "source": "USDA FoodData Central"
    }