"""
Simple USDA API Key test
Checks if your key is valid and can fetch food data.
"""

import requests
import os
from dotenv import load_dotenv

# Load .env so USDA_API_KEY is available
load_dotenv()

API_KEY = os.getenv("USDA_API_KEY")

if not API_KEY:
    print("USDA_API_KEY not found in .env. Please add it first.")
    exit(1)

# USDA API endpoint
URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

# Query any food (you can change 'apple' to 'chicken biryani', etc.)
params = {
    "api_key": API_KEY,
    "query": "apple",
    "pageSize": 1
}

print("🔍 Testing USDA API key...")
try:
    response = requests.get(URL, params=params, timeout=10)
    if response.status_code == 200:
        data = response.json()
        foods = data.get("foods", [])
        if foods:
            print("API Key is valid!")
            print(f"Found food item: {foods[0].get('description')}")
        else:
            print("API key is valid, but no results returned for query.")
    elif response.status_code == 403:
        print("Invalid or expired API key (HTTP 403). Check your key.")
    else:
        print(f"Request failed with status code {response.status_code}: {response.text[:200]}")
except requests.RequestException as e:
    print(f"Network or connection error: {e}")
