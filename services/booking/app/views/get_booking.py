import sys
from flask import make_response
from app import (
    booking_logger,
    app_manager_db_obj,
)
from common.pyportal_common.error_handlers.not_found_error_handler import (
    send_notfound_request_error_to_client,
)
from common.pyportal_common.error_handlers.internal_server_error_handler import (
    send_internal_server_error_to_client,
)
from app.models.booking_model import BookingModel


def get_booking(booking_id):
    try:
        booking_logger.info(
            f"REQUEST ==> Get booking: {booking_id}"
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

            response_data = {
                "booking": {
                    "bookingId": booking.ID,
                    "bookingReference": booking.BookingReference,
                    "userId": booking.UserID,
                    "flightId": booking.FlightID,
                    "numberOfSeats": booking.NumberOfSeats,
                    "totalPrice": str(booking.TotalPrice),
                    "status": booking.Status,
                    "createdAt": str(booking.CreatedAt),
                    "updatedAt": str(booking.UpdatedAt),
                }
            }

            response = make_response(response_data)
            response.headers["Content-Type"] = "application/json"
            response.status_code = 200

            app_manager_db_obj.close_session(session_instance=session)
            return response

        except Exception as ex:
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

