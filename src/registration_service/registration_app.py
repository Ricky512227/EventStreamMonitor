from airliner_common.base_blueprint_creation import AirlinerBluePrint
from src.registration_service import create_app

registration_app_init_data = create_app()
service_name = registration_app_init_data["SERVICE_NAME"]
registration_app = registration_app_init_data["app_instance"]
registration_app_logger = registration_app_init_data["logger_instance"]
req_headers_schema = registration_app_init_data["req_headers_schema"]
login_user_req_schema = registration_app_init_data["login_user_req_schema"]
reg_user_req_schema = registration_app_init_data["reg_user_req_schema"]
registration_db_engine = registration_app_init_data["registration_db_engine"]
registration_pool_obj = registration_app_init_data["registration_pool_obj"]





if __name__ == "__main__":
    # create the Blueprint
    registration_app, registration_blueprint = AirlinerBluePrint.create_blueprint(reg_app_flask_instance=registration_app, blueprint_name="registration")
    from src.registration_service.controllers.registration_controller import add_user
    registration_blueprint.route('/api/v1/airliner/registerUser', methods=['POST'])(add_user)
    registration_app, registration_blueprint = AirlinerBluePrint.register_blueprint(reg_app_flask_instance=registration_app, created_blueprint_instance=registration_blueprint)
    AirlinerBluePrint.display_registered_blueprints_for_service(registration_app)
    registration_app_logger.info("Application is ready to server traffic.")
    registration_app.run(debug=True, port="50050", host="127.0.0.1", threaded=True)
