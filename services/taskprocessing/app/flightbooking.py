# pylint: disable=line-too-long

"""
This module contains the main entry point for the Flight Booking service.

It initializes the server, configures settings, and starts serving traffic.
"""
import sys
from app import (
    booking_app,
    booking_logger,
)
from common.pyportal_common.utils import mask_ip_address

if __name__ == "__main__":
    print("Starting flight booking service")
    try:
        server_ip = booking_app.config["BOOKING_SERVER_IPADDRESS"]
        masked_server_ip = mask_ip_address(server_ip)
        booking_logger.info(
            "Bound FLIGHT-BOOKING-SERVICE at IP-ADDRESS:PORT :: %s:%s",
            masked_server_ip,
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

