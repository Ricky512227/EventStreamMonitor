from src.auth_token_service import auth_server_app

if __name__ == "__main__":
    print("Application [Token Auth Server] is ready to server traffic.")
    auth_server_app.run(debug=True, port="6000", host="127.0.0.2", threaded=True)
