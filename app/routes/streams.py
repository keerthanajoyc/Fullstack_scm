from fastapi import APIRouter, Request, Depends
from app.core.config import streams_collection
from app.core.dependencies import get_current_user
from app.main import templates

ui_router = APIRouter(tags=["Stream"])
api_router = APIRouter(prefix="/api/streams", tags=["Stream"])
# 💡 removed dependency=[Depends(get_current_user)]


# ---------- UI ROUTE ----------
@ui_router.get("/DataStream", include_in_schema=False)
async def data_stream_page(request: Request, user_email: str = Depends(get_current_user)):
    return templates.TemplateResponse(
        "data_stream.html",
        {
            "request": request,
            "active_page": "stream",
        },
    )


# ---------- API ROUTE (NO FILTERING) ----------
@api_router.get("/")
async def get_stream_data():
    """Return latest 50 IoT streaming records from MongoDB (NO user or route filtering)."""
    try:
        docs = list(
            streams_collection.find({}, {"_id": 0})
            .sort("Timestamp", -1)
            .limit(50)
        )
        return docs
    
    except Exception as e:
        print(f"Stream error: {str(e)}")
        return []
