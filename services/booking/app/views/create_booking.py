import sys
import json
import uuid
from datetime import datetime
from flask import request, make_response
from app import (
    booking_logger,
    booking_manager,
    app_manager_db_obj,
    booking_kafka_producer,
    booking_headers_schema,
    booking_req_schema,
)
from common.pyportal_common.error_handlers.invalid_request_handler import (
    send_invalid_request_error_to_client,
)
from common.pyportal_common.error_handlers.internal_server_error_handler import (
    send_internal_server_error_to_client,
)
from app.models.booking_model import BookingModel, FlightModel


def create_booking():
    try:
        booking_logger.info(
            f"REQUEST ==> Received Endpoint: {request.endpoint}"
        )
        booking_logger.info(
            f"REQUEST ==> Received url for the request :: {request.url}"
        )
        
        if request.method == "POST":
            rec_req_headers = dict(request.headers)
            booking_logger.info(
                f"Received Headers from the request :: {rec_req_headers}"
            )
            
            # Validate headers
            header_result = booking_manager.generate_req_missing_params(
                rec_req_headers, booking_headers_schema
            )
            if len(header_result) > 0:
                return send_invalid_request_error_to_client(
                    app_logger_name=booking_logger,
                    message_data="Request Headers Missing",
                    err_details=header_result,
                )

            rec_req_data = request.get_json()
            
            # Validate request body
            body_result = booking_manager.generate_req_missing_params(
                rec_req_data, booking_req_schema
            )
            if len(body_result) > 0:
                return send_invalid_request_error_to_client(
                    app_logger_name=booking_logger,
                    message_data="Request Params Missing",
                    err_details=body_result,
                )

            # Extract booking data
            user_id = rec_req_data["userId"]
            flight_id = rec_req_data["flightId"]
            number_of_seats = rec_req_data["numberOfSeats"]

            booking_logger.info("Processing booking request... [STARTED]")
            
            # Get session
            session = app_manager_db_obj.get_session_from_session_maker()
            if session is None:
                return send_internal_server_error_to_client(
                    app_logger_name=booking_logger,
                    message_data="Create Session Failed",
                )

            try:
                # Check if flight exists and has available seats
                flight = session.query(FlightModel).filter(
                    FlightModel.ID == flight_id
                ).first()
                
                if not flight:
                    app_manager_db_obj.close_session(session_instance=session)
                    return send_invalid_request_error_to_client(
                        app_logger_name=booking_logger,
                        message_data="Flight not found",
                    )
                
                if flight.AvailableSeats < number_of_seats:
                    app_manager_db_obj.close_session(session_instance=session)
                    return send_invalid_request_error_to_client(
                        app_logger_name=booking_logger,
                        message_data="Insufficient seats available",
                    )

                # Create booking
                booking_reference = f"BK{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"
                total_price = float(flight.Price) * number_of_seats
                
                booking = BookingModel(
                    UserID=user_id,
                    FlightID=flight_id,
                    NumberOfSeats=number_of_seats,
                    TotalPrice=total_price,
                    Status="confirmed",
                    BookingReference=booking_reference,
                    CreatedAt=datetime.now(),
                    UpdatedAt=datetime.now(),
                )

                session.add(booking)
                session.flush()
                booking_id = booking.ID

                # Update flight available seats
                flight.AvailableSeats -= number_of_seats
                flight.UpdatedAt = datetime.now()

                # Commit transaction
                session.commit()

                booking_logger.info(
                    f"Booking created successfully: {booking_reference}"
                )

                # Publish booking event to Kafka
                if booking_kafka_producer:
                    try:
                        booking_event = {
                            "eventType": "booking_created",
                            "bookingId": booking_id,
                            "bookingReference": booking_reference,
                            "userId": user_id,
                            "flightId": flight_id,
                            "numberOfSeats": number_of_seats,
                            "totalPrice": str(total_price),
                            "timestamp": datetime.now().isoformat(),
                        }
                        booking_kafka_producer.publish_data_to_producer(
                            booking_event
                        )
                        booking_logger.info(
                            f"Published booking event to Kafka: {booking_reference}"
                        )
                    except Exception as kafka_ex:
                        booking_logger.warning(
                            f"Failed to publish to Kafka: {kafka_ex}"
                        )

                # Prepare response
                response_data = {
                    "booking": {
                        "bookingId": booking_id,
                        "bookingReference": booking_reference,
                        "userId": user_id,
                        "flightId": flight_id,
                        "numberOfSeats": number_of_seats,
                        "totalPrice": str(total_price),
                        "status": "confirmed",
                        "createdAt": str(booking.CreatedAt),
                    }
                }

                reg_booking_response = make_response(response_data)
                reg_booking_response.headers["Content-Type"] = "application/json"
                reg_booking_response.headers["Cache-Control"] = "no-cache"
                reg_booking_response.status_code = 201

                app_manager_db_obj.close_session(session_instance=session)
                return reg_booking_response

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

