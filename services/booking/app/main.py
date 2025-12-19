#!/usr/bin/env python3
"""
Main entry point for the Flight Booking Service.
"""
import sys
import os

# Add parent directory to path for common imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from app import (
    booking_app,
    booking_logger,
)

if __name__ == "__main__":
    print("Starting Flight Booking Service")
    try:
        booking_logger.info(
            "Bound BOOKING-SERVICE at IP-ADDRESS:PORT :: %s:%s",
            booking_app.config.get("BOOKING_SERVER_IPADDRESS", "0.0.0.0"),
            booking_app.config.get("BOOKING_SERVER_PORT", 9092),
        )
        booking_logger.info("Started the BOOKING server ...")
        booking_logger.info("Application is ready to serve traffic.")
        booking_app.run(
            host=booking_app.config.get("BOOKING_SERVER_IPADDRESS", "0.0.0.0"),
            port=booking_app.config.get("BOOKING_SERVER_PORT", 9092),
            debug=False
        )
    except Exception as ex:
        booking_logger.exception(
            "Error occurred :: %s\tLine No:: %s",
            ex,
            sys.exc_info()[2].tb_lineno
        )
        sys.exit(1)
