from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from .database import Base, engine
from .routes import auth_routes, calorie_routes
from .middleware.rate_limit import limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

app = FastAPI(title="Meal Calorie Count Generator")

Base.metadata.create_all(bind=engine)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth_routes.router)
app.include_router(calorie_routes.router)

frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/", include_in_schema=False)
def serve_home():
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/register", include_in_schema=False)
def serve_register_page():
    return FileResponse(os.path.join(frontend_path, "register.html"))

@app.get("/login", include_in_schema=False)
def serve_login_page():
    return FileResponse(os.path.join(frontend_path, "login.html"))

@app.get("/calories", include_in_schema=False)
def serve_calorie_page():
    return FileResponse(os.path.join(frontend_path, "calories.html"))
