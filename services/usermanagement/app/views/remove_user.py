import sys

import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
from flask import request, make_response
from app.models.user_model import UsersModel
from app import (
    user_management_app_logger,
    del_user_headers_schema,
    usermanager,
)
from app.redis_helper import UserManagementRedisHelper
from common.pyportal_common.error_handlers.base_error_handler import (
    PyPortalAdminInvalidRequestError,
    PyPortalAdminInternalServerError,
    PyPortalAdminNotFoundError,
)


def deregister_user(userid):
    try:
        user_management_app_logger.info(
            f"REQUEST ==> Received Endpoint for the request:: {request.endpoint}"
        )
        user_management_app_logger.info(
            f"REQUEST ==> Received url for the request :: {request.url}"
        )
        if request.method == "DELETE":
            rec_req_headers = dict(request.headers)
            user_management_app_logger.info(
                f"Received Headers from the request :: {rec_req_headers}"
            )
            """
                1. Find the missing headers, any schema related issue related to headers in the request
                2. If any missing headers or schema related issue , send the error response back to client.
                3. Custom error response contains the information about headers related to missing/schema issue, with status code as 400,BAD_REQUEST
            """
            del_header_result = usermanager.generate_req_missing_params(
                rec_req_headers, del_user_headers_schema
            )
            if len(del_header_result.keys()) != 0:
                invalid_header_err_res = PyPortalAdminInvalidRequestError(
                    message="Request Headers Missing",
                    error_details=del_header_result,
                    logger=user_management_app_logger,
                )
                return invalid_header_err_res.send_response_to_client()
            # Initialize Redis helper for cache invalidation
            redis_helper = UserManagementRedisHelper()
            
            # Retrieve the user logic.
            del_user_management_session = usermanager.get_session_from_pool()()
            if del_user_management_session is None:
                session_err_res = PyPortalAdminInternalServerError(
                    message="Create Session Failed", logger=user_management_app_logger
                )
                return session_err_res.send_response_to_client()
            # IF the created session is not active, send the response back to client as internal error
            if del_user_management_session.is_active:
                try:
                    """1. Delete the user record from the database using the primary key userid
                    2. Get user info before deletion to invalidate lookup caches
                    3. Invalidate Redis cache after successful deletion
                    4. Using the serialize , Generating the success custom response , headers
                    """
                    del_user_instance = del_user_management_session.query(
                        UsersModel
                    ).get(userid)
                    if del_user_instance is None:
                        usr_not_found_err_res = PyPortalAdminNotFoundError(
                            message="Retrieved user doesn't exists",
                            logger=user_management_app_logger,
                        )
                        return usr_not_found_err_res.send_response_to_client()
                except sqlalchemy.exc.NoResultFound as ex:
                    usermanager.close_session(sessionname=del_user_management_session)
                    user_management_app_logger.error(
                        f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
                    )
                    db_err_res = PyPortalAdminInternalServerError(
                        message="Database Error", logger=user_management_app_logger
                    )
                    return db_err_res.send_response_to_client()
                except Exception as ex:
                    usermanager.close_session(sessionname=del_user_management_session)
                    user_management_app_logger.error(
                        f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
                    )
                    internal_err_res = PyPortalAdminInternalServerError(
                        message="Internal Server Error",
                        logger=user_management_app_logger,
                    )
                    return internal_err_res.send_response_to_client()
                else:
                    user_management_app_logger.info(
                        f"Found user with the id in the db :: {userid}"
                    )
                    try:
                        with del_user_management_session.begin():
                            del_user_management_session.query(UsersModel).filter(
                                UsersModel.ID == userid
                            ).delete()
                    except sqlalchemy.exc.NoResultFound as ex:
                        usermanager.close_session(
                            sessionname=del_user_management_session
                        )
                        user_management_app_logger.error(
                            f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
                        )
                        db_err_res = PyPortalAdminInternalServerError(
                            message="Database Error", logger=user_management_app_logger
                        )
                        return db_err_res.send_response_to_client()
                    except Exception as ex:
                        usermanager.close_session(
                            sessionname=del_user_management_session
                        )
                        user_management_app_logger.error(
                            f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
                        )
                        internal_err_res = PyPortalAdminInternalServerError(
                            message="Internal Server Error",
                            logger=user_management_app_logger,
                        )
                        return internal_err_res.send_response_to_client()
                    else:
                        # Invalidate Redis cache after successful deletion
                        try:
                            # Get username and email before deletion for lookup cache invalidation
                            username = del_user_instance.Username if del_user_instance else None
                            email = del_user_instance.Email if del_user_instance else None
                            
                            # Invalidate user cache
                            redis_helper.invalidate_user_cache(userid)
                            
                            # Invalidate lookup caches if we have username/email
                            if username:
                                lookup_key_username = f"user:lookup:username:{username}"
                                redis_helper.redis_client.delete(lookup_key_username)
                            
                            if email:
                                lookup_key_email = f"user:lookup:email:{email}"
                                redis_helper.redis_client.delete(lookup_key_email)
                            
                            user_management_app_logger.info(
                                f"Invalidated Redis cache for user {userid} [SUCCESS]"
                            )
                        except Exception as cache_ex:
                            # Log cache error but don't fail the request
                            user_management_app_logger.warning(
                                f"Failed to invalidate cache for user {userid}: {cache_ex}"
                            )
                        
                        del_usr_response = make_response("")
                        del_usr_response.headers["Cache-Control"] = "no-cache"
                        del_usr_response.status_code = 204
                        user_management_app_logger.info(
                            f"Prepared success response and sending back to client  {del_usr_response}:: [SUCCESS]"
                        )
                        usermanager.close_session(
                            sessionname=del_user_management_session
                        )
                        return del_usr_response
            else:
                session_err_res = PyPortalAdminInternalServerError(
                    message="Create Session Failed", logger=user_management_app_logger
                )
                return session_err_res.send_response_to_client()
    except Exception as ex:
        user_management_app_logger.error(
            f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
        )
        invalid_req_err_res = PyPortalAdminInternalServerError(
            message="Unknown error caused", logger=user_management_app_logger
        )
        return invalid_req_err_res.send_response_to_client()
