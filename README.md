# Food Calories Backend (FastAPI + USDA FDC)

1. Copy files and install dependencies:
   pip install -r requirements.txt

2. Create a PostgreSQL database and set DATABASE_URL in .env (or use any Postgres).
   Example .env is provided as .env.example

3. Get a USDA FDC API key: https://fdc.nal.usda.gov/api-key-signup.html
   Put it into FDC_API_KEY in .env

4. Run:
   uvicorn app.main:app --reload

Endpoints:
- POST /auth/register
  Body: { first_name, last_name, email, password }
  Returns: access_token

- POST /auth/login
  Body: { email, password }
  Returns: access_token

- POST /get-calories
  Body: { dish_name, servings }
  Returns: JSON with total_calories, calories_per_serving, best_match, breakdown

Notes:
- Keep your .env secret and do not commit it.
- This demo creates DB tables on startup for convenience. Use migrations for production.
- Rate limiting is applied: 15 requests/min per IP by default.
- Tests provided in tests/ require pytest.
