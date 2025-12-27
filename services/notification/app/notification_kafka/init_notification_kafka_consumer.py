import json

import threading

from datetime import datetime

from kafka import KafkaConsumer

from app import (

    notification_logger,

    app_manager_db_obj,

)

from app.models.notification_model import (

    NotificationLogModel,

)

class NotificationKafkaConsumer:

    def __init__(self, logger_instance):

        self.logger = logger_instance

        self.consumer = None

        self.topics = [

            "user-registration-events",

            "task-events",

            "flight-updates"

        ]

        self.running = False

    def initialize_consumer(self):

        """Initialize Kafka consumer"""

        try:

            kafka_bootstrap_servers = "kafka:29092"  # Docker service name

            self.consumer = KafkaConsumer(

                *self.topics,

                bootstrap_servers=kafka_bootstrap_servers,

                value_deserializer=lambda m: json.loads(m.decode('utf-8')),

                group_id='notification-service-group',

                auto_offset_reset='earliest',

                enable_auto_commit=True

            )

            self.logger.info(

                f"Kafka consumer initialized for topics: {self.topics}"

            )

            return True

        # pylint: disable=broad-except

        except Exception as ex:

            self.logger.error(

                "Failed to initialize Kafka consumer: %s", ex

            )

            return False

    def process_notification(self, event_data, topic):

        """Process notification event and send notification"""

        try:

            event_type = event_data.get("eventType", "unknown")

            self.logger.info(

                f"Processing event: {event_type} from topic: {topic}"

            )

            # Determine notification details based on event type

            if event_type == "user_registered":

                subject = "Welcome to EventStreamMonitor"

                message = (

                    f"Welcome {event_data.get('username', 'User')}! "

                    f"Your account has been successfully created."

                )

                recipient_email = event_data.get("email")

                user_id = event_data.get("userId")

            elif event_type == "task_created":

                subject = "Task Created"

                message = (

                    f"Your task {event_data.get('taskReference')} "

                    f"has been created. "

                    f"Task Type: {event_data.get('taskType')}, "

                    f"Priority: {event_data.get('priority')}"

                )

                recipient_email = event_data.get("userEmail", "user@example.com")

                user_id = event_data.get("userId")

            elif event_type == "task_cancelled":

                subject = "Task Cancelled"

                message = (

                    f"Your task {event_data.get('taskReference')} "

                    f"has been cancelled."

                )

                recipient_email = event_data.get("userEmail", "user@example.com")

                user_id = event_data.get("userId")

            else:

                self.logger.warning(f"Unknown event type: {event_type}")

                return

            # Log notification to database

            session = app_manager_db_obj.get_session_from_session_maker()

            if session:

                try:

                    notification_log = NotificationLogModel(

                        EventType=event_type,

                        UserID=user_id,

                        RecipientEmail=recipient_email,

                        Subject=subject,

                        Message=message,

                        Status="sent",  # In production, check actual send status

                        SentAt=datetime.now(),

                        CreatedAt=datetime.now(),

                        UpdatedAt=datetime.now(),

                    )

                    session.add(notification_log)

                    session.commit()

                    self.logger.info(

                        f"Notification logged: {subject} to {recipient_email}"

                    )

                # pylint: disable=broad-except

                except Exception as db_ex:

                    session.rollback()

                    self.logger.error(

                        "Error logging notification: %s", db_ex

                    )

                finally:

                    app_manager_db_obj.close_session(session_instance=session)

            # In production, here you would:

            # - Send email via SMTP/SendGrid/etc

            # - Send SMS via Twilio/etc

            # - Send push notification

            self.logger.info(

                f"Notification sent: {subject} to {recipient_email}"

            )

        # pylint: disable=broad-except

        except Exception as ex:

            self.logger.error(

                "Error processing notification: %s", ex

            )

    def start_consuming(self):

        """Start consuming messages from Kafka"""

        if not self.initialize_consumer():

            return

        self.running = True

        self.logger.info("Starting Kafka consumer...")

        try:

            for message in self.consumer:

                if not self.running:

                    break

                try:

                    event_data = message.value

                    topic = message.topic

                    self.process_notification(event_data, topic)

                # pylint: disable=broad-except

                except Exception as ex:

                    self.logger.error(

                        "Error processing message: %s", ex

                    )

        # pylint: disable=broad-except

        except Exception as ex:

            self.logger.error("Consumer error: %s", ex)

        finally:

            if self.consumer:

                self.consumer.close()

            self.logger.info("Kafka consumer stopped")

    def stop_consuming(self):

        """Stop consuming messages"""

        self.running = False

        if self.consumer:

            self.consumer.close()

def start_notification_kafka_consumer(notification_logger):

    """Initialize and return Kafka consumer"""

    try:

        consumer = NotificationKafkaConsumer(notification_logger)

        return consumer

    # pylint: disable=broad-except

    except Exception as ex:

        notification_logger.error(

            "Failed to create Kafka consumer: %s", ex

        )

        return None
