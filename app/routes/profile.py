# app/routes/profile.py

from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse


from app.core.config import users_collection
from app.core.security import hash_password
from app.core.dependencies import get_current_user
from app.main import templates


ui_router = APIRouter(tags=["Profile"])
api_router = APIRouter(prefix="/api/profile", tags=["Profile"], dependencies=[Depends(get_current_user)])


# ---------- UI (HTML) ----------

@ui_router.get("/profile", include_in_schema=False)
async def profile_page(request: Request, user_email: str = Depends(get_current_user)):
    flash = request.cookies.get("flash")
    user = users_collection.find_one({"email": user_email}, {"password": 0})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    context = {
        "request": request,
        "user": user,
        "active_page": "profile",
        "flash": flash,
    }

    response = templates.TemplateResponse("profile.html", context)
    if flash:
        response.delete_cookie("flash")
    return response


@ui_router.post("/profile", include_in_schema=False)
async def update_profile_ui(
    request: Request,
    fullname: str = Form(...),
    new_password: str = Form(None),
    user_email: str = Depends(get_current_user),
):
    update_fields = {"name": fullname.strip()}

    if new_password and new_password.strip():
        update_fields["password"] = hash_password(new_password)

    users_collection.update_one({"email": user_email}, {"$set": update_fields})

    response = RedirectResponse("/profile", status_code=303)
    response.set_cookie("flash", "Profile updated ", max_age=3)
    return response


# ---------- API (Swagger) ----------

@api_router.get("/")
async def get_profile_api(user_email: str = Depends(get_current_user)):
    user = users_collection.find_one({"email": user_email}, {"password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}


@api_router.put("/")
async def update_profile_api(
    fullname: str = Form(...),
    new_password: str = Form(None),
    user_email: str = Depends(get_current_user),
):
    update_fields = {"name": fullname.strip()}

    if new_password and new_password.strip():
        update_fields["password"] = hash_password(new_password)

    users_collection.update_one({"email": user_email}, {"$set": update_fields})
    return {"message": "Profile updated successfully"}
