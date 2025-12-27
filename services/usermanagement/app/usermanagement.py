# pylint: disable=line-too-long

"""
This module contains the main entry point for the User Management service.

It initializes the server, configures settings, and starts serving traffic.
"""
import sys
from app import (
    usermanager_app,
    user_management_logger,
)
from common.pyportal_common.utils import mask_ip_address

if __name__ == "__main__":
    print("Starting user management service")
    try:
        # user_management_grpc_server.start_base_server()
        server_ip = usermanager_app.config["USER_MANAGEMENT_SERVER_IPADDRESS"]
        masked_server_ip = mask_ip_address(server_ip)
        user_management_logger.info(
            "Bound USER-MANAGEMENT-SERVICE at IP-ADDRESS:PORT :: %s:%s",
            masked_server_ip,
            usermanager_app.config["USER_MANAGEMENT_SERVER_PORT"],
        )
        user_management_logger.info("Started the USER-MANAGEMENT server ...")
        user_management_logger.info("Application is ready to serve traffic.")
        usermanager_app.run(
            host=usermanager_app.config["USER_MANAGEMENT_SERVER_IPADDRESS"],
            port=usermanager_app.config["USER_MANAGEMENT_SERVER_PORT"],
        )

    except Exception as ex:
        user_management_logger.exception(
            "Error occurred :: %s\tLine No:: %s",
            ex,
            sys.exc_info()[2].tb_lineno
        )
