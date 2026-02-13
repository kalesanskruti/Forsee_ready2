import json
from confluent_kafka import Producer, Consumer
from app.core.config import settings
from loguru import logger

class EventBus:
    def __init__(self):
        self.producer = None
        try:
            self.producer = Producer({
                'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
                'client.id': 'forsee-backend'
            })
        except Exception as e:
            logger.warning(f"Kafka connection failed, EventBus disabled: {e}")

    def emit(self, topic: str, key: str, data: dict):
        if not self.producer:
            return

        try:
            self.producer.produce(
                topic,
                key=key,
                value=json.dumps(data).encode('utf-8'),
                callback=self._delivery_report
            )
            self.producer.poll(0)
        except Exception as e:
            logger.error(f"Failed to emit event to {topic}: {e}")

    def _delivery_report(self, err, msg):
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")

bus = EventBus()
