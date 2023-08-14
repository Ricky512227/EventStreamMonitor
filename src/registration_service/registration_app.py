from src.registration_service import user_app









if __name__ == "__main__":
    print("Application is ready to server traffic.")
    user_app.run(debug=True, port="50050", host="127.0.0.1", threaded=True)
