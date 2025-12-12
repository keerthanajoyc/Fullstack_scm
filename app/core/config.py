# app/core/config.py

import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
import bcrypt

load_dotenv()


# ======================================================
# APP SECURITY CONFIG
# ======================================================
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# ======================================================
# MONGODB CONFIG
# ======================================================
MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "fastapi_auth_db")

if not MONGO_URL:
    raise RuntimeError("MONGO_URL missing in environment!")

client = MongoClient(MONGO_URL, tls=True, tlsAllowInvalidCertificates=True)

auth_db = client[DB_NAME]
stream_db = client.get_database("device_data")

users_collection = auth_db["users"]
shipments_collection = auth_db["shipments"]

streams_collection = stream_db["streams"]
iot_readings_collection = stream_db["iot_readings"]

# ======================================================
# KAFKA / REDPANDA CONFIG
# ======================================================
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "device_streams")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "shipment-consumer-group")

# ======================================================
# EMAIL CONFIG
# ======================================================
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def get_consumer_collections():
    return {
        "shipments": shipments_collection,
        "iot_readings": iot_readings_collection,
    }
