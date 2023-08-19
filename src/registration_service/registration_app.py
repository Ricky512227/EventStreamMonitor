from src.registration_service import registration_app, server, registration_app_logger

if __name__ == "__main__":
    server.start()
    registration_app_logger.info("Started the grpc server ...")
    registration_app_logger.info("Started the REGISTRATION server ...")
    registration_app_logger.info("Application is ready to server traffic.")
    registration_app.run(debug=True, port=9091, host="127.0.0.1", threaded=True)





