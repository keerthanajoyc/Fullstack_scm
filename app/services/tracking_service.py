import json
from datetime import datetime
from kafka import KafkaConsumer
from fastapi import BackgroundTasks

from app.core.config import (
    KAFKA_BROKER,
    KAFKA_TOPIC,
    get_consumer_collections
)

from app.services.shipments_service import (
    find_active_shipment_by_destination,
    update_shipment,
    snapshot_update
)

from app.services.status_service import derive_status
from app.utils.email_service import notify_shipment_status_change


collections = get_consumer_collections()
iot_col = collections["iot_readings"]


def start_tracking_engine():
    print("Tracking Engine ACTIVE")

    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=[KAFKA_BROKER],
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        enable_auto_commit=True,
        auto_offset_reset="latest",
        group_id="tracking-engine",
    )

    for msg in consumer:
        payload = msg.value
        if not payload:
            continue

        route_to = (payload.get("Route_To") or "").strip().lower()
        shipment = find_active_shipment_by_destination(route_to)

        if not shipment:
            continue

        payload["received_at"] = datetime.utcnow()
        iot_col.insert_one(payload)

        old_status = shipment.get("status", "Created")
        new_status = derive_status(payload, shipment)

        if new_status != old_status:
            update_shipment(shipment, new_status, payload)
            notify_shipment_status_change(shipment, old_status, new_status, payload)
        else:
            snapshot_update(shipment["shipment_id"], payload)
