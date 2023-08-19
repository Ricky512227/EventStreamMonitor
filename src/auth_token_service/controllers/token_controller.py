import sys
from sqlalchemy.exc import SQLAlchemyError
from flask import jsonify, request, abort

from airliner_common.airliner_error_handling import AirlinerSchemaValidationError
from auth_token_service.token_app import auth_token_app_logger,auth_token_pool_obj, auth_token_db_engine, service_name, auth_token_app
from src.airliner_common.create_db_engine import create_session_for_service
from src.auth_token_service.tokens.token import Token
from src.auth_token_service.models.token_model import TokensModel
from src.auth_token_service.client import TokenGrpcRequestPreparation, trigger_request, init_grpc_token_client


@auth_token_app.errorhandler(400)
def bad_request(error_data):
    auth_token_app_logger.info("Preparing Err_response :: {0}".format(error_data))
    err_message = error_data.description['message']
    err_details = error_data.description['details']
    error_res_obj = AirlinerSchemaValidationError(message=err_message, error_details=err_details)
    auth_token_app_logger.debug("Response ID of Final Response:: {0}".format(id(error_res_obj.to_dict())))
    auth_token_app_logger.info("Prepared Final Response  and sent to Client:: {0}".format(error_res_obj.to_dict()))
    return jsonify(error_res_obj.to_dict()), 400

@auth_token_app.errorhandler(500)
def internal_server_error(error_data):
    auth_token_app_logger.info("Preparing Err_response :: {0}".format(error_data))
    err_message = error_data.description['message']
    err_details = error_data.description['details']
    error_res_obj = AirlinerSchemaValidationError(message=err_message, error_details=err_details)
    auth_token_app_logger.debug("Response ID of Final Response:: {0}".format(id(error_res_obj.to_dict())))
    auth_token_app_logger.info("Prepared Final Response  and sent to Client:: {0}".format(error_res_obj.to_dict()))
    return jsonify(error_res_obj.to_dict()), 500

@auth_token_app.errorhandler(404)
def not_found(error_data):
    return jsonify({"status": 404, "message": "Not Found"}), 404








def create_token():
    try:
        if request.method == 'POST':
            rec_req_data = request.get_json()
            userid = rec_req_data['userId']
            username = rec_req_data['username']
            password = rec_req_data['password']
            token_obj = Token.create_custom_token(userid,username,password)
            data_to_send = TokenGrpcRequestPreparation(userid=userid, username=username, passcode=password)
            grpc_auth_token_client_ip = "127.0.0.1"
            grpc_auth_token_client_port = "8081"
            tokenstub, grpc_client_status = init_grpc_token_client(grpc_auth_token_client_ip, grpc_auth_token_client_port)
            resp_data, resp_status = trigger_request(tokenstub, data_to_send)

            token_map_db_instance = TokensModel(UserID=token_obj.user_id,
                                              Token=token_obj.custom_access_token,
                                              Expiry=token_obj.expiry,
                                              CreatedAt=token_obj.created_at,
                                              UpdatedAt=token_obj.updated_at)

            token_session = create_session_for_service(auth_token_pool_obj, auth_token_db_engine, service_name.lower())
            if token_session is not None:
                try:
                    token_session.add(token_map_db_instance)
                    auth_token_app_logger.info("Data added into  DataBase session {0}:: SUCCESS".format(token_map_db_instance))
                    token_session.commit()  # Commit the change
                    auth_token_app_logger.info("Added Data is committed into  DataBase {0}:: SUCCESS".format(token_session))

                    print("Commit the  changes  {0}:: SUCCESS".format(token_session))
                    auth_token_app_logger.info("Generating Success response  :: [STARTED]")
                    # custom_token_response = Token.convert_db_model_to_response(token_map_db_instance)
                    # print(custom_token_response)
                    # success_token_response = Token.generate_success_response(custom_token_response)
                    # auth_token_app_logger.info("Generating Success response  :: [STARTED] :: {0}".format(success_token_response))
                    return jsonify({"message": "ok"}), 201
            #
                except SQLAlchemyError as ex:
                    token_session.rollback()
                    print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
                    abort(500, description={'message': 'Create token Failed', 'details': {'params': ex}})

                except Exception as ex:
                    token_session.rollback()
                    print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
                    abort(500, description={'message': 'Create token Failed', 'details': {'params': str(ex)}})
                finally:
                    print("Closing the  session  {0}:: [STARTED]".format(token_session))
                    token_session.close()  # Close the change
                    print("Closed the  session  {0}:: [SUCCESS]".format(token_session))


    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))