# pylint: disable=line-too-long

"""
This module contains the main entry point for the Flight Booking service.

It initializes the server, configures settings, and starts serving traffic.
"""
import sys
from src.flightbooking_service import (
    booking_app,
    booking_logger,
)

if __name__ == "__main__":
    print("Starting flight booking service")
    try:
        booking_logger.info(
            "Bound FLIGHT-BOOKING-SERVICE at IP-ADDRESS:PORT :: %s:%s",
            booking_app.config["BOOKING_SERVER_IPADDRESS"],
            booking_app.config["BOOKING_SERVER_PORT"],
        )
        booking_logger.info("Started the FLIGHT-BOOKING server ...")
        booking_logger.info("Application is ready to serve traffic.")
        booking_app.run(
            host=booking_app.config["BOOKING_SERVER_IPADDRESS"],
            port=booking_app.config["BOOKING_SERVER_PORT"],
        )

    except Exception as ex:
        booking_logger.exception(
            "Error occurred :: %s\tLine No:: %s",
            ex,
            sys.exc_info()[2].tb_lineno
        )

