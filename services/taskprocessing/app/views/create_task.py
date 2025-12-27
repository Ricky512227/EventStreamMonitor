import sys
import uuid
import sqlalchemy
from datetime import datetime
from flask import request, make_response
from app import (
    taskprocessing_logger,
    taskprocessing_manager,
    app_manager_db_obj,
    taskprocessing_kafka_producer,
    taskprocessing_headers_schema,
    taskprocessing_req_schema,
)
from app.models.task_model import TaskModel
from common.pyportal_common.error_handlers.invalid_request_handler import (
    send_invalid_request_error_to_client,
)
from common.pyportal_common.error_handlers.\
    internal_server_error_handler import (
        send_internal_server_error_to_client,
    )
from common.pyportal_common.utils import mask_request_headers


def create_task():
    """Create a new task for processing"""
    try:
        taskprocessing_logger.info(
            f"REQUEST ==> Received Endpoint: {request.endpoint}"
        )
        taskprocessing_logger.info(
            f"REQUEST ==> Received url for the request :: {request.url}"
        )

        if request.method == "POST":
            rec_req_headers = dict(request.headers)
            masked_headers = mask_request_headers(rec_req_headers)
            taskprocessing_logger.info(
                f"Received Headers from the request :: {masked_headers}"
            )

            header_result = taskprocessing_manager.generate_req_missing_params(
                rec_req_headers, taskprocessing_headers_schema
            )
            if len(header_result) > 0:
                return send_invalid_request_error_to_client(
                    app_logger_name=taskprocessing_logger,
                    message_data="Request Headers Missing",
                    err_details=header_result,
                )

            rec_req_data = request.get_json()

            body_result = taskprocessing_manager.generate_req_missing_params(
                rec_req_data, taskprocessing_req_schema
            )
            if len(body_result) > 0:
                return send_invalid_request_error_to_client(
                    app_logger_name=taskprocessing_logger,
                    message_data="Request Params Missing",
                    err_details=body_result,
                )

            user_id = rec_req_data["userId"]
            task_type = rec_req_data.get("taskType", "data_processing")
            parameters = rec_req_data.get("parameters", {})
            priority = rec_req_data.get("priority", "medium")
            valid_task_types = [
                "data_processing",
                "file_upload",
                "report_generation",
                "data_export",
                "image_processing"
            ]
            if task_type not in valid_task_types:
                return send_invalid_request_error_to_client(
                    app_logger_name=taskprocessing_logger,
                    message_data=(
                        f"Invalid task type. Must be one of: "
                        f"{', '.join(valid_task_types)}"
                    ),
                )

            taskprocessing_logger.info(
                "Creating task - Type: %s, User: %s, Priority: %s",
                task_type, user_id, priority
            )

            session = app_manager_db_obj.get_session_from_session_maker()
            if session is None:
                return send_internal_server_error_to_client(
                    app_logger_name=taskprocessing_logger,
                    message_data="Create Session Failed",
                )

            try:
                task_reference = (
                    f"TASK{datetime.now().strftime('%Y%m%d')}"
                    f"{uuid.uuid4().hex[:8].upper()}"
                )

                task = TaskModel(
                    TaskType=task_type,
                    UserID=user_id,
                    Priority=priority,
                    Parameters=parameters,
                    Status="pending",
                    TaskReference=task_reference,
                    Progress=0,
                    CreatedAt=datetime.now(),
                    UpdatedAt=datetime.now(),
                )

                session.add(task)
                session.flush()
                task_id = task.ID
                session.commit()

                taskprocessing_logger.info(
                    "Task created successfully: %s (ID: %s)",
                    task_reference, task_id
                )

                if taskprocessing_kafka_producer:
                    try:
                        task_event = {
                            "eventType": "task_created",
                            "taskId": task_id,
                            "taskReference": task_reference,
                            "taskType": task_type,
                            "userId": user_id,
                            "priority": priority,
                            "timestamp": datetime.now().isoformat(),
                        }
                        taskprocessing_kafka_producer.publish_data_to_producer(
                            task_event
                        )
                        taskprocessing_logger.info(
                            "Published task_created event to Kafka: %s",
                            task_reference
                        )
                    # pylint: disable=broad-except
                    except Exception as kafka_ex:
                        taskprocessing_logger.warning(
                            f"Failed to publish to Kafka: {kafka_ex}"
                        )

                response_data = {
                    "task": {
                        "taskId": task_id,
                        "taskReference": task_reference,
                        "taskType": task_type,
                        "userId": user_id,
                        "priority": priority,
                        "status": "pending",
                        "progress": 0,
                        "createdAt": str(task.CreatedAt),
                    }
                }

                reg_task_response = make_response(response_data)
                reg_task_response.headers["Content-Type"] = "application/json"
                reg_task_response.headers["Cache-Control"] = "no-cache"
                reg_task_response.status_code = 201

                app_manager_db_obj.close_session(session_instance=session)
                return reg_task_response

            except sqlalchemy.exc.OperationalError as ex:
                # Specific: Database connection/operational issues
                session.rollback()
                app_manager_db_obj.close_session(session_instance=session)
                taskprocessing_logger.error(
                    f"OperationalError occurred - database connection "
                    f"issue :: {ex}\tLine No:: "
                    f"{sys.exc_info()[2].tb_lineno}"
                )
                return send_internal_server_error_to_client(
                    app_logger_name=taskprocessing_logger,
                    message_data="Database connection error",
                )
            except sqlalchemy.exc.SQLAlchemyError as ex:
                # Specific: Other SQLAlchemy database errors
                session.rollback()
                app_manager_db_obj.close_session(session_instance=session)
                taskprocessing_logger.error(
                    f"SQLAlchemyError occurred :: {ex}\tLine No:: "
                    f"{sys.exc_info()[2].tb_lineno}"
                )
                return send_internal_server_error_to_client(
                    app_logger_name=taskprocessing_logger,
                    message_data="Database Error",
                )
            except Exception as ex:  # pylint: disable=broad-except
                # Fallback: Unexpected errors
                session.rollback()
                app_manager_db_obj.close_session(session_instance=session)
                taskprocessing_logger.error(
                    f"Unexpected error occurred :: {ex}\tLine No:: "
                    f"{sys.exc_info()[2].tb_lineno}"
                )
                return send_internal_server_error_to_client(
                    app_logger_name=taskprocessing_logger,
                    message_data="Database Error",
                )

    except ValueError as ex:
        # Specific: Validation errors
        taskprocessing_logger.warning(
            f"Validation error occurred :: {ex}\tLine No:: "
            f"{sys.exc_info()[2].tb_lineno}"
        )
        return send_invalid_request_error_to_client(
            app_logger_name=taskprocessing_logger,
            message_data=str(ex),
        )
    except Exception as ex:  # pylint: disable=broad-except
        # Fallback: Unexpected errors
        taskprocessing_logger.exception(
            f"Unexpected error occurred :: {ex}\tLine No:: "
            f"{sys.exc_info()[2].tb_lineno}"
        )
        return send_internal_server_error_to_client(
            app_logger_name=taskprocessing_logger,
            message_data="Unknown error caused",
        )
