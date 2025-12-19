#!/usr/bin/env python3
"""
Main entry point for the Notification Service.
"""
import sys
import os

# Add parent directory to path for common imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from app import (
    notification_app,
    notification_logger,
)

if __name__ == "__main__":
    print("Starting Notification Service")
    try:
        notification_logger.info(
            "Bound NOTIFICATION-SERVICE at IP-ADDRESS:PORT :: %s:%s",
            notification_app.config.get("NOTIFICATION_SERVER_IPADDRESS", "0.0.0.0"),
            notification_app.config.get("NOTIFICATION_SERVER_PORT", 9093),
        )
        notification_logger.info("Started the NOTIFICATION server ...")
        notification_logger.info("Application is ready to serve traffic.")
        notification_app.run(
            host=notification_app.config.get("NOTIFICATION_SERVER_IPADDRESS", "0.0.0.0"),
            port=notification_app.config.get("NOTIFICATION_SERVER_PORT", 9093),
            debug=False
        )
    except Exception as ex:
        notification_logger.exception(
            "Error occurred :: %s\tLine No:: %s",
            ex,
            sys.exc_info()[2].tb_lineno
        )
        sys.exit(1)
