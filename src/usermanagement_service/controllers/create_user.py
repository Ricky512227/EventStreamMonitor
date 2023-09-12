import sys
import sqlalchemy.orm.exc
from sqlalchemy.exc import SQLAlchemyError
from flask import request, make_response
from src.usermanagement_service.users.user import User
from src.usermanagement_service.models.user_model import UsersModel
from src.usermanagement_service import user_management_app_logger, req_headers_schema, reg_user_req_schema, usermanager
from src.admin_common.admin_error_handling import PyPortalAdminInvalidRequestError, PyPortalAdminInternalServerError
from src.usermanagement_service.utils.util_helpers import is_username_email_already_exists_in_db


def register_user():
    try:
        user_management_app_logger.info('REQUEST ==> Received Endpoint for the request:: {0}'.format(request.endpoint))
        user_management_app_logger.info('REQUEST ==> Received url for the request :: {0}'.format(request.url))
        if request.method == 'POST':
            rec_req_headers = dict(request.headers)
            user_management_app_logger.info("Received Headers from the request :: {0}".format(rec_req_headers))
            ''' 
                1. Find the missing headers, any schema related issue related to headers in the request
                2. If any missing headers or schema related issue , send the error response back to client.
                3. Custom error response contains the information about headers related to missing/schema issue, with status code as 400,BAD_REQUEST
            '''
            reg_header_result = usermanager.generate_req_missing_params(rec_req_headers, req_headers_schema)
            if len(reg_header_result.keys()) != 0:
                invalid_header_err_res = PyPortalAdminInvalidRequestError(message="Request Headers Missing", error_details=reg_header_result, logger=user_management_app_logger)
                return invalid_header_err_res.send_resposne_to_client()

            rec_req_data = request.get_json()
            ''' 
                1. Find the missing params, any schema related issue related to params in the request body
                2. If any missing params or schema related issue , send the error response back to client.
                3. Custom error response contains the information about params related to missing/schema issue, with status code as 400,BAD_REQUEST
            '''
            body_result = usermanager.generate_req_missing_params(rec_req_data, reg_user_req_schema)
            if len(body_result.keys()) != 0:
                invalid_body_err_res = PyPortalAdminInvalidRequestError(message="Request Params Missing", error_details=body_result, logger=user_management_app_logger)
                return invalid_body_err_res.send_resposne_to_client()

            # Read the content which was received in the request
            username = rec_req_data['username']
            firstname = rec_req_data['firstName']
            lastname = rec_req_data['lastName']
            emailaddress = rec_req_data['email']
            password = rec_req_data['password']
            dateofbirth = rec_req_data['dateOfBirth']
            user_management_app_logger.info("Processing the request data... :: [STARTED]")
            session_to_validate_existing_user = usermanager.get_session_from_conn_pool()
            if session_to_validate_existing_user is None:
                '''
                    No need to close the connection/session if the timeout occurs during the session/connection creation.
                    If the queue is full, it will try to wait initiate/fetch connection from the overflows connections.
                '''
                invalid_req_err_res = PyPortalAdminInternalServerError(message="Create Session Failed", logger=user_management_app_logger)
                return invalid_req_err_res.send_response_to_client()
            # Doing the pre-validation checks before procession the request.
            if is_username_email_already_exists_in_db(sessionname=session_to_validate_existing_user, uname=username, email=emailaddress):
                invalid_req_err_res = PyPortalAdminInvalidRequestError(message="Username or EmailAddress already exists", logger=user_management_app_logger)
                usermanager.close_session(sessionname=session_to_validate_existing_user)
                return invalid_req_err_res.send_resposne_to_client()
            # Register user-logic begins here
            session_to_create_new_user = usermanager.get_session_from_conn_pool()
            if session_to_create_new_user is None:
                invalid_req_err_res = PyPortalAdminInternalServerError(message="Create Session Failed", logger=user_management_app_logger)
                return invalid_req_err_res.send_response_to_client()
            # IF the created session is not active, send the response back to client as internal error
            if session_to_create_new_user.is_active:
                try:
                    '''
                        Initialise the user object using the data received in the request, 
                        if the user object holds none, clos the active session  send the response back to client as the internal error
                    '''
                    user_obj = User(username=username, firstname=firstname, lastname=lastname, dateofbirth=dateofbirth, email=emailaddress, pwd=password)
                    if user_obj is None:
                        invalid_req_err_res = PyPortalAdminInternalServerError(message="Create User Failed", logger=user_management_app_logger)
                        usermanager.close_session(sesionname=session_to_create_new_user)
                        return invalid_req_err_res.send_response_to_client()
                    '''
                        Create the initialised user object using the data received in the request, 
                        if the user instance holds none, close the active session  send the response back to client as the internal error
                    '''
                    user_instance = user_obj.add_user()
                    if len(user_instance.keys()) <= 0:
                        invalid_req_err_res = PyPortalAdminInternalServerError(message="User Instance creation Failed", logger=user_management_app_logger)
                        usermanager.close_session(sessionname=session_to_create_new_user)
                        return invalid_req_err_res.send_response_to_client()
                    user_management_app_logger.info("Mapping the request data to the database model:: [STARTED]")
                    '''
                        Using the session begin the transaction, and add the user into the database using ORM.
                    '''
                    with session_to_create_new_user.begin():
                        user_map_db_instance = UsersModel(Username=user_instance["username"],
                                                          FirstName=user_instance["firstname"],
                                                          LastName=user_instance["lastname"],
                                                          Email=user_instance["email"],
                                                          DateOfBirth=user_instance["dateofbirth"],
                                                          Password=user_instance["password"],
                                                          CreatedAt=user_instance["created_at"],
                                                          UpdatedAt=user_instance["updated_at"])
                        user_management_app_logger.info("Mapping the request data to the database model:: [SUCCESS]")
                        ''' 
                            Add the user model to the database and commit the changes
                            Any exception occur, logs the exception and sends back the error response to the client as internal_server_error
                        '''
                        user_management_app_logger.info("Data adding into  DataBase session {0}:: [STARTED]".format(user_map_db_instance))
                        session_to_create_new_user.add(user_map_db_instance)
                        user_management_app_logger.info("Data added into  DataBase session {0}:: [SUCCESS]".format(user_map_db_instance))
                        user_management_app_logger.info("Added Data is committed into DataBase of session {0}:: [SUCCESS]".format(session_to_create_new_user))
                        locationheader = request.url + "/" + str(user_map_db_instance.ID)

                except sqlalchemy.exc.IntegrityError as ex:
                    usermanager.close_session(sessionname=session_to_create_new_user)
                    print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
                    db_err_res = PyPortalAdminInternalServerError(message="Database Error", logger=user_management_app_logger)
                    return db_err_res.send_response_to_client()
                except Exception as ex:
                    usermanager.close_session(sessionname=session_to_create_new_user)
                    print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
                    internal_err_res = PyPortalAdminInternalServerError(message="Internal Server Error", logger=user_management_app_logger)
                    return internal_err_res.send_response_to_client()

                else:
                    ''' 
                        1. Converting the database model of user to defined user and serialize to json
                        2. Using the serialize , Generating the success custom response , headers 
                        3. Sending the response back to client 
                    '''
                    user_instance = User.convert_db_model_to_resp(user_map_db_instance)
                    if len(user_instance.keys()) <= 0:
                        invalid_req_err_res = PyPortalAdminInternalServerError(message="User Response creation Failed", logger=user_management_app_logger)
                        usermanager.close_session(sessionname=session_to_create_new_user)
                        return invalid_req_err_res.send_response_to_client()
                    custom_user_response_body = User.generate_custom_response_body(user_instance=user_instance, messagedata="User Created")
                    if len(custom_user_response_body.keys()) <= 0:
                        invalid_req_err_res = PyPortalAdminInternalServerError(message="User success Response creation Failed", logger=user_management_app_logger)
                        usermanager.close_session(sessionname=session_to_create_new_user)
                        return invalid_req_err_res.send_response_to_client()

                    reg_usr_response = make_response(custom_user_response_body)
                    reg_usr_response.headers['Content-Type'] = 'application/json'
                    reg_usr_response.headers['Cache-Control'] = 'no-cache'
                    reg_usr_response.headers["location"] = locationheader
                    reg_usr_response.status_code = 201
                    user_management_app_logger.info("Prepared success response and sending back to client  {0}:: [STARTED]".format(reg_usr_response))
                    usermanager.close_session(sessionname=session_to_create_new_user)
                    return reg_usr_response

            else:
                invalid_req_err_res = PyPortalAdminInternalServerError(message="Create Session Failed", logger=user_management_app_logger)
                return invalid_req_err_res.send_response_to_client()
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        invalid_req_err_res = PyPortalAdminInternalServerError(message="Unknown error caused", logger=user_management_app_logger)
        return invalid_req_err_res.send_response_to_client()


