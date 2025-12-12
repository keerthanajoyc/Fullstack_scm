# app/services/shipments_service.py

from datetime import datetime
from typing import Dict, Optional, Tuple, List

from app.core.config import shipments_collection


# ---------------------------------------------------------
# SHIPMENT ID GENERATION
# ---------------------------------------------------------
def generate_shipment_id() -> str:
    """
    Generate a unique shipment ID in format: Sxxxx
    Increments based on the count of existing shipments.
    """
    count = shipments_collection.count_documents({})
    next_num = count + 1
    return f"S{next_num:04d}"


# ---------------------------------------------------------
# BASIC LOOKUPS
# ---------------------------------------------------------
def get_shipment_by_id(shipment_id: str) -> Optional[Dict]:
    """
    Fetch a single shipment document by its shipment_id.
    Used by tracking route (/track_shipment).
    """
    if not shipment_id:
        return None
    return shipments_collection.find_one({"shipment_id": shipment_id})


def find_active_shipment_by_destination(destination: str) -> Optional[Dict]:
    """
    For IoT tracking:
    Find the oldest active shipment whose destination matches the IoT Route_To.
    Only shipments not yet delivered are considered.
    """
    if not destination:
        return None

    return shipments_collection.find_one(
        {
            "destination": {"$regex": f"^{destination}$", "$options": "i"},
            "status": {"$ne": "Delivered"},
        },
        sort=[("created_at", 1)],
    )


# ---------------------------------------------------------
# WRITE OPERATIONS (STATUS + SNAPSHOT)
# ---------------------------------------------------------
def update_shipment(shipment: Dict, new_status: str, iot_data: Dict) -> None:
    """
    Full update when a status change happens:
      - status
      - last_iot_data
      - current_location
      - last_updated
      - append to status_history
    """
    now = datetime.utcnow()

    shipments_collection.update_one(
        {"shipment_id": shipment["shipment_id"]},
        {
            "$set": {
                "status": new_status,
                "last_iot_data": iot_data,
                "current_location": iot_data.get("Route_From"),
                "last_updated": now,
            },
            "$push": {
                "status_history": {
                    "from": shipment.get("status"),
                    "to": new_status,
                    "ts": now,
                    "iot": iot_data,
                }
            },
        },
    )


def snapshot_update(shipment_id: str, iot_data: Dict) -> None:
    """
    Lightweight update when status DOES NOT change:
      - last_iot_data
      - current_location
      - last_updated
    """
    now = datetime.utcnow()

    shipments_collection.update_one(
        {"shipment_id": shipment_id},
        {
            "$set": {
                "last_iot_data": iot_data,
                "current_location": iot_data.get("Route_From"),
                "last_updated": now,
            }
        },
    )


# ---------------------------------------------------------
# VIEW HELPERS FOR TRACKING PAGE
# ---------------------------------------------------------
def format_shipment_for_view(raw: Dict) -> Tuple[Dict, List[Dict]]:
    """
    Takes a raw shipment document and returns:
      - formatted shipment dict (string timestamps)
      - formatted status history (latest first)
    Used by the /track_shipment route.
    """
    shipment = dict(raw)

    # Format top-level timestamps
    for key in ["created_at", "last_updated"]:
        ts = shipment.get(key)
        if hasattr(ts, "strftime"):
            shipment[key] = ts.strftime("%Y-%m-%d %H:%M:%S")

    # Format history entries
    history = shipment.get("status_history", []) or []
    formatted_history: List[Dict] = []

    for h in history:
        entry = dict(h)
        ts = entry.get("ts")
        if hasattr(ts, "strftime"):
            entry["ts"] = ts.strftime("%Y-%m-%d %H:%M:%S")
        formatted_history.append(entry)

    # Newest first
    formatted_history.sort(key=lambda x: x["ts"], reverse=True)

    return shipment, formatted_history
