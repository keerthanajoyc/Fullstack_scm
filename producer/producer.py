import json
import random
import time
import os
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
from dotenv import load_dotenv

load_dotenv()

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC_NAME = os.getenv("RAW_TOPIC", "device_streams")  

print("\n---------------------")
print(" Kafka Producer Init ")
print("---------------------")
print(f"KAFKA_BROKER = {KAFKA_BROKER}")
print(f"TOPIC_NAME = {TOPIC_NAME}")


# ---------------------------------------------------------
# Auto Topic Creation
# ---------------------------------------------------------
def ensure_topic():
    try:
        admin = KafkaAdminClient(bootstrap_servers=KAFKA_BROKER)

        topic = NewTopic(
            name=TOPIC_NAME,
            num_partitions=3,
            replication_factor=1
        )

        admin.create_topics(new_topics=[topic], validate_only=False)
        print(f"Topic created: {TOPIC_NAME}")

    except TopicAlreadyExistsError:
        print(f"Topic already exists: {TOPIC_NAME}")

    except Exception as e:
        print(f"Topic creation failed: {e}")

    finally:
        try:
            admin.close()
        except:
            pass


# ---------------------------------------------------------
# Sensor Data Simulation
# ---------------------------------------------------------
def generate_sensor_data():
    return {
        "Device_ID": random.randint(1000, 9999),
        "Battery_Level": round(random.uniform(2.5, 4.2), 2),
        "Temperature": round(random.uniform(20, 40), 2),
        "Humidity": round(random.uniform(30, 80), 2),
        "Route_From": random.choice(["Chennai", "Delhi", "Mumbai"]),
        "Route_To": random.choice(["London", "Paris", "Tokyo"]),
        "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }


# ---------------------------------------------------------
# Kafka Connection Retry Logic
# ---------------------------------------------------------
def connect_kafka():
    retries = 5
    for attempt in range(retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            print("✔ Kafka Producer connected")
            return producer

        except Exception as e:
            print(f"Kafka connect failed (attempt {attempt+1}): {e}")
            time.sleep(5)

    print("Kafka connect failed after retries")
    exit(1)


# ---------------------------------------------------------
# Start Producer
# ---------------------------------------------------------
ensure_topic()  
producer = connect_kafka()

print("\nProducer running... pushing data to Kafka!\n")

if __name__ == "__main__":
    try:
        while True:
            data = generate_sensor_data()
            producer.send(TOPIC_NAME, data)
            producer.flush()
            print(f"Sent → {data}")
            time.sleep(2)

    except KeyboardInterrupt:
        print("Stopping Producer gracefully...")
    finally:
        producer.close()
        print("Producer stopped.")
