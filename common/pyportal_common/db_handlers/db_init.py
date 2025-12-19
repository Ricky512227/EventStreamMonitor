import os
from src.pyportal_common.db_handlers.db_pool_manager import DataBasePoolHandler

SERVICE_NAME = os.environ.get("SERVICE_NAME")
DB_DRIVER_NAME = os.environ.get("DB_DRIVER_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_IPADDRESS = os.environ.get("DB_IPADDRESS")
DB_PORT = int(os.environ.get("DB_PORT"))
DB_NAME = os.environ.get("DB_NAME")
POOL_SIZE = int(os.environ.get("POOL_SIZE"))
MAX_OVERFLOW = int(os.environ.get("MAX_OVERFLOW"))
POOL_RECYCLE = int(os.environ.get("POOL_RECYCLE"))
POOL_TIMEOUT = int(os.environ.get("POOL_TIMEOUT"))
RETRY_INTERVAL = int(os.environ.get("RETRY_INTERVAL"))
MAX_RETRIES = int(os.environ.get("MAX_RETRIES"))


def start_database_creation_work(cmn_logger, base, app_specific_flask_instance):
    app_manager_db_obj: DataBasePoolHandler = DataBasePoolHandler(
        logger_instance=cmn_logger,
        db_driver=DB_DRIVER_NAME,
        db_user=DB_USER,
        db_ip_address=DB_IPADDRESS,
        db_password=DB_PASSWORD,
        db_port=DB_PORT,
        db_name=DB_NAME,
        db_pool_size=POOL_SIZE,
        db_pool_max_overflow=MAX_OVERFLOW,
        db_pool_recycle=POOL_RECYCLE,
        db_pool_timeout=POOL_TIMEOUT,
        retry_interval=RETRY_INTERVAL,
        max_retries=MAX_RETRIES,
        model_base=base,
    )
    # Create a database engine
    app_db_engine, is_engine_created = app_manager_db_obj.create_db_engine_for_service(
        app_instance=app_specific_flask_instance
    )
    # If the engine doesn't create, then go for retry  of max_retries=3 with retry_delay=5.
    if is_engine_created:
        # If the engine is created then check the connection for the status of th db.
        if app_manager_db_obj.check_db_connectivity_and_retry(db_engine=app_db_engine):
            # If the connection  health is connected, then initialise the database for the particular service.
            if app_manager_db_obj.create_database_for_service():
                # If the connection  health is connected, then create the tables for the services which was defined in the models.
                if app_manager_db_obj.create_tables_associated_to_db_model(
                    db_engine=app_db_engine
                ):
                    # Bind the application with the sqlAlchemy.
                    app_db_sql_alchemy = app_manager_db_obj.bind_db_app(
                        app_instance=app_specific_flask_instance
                    )
                    # Bind the application with the migrations
                    app_manager_db_obj.migrate_db_bind_app(
                        app_instance=app_specific_flask_instance,
                        app_db=app_db_sql_alchemy,
                    )
                    # Initialize/Create a pool of connections for the service
                    app_db_connection_pool = (
                        app_manager_db_obj.create_pool_of_connections(
                            db_engine=app_db_engine
                        )
                    )
                    app_manager_db_obj.create_session_maker_bind_to_db_engine(app_db_engine, app_db_connection_pool, )
                    # app_db_session_maker = (
                    #     app_manager_db_obj.create_session_maker_to_connection_pool(
                    #         db_engine=app_db_engine,
                    #         connection_pool=app_db_connection_pool,
                    #     )
                    # )
                    # Display the  pool of connections for the service which was initialized
                    # app_manager_db_obj.display_pool_info(
                    #     connection_pool=app_db_connection_pool
                    # )
                    return app_manager_db_obj
