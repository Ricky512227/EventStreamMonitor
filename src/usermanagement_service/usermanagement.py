# pylint: disable=line-too-long

"""
This module contains the main entry point for the User Management service.

It initializes the server, configures settings, and starts serving traffic.
"""
import sys
from src.usermanagement_service import (
    usermanager_app,
    user_management_logger,
    user_management_grpc_server,
)

if __name__ == "__main__":
    try:
        user_management_grpc_server.start_base_server()
        user_management_logger.info(
            "Bound USER-MANAGEMENT-SERVICE at IP-ADDRESS:PORT :: %s:%s",
            usermanager_app.config["USER_MANAGEMENT_SERVER_IPADDRESS"],
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
            "Error occurred :: %s\tLine No:: %s", ex, sys.exc_info()[2].tb_lineno
        )
        print("Error occurred :: %s\tLine No:: %s", ex, sys.exc_info()[2].tb_lineno)
