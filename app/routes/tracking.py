# app/routes/tracking.py

from fastapi import APIRouter, Request, Form, Depends, HTTPException

from app.core.dependencies import get_current_user
from app.services.shipments_service import (
    get_shipment_by_id,
    format_shipment_for_view,
)
from app.main import templates


ui_router = APIRouter(tags=["Tracking"])
api_router = APIRouter(prefix="/api/tracking", tags=["Tracking"], dependencies=[Depends(get_current_user)])


# ---------- UI (HTML) ----------

@ui_router.get("/track_shipment", include_in_schema=False)
async def track_page(request: Request, user_email: str = Depends(get_current_user)):
    return templates.TemplateResponse(
        "track_shipment.html",
        {
            "request": request,
            "result": None,
            "error": None,
            "last_iot": None,
            "history": None,
            "active_page": "track",
        },
    )


@ui_router.post("/track_shipment", include_in_schema=False)
async def track_shipment_ui(
    request: Request,
    shipment_id: str = Form(...),
    user_email: str = Depends(get_current_user),
):
    shipment_doc = get_shipment_by_id(shipment_id.strip())

    if not shipment_doc:
        return templates.TemplateResponse(
            "track_shipment.html",
            {
                "request": request,
                "result": None,
                "error": "Shipment not found.",
                "last_iot": None,
                "history": None,
                "active_page": "track",
            },
        )

    # User must be sender or receiver
    if shipment_doc.get("sender_email") != user_email and shipment_doc.get("receiver_email") != user_email:
        return templates.TemplateResponse(
            "track_shipment.html",
            {
                "request": request,
                "result": None,
                "error": "You do not have access to this shipment.",
                "last_iot": None,
                "history": None,
                "active_page": "track",
            },
        )

    shipment, history = format_shipment_for_view(shipment_doc)

    return templates.TemplateResponse(
        "track_shipment.html",
        {
            "request": request,
            "result": shipment,
            "last_iot": shipment.get("last_iot_data"),
            "history": history,
            "error": None,
            "active_page": "track",
        },
    )


# ---------- API (Swagger) ----------

@api_router.get("/{shipment_id}")
async def track_shipment_api(
    shipment_id: str,
    user_email: str = Depends(get_current_user),
):
    """Get tracking details for a shipment. User must be sender or receiver."""
    shipment_doc = get_shipment_by_id(shipment_id.strip())

    if not shipment_doc:
        raise HTTPException(status_code=404, detail="Shipment not found")

    if shipment_doc.get("sender_email") != user_email and shipment_doc.get("receiver_email") != user_email:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    shipment, history = format_shipment_for_view(shipment_doc)

    return {
        "shipment": shipment,
        "last_iot": shipment.get("last_iot_data"),
        "history": history,
    }
