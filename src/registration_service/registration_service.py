import sys
from src.registration_service import registration_app, server, registration_app_logger

if __name__ == "__main__":
    try:
        server.start()
        registration_app_logger.info("Started the grpc server ...")
        registration_app_logger.info("Started the REGISTRATION server ...")
        registration_app_logger.info("Binded REGISTRATION-SERVICE at IP-ADDRESS:PORT :: {0}:{1}".format(registration_app.config['REGISTRATION_SERVER_IPADDRESS'],registration_app.config['REGISTRATION_SERVER_PORT']))
        registration_app_logger.info("Application is ready to server traffic.")
        # registration_app.run(debug=registration_app.config["DEBUG"], port=registration_app.config["REGISTRATION_SERVER_PORT"], host=registration_app.config['REGISTRATION_SERVER_IPADDRESS'])
        registration_app.run()
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))



