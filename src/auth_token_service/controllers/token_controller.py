import sys
from sqlalchemy.exc import SQLAlchemyError
from flask import jsonify, request, abort

from src.auth_token_service import authtoken_logger, req_headers_schema, reg_user_req_schema, Token, TokensModel, \
    create_session_for_service
from src.airliner_common.req_header_validation import generate_req_missing_params
from src.auth_token_service.client import TokenGrpcRequestPreparation, trigger_request



def create_token():
    if request.method == 'POST':
        rec_req_data = request.get_json()
        userid = rec_req_data['userId']
        username = rec_req_data['username']
        password = rec_req_data['password']
        token_obj = Token.create_custom_token(userid,username,password)

        data_to_send = TokenGrpcRequestPreparation(userid=userid, username=username, passcode=password)
        from src.auth_token_service import tokenstub
        resp_data, resp_status = trigger_request(tokenstub, data_to_send)
        print(">>>>>>>>",resp_data)
        token_map_db_instance = TokensModel(UserID=token_obj.user_id,
                                          Token=token_obj.custom_access_token,
                                          Expiry=token_obj.expiry,
                                          CreatedAt=token_obj.created_at,
                                          UpdatedAt=token_obj.updated_at)
        from src.auth_token_service import token_connection_pool, token_db_engine, TOKEN_SERVICE_NAME
        custom_token_session = create_session_for_service(token_connection_pool, token_db_engine, TOKEN_SERVICE_NAME.lower())
        if custom_token_session is not None:
            try:
                custom_token_session.add(token_map_db_instance)
                authtoken_logger.info("Data added into  DataBase session {0}:: SUCCESS".format(token_map_db_instance))
                custom_token_session.commit()  # Commit the change
                authtoken_logger.info("Added Data is committed into  DataBase {0}:: SUCCESS".format(custom_token_session))

                print("Commit the  changes  {0}:: SUCCESS".format(custom_token_session))
                authtoken_logger.info("Generating Success response  :: [STARTED]")
                # custom_token_response = Token.convert_db_model_to_response(token_map_db_instance)
                # print(custom_token_response)
                # success_token_response = Token.generate_success_response(custom_token_response)
                # authtoken_logger.info("Generating Success response  :: [STARTED] :: {0}".format(success_token_response))
                return jsonify({"message": "ok"}), 201
        #
            except SQLAlchemyError as ex:
                custom_token_session.rollback()
                print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
                abort(500, description={'message': 'Create token Failed', 'details': {'params': ex}})

            except Exception as ex:
                custom_token_session.rollback()
                print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
                abort(500, description={'message': 'Create token Failed', 'details': {'params': str(ex)}})
            finally:
                print("Closing the  session  {0}:: [STARTED]".format(custom_token_session))
                custom_token_session.close()  # Close the change
                print("Closed the  session  {0}:: [SUCCESS]".format(custom_token_session))


