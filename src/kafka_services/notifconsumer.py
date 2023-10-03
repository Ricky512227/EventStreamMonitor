import json
import time

from kafka import KafkaConsumer
NOTIF_EMAIL_TOPIC = "emailtobenotfiedtouser"

consumer: KafkaConsumer = KafkaConsumer(NOTIF_EMAIL_TOPIC, bootstrap_servers="localhost:29092")

print("Consumer starts consuming.. the topic ::{0}".format(NOTIF_EMAIL_TOPIC))
while True:
    for msg in consumer:
        consumed_msg = json.loads(msg.value.decode())
        print(consumed_msg)