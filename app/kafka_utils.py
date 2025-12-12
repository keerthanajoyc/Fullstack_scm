import os
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

def ensure_topic(topic_name: str, partitions: int = 3, replication_factor: int = 1):
    broker = os.getenv("KAFKA_BROKER", "localhost:9092")

    try:
        admin = KafkaAdminClient(bootstrap_servers=broker)

        topic = NewTopic(
            name=topic_name,
            num_partitions=partitions,
            replication_factor=replication_factor
        )

        admin.create_topics(
            new_topics=[topic],
            validate_only=False
        )
        print(f"✔ Created topic: {topic_name}")

    except TopicAlreadyExistsError:
        print(f"↺ Topic already exists: {topic_name}")

    except Exception as e:
        print(f"⚠ Kafka topic creation failed: {e}")

    finally:
        try:
            admin.close()
        except:
            pass
