import sys

import sqlalchemy
from flask import request, make_response
from app.models.user_model import UsersModel
from app import (
    user_management_logger,
    del_user_headers_schema,
    usermanager,
    app_manager_db_obj,
)
from app.redis_helper import UserManagementRedisHelper
from common.pyportal_common.error_handlers.invalid_request_handler import (
    EventStreamMonitorInvalidRequestError,
)
from common.pyportal_common.error_handlers.\
    internal_server_error_handler import (
        EventStreamMonitorInternalServerError,
    )
from common.pyportal_common.error_handlers.\
    not_found_error_handler import (
        EventStreamMonitorNotFoundError,
    )
from common.pyportal_common.utils import mask_request_headers


def deregister_user(userid):
    try:
        user_management_logger.info(
            "REQUEST ==> Received Endpoint for the request:: %s",
            request.endpoint
        )
        user_management_logger.info(
            "REQUEST ==> Received url for the request :: %s",
            request.url
        )
        if request.method == "DELETE":
            rec_req_headers = dict(request.headers)
            masked_headers = mask_request_headers(rec_req_headers)
            user_management_logger.info(
                "Received Headers from the request :: %s",
                masked_headers
            )
            # Steps:
            # 1. Find the missing headers, any schema related issue
            #    related to headers in the request
            # 2. If any missing headers or schema related issue,
            #    send the error response back to client.
            # 3. Custom error response contains the information about
            #    headers related to missing/schema issue, with status
            #    code as 400, BAD_REQUEST
            del_header_result = usermanager.generate_req_missing_params(
                rec_req_headers, del_user_headers_schema
            )
            if len(del_header_result.keys()) != 0:
                invalid_header_err_res = EventStreamMonitorInvalidRequestError(
                    message="Request Headers Missing",
                    error_details=del_header_result,
                    logger_instance=user_management_logger,
                )
                return invalid_header_err_res.send_response_to_client()
            # Initialize Redis helper for cache invalidation
            redis_helper = UserManagementRedisHelper()

            # Retrieve the user logic.
            del_user_management_session = (
                app_manager_db_obj.get_session_from_session_maker()
            )
            if del_user_management_session is None:
                session_err_res = EventStreamMonitorInternalServerError(
                    message="Create Session Failed",
                    logger_instance=user_management_logger
                )
                return session_err_res.send_response_to_client()
            # IF the created session is not active, send the response
            # back to client as internal error
            if del_user_management_session.is_active:
                try:
                    # Steps:
                    # 1. Delete the user record from the database using
                    #    the primary key userid
                    # 2. Get user info before deletion to invalidate
                    #    lookup caches
                    # 3. Invalidate Redis cache after successful deletion
                    # 4. Using the serialize, Generating the success
                    #    custom response, headers
                    del_user_instance = del_user_management_session.query(
                        UsersModel
                    ).get(userid)
                    if del_user_instance is None:
                        usr_not_found_err_res = EventStreamMonitorNotFoundError(
                            message="Retrieved user doesn't exists",
                            logger_instance=user_management_logger,
                        )
                        return usr_not_found_err_res.send_response_to_client()
                except sqlalchemy.exc.NoResultFound as ex:
                    # Specific: Query returned no results
                    app_manager_db_obj.close_session(
                        session_instance=del_user_management_session
                    )
                    user_management_logger.warning(
                        "NoResultFound occurred :: %s\tLine No:: %s",
                        ex, sys.exc_info()[2].tb_lineno
                    )
                    usr_not_found_err_res = EventStreamMonitorNotFoundError(
                        message="User not found",
                        logger_instance=user_management_logger,
                    )
                    return usr_not_found_err_res.send_response_to_client()
                except sqlalchemy.exc.OperationalError as ex:
                    # Specific: Database connection/operational issues
                    app_manager_db_obj.close_session(
                        session_instance=del_user_management_session
                    )
                    user_management_logger.error(
                        "OperationalError occurred - database connection "
                        "issue :: %s\tLine No:: %s",
                        ex, sys.exc_info()[2].tb_lineno
                    )
                    db_err_res = EventStreamMonitorInternalServerError(
                        message="Database connection error",
                        logger_instance=user_management_logger
                    )
                    return db_err_res.send_response_to_client()
                except sqlalchemy.exc.SQLAlchemyError as ex:
                    # Specific: Other SQLAlchemy database errors
                    app_manager_db_obj.close_session(
                        session_instance=del_user_management_session
                    )
                    user_management_logger.error(
                        "SQLAlchemyError occurred :: %s\tLine No:: %s",
                        ex, sys.exc_info()[2].tb_lineno
                    )
                    db_err_res = EventStreamMonitorInternalServerError(
                        message="Database Error",
                        logger_instance=user_management_logger
                    )
                    return db_err_res.send_response_to_client()
                except Exception as ex:  # pylint: disable=broad-except
                    # Fallback: Unexpected errors
                    app_manager_db_obj.close_session(
                        session_instance=del_user_management_session
                    )
                    user_management_logger.error(
                        "Unexpected error occurred :: %s\tLine No:: %s",
                        ex, sys.exc_info()[2].tb_lineno
                    )
                    internal_err_res = EventStreamMonitorInternalServerError(
                        message="Internal Server Error",
                        logger_instance=user_management_logger,
                    )
                    return internal_err_res.send_response_to_client()
                else:
                    user_management_logger.info(
                        "Found user with the id in the db :: %s",
                        userid
                    )
                    try:
                        with del_user_management_session.begin():
                            del_user_management_session.query(
                                UsersModel
                            ).filter(
                                UsersModel.ID == userid
                            ).delete()
                    except sqlalchemy.exc.NoResultFound as ex:
                        # Specific: Query returned no results
                        app_manager_db_obj.close_session(
                            session_instance=del_user_management_session
                        )
                        user_management_logger.warning(
                            "NoResultFound occurred :: %s\tLine No:: %s",
                            ex, sys.exc_info()[2].tb_lineno
                        )
                        db_err_res = EventStreamMonitorNotFoundError(
                            message="User not found",
                            logger_instance=user_management_logger
                        )
                        return db_err_res.send_response_to_client()
                    except sqlalchemy.exc.OperationalError as ex:
                        # Specific: Database connection/operational issues
                        app_manager_db_obj.close_session(
                            session_instance=del_user_management_session
                        )
                        user_management_logger.error(
                            "OperationalError occurred - database connection "
                            "issue :: %s\tLine No:: %s",
                            ex, sys.exc_info()[2].tb_lineno
                        )
                        db_err_res = EventStreamMonitorInternalServerError(
                            message="Database connection error",
                            logger_instance=user_management_logger
                        )
                        return db_err_res.send_response_to_client()
                    except sqlalchemy.exc.SQLAlchemyError as ex:
                        # Specific: Other SQLAlchemy database errors
                        app_manager_db_obj.close_session(
                            session_instance=del_user_management_session
                        )
                        user_management_logger.error(
                            "SQLAlchemyError occurred :: %s\tLine No:: %s",
                            ex, sys.exc_info()[2].tb_lineno
                        )
                        db_err_res = EventStreamMonitorInternalServerError(
                            message="Database Error",
                            logger_instance=user_management_logger
                        )
                        return db_err_res.send_response_to_client()
                    except Exception as ex:  # pylint: disable=broad-except
                        # Fallback: Unexpected errors
                        app_manager_db_obj.close_session(
                            session_instance=del_user_management_session
                        )
                        user_management_logger.error(
                            "Unexpected error occurred :: %s\tLine No:: %s",
                            ex, sys.exc_info()[2].tb_lineno
                        )
                        internal_err_res = EventStreamMonitorInternalServerError(
                            message="Internal Server Error",
                            logger_instance=user_management_logger,
                        )
                        return internal_err_res.send_response_to_client()
                    else:
                        # Invalidate Redis cache after successful deletion
                        try:
                            # Get username and email before deletion for
                            # lookup cache invalidation
                            username = (
                                del_user_instance.Username
                                if del_user_instance else None
                            )
                            email = (
                                del_user_instance.Email
                                if del_user_instance else None
                            )

                            # Invalidate user cache
                            redis_helper.invalidate_user_cache(userid)

                            # Invalidate lookup caches if we have
                            # username/email
                            if username:
                                lookup_key_username = (
                                    f"user:lookup:username:{username}"
                                )
                                redis_helper.redis_client.delete(
                                    lookup_key_username
                                )

                            if email:
                                lookup_key_email = (
                                    f"user:lookup:email:{email}"
                                )
                                redis_helper.redis_client.delete(
                                    lookup_key_email
                                )

                            user_management_logger.info(
                                "Invalidated Redis cache for user %s "
                                "[SUCCESS]",
                                userid
                            )
                        # pylint: disable=broad-except
                        except Exception as cache_ex:
                            # Log cache error but don't fail the request
                            user_management_logger.warning(
                                "Failed to invalidate cache for user "
                                "%s: %s",
                                userid, cache_ex
                            )

                        del_usr_response = make_response("")
                        del_usr_response.headers["Cache-Control"] = "no-cache"
                        del_usr_response.status_code = 204
                        user_management_logger.info(
                            "Prepared success response and sending back to "
                            "client %s:: [SUCCESS]",
                            del_usr_response
                        )
                        app_manager_db_obj.close_session(
                            session_instance=del_user_management_session
                        )
                        return del_usr_response
            else:
                session_err_res = EventStreamMonitorInternalServerError(
                    message="Create Session Failed",
                    logger_instance=user_management_logger
                )
                return session_err_res.send_response_to_client()
    # pylint: disable=broad-except
    except Exception as ex:
        user_management_logger.error(
            "Error occurred :: %s\tLine No:: %s",
            ex, sys.exc_info()[2].tb_lineno
        )
        invalid_req_err_res = EventStreamMonitorInternalServerError(
            message="Unknown error caused",
            logger_instance=user_management_logger
        )
        return invalid_req_err_res.send_response_to_client()
