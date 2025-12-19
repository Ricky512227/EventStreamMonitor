import sys
from datetime import datetime
from flask import make_response
from app import (
    booking_logger,
    app_manager_db_obj,
    booking_kafka_producer,
)
from common.pyportal_common.error_handlers.not_found_error_handler import (
    send_notfound_request_error_to_client,
)
from common.pyportal_common.error_handlers.invalid_request_handler import (
    send_invalid_request_error_to_client,
)
from common.pyportal_common.error_handlers.internal_server_error_handler import (
    send_internal_server_error_to_client,
)
from app.models.booking_model import (
    BookingModel,
    FlightModel,
)


def cancel_booking(booking_id):
    try:
        booking_logger.info(
            f"REQUEST ==> Cancel booking: {booking_id}"
        )
        
        session = app_manager_db_obj.get_session_from_session_maker()
        if session is None:
            return send_internal_server_error_to_client(
                app_logger_name=booking_logger,
                message_data="Create Session Failed",
            )

        try:
            booking = session.query(BookingModel).filter(
                BookingModel.ID == booking_id
            ).first()

            if not booking:
                app_manager_db_obj.close_session(session_instance=session)
                return send_notfound_request_error_to_client(
                    app_logger_name=booking_logger,
                    message_data="Booking not found",
                )

            if booking.Status == "cancelled":
                app_manager_db_obj.close_session(session_instance=session)
                return send_invalid_request_error_to_client(
                    app_logger_name=booking_logger,
                    message_data="Booking already cancelled",
                )

            # Update booking status
            booking.Status = "cancelled"
            booking.UpdatedAt = datetime.now()

            # Restore seats to flight
            flight = session.query(FlightModel).filter(
                FlightModel.ID == booking.FlightID
            ).first()
            if flight:
                flight.AvailableSeats += booking.NumberOfSeats
                flight.UpdatedAt = datetime.now()

            # Commit transaction
            session.commit()

            booking_logger.info(
                f"Booking cancelled successfully: {booking.BookingReference}"
            )

            # Publish cancellation event to Kafka
            if booking_kafka_producer:
                try:
                    cancel_event = {
                        "eventType": "booking_cancelled",
                        "bookingId": booking.ID,
                        "bookingReference": booking.BookingReference,
                        "userId": booking.UserID,
                        "flightId": booking.FlightID,
                        "timestamp": datetime.now().isoformat(),
                    }
                    booking_kafka_producer.publish_data_to_producer(
                        cancel_event
                    )
                    booking_logger.info(
                        f"Published cancellation event to Kafka: "
                        f"{booking.BookingReference}"
                    )
                except Exception as kafka_ex:
                    booking_logger.warning(
                        f"Failed to publish to Kafka: {kafka_ex}"
                    )

            response_data = {
                "booking": {
                    "bookingId": booking.ID,
                    "bookingReference": booking.BookingReference,
                    "status": "cancelled",
                    "message": "Booking cancelled successfully",
                }
            }

            response = make_response(response_data)
            response.headers["Content-Type"] = "application/json"
            response.status_code = 200

            app_manager_db_obj.close_session(session_instance=session)
            return response

        except Exception as ex:
            session.rollback()
            app_manager_db_obj.close_session(session_instance=session)
            booking_logger.error(
                f"Error occurred :: {ex}\t"
                f"Line No:: {sys.exc_info()[2].tb_lineno}"
            )
            return send_internal_server_error_to_client(
                app_logger_name=booking_logger,
                message_data="Database Error",
            )

    except Exception as ex:
        booking_logger.exception(
            f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
        )
        return send_internal_server_error_to_client(
            app_logger_name=booking_logger,
            message_data="Unknown error caused",
        )

