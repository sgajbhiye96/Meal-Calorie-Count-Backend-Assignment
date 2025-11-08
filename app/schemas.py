# app/schemas.py
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str = Field(min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class GetCaloriesRequest(BaseModel):
    dish_name: str
    servings: float

    @validator("servings")
    def validate_servings(cls, v):
        if v <= 0:
            raise ValueError("servings must be > 0")
        return v

class IngredientBreakdown(BaseModel):
    name: str
    calories: float

class GetCaloriesResponse(BaseModel):
    dish_name: str
    servings: float
    calories_per_serving: float
    total_calories: float
    source: str
    ingredients: Optional[List[IngredientBreakdown]] = None
