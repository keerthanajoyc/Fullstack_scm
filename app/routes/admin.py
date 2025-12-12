# app/routes/admin.py
# Admin routes have been removed. All users now have equal access.
# Users can only access their own profile and data.

from fastapi import APIRouter

# Stub routers to prevent import errors
ui_router = APIRouter(tags=["Admin"])
api_router = APIRouter(prefix="/api/admin", tags=["Admin"])
