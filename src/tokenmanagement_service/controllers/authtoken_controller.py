import sys
from sqlalchemy.exc import SQLAlchemyError
from flask import jsonify, request, abort
from src.tokenmanagement_service.tokens.token import Token
from src.tokenmanagement_service.models.token_model import TokensModel
from src.tokenmanagement_service import authtoken_app_logger, authtoken_app_obj, gen_token_req_schema, gen_token_req_headers_schema, authtoken_app
from src.tokenmanagement_service.authtoken_grpc.client import gRPCTokenClient


def create_token():
    try:
        authtoken_app_logger.info('REQUEST ==> Received Endpoint :: {0}'.format(request.endpoint))
        rec_req_headers = dict(request.headers)
        authtoken_app_logger.info("Received Headers from the request :: {0}".format(rec_req_headers))
        header_result = authtoken_app_obj.generate_req_missing_params(rec_req_headers, gen_token_req_headers_schema)
        if len(header_result.keys()) != 0:
            header_result["message"] = "Request Header Missing"
            authtoken_app_logger.info("Sending Error response back to client :: {0}".format(header_result))
            abort(400, description=header_result)
        if request.method == 'POST':
            rec_req_data = request.get_json()
            body_result = authtoken_app_obj.generate_req_missing_params(rec_req_data, gen_token_req_schema)
            if len(body_result.keys()) != 0:
                body_result["message"] = "Request Params Missing"
                authtoken_app_logger.info("Sending Error response back to client :: {0}".format(body_result))
                abort(400, description=body_result)
            userid = rec_req_data['userId']
            username = rec_req_data['username']
            password = rec_req_data['password']
            authtoken_app_logger.info("Processing the request data... :: [STARTED]")
            token_session = authtoken_app_obj.get_session_for_service()
            if token_session is None:
                authtoken_app_logger.info("Session Creation for the token :: [FAILED]")
                return jsonify({"message": "Internal Server Error"}), 500

            authtoken_app_logger.info("Checking for the token which is already exists or not for the user")
            token_record = token_session.query(TokensModel).filter_by(UserID=userid).first()
            if token_record is not None:
                authtoken_app_logger.info("Already token exists for the user not need to generate a new token.")
                token_instance = Token.convert_db_model_to_response(token_record)
                token_user_response = Token.generate_success_response(token_instance, "Token Already Exists")
                authtoken_app_logger.info("Generating Success response  :: [STARTED] :: {0}".format(token_user_response))
                return jsonify(token_user_response), 200

            authtoken_app_logger.info("Token not exists, so Validating whether it is registered user  :: [STARTED]")
            authtoken_app_logger.info("Sending gRPC message to Registration Service :: [STARTED]")
            token_grpc_client = gRPCTokenClient(grpc_auth_token_client_ip=authtoken_app.config["REGISTRATION_GRPC_SERVER_IP"], grpc_auth_token_client_port=authtoken_app.config["REGISTRATION_GRPC_SERVER_PORT"])
            tokenstub, grpc_client_status = token_grpc_client.create_channel_stub()
            if not grpc_client_status:
                authtoken_app_logger.error("Channel/stub  Creation, , Sending error response  :: [FAILED]")
                return jsonify({"message": "Internal Server Error"}), 500

            message_to_send = token_grpc_client.TokenGrpcRequestPreparation(userid=userid, username=username, passcode=password)
            if message_to_send is None:
                authtoken_app_logger.error("gRPC Message to preparation, Sending error response :: [FAILED]")
                return jsonify({"message": "Internal Server Error"}), 500
            token_grpc_client.data_to_send = message_to_send
            resp_data = token_grpc_client.trigger_request()
            if not resp_data.isvalid:
                authtoken_app_logger.info("InValid User, no need to create a new token")
                return jsonify({"message": "INVALID_USER"}), 400

            authtoken_app_logger.info("gRPC Response data :: {0}, Response status :: {1}".format(resp_data.userid, resp_data.isvalid))
            token_grpc_client.close_channel_stub()  # Close the channel
            token_obj = Token(user_id=userid, user_name=username, pwd=password)
            token_instance = token_obj.add_token()
            if token_instance is None:
                authtoken_app_logger.error("Token creation  :: [FAILED]")
                return jsonify({"message": "Internal Server Error"}), 500
            authtoken_app_logger.info("Valid User, need to create a new token")
            token_map_db_instance = TokensModel(UserID=token_instance["userid"], Token=token_instance["token"], Expiry=token_instance["expiry"],
                                                CreatedAt=token_instance["created_at"], UpdatedAt=token_instance["updated_at"])

            authtoken_app_logger.info("Mapping the request data to the database model:: [SUCCESS]")
            token_session = authtoken_app_obj.get_session_for_service()
            if token_session is None:
                abort(500, description={'message': 'Create Session Failed'})

            try:
                authtoken_app_logger.info("Data adding into  DataBase session {0}:: [STARTED]".format(token_map_db_instance))
                token_session.add(token_map_db_instance)
                authtoken_app_logger.info("Data added into  DataBase session {0}:: [SUCCESS]".format(token_map_db_instance))
                token_session.commit()  # Commit the change
                authtoken_app_logger.info("Added Data is committed into  DataBase {0}:: [SUCCESS]".format(token_session))
                token_instance = Token.convert_db_model_to_response(token_map_db_instance)
                token_user_response = Token.generate_success_response(token_instance, "Token Created")
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
                authtoken_app_obj.close_session_for_service(token_session) # Close the session
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return jsonify({"message": "Internal Server Error"}), 500



