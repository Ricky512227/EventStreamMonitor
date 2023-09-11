import json
import sys
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
from flask import jsonify, request, abort, make_response
from src.usermanagement_service.users.user import User
from src.usermanagement_service.models.user_model import UsersModel
from src.usermanagement_service import user_management_app_logger, req_headers_schema, getuser_headers_schema, \
    del_user_headers_schema, reg_user_req_schema, usermanager
from src.admin_common.admin_error_handling import PyPortalAdminInvalidRequestError, PyPortalAdminInternalServerError, \
    PyPortalAdminNotFoundError


def register_user():
    try:
        user_management_app_logger.info('REQUEST ==> Received Endpoint for the request:: {0}'.format(request.endpoint))
        user_management_app_logger.info('REQUEST ==> Received url for the request :: {0}'.format(request.url))
        if request.method == 'POST':
            try:
                rec_req_data = request.get_json()
            except:
                invalid_body_err_res = PyPortalAdminInvalidRequestError(message="Empty data payload received",
                                                                        logger=user_management_app_logger)
                print("Object ID of invalid_header_err_res:", id(invalid_body_err_res))
                return invalid_body_err_res.send_resposne_to_client()
            rec_req_headers = dict(request.headers)
            user_management_app_logger.info("Received Headers from the request :: {0}".format(rec_req_headers))
            ''' 
                1. Find the missing headers, any schema related issue related to headers in the request
                2. If any missing headers or schema related issue , send the error response back to client.
                3. Custom error response contains the information about headers related to missing/schema issue, with status code as 400,BAD_REQUEST
            '''
            reg_header_result = usermanager.generate_req_missing_params(rec_req_headers, req_headers_schema)
            if len(reg_header_result.keys()) != 0:
                invalid_header_err_res = PyPortalAdminInvalidRequestError(message="Request Headers Missing",
                                                                          error_details=reg_header_result,
                                                                          logger=user_management_app_logger)
                print("Object ID of invalid_header_err_res:", id(invalid_header_err_res))
                return invalid_header_err_res.send_resposne_to_client()
            ''' 
                1. Find the missing params, any schema related issue related to params in the request body
                2. If any missing params or schema related issue , send the error response back to client.
                3. Custom error response contains the information about params related to missing/schema issue, with status code as 400,BAD_REQUEST
            '''
            body_result = usermanager.generate_req_missing_params(rec_req_data, reg_user_req_schema)
            if len(body_result.keys()) != 0:
                invalid_body_err_res = PyPortalAdminInvalidRequestError(message="Request Params Missing",
                                                                        error_details=body_result,
                                                                        logger=user_management_app_logger)
                print("Object ID of invalid_header_err_res:", id(invalid_body_err_res))
                return invalid_body_err_res.send_resposne_to_client()

            # Read the content which was received in the request
            username = rec_req_data['username']
            firstname = rec_req_data['firstName']
            lastname = rec_req_data['lastName']
            emailaddress = rec_req_data['email']
            password = rec_req_data['password']
            dateofbirth = rec_req_data['dateOfBirth']
            user_management_app_logger.info("Processing the request data... :: [STARTED]")
            # Doing the pre-validation checks before procession the request.
            if is_username_email_already_exists(uname=username, email=emailaddress):
                invalid_req_err_res = PyPortalAdminInvalidRequestError(
                    message="Username or EmailAddress already exists", logger=user_management_app_logger)
                return invalid_req_err_res.send_resposne_to_client()

            user_obj = User(username=username, firstname=firstname, lastname=lastname, dateofbirth=dateofbirth,
                            email=emailaddress, pwd=password)
            if user_obj is None:
                invalid_req_err_res = PyPortalAdminInternalServerError(message="Create User Failed",
                                                                       logger=user_management_app_logger)
                return invalid_req_err_res.send_response_to_client()

            user_instance = user_obj.create_user()
            user_management_app_logger.info("Mapping the request data to the database model:: [STARTED]")
            user_management_session = usermanager.get_session_for_service()
            if user_management_session is None:
                invalid_req_err_res = PyPortalAdminInternalServerError(message="Create Session Failed",
                                                                       logger=user_management_app_logger)
                return invalid_req_err_res.send_response_to_client()
            #  Map the user obj to User model using ORM
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
            try:
                user_management_app_logger.info(
                    "Data adding into  DataBase session {0}:: [STARTED]".format(user_map_db_instance))
                user_management_session.add(user_map_db_instance)
                user_management_app_logger.info(
                    "Data added into  DataBase session {0}:: [SUCCESS]".format(user_map_db_instance))
                user_management_session.commit()
                user_management_app_logger.info(
                    "Added Data is committed into  DataBase {0}:: [SUCCESS]".format(user_management_session))
            except SQLAlchemyError as ex:
                db_err_res = teardown_db_session(error_message="Database Error", session_name=user_management_session)
                return db_err_res.send_response_to_client()
            except Exception as ex:
                db_err_res = teardown_db_session(error_message="Internal Server Error",
                                                 session_name=user_management_session)
                return db_err_res.send_response_to_client()
            ''' 
                1. Converting the database model of user to defined user and serialize to json
                2. Using the serialize , Generating the success custom response , headers 
                3. Sending the response back to client 
            '''
            user_instance = User.convert_db_model_to_resp(user_map_db_instance)
            custom_user_response_body = User.generate_custom_response_body(user_instance=user_instance,
                                                                           messagedata="User Created")
            reg_usr_response = make_response(custom_user_response_body)
            reg_usr_response.headers["location"] = request.url + "/" + str(custom_user_response_body["user"]["userId"])
            reg_usr_response.headers['Content-Type'] = 'application/json'
            reg_usr_response.headers['Cache-Control'] = 'no-cache'
            reg_usr_response.status_code = 201
            user_management_app_logger.info(
                "Prepared success response and sending back to client  {0}:: [STARTED]".format(reg_usr_response))
            usermanager.close_session_for_service(user_management_session)
            return reg_usr_response

    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        invalid_req_err_res = PyPortalAdminInternalServerError(message="Unknown error caused",
                                                               logger=user_management_app_logger)
        return invalid_req_err_res.send_response_to_client()


def teardown_db_session(error_message, session_name):
    try:
        session_name.rollback()
        usermanager.close_session_for_service(session_name)
        err_response = PyPortalAdminInternalServerError(message=error_message)
        user_management_app_logger.info("Sending Error response back to client :: {0}".format(err_response))
        return err_response
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))


def is_userid_exists(userid):
    is_user_exists_status = False
    try:
        user_management_session = usermanager.get_session_for_service()
        if user_management_session is not None:
            user_management_app_logger.info(
                "Querying Userid in the Database to check the if user exists :: {0}".format(userid))
            user_row = user_management_session.query(UsersModel).get(userid)
            if user_row is not None:
                is_user_exists_status = True
                user_management_app_logger.info(
                    "1 Result for the Query Response :: {0} - {1}".format(userid, is_user_exists_status))
            else:
                user_management_app_logger.info(
                    "2 Result for the Query Response :: {0} - {1}".format(userid, is_user_exists_status))
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
    user_management_app_logger.info(
        "3 Result for the Query Response :: {0} - {1}".format(userid, is_user_exists_status))
    return userid, is_user_exists_status


def is_username_email_already_exists(uname, email):
    try:
        user_management_session = usermanager.get_session_for_service()
        if user_management_session is not None:
            user_management_app_logger.info(
                "Querying UserName :: {0} , Email :: {1} in the Database to check the if already exists :: ".format(
                    uname, email))
            user_row = user_management_session.query(UsersModel).filter(
                or_(UsersModel.Username == uname, UsersModel.Email == email)).first()
            if user_row is not None:
                user_management_app_logger.info("Result for the Query Response :: {0}".format(True))
                return True
            else:
                user_management_app_logger.info("Result for the Query Response :: {0}".format(False))
                return False
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        user_management_app_logger.info("Result for the Query Response :: {0}".format(False))
        return False


def get_user_info(userid):
    try:
        user_management_app_logger.info('REQUEST ==> Received Endpoint for the request:: {0}'.format(request.endpoint))
        user_management_app_logger.info('REQUEST ==> Received url for the request :: {0}'.format(request.url))
        if request.method == 'GET':
            rec_req_headers = dict(request.headers)
            user_management_app_logger.info("Received Headers from the request :: {0}".format(rec_req_headers))
            ''' 
                1. Find the missing headers, any schema related issue related to headers in the request
                2. If any missing headers or schema related issue , send the error response back to client.
                3. Custom error response contains the information about headers related to missing/schema issue, with status code as 400,BAD_REQUEST
            '''
            get_header_result = usermanager.generate_req_missing_params(rec_req_headers, getuser_headers_schema)
            if len(get_header_result.keys()) != 0:
                invalid_header_err_res = PyPortalAdminInvalidRequestError(message="Request Headers Missing",
                                                                          error_details=get_header_result,
                                                                          logger=user_management_app_logger)
                return invalid_header_err_res.send_resposne_to_client()

            get_user_management_session = usermanager.get_session_for_service()
            if get_user_management_session is None:
                invalid_req_err_res = PyPortalAdminInternalServerError(message="Create Session Failed",
                                                                       logger=user_management_app_logger)
                return invalid_req_err_res.send_response_to_client()
            try:
                ''' 1. Fetching the user record from the database using the primary key userid
                    2. Converting the database model of user to defined user and serialize to json
                    3. Using the serialize , Generating the success custom response , headers  '''
                get_user_instance = get_user_management_session.query(UsersModel).get(userid)
                if get_user_instance is None:
                    usr_not_found_err_res = PyPortalAdminNotFoundError(message="Retrieved user doesn't exists",
                                                                       logger=user_management_app_logger)
                    return usr_not_found_err_res.send_response_to_client()
                get_user_instance = User.convert_db_model_to_resp(get_user_instance)
                custom_user_response_body = User.generate_custom_response_body(user_instance=get_user_instance,
                                                                               messagedata="Retrieved User")
                get_usr_response = make_response(custom_user_response_body)
                get_usr_response.headers['Content-Type'] = 'application/json'
                get_usr_response.headers['Cache-Control'] = 'no-cache'
                get_usr_response.status_code = 200
                user_management_app_logger.info(
                    "Prepared success response and sending back to client  {0}:: [STARTED]".format(get_usr_response))
                return get_usr_response
            except SQLAlchemyError as ex:
                return teardown_db_session(error_message="Database Error", session_name=get_user_management_session)
            except Exception as ex:
                return teardown_db_session(error_message="Internal Server Error",
                                           session_name=get_user_management_session)
            finally:
                usermanager.close_session_for_service(get_user_management_session)

    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        invalid_req_err_res = PyPortalAdminInternalServerError(message="Unknown error caused",
                                                               logger=user_management_app_logger)
        return invalid_req_err_res.send_response_to_client()


def remove_user(userid):
    try:
        user_management_app_logger.info('REQUEST ==> Received Endpoint for the request:: {0}'.format(request.endpoint))
        user_management_app_logger.info('REQUEST ==> Received url for the request :: {0}'.format(request.url))
        if request.method == 'DELETE':
            rec_req_headers = dict(request.headers)
            user_management_app_logger.info("Received Headers from the request :: {0}".format(rec_req_headers))
            ''' 
                1. Find the missing headers, any schema related issue related to headers in the request
                2. If any missing headers or schema related issue , send the error response back to client.
                3. Custom error response contains the information about headers related to missing/schema issue, with status code as 400,BAD_REQUEST
            '''
            del_header_result = usermanager.generate_req_missing_params(rec_req_headers, del_user_headers_schema)
            if len(del_header_result.keys()) != 0:
                invalid_header_err_res = PyPortalAdminInvalidRequestError(message="Request Headers Missing",
                                                                          error_details=del_header_result,
                                                                          logger=user_management_app_logger)
                return invalid_header_err_res.send_resposne_to_client()

            del_user_management_session = usermanager.get_session_for_service()
            if del_user_management_session is None:
                invalid_req_err_res = PyPortalAdminInternalServerError(message="Create Session Failed",
                                                                       logger=user_management_app_logger)
                return invalid_req_err_res.send_response_to_client()
            try:
                ''' 1. Delete the user record from the database using the primary key userid
                    2. Converting the database model of user to defined user and serialize to json
                    3. Using the serialize , Generating the success custom response , headers  '''
                get_user_instance = del_user_management_session.query(UsersModel).get(userid)
                if get_user_instance is None:
                    usr_not_found_err_res = PyPortalAdminNotFoundError(message="Retrieved user doesn't exists", logger=user_management_app_logger)
                    return usr_not_found_err_res.send_response_to_client()
                user_management_app_logger.info("Found user with the id in the db :: {0}".format(userid))
                del_user_management_session.query(UsersModel).filter(UsersModel.ID == userid).delete()
                del_user_management_session.commit()
                del_usr_response = make_response('')
                del_usr_response.headers['Cache-Control'] = 'no-cache'
                del_usr_response.status_code = 204
                user_management_app_logger.info("Prepared success response and sending back to client  {0}:: [STARTED]".format(del_usr_response))
                return del_usr_response
            except SQLAlchemyError as ex:
                db_err_res = teardown_db_session(error_message="Database Error", session_name=del_user_management_session)
                return db_err_res.send_response_to_client()
            except Exception as ex:
                db_err_res = teardown_db_session(error_message="Internal Server Error",
                                                 session_name=del_user_management_session)
                return db_err_res.send_response_to_client()

    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        invalid_req_err_res = PyPortalAdminInternalServerError(message="Unknown error caused",
                                                               logger=user_management_app_logger)
        return invalid_req_err_res.send_response_to_client()
