import sys
from sqlalchemy.exc import SQLAlchemyError
from flask import jsonify, request, abort
from src.authtoken_service.tokens.token import Token
from src.authtoken_service.models.token_model import TokensModel
from src.authtoken_service import authtoken_app_logger, gen_token_headers_schema, gen_token_req_schema, authtoken_app_obj
from src.authtoken_service.authtoken_grpc.client import TokenGrpcRequestPreparation, init_grpc_token_client, trigger_request
from src.airliner_common.req_header_validation import generate_req_missing_params




def create_token():
    try:
        authtoken_app_logger.info('REQUEST ==> Received Endpoint :: {0}'.format(request.endpoint))
        rec_req_headers = dict(request.headers)
        authtoken_app_logger.info("Received Headers from the request :: {0}".format(rec_req_headers))
        authtoken_app_logger.info("Validation for Request-Header is  :: [STARTED]")
        headers_result = generate_req_missing_params(rec_req_headers, gen_token_headers_schema)
        if len(headers_result.keys()) == 0:
            authtoken_app_logger.info("Validation for Request-Header is  :: [SUCCESS]")
            if request.method == 'POST':
                rec_req_data = request.get_json()
                authtoken_app_logger.info("Validation for Request-Body is  :: [STARTED]")
                payload_result = generate_req_missing_params(rec_req_data, gen_token_req_schema)
                if len(payload_result.keys()) == 0:
                    userid = rec_req_data['userId']
                    username = rec_req_data['username']
                    password = rec_req_data['password']
                    token_session = authtoken_app_obj.create_session_for_service()
                    if token_session is not None:
                        authtoken_app_logger.info("Checking for the token which is already exists or not for the user")
                        token_record = token_session.query(TokensModel).filter_by(UserID=userid).first()
                        if token_record is None:
                            authtoken_app_logger.info("Token not exists, so Validating whether it is registered user  :: [STARTED]")
                            authtoken_app_logger.info("Sending gRPC message to Registration Service :: [STARTED]")
                            data_to_send = TokenGrpcRequestPreparation(userid=userid, username=username, passcode=password)
                            tokenstub, grpc_client_status = init_grpc_token_client()
                            if grpc_client_status:
                                resp_data, resp_status = trigger_request(tokenstub, data_to_send)
                                if resp_status:
                                    authtoken_app_logger.info("gRPC Response data :: {0}, Response status :: {1}".format(resp_data, resp_status))
                                    token_obj = Token.create_custom_token(userid, username, password)
                                    if token_obj is not None:
                                        authtoken_app_logger.info("Valid User, need to create a new token")
                                        token_map_db_instance = TokensModel(UserID=token_obj.user_id,
                                                                            Token=token_obj.custom_access_token,
                                                                            Expiry=token_obj.expiry,
                                                                            CreatedAt=token_obj.created_at,
                                                                            UpdatedAt=token_obj.updated_at)

                                        try:
                                            token_session.add(token_map_db_instance)
                                            authtoken_app_logger.info("Data added into  DataBase session {0}:: [SUCCESS]".format(token_map_db_instance))
                                            token_session.commit()  # Commit the change
                                            authtoken_app_logger.info("Added Data is committed into  DataBase {0}:: [SUCCESS]".format(token_session))
                                            print("Commit the  changes  {0}:: SUCCESS".format(token_session))
                                            authtoken_app_logger.info("Generating Success response  :: [STARTED]")
                                            token_instance = Token.convert_db_model_to_response(token_map_db_instance)
                                            token_user_response = Token.generate_success_response(token_instance)
                                            authtoken_app_logger.info("Generating Success response  :: [STARTED] :: {0}".format(token_user_response))
                                            return jsonify(token_user_response), 201
                                        except SQLAlchemyError as ex:
                                            token_session.rollback()
                                            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
                                            return jsonify({"message": "Internal Server Error"}), 500

                                        except Exception as ex:
                                            token_session.rollback()
                                            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
                                            return jsonify({"message": "Internal Server Error"}), 500
                                        finally:
                                            print("Closing the  session  {0}:: [STARTED]".format(token_session))
                                            token_session.close()  # Close the change
                                            print("Closed the  session  {0}:: [SUCCESS]".format(token_session))
                                    else:
                                        authtoken_app_logger.error("Token creation  :: [FAILED]")
                                        return jsonify({"message": "Internal Server Error"}), 500
                                else:
                                    authtoken_app_logger.error("Sending gRPC message to Registration Service :: [FAILED]")
                                    return jsonify({"message": "Internal Server Error"}), 500
                            else:
                                authtoken_app_logger.error("Sending gRPC message to Registration Service :: [FAILED]")
                                return jsonify({"message": "Internal Server Error"}), 500
                        else:
                            authtoken_app_logger.info("Already token exists for the user not need to generate a new token.")
                            token_instance = Token.convert_db_model_to_response(token_record)
                            token_user_response = Token.generate_success_response(token_instance)
                            authtoken_app_logger.info("Generating Success response  :: [STARTED] :: {0}".format(token_user_response))
                            return jsonify(token_user_response), 200

                else:
                    authtoken_app_logger.error("Validation for Request-Body is  :: [FAILED]")
                    payload_result["message"] = "Request Params Missing"
                    authtoken_app_logger.info("Sending Error response back to client :: {0}".format(payload_result))
                    abort(400, description=payload_result)
        else:
            authtoken_app_logger.error("Validation for Request-Header is  :: [FAILED]")
            headers_result["message"] = "Request Header Missing"
            authtoken_app_logger.info("Sending Error response back to client :: {0}".format(headers_result))
            abort(400, description=headers_result)
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        
        

