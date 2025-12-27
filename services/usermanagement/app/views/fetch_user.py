import sys
import sqlalchemy.exc
from flask import request, make_response
from usermanagement_service.users.request_handlers.user import User
from app.models.user_model import UsersModel
from app import (
    user_management_logger,
    getuser_headers_schema,
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
from common.pyportal_common.error_handlers.not_found_error_handler import (
    EventStreamMonitorNotFoundError,
)
from common.pyportal_common.utils import mask_request_headers


def get_user_info(userid):
    try:
        user_management_logger.info(
            "REQUEST ==> Received Endpoint for the request:: %s",
            request.endpoint
        )
        user_management_logger.info(
            "REQUEST ==> Received url for the request :: %s",
            request.url
        )
        if request.method == "GET":
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
            get_header_result = usermanager.generate_req_missing_params(
                rec_req_headers, getuser_headers_schema
            )
            if len(get_header_result.keys()) != 0:
                invalid_header_err_res = EventStreamMonitorInvalidRequestError(
                    message="Request Headers Missing",
                    error_details=get_header_result,
                    logger_instance=user_management_logger,
                )
                return invalid_header_err_res.send_response_to_client()
            # Initialize Redis helper for caching
            redis_helper = UserManagementRedisHelper()
            # Try to get user from cache first (Cache-Aside pattern)
            cached_user = redis_helper.get_cached_user(userid)
            if cached_user:
                user_management_logger.info(
                    "User %s retrieved from Redis cache [CACHE HIT]",
                    userid
                )
                # Reconstruct the format expected by
                # generate_custom_response_body
                # Cached data is the "data" dict, need to wrap it in
                # the same format
                get_user_instance = {
                    "data": cached_user,
                    "message": ""
                }
                # Generate response from cached data
                custom_user_response_body = User.generate_custom_response_body(
                    user_instance=get_user_instance,
                    messagedata="Retrieved User"
                )
                if len(custom_user_response_body.keys()) <= 0:
                    invalid_req_err_res = (
                        EventStreamMonitorInternalServerError(
                            message="Get User Response creation Failed",
                            logger_instance=user_management_logger,
                        )
                    )
                    return invalid_req_err_res.send_response_to_client()
                get_usr_response = make_response(custom_user_response_body)
                get_usr_response.headers["Content-Type"] = "application/json"
                get_usr_response.headers["Cache-Control"] = "no-cache"
                get_usr_response.status_code = 200
                user_management_logger.info(
                    "Prepared success response from cache and sending "
                    "back to client [SUCCESS]"
                )
                return get_usr_response
            # Cache miss - retrieve from database
            user_management_logger.info(
                "User %s not found in cache, querying database "
                "[CACHE MISS]",
                userid
            )
            # Retrieve the user logic.
            get_user_management_session = (
                app_manager_db_obj.get_session_from_session_maker()
            )
            if get_user_management_session is None:
                session_err_res = EventStreamMonitorInternalServerError(
                    message="Create Session Failed",
                    logger_instance=user_management_logger
                )
                return session_err_res.send_response_to_client()
            # IF the created session is not active, send the response
            # back to client as internal error
            if get_user_management_session.is_active:
                try:
                    # Steps:
                    # 1. Fetching the user record from the database using
                    #    the primary key userid
                    # 2. Converting the database model of user to defined
                    #    user and serialize to json
                    # 3. Using the serialize, Generating the success custom
                    #    response, headers
                    # 4. Caching the user data in Redis for future requests
                    get_user_instance = get_user_management_session.query(
                        UsersModel
                    ).get(userid)
                    if get_user_instance is None:
                        usr_not_found_err_res = (
                            EventStreamMonitorNotFoundError(
                                message="Retrieved user doesn't exists",
                                logger_instance=user_management_logger,
                            )
                        )
                        return usr_not_found_err_res.send_response_to_client()
                except sqlalchemy.exc.NoResultFound as ex:
                    # Specific: Query returned no results
                    app_manager_db_obj.close_session(
                        session_instance=get_user_management_session
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
                        session_instance=get_user_management_session
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
                        session_instance=get_user_management_session
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
                        session_instance=get_user_management_session
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
                    get_user_instance = User.convert_db_model_to_resp(
                        get_user_instance
                    )
                    if len(get_user_instance.keys()) <= 0:
                        invalid_req_err_res = (
                            EventStreamMonitorInternalServerError(
                                message="Get User Response creation Failed",
                                logger_instance=user_management_logger,
                            )
                        )
                        app_manager_db_obj.close_session(
                            session_instance=get_user_management_session
                        )
                        return invalid_req_err_res.send_response_to_client()
                    # Cache the user data in Redis for future requests
                    # (TTL: 1 hour)
                    try:
                        # Extract user data for caching
                        # (convert to dict format)
                        user_data_for_cache = get_user_instance.get("data", {})
                        if user_data_for_cache:
                            redis_helper.cache_user(
                                user_id=userid,
                                user_data=user_data_for_cache,
                                ttl=3600  # 1 hour TTL
                            )
                            user_management_logger.info(
                                "User %s cached in Redis [SUCCESS]",
                                userid
                            )
                    # pylint: disable=broad-except
                    except Exception as cache_ex:
                        # Log cache error but don't fail the request
                        user_management_logger.warning(
                            "Failed to cache user %s in Redis: %s",
                            userid, cache_ex
                        )
                    custom_user_response_body = (
                        User.generate_custom_response_body(
                            user_instance=get_user_instance,
                            messagedata="Retrieved User"
                        )
                    )
                    if len(custom_user_response_body.keys()) <= 0:
                        invalid_req_err_res = (
                            EventStreamMonitorInternalServerError(
                                message="Get User success Response "
                                        "creation Failed",
                                logger_instance=user_management_logger,
                            )
                        )
                        app_manager_db_obj.close_session(
                            session_instance=get_user_management_session
                        )
                        return invalid_req_err_res.send_response_to_client()
                    get_usr_response = make_response(custom_user_response_body)
                    get_usr_response.headers["Content-Type"] = (
                        "application/json"
                    )
                    get_usr_response.headers["Cache-Control"] = "no-cache"
                    get_usr_response.status_code = 200
                    user_management_logger.info(
                        "Prepared success response and sending back to "
                        "client %s:: [SUCCESS]",
                        get_usr_response
                    )
                    app_manager_db_obj.close_session(
                        session_instance=get_user_management_session
                    )
                    return get_usr_response
            else:
                invalid_req_err_res = (
                    EventStreamMonitorInternalServerError(
                        message="Create Session Failed",
                        logger_instance=user_management_logger
                    )
                )
                return invalid_req_err_res.send_response_to_client()

    except Exception as ex:  # pylint: disable=broad-except
        user_management_logger.error(
            "Error occurred :: %s\tLine No:: %s",
            ex, sys.exc_info()[2].tb_lineno
        )
        invalid_req_err_res = EventStreamMonitorInternalServerError(
            message="Unknown error caused",
            logger_instance=user_management_logger
        )
        return invalid_req_err_res.send_response_to_client()
