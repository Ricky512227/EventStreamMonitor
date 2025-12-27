import sys
from datetime import datetime
from flask import make_response
from app import (
    taskprocessing_logger,
    app_manager_db_obj,
    taskprocessing_kafka_producer,
)
from app.models.task_model import TaskModel
from common.pyportal_common.error_handlers.not_found_error_handler import (
    send_notfound_request_error_to_client,
)
from common.pyportal_common.error_handlers.invalid_request_handler import (
    send_invalid_request_error_to_client,
)
from common.pyportal_common.error_handlers.internal_server_error_handler import (
    send_internal_server_error_to_client,
)


def cancel_task(task_id):
    try:
        taskprocessing_logger.info(
            f"REQUEST ==> Cancel task: {task_id}"
        )
        
        session = app_manager_db_obj.get_session_from_session_maker()
        if session is None:
            return send_internal_server_error_to_client(
                app_logger_name=taskprocessing_logger,
                message_data="Create Session Failed",
            )

        try:
            task = session.query(TaskModel).filter(
                TaskModel.ID == task_id
            ).first()

            if not task:
                app_manager_db_obj.close_session(session_instance=session)
                return send_notfound_request_error_to_client(
                    app_logger_name=taskprocessing_logger,
                    message_data="Task not found",
                )

            if task.Status == "cancelled":
                app_manager_db_obj.close_session(session_instance=session)
                return send_invalid_request_error_to_client(
                    app_logger_name=taskprocessing_logger,
                    message_data="Task already cancelled",
                )
            
            if task.Status == "completed":
                app_manager_db_obj.close_session(session_instance=session)
                return send_invalid_request_error_to_client(
                    app_logger_name=taskprocessing_logger,
                    message_data="Cannot cancel completed task",
                )
            
            if task.Status == "failed":
                app_manager_db_obj.close_session(session_instance=session)
                return send_invalid_request_error_to_client(
                    app_logger_name=taskprocessing_logger,
                    message_data="Cannot cancel failed task",
                )

            old_status = task.Status
            task.Status = "cancelled"
            task.UpdatedAt = datetime.now()
            task.CompletedAt = datetime.now()
            session.commit()

            taskprocessing_logger.info(
                f"Task cancelled successfully: {task.TaskReference} "
                f"(was: {old_status})"
            )

            if taskprocessing_kafka_producer:
                try:
                    cancel_event = {
                        "eventType": "task_cancelled",
                        "taskId": task.ID,
                        "taskReference": task.TaskReference,
                        "taskType": task.TaskType,
                        "userId": task.UserID,
                        "previousStatus": old_status,
                        "timestamp": datetime.now().isoformat(),
                    }
                    taskprocessing_kafka_producer.publish_data_to_producer(
                        cancel_event
                    )
                    taskprocessing_logger.info(
                        f"Published task_cancelled event to Kafka: "
                        f"{task.TaskReference}"
                    )
                except Exception as kafka_ex:
                    taskprocessing_logger.warning(
                        f"Failed to publish to Kafka: {kafka_ex}"
                    )

            response_data = {
                "task": {
                    "taskId": task.ID,
                    "taskReference": task.TaskReference,
                    "status": "cancelled",
                    "message": "Task cancelled successfully",
                }
            }

            response = make_response(response_data)
            response.headers["Content-Type"] = "application/json"
            response.status_code = 200

            app_manager_db_obj.close_session(session_instance=session)
            return response

        except Exception as ex:
            session.rollback()
            app_manager_db_obj.close_session(session_instance=session)
            taskprocessing_logger.error(
                f"Error occurred :: {ex}\t"
                f"Line No:: {sys.exc_info()[2].tb_lineno}"
            )
            return send_internal_server_error_to_client(
                app_logger_name=taskprocessing_logger,
                message_data="Database Error",
            )

    except Exception as ex:
        taskprocessing_logger.exception(
            f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
        )
        return send_internal_server_error_to_client(
            app_logger_name=taskprocessing_logger,
            message_data="Unknown error caused",
        )

