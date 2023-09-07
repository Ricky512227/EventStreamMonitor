import sys
from src.authtoken_service import authtoken_app, authtoken_app_logger

if __name__ == "__main__":
    try:
        authtoken_app_logger.info("Binded REGISTRATION-SERVICE at IP-ADDRESS:PORT :: {0}:{1}".format(registration_app.config['REGISTRATION_SERVER_IPADDRESS'],registration_app.config['REGISTRATION_SERVER_PORT']))
        authtoken_app_logger.info("Application is ready to server traffic.")
        authtoken_app.run()
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))



