#!/usr/bin/env python3
"""
Main entry point for the Task Processing Service.
"""
import sys
import os

# Add parent directory to path for common imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from app import (
    taskprocessing_app,
    taskprocessing_logger,
)
from common.pyportal_common.utils import mask_ip_address

if __name__ == "__main__":
    print("Starting Task Processing Service")
    try:
        server_ip = taskprocessing_app.config.get("TASKPROCESSING_SERVER_IPADDRESS", "0.0.0.0")
        masked_server_ip = mask_ip_address(server_ip)
        taskprocessing_logger.info(
            "Bound TASKPROCESSING-SERVICE at IP-ADDRESS:PORT :: %s:%s",
            masked_server_ip,
            taskprocessing_app.config.get("TASKPROCESSING_SERVER_PORT", 9092),
        )
        taskprocessing_logger.info("Started the TASKPROCESSING server ...")
        taskprocessing_logger.info("Application is ready to serve traffic.")
        taskprocessing_app.run(
            host=taskprocessing_app.config.get("TASKPROCESSING_SERVER_IPADDRESS", "0.0.0.0"),
            port=taskprocessing_app.config.get("TASKPROCESSING_SERVER_PORT", 9092),
            debug=False
        )
    except Exception as ex:
        taskprocessing_logger.exception(
            "Error occurred :: %s\tLine No:: %s",
            ex,
            sys.exc_info()[2].tb_lineno
        )
        sys.exit(1)
