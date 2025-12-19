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
            "booking-events",
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
        except Exception as ex:
            self.logger.error(f"Failed to initialize Kafka consumer: {ex}")
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

            elif event_type == "booking_created":
                subject = "Booking Confirmation"
                message = (
                    f"Your booking {event_data.get('bookingReference')} "
                    f"has been confirmed. "
                    f"Flight: {event_data.get('flightId')}, "
                    f"Seats: {event_data.get('numberOfSeats')}, "
                    f"Total: ${event_data.get('totalPrice')}"
                )
                recipient_email = event_data.get("userEmail", "user@example.com")
                user_id = event_data.get("userId")

            elif event_type == "booking_cancelled":
                subject = "Booking Cancellation"
                message = (
                    f"Your booking {event_data.get('bookingReference')} "
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
                except Exception as db_ex:
                    session.rollback()
                    self.logger.error(f"Error logging notification: {db_ex}")
                finally:
                    app_manager_db_obj.close_session(session_instance=session)

            # In production, here you would:
            # - Send email via SMTP/SendGrid/etc
            # - Send SMS via Twilio/etc
            # - Send push notification
            self.logger.info(
                f"Notification sent: {subject} to {recipient_email}"
            )

        except Exception as ex:
            self.logger.error(f"Error processing notification: {ex}")

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
                except Exception as ex:
                    self.logger.error(
                        f"Error processing message: {ex}"
                    )

        except Exception as ex:
            self.logger.error(f"Consumer error: {ex}")
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
    except Exception as ex:
        notification_logger.error(
            f"Failed to create Kafka consumer: {ex}"
        )
        return None

