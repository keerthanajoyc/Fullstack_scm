# app/routes/oauth.py
# Google OAuth has been removed. Use email/password authentication instead.
# Forgot password flow is available for account recovery.

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter(tags=["OAuth"])

# Stub endpoints - redirect to login
@router.get("/auth/google", include_in_schema=False)
async def google_login():
    """Google OAuth is disabled. Use email/password login instead."""
    return RedirectResponse("/login?flash=Google+OAuth+is+disabled.+Please+use+email+login.", status_code=303)


@router.get("/auth/google/callback", include_in_schema=False)
async def google_callback():
    """Google OAuth is disabled."""
    return RedirectResponse("/login?flash=Google+OAuth+is+disabled.", status_code=303)
