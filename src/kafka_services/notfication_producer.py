import json
import time

from kafka import KafkaProducer
from confluent_kafka import Producer

class PyPortalKafkaConsumer:
    def __init__(self, producer_ip_address, producer_port):
        self.topic_to_set = None
        self.producer: KafkaProducer = KafkaProducer(bootstrap_servers=producer_ip_address + ":" + str(producer_port))
        for key, value in vars(self).items():
            print(f"Initialized {key} with value: {value}")

    def assign_topic_to_producer(self, topic_name):
        self.topic_to_set = topic_name

    def _send_data_to_topic(self, data_to_be_sent):
        if self.topic_to_set is None:
            raise ValueError("Topic is not set to the producer to publish")
        self.producer.send(topic=self.topic_to_set, value=json.dumps(data_to_be_sent).encode("utf-8"))

    def publish_some_data(self, range_start, range_end):
        for i in range(range_start, range_end):
            datastore = {"message": "Hello this is MSG :: {0}".format(i)}
            try:
                self._send_data_to_topic(data_to_be_sent=datastore)
                print("Message sent :: {0}".format(i))
            except ValueError as e:
                print(e)
            time.sleep(1)

    def close_the_producer(self):
        if self.producer is not None:
            self.producer.close()


if __name__ == "__main__":
    producer_ip_address = "127.0.0.1"
    producer_port = 29092
    notif_producer = PyPortalKafkaConsumer(producer_ip_address=producer_ip_address, producer_port=producer_port)
    notif_producer.topic_to_set = "emailtobenotfiedtouser"
    notif_producer.publish_some_data(1, 20)
    notif_producer.close_the_producer()

    # notif_producer2 = PyPortalKafkaConsumer(producer_ip_address=producer_ip_address, producer_port=producer_port)
    # notif_producer2.topic_to_set = "emailtobenotfiedtouser"
    # notif_producer2.publish_some_data(100, 200)
    # notif_producer2.close_the_producer()
