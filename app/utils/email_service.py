from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from datetime import datetime

from app.core.config import EMAIL_SENDER, EMAIL_PASSWORD


# =====================================================
# BASIC EMAIL SENDER (Plain-Text Only)
# =====================================================
def _send_email(to_email: str, subject: str, body: str):
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print("⚠ Email credentials not set. Skipping email...")
        return

    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)

        print(f"Email sent → {to_email}")

    except Exception as e:
        print(f" Email send failed → {to_email}: {e}")


# =====================================================
# SHIPMENT CREATION EMAIL
# =====================================================
def send_shipment_created_email(shipment: dict, created_by: str):
    shipment_id = shipment.get("shipment_id", "Unknown")
    sender = shipment.get("sender_name", "Sender")
    receiver = shipment.get("receiver_name", "Receiver")
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    body = f"""
Shipment Successfully Created 

Shipment ID: {shipment_id}
Sender: {sender}
Receiver: {receiver}
Origin: {shipment.get('initial_location')}
Destination: {shipment.get('destination').title()}
Created By: {created_by}
Created At: {ts}

Track status anytime in SCMLite!

Regards,
SCMLite Admin Team
"""

    # Notify Sender
    if shipment.get("sender_email"):
        _send_email(
            shipment["sender_email"],
            f"Shipment {shipment_id} Created",
            body
        )

    # Notify Receiver
    if shipment.get("receiver_email"):
        _send_email(
            shipment["receiver_email"],
            f"Incoming Shipment {shipment_id}",
            body.replace("Successfully Created", "Incoming"),
        )


# =====================================================
# SHIPMENT STATUS CHANGE EMAIL
# =====================================================
def notify_shipment_status_change(shipment: dict, old_status: str, new_status: str, iot_data=None):
    shipment_id = shipment.get("shipment_id", "Unknown")
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    iot_text = ""
    if iot_data:
        iot_text = "\nLatest IoT Sensor Data:\n"
        for key, val in iot_data.items():
            iot_text += f" - {key}: {val}\n"

    body = f"""
Shipment Status Update 

Shipment ID: {shipment_id}
Old Status: {old_status}
New Status: {new_status}
Updated At: {ts}
{iot_text}

Stay tuned for more updates!

Regards,
SCMLite Admin Team
"""

    subject = f"Shipment {shipment_id} Status: {new_status}"

    for field in ["sender_email", "receiver_email"]:
        if shipment.get(field):
            _send_email(shipment[field], subject, body)
