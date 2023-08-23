import sys
from src.airliner_common.create_app import CreatFlaskApp

from src.auth_token_service.models.token_model import Base

SERVICE_NAME = "authtoken"
DB_DRIVER_NAME = "mysql+pymysql"
DB_USER = "root"
DB_PASSWORD = "testeventstreammonitor#123"
DB_IPADDRESS = "127.0.0.1"
DB_PORT = "3305"
DB_NAME = "AUTHTOKENS"
POOL_SIZE = 100
MAX_OVERFLOW = 20

try:
    authtoken_app_obj = CreatFlaskApp(service_name=SERVICE_NAME, db_driver=DB_DRIVER_NAME, db_user=DB_USER,
                                db_ip_address=DB_IPADDRESS, db_password=DB_PASSWORD, db_port=DB_PORT,
                                db_name=DB_NAME, db_pool_size=POOL_SIZE, db_pool_max_overflow=MAX_OVERFLOW, base=Base)

    authtoken_app_logger = authtoken_app_obj.app_logger

    authtoken_app = authtoken_app_obj.create_app_instance()


    authtoken_app_jwt = authtoken_app_obj.init_jwt_manger()

    # Read Schema File
    login_user_req_schema_filepath = "/Users/kamalsaidevarapalli/Desktop/Workshop/AirlinerAdminstration/src/auth_token_service/schemas/requests/login_user/req_schema.json"
    gen_token_req_schema_filepath = "/Users/kamalsaidevarapalli/Desktop/Workshop/AirlinerAdminstration/src/auth_token_service/schemas/requests/generate_token/req_schema.json"
    req_headers_schema_filepath = "/Users/kamalsaidevarapalli/Desktop/Workshop/AirlinerAdminstration/src/auth_token_service/schemas/headers/request_headers_schema.json"

    req_headers_schema, _ = authtoken_app_obj.read_json_schema(req_headers_schema_filepath)
    login_user_req_schema, _ = authtoken_app_obj.read_json_schema(login_user_req_schema_filepath)
    gen_token_req_schema, _ = authtoken_app_obj.read_json_schema(gen_token_req_schema_filepath)

    authtoken_bp = authtoken_app_obj.create_blueprint()

    authtoken_app_obj.display_registered_blueprints_for_service()
    from src.airliner_common.airliner_err_handlers import internal_server_error, bad_request, not_found

    # authtoken_app.register_error_handler(400, bad_request)
    # authtoken_app.register_error_handler(500, internal_server_error)
    # authtoken_app.register_error_handler(404, not_found)

    authtoken_app_obj.register_err_handler(500, internal_server_error)
    authtoken_app_obj.register_err_handler(400, bad_request)
    authtoken_app_obj.register_err_handler(404, not_found)

    authtoken_app_obj.display_registered_err_handlers()


    authtoken_db_engine = authtoken_app_obj.create_db_engine()
    if authtoken_app_obj.check_db_connectivity_and_retry():
        if authtoken_app_obj.init_databases_for_service():
            if authtoken_app_obj.create_tables_associated_to_db_model():
                registration_SQLAlchemy = authtoken_app_obj.bind_db_app()
                registration_connection_pool = authtoken_app_obj.create_pool()
                authtoken_app_obj.display_pool_info()

                from src.auth_token_service.controllers.token_controller import create_token

                authtoken_bp.route('/api/v1/airliner/generateToken', methods=['POST'])(create_token)
                authtoken_app_obj.register_blueprint()
                authtoken_app_obj.display_registered_blueprints_for_service()

except Exception as ex:
    print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
