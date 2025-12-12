# app/services/status_service.py

from typing import Dict


def derive_status(iot: Dict, shipment: Dict) -> str:
    """
    Determine new shipment status based on IoT telemetry.

    Rules:
      - If Route_To == destination     → Delivered
      - If Battery_Level < 3.0         → Delayed (Low Battery)
      - If Temperature > 35            → Delayed (High Temp)
      - If shipment was Pending        → In Transit
      - Otherwise                      → In Transit
    """

    battery = float(iot.get("Battery_Level", 0) or 0)
    temp = float(iot.get("Temperature", 0) or 0)

    route_to = (iot.get("Route_To") or "").strip().lower()
    destination = (shipment.get("destination") or "").strip().lower()

    # Delivered
    if route_to and destination and route_to == destination:
        return "Delivered"

    # Delay rules
    if battery < 3.0:
        return "Delayed (Low Battery)"

    if temp > 35:
        return "Delayed (High Temp)"

    # First movement → goes to In Transit
    if shipment.get("status") == "Pending":
        return "In Transit"

    # Default
    return "In Transit"
