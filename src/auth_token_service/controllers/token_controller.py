import sys
from sqlalchemy.exc import SQLAlchemyError
from flask import jsonify, request, abort
from src.auth_token_service.tokens.token import Token
from src.auth_token_service.models.token_model import TokensModel
from src.auth_token_service import authtoken_app, authtoken_app_logger, req_headers_schema, gen_token_req_schema,\
    login_user_req_schema, authtoken_app_obj
from src.auth_token_service.authtoken_grpc.client import TokenGrpcRequestPreparation, init_grpc_token_client, trigger_request
from src.airliner_common.airliner_error_handling import AirlinerError404, AirlinerError500, AirlinerError400





def create_token():
    try:
        if request.method == 'POST':
            rec_req_data = request.get_json()
            userid = rec_req_data['userId']
            username = rec_req_data['username']
            password = rec_req_data['password']
            token_obj = Token.create_custom_token(userid,username,password)
            data_to_send = TokenGrpcRequestPreparation(userid=userid, username=username, passcode=password)
            tokenstub, grpc_client_status = init_grpc_token_client()
            resp_data, resp_status = trigger_request(tokenstub, data_to_send)
            print("resp_data :: {0}, resp_status :: {1}".format(resp_data, resp_status))
            if resp_status:
                token_map_db_instance = TokensModel(UserID=token_obj.user_id,
                                                  Token=token_obj.custom_access_token,
                                                  Expiry=token_obj.expiry,
                                                  CreatedAt=token_obj.created_at,
                                                  UpdatedAt=token_obj.updated_at)

                token_session = authtoken_app_obj.create_session_for_service()
                if token_session is not None:
                    try:
                        token_session.add(token_map_db_instance)
                        authtoken_app_logger.info("Data added into  DataBase session {0}:: SUCCESS".format(token_map_db_instance))
                        token_session.commit()  # Commit the change
                        authtoken_app_logger.info("Added Data is committed into  DataBase {0}:: SUCCESS".format(token_session))

                        print("Commit the  changes  {0}:: SUCCESS".format(token_session))
                        authtoken_app_logger.info("Generating Success response  :: [STARTED]")
                        # custom_token_response = Token.convert_db_model_to_response(token_map_db_instance)
                        # print(custom_token_response)
                        # success_token_response = Token.generate_success_response(custom_token_response)
                        # authtoken_app_logger.info("Generating Success response  :: [STARTED] :: {0}".format(success_token_response))
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
            else:
                print("Aborting now")
                abort(500)

    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))