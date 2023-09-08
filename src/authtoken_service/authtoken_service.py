import sys
from src.authtoken_service import authtoken_app, authtoken_app_logger

if __name__ == "__main__":
    try:
        authtoken_app_logger.info("Bound AuthToken-SERVICE at IP-ADDRESS:PORT :: {0}:{1}".format(authtoken_app.config['AUTHTOKEN_SERVER_IPADDRESS'], authtoken_app.config['AUTHTOKEN_SERVER_PORT']))
        authtoken_app_logger.info("Application is ready to server traffic.")
        authtoken_app.run(host=authtoken_app.config['AUTHTOKEN_SERVER_IPADDRESS'], port=authtoken_app.config['AUTHTOKEN_SERVER_PORT'])
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))



