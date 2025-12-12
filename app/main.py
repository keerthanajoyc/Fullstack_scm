# app/main.py

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.openapi.utils import get_openapi
from fastapi.templating import Jinja2Templates
import threading
from app.services.tracking_service import start_tracking_engine




app = FastAPI(
    title="SCMLite API",
    version="2.0.0",
    description="SCMLite backend with dual auth: Cookie (UI) + Bearer (Swagger API)",
)

# ============================
# Static & Templates
# ============================
templates = Jinja2Templates(directory="/app/app/templates")
app.mount("/static", StaticFiles(directory="/app/app/static"), name="static")




# ============================
# Swagger Bearer Token Button
# ============================
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    schema.setdefault("components", {}).setdefault("securitySchemes", {})
    schema["components"]["securitySchemes"]["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }

    schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi

# ============================
# Include Routers
# ============================

from app.routes.auth import ui_router as auth_ui_router, api_router as auth_api_router
from app.routes.home import ui_router as home_ui_router, api_router as home_api_router
from app.routes.profile import ui_router as profile_ui_router, api_router as profile_api_router
from app.routes.shipments import ui_router as shipments_ui_router, api_router as shipments_api_router
from app.routes.tracking import ui_router as tracking_ui_router, api_router as tracking_api_router
from app.routes.streams import ui_router as streams_ui_router, api_router as streams_api_router
from app.routes.admin import ui_router as admin_ui_router, api_router as admin_api_router
from app.routes.users import api_router as users_api_router

# UI HTML routes
app.include_router(auth_ui_router)
app.include_router(home_ui_router)
app.include_router(profile_ui_router)
app.include_router(shipments_ui_router)
app.include_router(tracking_ui_router)
app.include_router(streams_ui_router)
app.include_router(admin_ui_router)

# API JSON routes
app.include_router(auth_api_router)
app.include_router(home_api_router)
app.include_router(profile_api_router)
app.include_router(shipments_api_router)
app.include_router(tracking_api_router)
app.include_router(streams_api_router)
app.include_router(admin_api_router)
app.include_router(users_api_router)

# ============================
# Startup Event
# ============================
from urllib.parse import quote
from app.core.security import decode_token

@app.on_event("startup")
async def startup_event():
    """Application startup tasks."""
    print("SCMLite backend initialized")

PUBLIC_UI_PATHS = {"/", "/login", "/signup", "/forgot-password"}

@app.middleware("http")
async def auth_redirect_middleware(request: Request, call_next):
    path = request.url.path.lower()
    token = request.cookies.get("access_token")
    require_reauth = request.cookies.get("require_reauth")
    email = decode_token(token) if token else None
    logged_in = email is not None

    # API → Always allow (FastAPI security handles auth)
    if path.startswith("/api"):
        return await call_next(request)

    # Reset password routes (dynamic) - allow for everyone
    if path.startswith("/reset-password/"):
        return await call_next(request)

    # Public routes
    if path in PUBLIC_UI_PATHS:
        # If already logged in and go to "/" → go dashboard
        if logged_in and path == "/":
            return RedirectResponse("/dashboard", status_code=303)
        return await call_next(request)

    # Protected routes → must be logged in
    if not logged_in:
        flash_msg = quote("Please login first!")
        return RedirectResponse(f"/?flash={flash_msg}", status_code=303)

    # After logout, restrict email access until re-authentication
    if require_reauth and path == "/profile":
        flash_msg = quote("Please login again to access your profile.")
        return RedirectResponse(f"/?flash={flash_msg}", status_code=303)

    # Allow & disable caching for authenticated pages
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    return response
