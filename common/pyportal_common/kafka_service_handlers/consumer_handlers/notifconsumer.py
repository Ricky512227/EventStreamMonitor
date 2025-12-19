import json
from kafka import KafkaConsumer

NOTIF_EMAIL_TOPIC = "emailtobenotfiedtouser"

consumer: KafkaConsumer = KafkaConsumer(NOTIF_EMAIL_TOPIC,
                                        bootstrap_servers="localhost:29092")

while True:
    for msg in consumer:
        consumed_msg = json.loads(msg.value.decode())
