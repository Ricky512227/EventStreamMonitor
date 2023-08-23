import sys
from src.auth_token_service import authtoken_app_logger, authtoken_app





if __name__ == "__main__":
    try:
        authtoken_app_logger.info("Started the AUTHTOKENS server ...")
        authtoken_app_logger.info("Application is ready to server traffic.")
        authtoken_app.run(debug=True, port=9092, host="127.0.0.1", threaded=True)
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))