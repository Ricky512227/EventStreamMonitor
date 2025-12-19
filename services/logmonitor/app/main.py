#!/usr/bin/env python3
"""
Main entry point for the Log Monitoring Service
"""
import sys
import os

# Add parent directory to path for common imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from app import (
    logmonitor_app,
    logmonitor_logger,
)

if __name__ == "__main__":
    print("Starting Log Monitoring Service")
    try:
        logmonitor_logger.info(
            "Bound LOG-MONITOR-SERVICE at IP-ADDRESS:PORT :: %s:%s",
            logmonitor_app.config.get("LOG_MONITOR_SERVER_IPADDRESS", "0.0.0.0"),
            logmonitor_app.config.get("LOG_MONITOR_SERVER_PORT", 9094),
        )
        logmonitor_logger.info("Started the LOG-MONITOR server ...")
        logmonitor_logger.info("Application is ready to serve traffic.")
        logmonitor_app.run(
            host=logmonitor_app.config.get("LOG_MONITOR_SERVER_IPADDRESS", "0.0.0.0"),
            port=logmonitor_app.config.get("LOG_MONITOR_SERVER_PORT", 9094),
            debug=False
        )
    except Exception as ex:
        logmonitor_logger.exception(
            "Error occurred :: %s\tLine No:: %s",
            ex,
            sys.exc_info()[2].tb_lineno
        )
        sys.exit(1)

