import sys
import sqlalchemy.exc
from flask import request, make_response
from usermanagement_service.users.request_handlers.user import User
from src.usermanagement_service.models.user_model import UsersModel
from src.usermanagement_service import (
    user_management_app_logger,
    getuser_headers_schema,
    usermanager,
)
from pyportal_common.error_handlers.base_error_handler import (
    PyPortalAdminInvalidRequestError,
    PyPortalAdminInternalServerError,
    PyPortalAdminNotFoundError,
)


def get_user_info(userid):
    try:
        user_management_app_logger.info(
            f"REQUEST ==> Received Endpoint for the request:: {request.endpoint}"
        )
        user_management_app_logger.info(
            f"REQUEST ==> Received url for the request :: {request.url}"
        )
        if request.method == "GET":
            rec_req_headers = dict(request.headers)
            user_management_app_logger.info(
                f"Received Headers from the request :: {rec_req_headers}"
            )
            """
                1. Find the missing headers, any schema related issue related to headers in the request
                2. If any missing headers or schema related issue , send the error response back to client.
                3. Custom error response contains the information about headers related to missing/schema issue, with status code as 400,BAD_REQUEST
            """
            get_header_result = usermanager.generate_req_missing_params(
                rec_req_headers, getuser_headers_schema
            )
            if len(get_header_result.keys()) != 0:
                invalid_header_err_res = PyPortalAdminInvalidRequestError(
                    message="Request Headers Missing",
                    error_details=get_header_result,
                    logger=user_management_app_logger,
                )
                return invalid_header_err_res.send_response_to_client()
            # Retrieve the user logic.
            get_user_management_session = usermanager.get_session_from_pool()()
            if get_user_management_session is None:
                session_err_res = PyPortalAdminInternalServerError(
                    message="Create Session Failed", logger=user_management_app_logger
                )
                return session_err_res.send_response_to_client()
            # IF the created session is not active, send the response back to client as internal error
            if get_user_management_session.is_active:
                try:
                    """
                    1. Fetching the user record from the database using the primary key userid
                     2. Converting the database model of user to defined user and serialize to json
                     3. Using the serialize , Generating the success custom response , headers
                    """
                    get_user_instance = get_user_management_session.query(
                        UsersModel
                    ).get(userid)
                    if get_user_instance is None:
                        usr_not_found_err_res = PyPortalAdminNotFoundError(
                            message="Retrieved user doesn't exists",
                            logger=user_management_app_logger,
                        )
                        return usr_not_found_err_res.send_response_to_client()
                except sqlalchemy.exc.NoResultFound as ex:
                    usermanager.close_session(sessionname=get_user_management_session)
                    user_management_app_logger.error(
                        f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
                    )
                    db_err_res = PyPortalAdminInternalServerError(
                        message="Database Error", logger=user_management_app_logger
                    )
                    return db_err_res.send_response_to_client()
                except Exception as ex:
                    usermanager.close_session(sessionname=get_user_management_session)
                    user_management_app_logger.error(
                        f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
                    )
                    internal_err_res = PyPortalAdminInternalServerError(
                        message="Internal Server Error",
                        logger=user_management_app_logger,
                    )
                    return internal_err_res.send_response_to_client()
                else:
                    get_user_instance = User.convert_db_model_to_resp(get_user_instance)
                    if len(get_user_instance.keys()) <= 0:
                        invalid_req_err_res = PyPortalAdminInternalServerError(
                            message="Get User Response creation Failed",
                            logger=user_management_app_logger,
                        )
                        usermanager.close_session(
                            sessionname=get_user_management_session
                        )
                        return invalid_req_err_res.send_response_to_client()
                    custom_user_response_body = User.generate_custom_response_body(
                        user_instance=get_user_instance, messagedata="Retrieved User"
                    )
                    if len(custom_user_response_body.keys()) <= 0:
                        invalid_req_err_res = PyPortalAdminInternalServerError(
                            message="Get User success Response creation Failed",
                            logger=user_management_app_logger,
                        )
                        usermanager.close_session(
                            sessionname=get_user_management_session
                        )
                        return invalid_req_err_res.send_response_to_client()
                    get_usr_response = make_response(custom_user_response_body)
                    get_usr_response.headers["Content-Type"] = "application/json"
                    get_usr_response.headers["Cache-Control"] = "no-cache"
                    get_usr_response.status_code = 200
                    user_management_app_logger.info(
                        f"Prepared success response and sending back to client  {get_usr_response}:: [STARTED]"
                    )
                    usermanager.close_session(sessionname=get_user_management_session)
                    return get_usr_response
            else:
                invalid_req_err_res = PyPortalAdminInternalServerError(
                    message="Create Session Failed", logger=user_management_app_logger
                )
                return invalid_req_err_res.send_response_to_client()

    except Exception as ex:
        user_management_app_logger.error(
            f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
        )
        invalid_req_err_res = PyPortalAdminInternalServerError(
            message="Unknown error caused", logger=user_management_app_logger
        )
        return invalid_req_err_res.send_response_to_client()
