# pylint: disable=line-too-long
import os
import sys
import concurrent.futures
from logging import Logger
from flask import Flask, Blueprint, jsonify

# Add parent directory to path for common imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from common.pyportal_common.logging_handlers.base_logger import LogMonitor
from common.pyportal_common.app_handlers.app_manager import AppHandler
from app.app_configs import init_app_configs
from app.models.task_model import TaskBase

taskprocessing_logger = None
taskprocessing_app = None
taskprocessing_grpc_server = None
taskprocessing_kafka_producer = None

try:
    service_dir = os.path.dirname(os.path.abspath(__file__))
    
    taskprocessing_req_schema_filepath = os.path.join(
        service_dir,
        "schemas/requests/create_task/"
        "req_schema.json"
    )
    taskprocessing_headers_schema_filepath = os.path.join(
        service_dir,
        "schemas/headers/"
        "task_headers_schema.json"
    )

    taskprocessing_logger: Logger = LogMonitor("taskprocessing").logger
    taskprocessing_logger.info(
        "Environment variables loaded from docker-compose"
    )
    taskprocessing_manager: AppHandler = AppHandler(
        logger_instance=taskprocessing_logger
    )
    taskprocessing_app: Flask = taskprocessing_manager.create_app_instance()
    if taskprocessing_app is None:
        taskprocessing_logger.error("App creation failed")
        sys.exit()

    init_app_configs(taskprocessing_app)
    
    # Add health check endpoint (before database initialization)
    @taskprocessing_app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'taskprocessing'
        }), 200
    
    (
        taskprocessing_headers_schema_status,
        taskprocessing_headers_schema,
    ) = taskprocessing_manager.read_json_schema(taskprocessing_headers_schema_filepath)
    (
        taskprocessing_req_schema_status,
        taskprocessing_req_schema,
    ) = taskprocessing_manager.read_json_schema(taskprocessing_req_schema_filepath)
    
    __all__ = [
        "taskprocessing_logger",
        "taskprocessing_app",
        "taskprocessing_manager",
        "app_manager_db_obj",
        "taskprocessing_headers_schema",
        "taskprocessing_req_schema",
        "taskprocessing_kafka_producer",
    ]

    taskprocessing_bp: Blueprint = (
        taskprocessing_manager.create_blueprint_instance()
    )
    if taskprocessing_bp is None:
        taskprocessing_logger.error(
            "Blue print creation failed for the App"
        )
        sys.exit()
    
    taskprocessing_app_jwt = taskprocessing_manager.bind_jwt_manger_to_app_instance(
        app_instance=taskprocessing_app
    )
    
    from common.pyportal_common.db_handlers.db_init import (
        start_database_creation_work
    )

    app_manager_db_obj = start_database_creation_work(
        taskprocessing_logger, TaskBase, taskprocessing_app
    )
    
    if app_manager_db_obj:
        taskprocessing_kafka_producer = None
        try:
            from app.kafka import (
                init_task_kafka_producer,
            )
            taskprocessing_kafka_producer = (
                init_task_kafka_producer.start_taskprocessing_kafka_producer(
                    taskprocessing_logger
                )
            )
        except Exception as ex:
            taskprocessing_logger.warning(
                f"Failed to initialize Kafka producer: {ex}"
            )

        from app.views.create_task import (
            create_task,
        )
        from app.views.get_task import (
            get_task,
        )
        from app.views.list_tasks import (
            list_tasks,
        )
        from app.views.cancel_task import (
            cancel_task,
        )

        taskprocessing_bp.route(
            "/api/v1/eventstreammonitor/tasks", methods=["POST"]
        )(create_task)
        taskprocessing_bp.route(
            "/api/v1/eventstreammonitor/tasks", methods=["GET"]
        )(list_tasks)
        taskprocessing_bp.route(
            "/api/v1/eventstreammonitor/tasks/<int:task_id>", methods=["GET"]
        )(get_task)
        taskprocessing_bp.route(
            "/api/v1/eventstreammonitor/tasks/<int:task_id>/cancel",
            methods=["PUT"]
        )(cancel_task)

        taskprocessing_manager.register_blueprint_for_service(
            app_instance=taskprocessing_app,
            blueprint_instance=taskprocessing_bp,
        )
        taskprocessing_manager.display_registered_blueprints_for_service(
            app_instance=taskprocessing_app
        )
except Exception as ex:
    print(f"Exception in __init__: {ex}")
    import traceback
    traceback.print_exc()

