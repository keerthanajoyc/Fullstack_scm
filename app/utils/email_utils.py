# app/utils/email_utils.py 

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from datetime import datetime

from app.core.config import EMAIL_SENDER, EMAIL_PASSWORD


# ============================================================
# BASIC EMAIL SENDER (Plain Text Format)
# ============================================================
def _send_email(to_email: str, subject: str, body: str):
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print("⚠ Email credentials missing — skipping email.")
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
        print(f"Email failed → {to_email}: {e}")


# ============================================================
# NEW ACCOUNT EMAIL (Signup)
# ============================================================
def send_account_created_email(to_email: str, username: str, password: str):
    subject = "SCMLite - Your Login Credentials"

    body = f"""
Hello {username},

Welcome to SCMLite!

Your account has been successfully created.

Login Credentials:
------------------
Email: {to_email}
Password: {password}

Login here:
https://scmlite-login.com/   

For security, please change your password after your first login.

If you did not request this account, please notify support immediately.

Regards,
SCMLite Admin Team
"""

    _send_email(to_email, subject, body)


# ============================================================
# PASSWORD RESET EMAIL
# ============================================================
def send_password_reset_email(to_email: str, reset_link: str):
    subject = "SCMLite - Password Reset Request"

    body = f"""
Hello,

We received a request to reset the password for your SCMLite account.

To reset your password, click the link below (valid for 1 hour):

{reset_link}

If you did not request a password reset, please ignore this email or contact support.

For security reasons, never share this link with anyone.

Regards,
SCMLite Admin Team
"""

    _send_email(to_email, subject, body)


# ============================================================
# SHIPMENT CREATION EMAIL
# ============================================================
def send_shipment_created_email(shipment: dict, created_by: str):
    shipment_id = shipment.get("shipment_id", "Unknown")
    created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    subject = f"SCMLite - Shipment {shipment_id} Created"

    body = f"""
Dear User,

A new shipment has been registered.

Shipment Information:
--------------------
Shipment ID   : {shipment_id}
Origin        : {shipment.get('initial_location')}
Destination   : {shipment.get('destination', '').title()}
Weight        : {shipment.get('weight')} kg
Sender        : {shipment.get('sender_name')}
Receiver      : {shipment.get('receiver_name')}
Created By    : {created_by}
Created At    : {created_at}

You will receive tracking updates as the shipment progresses.

Thank you,

Regards,
SCMLite Admin Team
"""

    for field in ["sender_email", "receiver_email"]:
        if shipment.get(field):
            _send_email(shipment[field], subject, body)
