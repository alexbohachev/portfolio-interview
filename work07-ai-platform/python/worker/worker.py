"""MVP worker: читає document.uploaded і індексує документ у Elasticsearch."""
from __future__ import annotations

import json
import os
import time

from elasticsearch import Elasticsearch
from kafka import KafkaConsumer

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "document.uploaded")
INDEX = os.getenv("ES_INDEX", "agri-knowledge")
ES_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")


def main() -> None:
    es = Elasticsearch(ES_URL)
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP,
        auto_offset_reset="earliest",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        consumer_timeout_ms=1000,
    )
    while True:
        polled = False
        for msg in consumer:
            polled = True
            doc = msg.value
            doc_id = doc.get("doc_id", msg.key.decode() if msg.key else "unknown")
            es.index(index=INDEX, id=doc_id, document=doc)
            es.indices.refresh(index=INDEX)
        if not polled:
            time.sleep(2)


if __name__ == "__main__":
    main()