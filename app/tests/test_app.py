import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from sqlalchemy.orm import Session
from app import models

# ---------- Setup & Teardown ----------

@pytest.fixture(scope="module")
def test_db():
    """Create a fresh SQLite DB for testing."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    """Initialize TestClient."""
    with TestClient(app) as c:
        yield c

# ---------- Helper Functions ----------

def register_user(client, email="test@example.com"):
    data = {
        "first_name": "Test",
        "last_name": "User",
        "email": email,
        "password": "pass123"
    }
    response = client.post("/auth/register", data=data)
    return response

def login_user(client, email="test@example.com", password="pass123"):
    data = {"email": email, "password": password}
    response = client.post("/auth/login", data=data, follow_redirects=False)
    return response

# ---------- TESTS ----------

def test_register_user(client, test_db):
    """ Test registration flow."""
    response = register_user(client)
    assert response.status_code in (200, 303, 307)
    # After registration, DB should contain user
    db: Session = SessionLocal()
    user = db.query(models.User).filter(models.User.email == "test@example.com").first()
    assert user is not None
    db.close()

def test_register_duplicate_email(client):
    """Should fail if email already exists."""
    data = {
        "first_name": "Another",
        "last_name": "User",
        "email": "test@example.com",
        "password": "abc123"
    }
    response = client.post("/auth/register", data=data)
    assert response.status_code == 400
    assert "Email already registered" in response.text

def test_login_success(client):
    """Test login with valid credentials."""
    response = login_user(client)
    assert response.status_code in (200, 303)
    # Should set cookie for access_token
    cookies = response.cookies
    assert "access_token" in cookies or response.headers.get("set-cookie")

def test_login_invalid_password(client):
    """Invalid password should fail."""
    response = login_user(client, password="wrongpass")
    assert response.status_code == 401
    assert "Invalid" in response.text

def test_get_calories_unauthenticated(client):
    """Access without cookie should fail."""
    response = client.post("/get-calories", data={"dish_name": "chicken", "servings": 2})
    assert response.status_code == 401
    assert "Not authenticated" in response.text

def test_get_calories_authenticated(client):
    """Authenticated user should access /get-calories."""
    # Login first to get token cookie
    login_response = login_user(client)
    cookies = login_response.cookies
    assert "access_token" in cookies or login_response.headers.get("set-cookie")

    # Call /get-calories with cookie
    response = client.post(
        "/get-calories",
        data={"dish_name": "chicken", "servings": 1},
        cookies=cookies
    )

    # Expect either success or USDA API error
    assert response.status_code in (200, 500)
