# app/core/db/mongo.py

import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# ---------------------------------------------------------
# ENV VARIABLES
# ---------------------------------------------------------
MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "fastapi_auth_db")

if not MONGO_URL:
    raise RuntimeError("MONGO_URL missing in .env or environment!")


# ---------------------------------------------------------
# MONGO CLIENT (Shared for App + Consumer)
# ---------------------------------------------------------
client = MongoClient(
    MONGO_URL,
    tls=True,
    tlsAllowInvalidCertificates=True
)


# ---------------------------------------------------------
# DATABASE REFERENCES
# ---------------------------------------------------------
auth_db = client[DB_NAME]              
stream_db = client.get_database("device_data")  


# ---------------------------------------------------------
# COLLECTION REFERENCES
# ---------------------------------------------------------
users_collection = auth_db["users"]
shipments_collection = auth_db["shipments"]
role_history_collection = auth_db["role_history"]

streams_collection = stream_db["streams"]
iot_collection = stream_db["iot_readings"]   


# ---------------------------------------------------------
# Helper: Expose all collections for consumer + services
# ---------------------------------------------------------
def get_collections():
    return {
        "users": users_collection,
        "shipments": shipments_collection,
        "streams": streams_collection,
        "role_history": role_history_collection,
        "iot_readings": iot_collection,
    }


def get_db():
    """Return main authentication DB reference."""
    return auth_db
