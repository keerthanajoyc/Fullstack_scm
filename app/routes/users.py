# app/routes/users.py
# User management routes have been removed. All users have equal access.
# Users can only manage their own profile and data.

from fastapi import APIRouter

# Stub router to prevent import errors
api_router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
)
