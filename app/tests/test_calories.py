import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_invalid_servings():
    r = client.post("/get-calories", json={"dish_name": "macaroni and cheese", "servings": 0})
    assert r.status_code == 400

def test_nonexistent_dish(monkeypatch):
    # patch utils.search_usda to return empty
    from app import utils
    monkeypatch.setattr(utils, "search_usda", lambda q, pageSize=10: {"foods": []})
    r = client.post("/get-calories", json={"dish_name": "some totally unknown dish qwertyuiop", "servings": 1})
    assert r.status_code == 404

# The tests below assume your FDC_API_KEY is valid and network is available.
@pytest.mark.skipif(not True, reason="Integration test - requires USDA API key and network")
def test_common_dish():
    r = client.post("/get-calories", json={"dish_name": "macaroni and cheese", "servings": 2})
    assert r.status_code == 200
    data = r.json()
    assert "total_calories" in data
    assert data["servings"] == 2
