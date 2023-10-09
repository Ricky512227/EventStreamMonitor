import sys
from typing import Dict, Union, Any, Optional

import sqlalchemy.orm.exc
from flask import request, make_response

from src.pyportal_common.db_handlers.db_utilities import (
    get_session_from_pool,
    close_session,
)
from src.usermanagement_service.users.request_handlers.user import User
from src.usermanagement_service import (
    user_management_logger,
    req_headers_schema,
    reg_user_req_schema,
    usermanager,
    session_maker_obj,
)
from src.pyportal_common.error_handlers.invalid_request_handler import (
    send_invalid_request_error_to_client,
)
from src.pyportal_common.error_handlers.internal_server_error_handler import (
    send_internal_server_error_to_client,
)
from src.usermanagement_service.utils.util_helpers import (
    is_username_email_already_exists_in_db,
    convert_db_model_to_resp,
)
from src.usermanagement_service.users.response_handlers.create_user_success_response import (
    generate_success_response,
)
from usermanagement_service.models.user_model import UsersModel


def register_user():
    try:
        user_management_logger.info(
            "REQUEST ==> Received Endpoint for the request:: {0}".format(
                request.endpoint
            )
        )
        user_management_logger.info(
            "REQUEST ==> Received url for the request :: {0}".format(request.url)
        )
        if request.method == "POST":
            rec_req_headers = dict(request.headers)
            user_management_logger.info(
                "Received Headers from the request :: {0}".format(rec_req_headers)
            )
            """ 
                1. Find the missing headers, any schema related issue related to headers in the request
                2. If any missing headers or schema related issue , send the error response back to client.
                3. Custom error response contains the information about headers related to missing/schema issue, with status code as 400,BAD_REQUEST
            """
            reg_header_result = usermanager.generate_req_missing_params(rec_req_headers, req_headers_schema)
            if not reg_header_result:
                return send_invalid_request_error_to_client(app_logger_name=user_management_logger,message_data="Request Headers Missing",err_details=reg_header_result,)

            rec_req_data = request.get_json()
            """ 
                1. Find the missing params, any schema related issue related to params in the request body
                2. If any missing params or schema related issue , send the error response back to client.
                3. Custom error response contains the information about params related to missing/schema issue, with status code as 400,BAD_REQUEST
            """
            body_result = usermanager.generate_req_missing_params(
                rec_req_data, reg_user_req_schema
            )
            if not body_result:
                return send_invalid_request_error_to_client(
                    app_logger_name=user_management_logger,
                    message_data="Request Params Missing",
                    err_details=body_result,
                )

            # Read the content which was received in the request
            username = rec_req_data["username"]
            firstname = rec_req_data["firstName"]
            lastname = rec_req_data["lastName"]
            emailaddress = rec_req_data["email"]
            password = rec_req_data["password"]
            dateofbirth = rec_req_data["dateOfBirth"]
            user_management_logger.info("Processing the request data... :: [STARTED]")
            session_to_validate_existing_user = get_session_from_pool(
                session_maker_to_get_session=session_maker_obj
            )
            if session_to_validate_existing_user is None:
                """
                No need to close the connection/session if the timeout occurs during the session/connection creation.
                If the queue is full, it will try to wait initiate/fetch connection from the overflows connections.
                """
                return send_internal_server_error_to_client(
                    app_logger_name=user_management_logger,
                    message_data="Create Session Failed",
                )
            # Doing the pre-validation checks before procession the request.
            if is_username_email_already_exists_in_db(
                session_instance=session_to_validate_existing_user,
                uname=username,
                email=emailaddress,
            ):
                close_session(session_instance=session_to_validate_existing_user)
                return send_invalid_request_error_to_client(
                    app_logger_name=user_management_logger,
                    message_data="Existing User",
                )
            # Register user-logic begins here
            try:
                user_obj = User(
                    username=username,
                    firstname=firstname,
                    lastname=lastname,
                    dateofbirth=dateofbirth,
                    email=emailaddress,
                    pwd=password,
                )
                if user_obj is None:
                    return send_internal_server_error_to_client(
                        app_logger_name=user_management_logger,
                        message_data="Create User Failed",
                    )
                user_instance: dict[
                    str, Union[Optional[str], Any]
                ] = user_obj.add_user()
                if not user_instance:
                    return send_internal_server_error_to_client(
                        app_logger_name=user_management_logger,
                        message_data="User Instance creation Failed",
                    )
                """
                    Using the session begin the transaction, and add the user into the database using ORM.
                """
                session_to_create_new_user = get_session_from_pool(
                    session_maker_to_get_session=session_maker_obj
                )
                if session_to_create_new_user is None:
                    return send_internal_server_error_to_client(
                        app_logger_name=user_management_logger,
                        message_data="Create Session Failed",
                    )
                with session_to_create_new_user.begin():
                    user_db_record_to_insert: Union[
                        Optional[UsersModel], Any
                    ] = user_obj.map_user_instance_to_db_model()
                    if user_db_record_to_insert is None:
                        close_session(session_instance=session_to_create_new_user)
                        return send_internal_server_error_to_client(
                            app_logger_name=user_management_logger,
                            message_data="User DB - Instance " "mapping Failed",
                        )
                    """ 
                        Add the user model to the database and commit the changes
                        Any exception occur, logs the exception and sends back the error response to the client as internal_server_error
                    """
                    try:
                        user_management_logger.info(
                            "Data adding into  DataBase session {0}:: [STARTED]".format(
                                user_db_record_to_insert
                            )
                        )
                        session_to_create_new_user.add(user_db_record_to_insert)
                        user_management_logger.info(
                            "Data added into  DataBase session {0}:: [SUCCESS]".format(
                                user_db_record_to_insert
                            )
                        )
                        user_management_logger.info(
                            "Added Data is committed into DataBase of session {0}:: [SUCCESS]".format(
                                session_to_create_new_user
                            )
                        )
                        locationheader = (
                            request.url + "/" + str(user_db_record_to_insert.ID)
                        )

                    except sqlalchemy.exc.IntegrityError as ex:
                        close_session(session_instance=session_to_create_new_user)
                        print(
                            "Error occurred :: {0}\tLine No:: {1}".format(
                                ex, sys.exc_info()[2].tb_lineno
                            )
                        )
                        return send_internal_server_error_to_client(app_logger_name=user_management_logger, message_data="Database Error",)
                    else:
                        """
                        1. Converting the database model of user to defined user and serialize to json
                        2. Using the serialize , Generating the success custom response , headers
                        3. Sending the response back to client
                        """
                        user_instance = convert_db_model_to_resp(model_instance=user_db_record_to_insert)
                        if not user_instance:
                            close_session(session_instance=session_to_create_new_user)
                            return send_internal_server_error_to_client(
                                app_logger_name=user_management_logger,
                                message_data="User Response creation " "Failed",
                            )

                        custom_user_response_body = generate_success_response(user_instance)
                        if len(custom_user_response_body) == 0:
                            close_session(session_instance=session_to_create_new_user)
                            return send_internal_server_error_to_client(
                                app_logger_name=user_management_logger,
                                message_data="User success Response creation Failed",
                            )
                        reg_usr_response = make_response(custom_user_response_body)
                        reg_usr_response.headers["Content-Type"] = "application/json"
                        reg_usr_response.headers["Cache-Control"] = "no-cache"
                        reg_usr_response.headers["location"] = locationheader
                        reg_usr_response.status_code = 201
                        close_session(session_instance=session_to_create_new_user)
                        user_management_logger.info(
                            f"Prepared success response and sending back to client  {reg_usr_response}:: [STARTED]"
                        )
                        return reg_usr_response
            except Exception as ex:
                print(
                    f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
                )
                return send_internal_server_error_to_client(
                    app_logger_name=user_management_logger,
                    message_data="Unknown error caused",
                )
    except Exception as ex:
        print(f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}")
        return send_internal_server_error_to_client(
            app_logger_name=user_management_logger, message_data="Unknown error caused"
        )
