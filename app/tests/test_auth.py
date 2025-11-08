import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from sqlalchemy.orm import Session
from app.models import User

client = TestClient(app)

def setup_module(module):
    # Recreate tables for tests
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def test_register_and_login():
    payload = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password": "strongpassword"
    }
    r = client.post("/auth/register", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data

    # login
    r2 = client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert r2.status_code == 200
    assert "access_token" in r2.json()
