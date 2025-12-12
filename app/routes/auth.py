# app/routes/auth.py

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from datetime import datetime

from app.core.config import users_collection
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
    validate_password,
    create_reset_token,
    verify_reset_token,
)
from app.core.dependencies import get_current_user
from app.utils.email_utils import send_account_created_email, send_password_reset_email
from urllib.parse import unquote
from app.main import templates


# =======================
# UI ROUTER (HTML)
# =======================
ui_router = APIRouter(tags=["Auth"])


def redirect_user(email: str) -> str:
    """Always redirect to home after login; dashboard is a page in home"""
    return "/home"



@ui_router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def landing_page(request: Request, flash: str = None):
    token = request.cookies.get("access_token")
    if token:
        email = decode_token(token)
        if email:
            return RedirectResponse(redirect_user(email), status_code=303)

    # Read flash from cookie OR URL param
    flash_cookie = request.cookies.get("flash")
    flash_msg = flash or flash_cookie  # Prefer URL message if exists
    flash_msg = unquote(flash_msg) if flash_msg else None

    response = templates.TemplateResponse(
        "landing.html",
        {"request": request, "flash": flash_msg},
    )

    # Only delete message if stored in cookies
    if flash_cookie:
        response.delete_cookie("flash")

    return response


@ui_router.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def login_page(request: Request):
    flash = request.cookies.get("flash")
    response = templates.TemplateResponse(
        "login.html",
        {"request": request, "flash": flash},
    )
    if flash:
        response.delete_cookie("flash")
    return response


@ui_router.post("/login", include_in_schema=False)
async def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
    email = email.strip()
    user = users_collection.find_one({"email": email})

    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "flash": "User not found. Please sign up first."},
        )

    if not verify_password(password, user["password"]):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "flash": "Invalid email or password"},
        )

    token = create_access_token(email)
    response = RedirectResponse("/home", status_code=303)
    response.set_cookie("access_token", token, httponly=True, samesite="strict")
    # Clear the re-auth flag on successful login
    response.delete_cookie("require_reauth")
    response.set_cookie("flash", "Login successful!", max_age=3)
    return response


@ui_router.get("/signup", response_class=HTMLResponse, include_in_schema=False)
async def signup_page(request: Request):
    flash = request.cookies.get("flash")
    response = templates.TemplateResponse(
        "signup.html",
        {"request": request, "flash": flash},
    )
    if flash:
        response.delete_cookie("flash")
    return response


@ui_router.post("/signup", include_in_schema=False)
async def signup_user(
    request: Request,
    fullname: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    fullname = fullname.strip()
    email = email.strip()

    if password != confirm_password:
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "flash": "Passwords do not match!"},
        )

    if not validate_password(password):
        return templates.TemplateResponse(
            "signup.html",
            {"request": request,
             "flash": "Weak Password — Min 8 chars, uppercase, lowercase, number, special char (!@#$%^&*)"},
        )

    if users_collection.find_one({"email": email}):
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "flash": "Email already registered!"},
        )

    users_collection.insert_one({
        "name": fullname,
        "email": email,
        "password": hash_password(password),
        "role": "User",
        "status": "Active",
        "created_at": datetime.utcnow(),
    })

    try:
        send_account_created_email(email, fullname, password)
    except Exception:
        pass

    response = RedirectResponse("/login", status_code=303)
    response.set_cookie("flash", "Signup successful! Please login.", max_age=3)
    return response


@ui_router.get("/forgot-password", response_class=HTMLResponse, include_in_schema=False)
async def forgot_password_page(request: Request):
    flash = request.cookies.get("flash")
    response = templates.TemplateResponse(
        "forgot_password.html",
        {"request": request, "flash": flash},
    )
    if flash:
        response.delete_cookie("flash")
    return response


@ui_router.post("/forgot-password", include_in_schema=False)
async def forgot_password_submit(
    request: Request,
    email: str = Form(...),
):
    email = email.strip()
    user = users_collection.find_one({"email": email})

    if not user:
        # Don't reveal if email exists (security)
        return templates.TemplateResponse(
            "forgot_password.html",
            {"request": request, "success": "If an account exists, a reset link has been sent to your email."},
        )

    reset_token = create_reset_token(email)
    reset_link = f"http://localhost:8000/reset-password/{reset_token}"  # TODO: Use DOMAIN env var

    try:
        send_password_reset_email(email, reset_link)
    except Exception:
        pass

    return templates.TemplateResponse(
        "forgot_password.html",
        {"request": request, "success": "If an account exists, a reset link has been sent to your email."},
    )


@ui_router.get("/reset-password/{token}", response_class=HTMLResponse, include_in_schema=False)
async def reset_password_page(request: Request, token: str):
    email = verify_reset_token(token)
    
    if not email:
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "flash": "Invalid or expired reset link. Please try again."},
        )

    response = templates.TemplateResponse(
        "reset_password.html",
        {"request": request, "flash": None},
    )
    return response


@ui_router.post("/reset-password/{token}", include_in_schema=False)
async def reset_password_submit(
    request: Request,
    token: str,
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    email = verify_reset_token(token)
    
    if not email:
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "flash": "Invalid or expired reset link. Please try again."},
        )

    if password != confirm_password:
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "flash": "Passwords do not match!"},
        )

    if not validate_password(password):
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request,
             "flash": "Weak Password — Min 8 chars, uppercase, lowercase, number, special char (!@#$%^&*)"},
        )

    # Update password in DB
    users_collection.update_one(
        {"email": email},
        {"$set": {"password": hash_password(password)}}
    )

    response = RedirectResponse("/login", status_code=303)
    response.set_cookie("flash", "Password reset successful! Please login.", max_age=3)
    return response


@ui_router.get("/logout", include_in_schema=False)
async def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("access_token")
    # Set flag to restrict email access until re-authentication
    response.set_cookie("require_reauth", "true", httponly=True, samesite="strict", max_age=86400)
    response.set_cookie("flash", "Logged out successfully. Please login again to continue.", max_age=3)
    return response


# =======================
# API ROUTER
# =======================
api_router = APIRouter(prefix="/api/auth", tags=["Auth"])


@api_router.post("/login")
async def api_login(
    email: str = Form(...),
    password: str = Form(...)
):
    email = email.strip()
    user = users_collection.find_one({"email": email})

    if not user or not verify_password(password, user["password"]):
        return {"detail": "Invalid credentials"}

    return {"access_token": create_access_token(email), "token_type": "bearer"}


@api_router.post("/signup")
async def api_signup(
    fullname: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    fullname = fullname.strip()
    email = email.strip()

    if password != confirm_password:
        return {"detail": "Passwords do not match"}

    if not validate_password(password):
        return {"detail": "Weak Password — Min 8 chars, uppercase, lowercase, number, special char (!@#$%^&*)"}

    if users_collection.find_one({"email": email}):
        return {"detail": "Email already registered"}

    users_collection.insert_one({
        "name": fullname,
        "email": email,
        "password": hash_password(password),
        "role": "User",
        "status": "Active",
        "created_at": datetime.utcnow(),
    })

    return {"message": "Signup successful"}


@api_router.get("/me")
async def api_me(user_email: str = Depends(get_current_user)):
    user = users_collection.find_one({"email": user_email}, {"password": 0})
    return {"user": user}
