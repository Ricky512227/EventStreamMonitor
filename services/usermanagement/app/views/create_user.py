import sys
from typing import Union, Any, Optional

import sqlalchemy.orm.exc
from flask import request, make_response

from app.users.request_handlers.user import User
from app import (
    user_management_logger,
    req_headers_schema,
    reg_user_req_schema,
    usermanager,
    app_manager_db_obj
)
from common.pyportal_common.error_handlers.invalid_request_handler import (
    send_invalid_request_error_to_client,
)
from common.pyportal_common.error_handlers.internal_server_error_handler import (
    send_internal_server_error_to_client,
)
from app.utils.util_helpers import (
    is_username_email_already_exists_in_db,
    convert_db_model_to_resp,
)
from app.users.response_handlers.create_user_success_response import generate_success_response


def register_user():
    try:
        user_management_logger.info(
            f"REQUEST ==> Received Endpoint: {request.endpoint}"
        )
        user_management_logger.info(
            f"REQUEST ==> Received url for the request :: {request.url}"
        )
        if request.method == "POST":
            rec_req_headers = dict(request.headers)
            user_management_logger.info(
                f"Received Headers from the request :: {rec_req_headers}"
            )
            """
                1. Find the missing headers, any schema related issue related to headers in the request
                2. If any missing headers or schema related issue, send the error response back to client.
                3. Custom error response contains the information about headers related to missing/schema issue, with status code as 400,BAD_REQUEST
            """
            reg_header_result = usermanager.generate_req_missing_params(
                rec_req_headers, req_headers_schema
            )
            if len(reg_header_result) > 0:
                return send_invalid_request_error_to_client(
                    app_logger_name=user_management_logger,
                    message_data="Request Headers Missing",
                    err_details=reg_header_result,
                )

            rec_req_data = request.get_json()
            """
                1. Find the missing params, any schema related issue related
                   to params in the request body
                2. If any missing params or schema related issue, send the
                   error response back to client.
                3. Custom error response contains the information about params
                   related to missing/schema issue, with status code as
                   400,BAD_REQUEST
            """
            # Commented out validation - uncomment if needed
            # body_result = usermanager.generate_req_missing_params(
            #     rec_req_data, reg_user_req_schema
            # )
            # if len(body_result) > 0:
            #     return send_invalid_request_error_to_client(
            #         app_logger_name=user_management_logger,
            #         message_data="Request Params Missing",
            #         err_details=body_result,
            # )

            # Read the content which was received in the request
            username = rec_req_data["username"]
            firstname = rec_req_data["firstName"]
            lastname = rec_req_data["lastName"]
            emailaddress = rec_req_data["email"]
            password = rec_req_data["password"]
            dateofbirth = rec_req_data["dateOfBirth"]
            user_management_logger.info("Processing request data... [STARTED]")
            session_to_validate_existing_user = (
                app_manager_db_obj.get_session_from_session_maker()
            )
            if session_to_validate_existing_user is None:
                return send_internal_server_error_to_client(
                    app_logger_name=user_management_logger,
                    message_data="Create Session Failed",
                )
            # Doing the pre-validation checks before procession the request.
            user_exists_result = is_username_email_already_exists_in_db(
                session_instance=session_to_validate_existing_user,
                uname=username,
                email=emailaddress,
            )
            if user_exists_result is None:
                app_manager_db_obj.close_session(
                    session_instance=session_to_validate_existing_user
                )
                return send_internal_server_error_to_client(
                    app_logger_name=user_management_logger,
                    message_data="Db error"
                )
            if user_exists_result:
                app_manager_db_obj.close_session(
                    session_instance=session_to_validate_existing_user
                )
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
                session_to_create_new_user = (
                    app_manager_db_obj.get_session_from_session_maker()
                )
                if session_to_create_new_user is None:
                    return send_internal_server_error_to_client(
                        app_logger_name=user_management_logger,
                        message_data="Create Session Failed",
                    )
                
                try:
                    user_db_record_to_insert = user_obj.map_user_instance_to_db_model()
                    if user_db_record_to_insert is None:
                        app_manager_db_obj.close_session(
                            session_instance=session_to_create_new_user
                        )
                        return send_internal_server_error_to_client(
                            app_logger_name=user_management_logger,
                            message_data="User DB - Instance mapping Failed",
                        )
                    
                    user_management_logger.info(
                        f"Data adding into DataBase session "
                        f"{user_db_record_to_insert}:: [STARTED]"
                    )
                    
                    # Add object to session and flush to get the ID
                    session_to_create_new_user.add(user_db_record_to_insert)
                    session_to_create_new_user.flush()  # Flush to get the ID
                    
                    # Get ID and timestamps before commit
                    user_id = user_db_record_to_insert.ID
                    created_at = user_db_record_to_insert.CreatedAt
                    updated_at = user_db_record_to_insert.UpdatedAt
                    locationheader = request.url + "/" + str(user_id)
                    
                    # Commit the transaction
                    session_to_create_new_user.commit()
                    
                    user_management_logger.info(
                        f"Data added and committed to DataBase "
                        f"(ID: {user_id}):: [SUCCESS]"
                    )
                    
                    # Publish user registration event to Kafka
                    from app import (
                        user_management_kafka_producer,
                    )
                    if user_management_kafka_producer:
                        try:
                            registration_event = {
                                "eventType": "user_registered",
                                "userId": user_id,
                                "username": user_instance["username"],
                                "email": user_instance["email"],
                                "firstName": user_instance["firstname"],
                                "lastName": user_instance["lastname"],
                                "timestamp": str(created_at),
                            }
                            user_management_kafka_producer.publish_data_to_producer(
                                registration_event
                            )
                            user_management_logger.info(
                                f"Published user registration event to Kafka: "
                                f"{user_instance['username']}"
                            )
                        except Exception as kafka_ex:
                            user_management_logger.warning(
                                f"Failed to publish to Kafka: {kafka_ex}"
                            )
                    
                    # Convert to the format expected by generate_success_response
                    # The function expects a dict with 'data' key containing model fields
                    # Convert datetime objects to strings for JSON serialization
                    response_user_data = {
                        "data": {
                            "ID": user_id,
                            "Username": user_instance["username"],
                            "Email": user_instance["email"],
                            "DateOfBirth": user_instance["dateofbirth"],
                            "FirstName": user_instance["firstname"],
                            "LastName": user_instance["lastname"],
                            "CreatedAt": str(created_at) if created_at else user_instance["created_at"],
                            "UpdatedAt": str(updated_at) if updated_at else user_instance["updated_at"]
                        }
                    }
                    
                    try:
                        custom_user_response_body = generate_success_response(
                            response_user_data
                        )
                        if not custom_user_response_body or len(custom_user_response_body) == 0:
                            app_manager_db_obj.close_session(
                                session_instance=session_to_create_new_user
                            )
                            return send_internal_server_error_to_client(
                                app_logger_name=user_management_logger,
                                message_data="User success Response creation Failed",
                            )
                        
                        # Parse JSON string to dict for make_response
                        import json
                        try:
                            response_dict = json.loads(custom_user_response_body)
                        except json.JSONDecodeError:
                            # If it's already a dict, use it directly
                            response_dict = custom_user_response_body
                        
                        reg_usr_response = make_response(response_dict)
                        reg_usr_response.headers["Content-Type"] = "application/json"
                        reg_usr_response.headers["Cache-Control"] = "no-cache"
                        reg_usr_response.headers["location"] = locationheader
                        reg_usr_response.status_code = 201
                    except Exception as resp_ex:
                        app_manager_db_obj.close_session(
                            session_instance=session_to_create_new_user
                        )
                        user_management_logger.exception(
                            f"Error creating response :: {resp_ex}\t"
                            f"Line No:: {sys.exc_info()[2].tb_lineno}"
                        )
                        return send_internal_server_error_to_client(
                            app_logger_name=user_management_logger,
                            message_data="Response creation failed",
                        )
                    
                    user_management_logger.info(
                        f"Prepared success response and sending back to client "
                        f"{reg_usr_response}:: [SUCCESS]"
                    )
                    
                    # Close session after successful commit
                    app_manager_db_obj.close_session(
                        session_instance=session_to_create_new_user
                    )
                    return reg_usr_response
                    
                except sqlalchemy.exc.IntegrityError as ex:
                    app_manager_db_obj.close_session(
                        session_instance=session_to_create_new_user
                    )
                    user_management_logger.error(
                        f"IntegrityError occurred :: {ex}\t"
                        f"Line No:: {sys.exc_info()[2].tb_lineno}"
                    )
                    return send_invalid_request_error_to_client(
                        app_logger_name=user_management_logger,
                        message_data="User already exists",
                    )
                except Exception as ex:
                    app_manager_db_obj.close_session(
                        session_instance=session_to_create_new_user
                    )
                    user_management_logger.error(
                        f"Error occurred :: {ex}\t"
                        f"Line No:: {sys.exc_info()[2].tb_lineno}"
                    )
                    return send_internal_server_error_to_client(
                        app_logger_name=user_management_logger,
                        message_data="Database Error",
                    )
            except Exception as ex:
                user_management_logger.error(
                    f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
                )
                return send_internal_server_error_to_client(
                    app_logger_name=user_management_logger,
                    message_data="Unknown error caused",
                )
    except Exception as ex:
        return send_internal_server_error_to_client(
            app_logger_name=user_management_logger, message_data="Unknown error caused"
        )
