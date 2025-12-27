import sys
import sqlalchemy
from flask import make_response
from app import (
    taskprocessing_logger,
    app_manager_db_obj,
)
from app.models.task_model import TaskModel
from common.pyportal_common.error_handlers.not_found_error_handler import (
    send_notfound_request_error_to_client,
)
from common.pyportal_common.error_handlers.\
    internal_server_error_handler import (
        send_internal_server_error_to_client,
    )


def get_task(task_id):
    try:
        taskprocessing_logger.info(
            f"REQUEST ==> Get task: {task_id}"
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
                    "processingTime": (
                        float(task.ProcessingTime)
                        if task.ProcessingTime else None
                    ),
                    "createdAt": str(task.CreatedAt),
                    "startedAt": (
                        str(task.StartedAt) if task.StartedAt else None
                    ),
                    "completedAt": (
                        str(task.CompletedAt) if task.CompletedAt else None
                    ),
                    "updatedAt": str(task.UpdatedAt),
                }
            }

            response = make_response(response_data)
            response.headers["Content-Type"] = "application/json"
            response.status_code = 200

            app_manager_db_obj.close_session(session_instance=session)
            return response

        except sqlalchemy.exc.OperationalError as ex:
            # Specific: Database connection/operational issues
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
            app_manager_db_obj.close_session(session_instance=session)
            taskprocessing_logger.error(
                f"Unexpected error occurred :: {ex}\tLine No:: "
                f"{sys.exc_info()[2].tb_lineno}"
            )
            return send_internal_server_error_to_client(
                app_logger_name=taskprocessing_logger,
                message_data="Database Error",
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

