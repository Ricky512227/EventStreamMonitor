import sys
from src.usermanagement_service import user_management_app, server, user_management_app_logger

if __name__ == "__main__":
    try:
        server.start()
        user_management_app_logger.info("Started the grpc server ...")
        user_management_app_logger.info("Started the USER-MANAGEMENT server ...")
        user_management_app_logger.info("Binded USER-MANAGEMENT-SERVICE at IP-ADDRESS:PORT :: {0}:{1}".format(user_management_app.config['USER_MANAGEMENT_SERVER_IPADDRESS'], user_management_app.config['USER_MANAGEMENT_SERVER_PORT']))
        user_management_app_logger.info("Application is ready to server traffic.")
        user_management_app.run(host=user_management_app.config["USER_MANAGEMENT_SERVER_IPADDRESS"], port=user_management_app.config["USER_MANAGEMENT_SERVER_PORT"])
    except Exception as ex:
        user_management_app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
