import sys
from flask import request, make_response
from app import (
    taskprocessing_logger,
    app_manager_db_obj,
)
from app.models.task_model import TaskModel
from common.pyportal_common.error_handlers.internal_server_error_handler import (
    send_internal_server_error_to_client,
)


def list_tasks():
    try:
        taskprocessing_logger.info(
            f"REQUEST ==> List tasks"
        )
        
        status = request.args.get('status')
        task_type = request.args.get('taskType')
        user_id = request.args.get('userId', type=int)
        limit = request.args.get('limit', default=50, type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        taskprocessing_logger.info(
            f"List tasks filters - status: {status}, taskType: {task_type}, "
            f"userId: {user_id}, limit: {limit}, offset: {offset}"
        )
        
        session = app_manager_db_obj.get_session_from_session_maker()
        if session is None:
            return send_internal_server_error_to_client(
                app_logger_name=taskprocessing_logger,
                message_data="Create Session Failed",
            )

        try:
            query = session.query(TaskModel)
            
            if status:
                query = query.filter(TaskModel.Status == status)
            if task_type:
                query = query.filter(TaskModel.TaskType == task_type)
            if user_id:
                query = query.filter(TaskModel.UserID == user_id)
            
            query = query.order_by(TaskModel.CreatedAt.desc())
            total_count = query.count()
            tasks = query.offset(offset).limit(limit).all()

            tasks_list = []
            for task in tasks:
                tasks_list.append({
                    "taskId": task.ID,
                    "taskReference": task.TaskReference,
                    "taskType": task.TaskType,
                    "userId": task.UserID,
                    "status": task.Status,
                    "priority": task.Priority,
                    "progress": task.Progress,
                    "createdAt": str(task.CreatedAt),
                    "completedAt": str(task.CompletedAt) if task.CompletedAt else None,
                })

            response_data = {
                "tasks": tasks_list,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "hasMore": (offset + limit) < total_count
                }
            }

            response = make_response(response_data)
            response.headers["Content-Type"] = "application/json"
            response.status_code = 200

            taskprocessing_logger.info(
                f"Listed {len(tasks_list)} tasks (total: {total_count})"
            )

            app_manager_db_obj.close_session(session_instance=session)
            return response

        except Exception as ex:
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

