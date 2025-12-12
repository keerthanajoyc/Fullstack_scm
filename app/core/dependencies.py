# app/core/dependencies.py

from fastapi import Request, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

from app.core.security import decode_token
from app.core.config import users_collection


def _extract_token(request: Request) -> str | None:
    """
    Priority:
    1. Cookie: access_token  (browser UI)
    2. Authorization: Bearer <token>  (Swagger / API clients)
    """
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        return cookie_token

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[len("Bearer "):].strip()

    return None


def get_current_user(request: Request) -> str:
    """Extract and validate JWT token from request. Returns user email."""
    token = _extract_token(request)

    if not token:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    email = decode_token(token)
    if not email:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return email
