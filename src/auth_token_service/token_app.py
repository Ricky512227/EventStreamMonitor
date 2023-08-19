import sys
from src.auth_token_service import create_app
from src.airliner_common.base_blueprint_creation import AirlinerBluePrint



auth_token_app_init_data = create_app()

service_name = auth_token_app_init_data["SERVICE_NAME"]
auth_token_app = auth_token_app_init_data["app_instance"]
auth_token_app_logger = auth_token_app_init_data["logger_instance"]
req_headers_schema = auth_token_app_init_data["req_headers_schema"]
login_user_req_schema = auth_token_app_init_data["login_user_req_schema"]
gen_token_req_schema = auth_token_app_init_data["gen_token_req_schema"]
auth_token_db_engine = auth_token_app_init_data["auth_token_db_engine"]
auth_token_pool_obj = auth_token_app_init_data["auth_token_pool_obj"]


if __name__ == "__main__":
    try:

        auth_token_client_ip = "127.0.0.1"
        auth_token_client_port= "50051"

        auth_token_app, auth_token_blueprint = AirlinerBluePrint.create_blueprint(reg_app_flask_instance=auth_token_app, blueprint_name="authtoken")
        from src.auth_token_service.controllers.token_controller import create_token
        auth_token_blueprint.route('/api/v1/airliner/generateToken', methods=['POST'])(create_token)
        auth_token_app, auth_token_blueprint = AirlinerBluePrint.register_blueprint(reg_app_flask_instance=auth_token_app, created_blueprint_instance=auth_token_blueprint)
        AirlinerBluePrint.display_registered_blueprints_for_service(auth_token_app)

        auth_token_app.run(debug=True, port=auth_token_client_port, host=auth_token_client_ip, threaded=True)
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))