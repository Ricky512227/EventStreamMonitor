import sys
from sqlalchemy.exc import SQLAlchemyError
from flask import jsonify, request, abort
from src.authtoken_service.tokens.token import Token
from src.authtoken_service.models.token_model import TokensModel
from src.authtoken_service import authtoken_app_logger, gen_token_headers_schema, gen_token_req_schema, authtoken_app_obj
from src.authtoken_service.authtoken_grpc.client import gRPCTokenClient
from src.airliner_common.req_header_validation import generate_req_missing_params




def create_token():
    try:
        authtoken_app_logger.info('REQUEST ==> Received Endpoint :: {0}'.format(request.endpoint))
        rec_req_headers = dict(request.headers)
        authtoken_app_logger.info("Received Headers from the request :: {0}".format(rec_req_headers))
        authtoken_app_logger.info("Validation for Request-Header is  :: [STARTED]")
        headers_result = generate_req_missing_params(rec_req_headers, gen_token_headers_schema)
        # Header Validation
        if len(headers_result.keys()) != 0:
            authtoken_app_logger.error("Validation for Request-Header is  :: [FAILED]")
            headers_result["message"] = "Request Header Missing"
            authtoken_app_logger.info("Sending Error response back to client :: {0}".format(headers_result))
            abort(400, description=headers_result)
        authtoken_app_logger.info("Validation for Request-Header is  :: [SUCCESS]")
        # Method Validation
        if request.method == 'POST':
            rec_req_data = request.get_json()
            userid = rec_req_data['userId']
            username = rec_req_data['username']
            password = rec_req_data['password']
            # PAYLOAD VALIDATION
            authtoken_app_logger.info("Validation for Request-Body is  :: [STARTED]")
            payload_result = generate_req_missing_params(rec_req_data, gen_token_req_schema)
            if len(payload_result.keys()) != 0:
                authtoken_app_logger.error("Validation for Request-Body is  :: [FAILED]")
                payload_result["message"] = "Request Params Missing"
                authtoken_app_logger.info("Sending Error response back to client :: {0}".format(payload_result))
                abort(400, description=payload_result)

            # Create a session
            token_session = authtoken_app_obj.get_session_for_service()
            if token_session is None:
                authtoken_app_logger.info("Session Creation for the token :: [FAILED]")
                return jsonify({"message": "Internal Server Error"}), 500

            authtoken_app_logger.info("Checking for the token which is already exists or not for the user")
            token_record = token_session.query(TokensModel).filter_by(UserID=userid).first()

            if token_record is not None:
                authtoken_app_logger.info("Already token exists for the user not need to generate a new token.")
                token_instance = Token.convert_db_model_to_response(token_record)
                token_user_response = Token.generate_success_response(token_instance)
                authtoken_app_logger.info("Generating Success response  :: [STARTED] :: {0}".format(token_user_response))
                return jsonify(token_user_response), 200

            authtoken_app_logger.info("Token not exists, so Validating whether it is registered user  :: [STARTED]")
            authtoken_app_logger.info("Sending gRPC message to Registration Service :: [STARTED]")
            token_grpc_client = gRPCTokenClient("127.0.0.1", "8081")
            tokenstub, grpc_client_status = token_grpc_client.create_channel_stub()
            if not grpc_client_status:
                authtoken_app_logger.error("Channel/stub  Creation :: [FAILED]")
                return jsonify({"message": "Internal Server Error"}), 500

            message_to_send = token_grpc_client.TokenGrpcRequestPreparation(userid=userid, username=username, passcode=password)
            if message_to_send is None:
                authtoken_app_logger.error("gRPC Message to preparation  :: [FAILED]")
                return jsonify({"message": "Internal Server Error"}), 500
            token_grpc_client.data_to_send = message_to_send
            resp_data, resp_status = token_grpc_client.trigger_request()
            if not resp_status:
                authtoken_app_logger.error("Sending gRPC message to Registration Service :: [FAILED]")
                return jsonify({"message": "Internal Server Error"}), 500

            authtoken_app_logger.info("gRPC Response data :: {0}, Response status :: {1}".format(resp_data, resp_status))
            token_grpc_client.close_channel_stub()  # Close the channel
            token_obj = Token(user_id=userid, user_name=username, pwd=password)
            token_instance = token_obj.add_token()
            if token_instance is None:
                authtoken_app_logger.error("Token creation  :: [FAILED]")
                return jsonify({"message": "Internal Server Error"}), 500
            authtoken_app_logger.info("Valid User, need to create a new token")
            token_map_db_instance = TokensModel(UserID=token_instance["userid"], Token=token_instance["token"], Expiry=token_instance["expiry"],
                                                CreatedAt=token_instance["created_at"], UpdatedAt=token_instance["updated_at"])

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
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return jsonify({"message": "Internal Server Error"}), 500



