import json
import time
from kafka import KafkaProducer


class PyPortalKafkaProducer:

    def __init__(self, **kwargs):
        self.cmn_logger = kwargs.get('logger_instance')
        self.producer_ip_address = kwargs.get('producer_ip_address')
        self.producer_port = kwargs.get('producer_port')
        self.topic_to_set = None
        self.producer: KafkaProducer = KafkaProducer(bootstrap_servers=self.producer_ip_address + ":" + str(self.producer_port))
        for key, value in vars(self).items():
            self.cmn_logger.info(f"Initialized {key} with value: {value}")

    def assign_topic_to_producer(self, topic_to_set: str):
        self.topic_to_set = topic_to_set

    def _send_data_to_topic(self, data_to_be_sent):
        if self.topic_to_set is None:
            raise ValueError("Topic is not set to the producer to publish")
        self.producer.send(
            topic=self.topic_to_set,
            value=json.dumps(data_to_be_sent).encode("utf-8")
        )
        self.producer.flush()  # Ensure message is sent immediately

    def publish_data_to_producer(self, data_to_send):
        """
        Publish a single message or a list of messages to the topic.
        
        Args:
            data_to_send: dict or list of dicts to send
        """
        try:
            if isinstance(data_to_send, list):
                for data in data_to_send:
                    self._send_data_to_topic(data_to_be_sent=data)
                    self.cmn_logger.info(f"Message sent: {data}")
            else:
                self._send_data_to_topic(data_to_be_sent=data_to_send)
                self.cmn_logger.info(f"Message sent: {data_to_send}")
        except ValueError as e:
            self.cmn_logger.error(f"Error publishing message: {e}")
        except Exception as e:
            self.cmn_logger.error(f"Unexpected error: {e}")

    def publish_data_to_producer_range(self, range_start, range_end):
        """Legacy method for backward compatibility"""
        for i in range(range_start, range_end):
            datastore = {"message": f"Hello this is MSG :: {i}"}
            try:
                self._send_data_to_topic(data_to_be_sent=datastore)
                self.cmn_logger.info(f"Message sent :: {i}")
            except ValueError as e:
                self.cmn_logger.error(e)
            time.sleep(1)

    def close_the_producer(self):
        if self.producer is not None:
            self.producer.close()




    # notif_producer2 = PyPortalKafkaConsumer(producer_ip_address=producer_ip_address, producer_port=producer_port)
    # notif_producer2.topic_to_set = "emailtobenotfiedtouser"
    # notif_producer2.publish_data_to_cosumer(100, 200)
    # notif_producer2.close_the_producer()
