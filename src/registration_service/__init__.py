import sys
import grpc
from concurrent import futures
from src.airliner_grpc import token_pb2_grpc
from src.airliner_common.create_app import CreatFlaskApp
from src.registration_service.models.user_model import Base

SERVICE_NAME = "registration"
DB_DRIVER_NAME = "mysql+pymysql"
DB_USER = "root"
DB_PASSWORD = "testeventstreammonitor#123"
DB_IPADDRESS = "127.0.0.1"
DB_PORT = "3304"
DB_NAME = "REGISTRATIONS"
POOL_SIZE = 100
MAX_OVERFLOW = 20

try:
    res_app_obj = CreatFlaskApp(service_name=SERVICE_NAME, db_driver=DB_DRIVER_NAME, db_user=DB_USER,
                                db_ip_address=DB_IPADDRESS, db_password=DB_PASSWORD, db_port=DB_PORT,
                                db_name=DB_NAME, db_pool_size=POOL_SIZE, db_pool_max_overflow=MAX_OVERFLOW, base=Base)

    registration_app_logger = res_app_obj.app_logger

    registration_app = res_app_obj.create_app_instance()

    # Read Schema File
    reg_user_req_schema_filepath = "/Users/kamalsaidevarapalli/Desktop/Workshop/AirlinerAdminstration/src/registration_service/schemas/requests/register_user/req_schema.json"
    req_headers_schema_filepath = "/Users/kamalsaidevarapalli/Desktop/Workshop/AirlinerAdminstration/src/registration_service/schemas/headers/request_headers_schema.json"

    _, req_headers_schema = res_app_obj.read_json_schema(req_headers_schema_filepath)
    _, reg_user_req_schema = res_app_obj.read_json_schema(reg_user_req_schema_filepath)

    registration_bp = res_app_obj.create_blueprint()

    res_app_obj.display_registered_blueprints_for_service()
    registration_db_engine = res_app_obj.create_db_engine()
    if res_app_obj.check_db_connectivity_and_retry():
        if res_app_obj.init_databases_for_service():
            if res_app_obj.create_tables_associated_to_db_model():
                registration_SQLAlchemy = res_app_obj.bind_db_app()
                registration_connection_pool = res_app_obj.create_pool()
                res_app_obj.display_pool_info()

                from src.registration_service.controllers.registration_controller import add_user

                registration_bp.route('/api/v1/airliner/registerUser', methods=['POST'])(add_user)
                res_app_obj.register_blueprint()
                res_app_obj.display_registered_blueprints_for_service()

                from src.airliner_common.airliner_err_handlers import internal_server_error, bad_request, not_found
                res_app_obj.register_err_handler(500, internal_server_error)
                res_app_obj.register_err_handler(400, bad_request)
                res_app_obj.register_err_handler(404, not_found)
                res_app_obj.display_registered_err_handlers()

                from src.registration_service.registration_grpc.server import UserValidationForTokenGenerationService

                server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
                registration_app_logger.info("Created GRPC server with the workers of max :: {0}".format(10))
                token_pb2_grpc.add_UserValidationForTokenGenerationServicer_to_server(
                    UserValidationForTokenGenerationService(), server)
                registration_app_logger.info(
                    "Registered GRPC server to the server :: {0}".format("UserValidationForTokenGenerationService"))
                server.add_insecure_port('127.0.0.1:8081')
                registration_app_logger.info(
                    "Starting GRPC server for the Token-User service with the IP & PORT:: {0}:{1}".format("localhost",
                                                                                                          "8081"))

except Exception as ex:
    print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
