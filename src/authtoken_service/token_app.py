from src.authtoken_service import authtoken_app, authtoken_app_logger

if __name__ == "__main__":

    authtoken_app_logger.info("Started the AUTH TOKEN server ...")
    authtoken_app_logger.info("Application is ready to server traffic.")
    authtoken_app.run(debug=True, port=9092, host="127.0.0.1", threaded=True)





