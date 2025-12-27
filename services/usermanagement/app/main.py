#!/usr/bin/env python3
"""
Main entry point for the User Management Service.
"""
import sys
import os

# Add parent directory to path for common imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from app import (
    usermanager_app,
    user_management_logger,
)
from common.pyportal_common.utils import mask_ip_address

if __name__ == "__main__":
    print("Starting User Management Service")
    try:
        server_ip = usermanager_app.config.get("USER_MANAGEMENT_SERVER_IPADDRESS", "0.0.0.0")
        masked_server_ip = mask_ip_address(server_ip)
        user_management_logger.info(
            "Bound USER-MANAGEMENT-SERVICE at IP-ADDRESS:PORT :: %s:%s",
            masked_server_ip,
            usermanager_app.config.get("USER_MANAGEMENT_SERVER_PORT", 9091),
        )
        user_management_logger.info("Started the USER-MANAGEMENT server ...")
        user_management_logger.info("Application is ready to serve traffic.")
        usermanager_app.run(
            host=usermanager_app.config.get("USER_MANAGEMENT_SERVER_IPADDRESS", "0.0.0.0"),
            port=usermanager_app.config.get("USER_MANAGEMENT_SERVER_PORT", 9091),
            debug=False
        )
    except Exception as ex:
        user_management_logger.exception(
            "Error occurred :: %s\tLine No:: %s",
            ex,
            sys.exc_info()[2].tb_lineno
        )
        sys.exit(1)
