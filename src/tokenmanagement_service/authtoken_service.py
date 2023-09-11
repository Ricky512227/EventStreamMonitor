import sys
from src.tokenmanagement_service import token_management, token_management_logger

if __name__ == "__main__":
    try:
        token_management_logger.info("Bound AuthToken-SERVICE at IP-ADDRESS:PORT :: {0}:{1}".format(token_management.config['AUTHTOKEN_SERVER_IPADDRESS'], token_management.config['AUTHTOKEN_SERVER_PORT']))
        token_management_logger.info("Application is ready to server traffic.")
        token_management.run(host=token_management.config['AUTHTOKEN_SERVER_IPADDRESS'], port=token_management.config['AUTHTOKEN_SERVER_PORT'])
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))



