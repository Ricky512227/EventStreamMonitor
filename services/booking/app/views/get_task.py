import sys
from flask import make_response
from app import (
    booking_logger,
    app_manager_db_obj,
)
from common.pyportal_common.error_handlers.not_found_error_handler import (
    send_notfound_request_error_to_client,
)
from common.pyportal_common.error_handlers.internal_server_error_handler import (
    send_internal_server_error_to_client,
)
from app.models.task_model import TaskModel


def get_task(task_id):
    try:
        booking_logger.info(
            f"REQUEST ==> Get task: {task_id}"
        )
        
        session = app_manager_db_obj.get_session_from_session_maker()
        if session is None:
            return send_internal_server_error_to_client(
                app_logger_name=booking_logger,
                message_data="Create Session Failed",
            )

        try:
            task = session.query(TaskModel).filter(
                TaskModel.ID == task_id
            ).first()

            if not task:
                app_manager_db_obj.close_session(session_instance=session)
                return send_notfound_request_error_to_client(
                    app_logger_name=booking_logger,
                    message_data="Task not found",
                )

            response_data = {
                "task": {
                    "taskId": task.ID,
                    "taskReference": task.TaskReference,
                    "taskType": task.TaskType,
                    "userId": task.UserID,
                    "status": task.Status,
                    "priority": task.Priority,
                    "progress": task.Progress,
                    "parameters": task.Parameters,
                    "result": task.Result,
                    "errorMessage": task.ErrorMessage,
                    "processingTime": float(task.ProcessingTime) if task.ProcessingTime else None,
                    "createdAt": str(task.CreatedAt),
                    "startedAt": str(task.StartedAt) if task.StartedAt else None,
                    "completedAt": str(task.CompletedAt) if task.CompletedAt else None,
                    "updatedAt": str(task.UpdatedAt),
                }
            }

            response = make_response(response_data)
            response.headers["Content-Type"] = "application/json"
            response.status_code = 200

            app_manager_db_obj.close_session(session_instance=session)
            return response

        except Exception as ex:
            app_manager_db_obj.close_session(session_instance=session)
            booking_logger.error(
                f"Error occurred :: {ex}\t"
                f"Line No:: {sys.exc_info()[2].tb_lineno}"
            )
            return send_internal_server_error_to_client(
                app_logger_name=booking_logger,
                message_data="Database Error",
            )

    except Exception as ex:
        booking_logger.exception(
            f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
        )
        return send_internal_server_error_to_client(
            app_logger_name=booking_logger,
            message_data="Unknown error caused",
        )

