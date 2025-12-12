from kafka import KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
from pymongo import MongoClient
import json
import os
import sys
import time

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC_NAME = os.getenv("RAW_TOPIC", "device_streams")
MONGO_URL = os.getenv("MONGO_URL")

print("\n---------------------")
print(" Kafka Consumer Init ")
print("---------------------")
print(f"KAFKA_BROKER = {KAFKA_BROKER}")
print(f"TOPIC_NAME = {TOPIC_NAME}")
print("MongoDB: Using MongoDB Atlas URL")


# ---------------------------------------------------------
# Auto-Create Kafka Topic (Producer/Consumer friendly)
# ---------------------------------------------------------
def ensure_topic():
    try:
        admin = KafkaAdminClient(bootstrap_servers=KAFKA_BROKER)

        topic = NewTopic(
            name=TOPIC_NAME,
            num_partitions=3,
            replication_factor=1  # MSK will override in production
        )

        admin.create_topics(new_topics=[topic], validate_only=False)
        print(f"Topic created: {TOPIC_NAME}")

    except TopicAlreadyExistsError:
        print(f"Topic already exists: {TOPIC_NAME}")

    except Exception as e:
        print("Topic creation failed:", e)

    finally:
        try:
            admin.close()
        except:
            pass


# ---------------------------------------------------------
# MongoDB Connect
# ---------------------------------------------------------
def connect_mongo():
    if not MONGO_URL:
        print("Missing MONGO_URL environment variable")
        sys.exit(1)

    try:
        client = MongoClient(MONGO_URL, tls=True, tlsAllowInvalidCertificates=True)
        print("✔ Connected to MongoDB Atlas")
        return client["device_data"]["streams"]
    except Exception as e:
        print("MongoDB Atlas connection failed:", e)
        sys.exit(1)


# ---------------------------------------------------------
# Kafka Consumer Connect
# ---------------------------------------------------------
def create_consumer():
    retries = 5
    for attempt in range(retries):
        try:
            consumer = KafkaConsumer(
                TOPIC_NAME,
                bootstrap_servers=[KAFKA_BROKER],
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                auto_offset_reset="earliest",
                enable_auto_commit=True
            )
            print("Kafka Consumer connected")
            return consumer
        except Exception as e:
            print(f"Kafka connection failed (attempt {attempt+1}/{retries}): {e}")
            time.sleep(5)

    print(" Kafka failed after retries")
    sys.exit(1)


# ---------------------------------------------------------
# Start
# ---------------------------------------------------------
ensure_topic() 
collection = connect_mongo()
consumer = create_consumer()

print("\n Consumer is running... (Writing to MongoDB Atlas)\n")

def consume_messages():
    for message in consumer:
        data = message.value
        print(f" Received: {data}")
        try:
            collection.insert_one(data)
            print(" Data inserted in MongoDB Atlas")
        except Exception as e:
            print("Insert Error:", e)


if __name__ == "__main__":
    consume_messages()
