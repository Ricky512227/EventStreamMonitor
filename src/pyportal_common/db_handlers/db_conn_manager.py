# pylint: disable=line-too-long

import sys
import time
from typing import Union, Optional
import flask
import sqlalchemy.exc
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import QueuePool
from sqlalchemy import create_engine, Engine
from flask_migrate import Migrate
from sqlalchemy_utils import database_exists, create_database
from urllib.parse import quote_plus


class DataBaseConnectionHandler:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    def __init__(self, **kwargs) -> None:
        """
        Initializes the DataBaseHandler object with database connection parameters.

        Args:
            logger_instance: Logger instance for logging.
            db_driver: Database driver (e.g., "postgresql").
            db_user: Database username.
            db_ip_address: Database IP address.
            db_password: Database password.
            db_port: Database port.
            db_name: Database name.
            db_pool_size: Size of the connection pool.
            db_pool_max_overflow: Maximum overflow size of the connection pool.
            db_pool_recycle: Recycle time for connections in the pool.
            db_pool_timeout: Connection timeout for the pool.
            retry_interval: Interval between retry attempts.
            max_retries: Maximum number of retry attempts.
            base: SQLAlchemy Base object for database modeling.
        """
        self.cmn_logger = kwargs.get("logger_instance")
        self.db_driver = kwargs.get("db_driver")
        self.db_user = kwargs.get("db_user")
        self._db_password = kwargs.get("db_password")
        self._db_ip_address = kwargs.get("db_ip_address")
        self.db_port = kwargs.get("db_port")
        self.db_name = kwargs.get("db_name")
        self.base = kwargs.get("model_base")
        self._retry_interval = kwargs.get("retry_interval")
        self._max_retries = kwargs.get("max_retries")
        self._database_uri = None

    def _prepare_database_uri(self) -> Union[str, None]:
        try:
            self.cmn_logger.info(
                f"Preparing DatabaseURI for Service :: [{self.cmn_logger}]"
            )

            if (
                not self.db_driver
                or not self.db_user
                or not self.cmn_logger.name
                or not self.db_port
                or not self.db_name
            ):
                return self._database_uri
            else:
                self._database_uri = (
                    f"{self.db_driver}://{self.db_user}:{quote_plus(self._db_password)}@{self._db_ip_address}:{str(self.db_port)}"
                    f"/{self.db_name}"
                )
                self.cmn_logger.info(f"Prepared DatabaseURI for Service :: [{self.cmn_logger.name}] - {self._database_uri}")
                return self._database_uri
        except Exception as ex:
            self.cmn_logger.error(
                f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
            )
            return self._database_uri

    def create_db_engine_for_service(
        self, app_instance: flask.Flask
    ) -> tuple[object, bool]:
        try:
            _retries = 0
            while _retries < self._max_retries:
                try:
                    self.cmn_logger.info(
                        f"Creating DB-Engine using DatabaseURI for Service :: [{self.cmn_logger.name}]"
                    )
                    app_instance.config["SQLALCHEMY_DATABASE_URI"] = self._prepare_database_uri()
                    db_engine: Engine = create_engine(
                        app_instance.config["SQLALCHEMY_DATABASE_URI"]
                    )
                    self.cmn_logger.info(
                        f"Created DB-Engine using DatabaseURI for Service :: [{db_engine}]"
                    )
                    return db_engine, True
                except Exception as ex:
                    self.cmn_logger.error(
                        f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
                    )
                    self.cmn_logger.error(
                        f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
                    )
                    _retries += 1
                    if _retries < self._max_retries:
                        self.cmn_logger.info(
                            f"Retrying in {self._retry_interval} seconds..."
                        )
                        time.sleep(self._retry_interval)
                    else:
                        return None, False
        except Exception as ex:
            self.cmn_logger.error(
                f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
            )
            return None, False

    def create_database_for_service(self) -> Union[bool, None]:
        try:
            if not database_exists(self._database_uri):
                self.cmn_logger.info(
                    f"Database doesn't exists :: {self._database_uri.split('/')[-1]}"
                )
                create_database(self._database_uri)
                self.cmn_logger.info(
                    f"Created the database :: {self._database_uri.split('/')[-1]}"
                )
            else:
                self.cmn_logger.info(
                    f"Database already exists :: {self._database_uri.split('/')[-1]}"
                )
            return True
        except Exception as ex:
            self.cmn_logger.error(
                f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
            )
            self.cmn_logger.error(
                f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
            )

    def bind_db_app(self, app_instance: flask.Flask) -> Union[SQLAlchemy, None]:
        try:
            self.cmn_logger.info(
                f"Binding SQLALCHEMY  to Application Instance for Service :: [{self.cmn_logger.name}]"
            )
            app_db = SQLAlchemy(app=app_instance)
            self.cmn_logger.info(
                f"Bound SQLALCHEMY :: [{app_db}] to Application Instance for Service :: [{self.cmn_logger.name}]"
            )
            return True
        except Exception as ex:
            self.cmn_logger.error(
                f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
            )
            self.cmn_logger.error(
                f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
            )

    def migrate_db_bind_app(
        self, app_instance: flask.Flask, app_db: SQLAlchemy
    ) -> Union[Migrate, None]:
        try:
            self.cmn_logger.info(
                f"Binding the db :: [{app_db}] to app instance :: [{app_instance}] for migrations"
            )
            migrate_instance = Migrate(app_instance, app_db)
            self.cmn_logger.info(
                f"Bound the db :: [{app_db}] to app instance :: [{app_instance}] for migrations"
            )
            return migrate_instance
        except Exception as ex:
            self.cmn_logger.error(
                f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
            )
            self.cmn_logger.error(
                f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
            )

    def display_pool_info(self, connection_pool: QueuePool) -> None:
        try:
            if connection_pool:
                self.cmn_logger.info(
                    "#---------------------------------[ POOL INFO ]----------------------------------------#"
                )
                self.cmn_logger.info(
                    f"Displaying Pool Info for Service ==>[{self.cmn_logger.name}]"
                )
                self.cmn_logger.info(
                    f"Current Pool Info :: {connection_pool} - ID: {id(connection_pool)}"
                )
                self.cmn_logger.info(
                    f"Current Pool Size :: {connection_pool.size()}"
                )
                self.cmn_logger.info(
                    f"Checked Out Connections from Pool: {connection_pool.checkedin()}"
                )
                self.cmn_logger.info(
                    f"Checked in Connections available in Pool: {connection_pool.checkedout()}"
                )
                self.cmn_logger.info(
                    f"Current Pool Overflow Info: {connection_pool.overflow()}"
                )
                self.cmn_logger.info(
                    "#---------------------------------[ POOL INFO ]----------------------------------------#"
                )
        except Exception as ex:
            self.cmn_logger.error(
                f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
            )
            self.cmn_logger.error(
                f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
            )

    def check_db_connectivity_and_retry(
        self, db_engine: SQLAlchemy.engine
    ) -> Union[bool, None]:
        try:
            # Establishing the connection to the database and create a database/table if not exists
            while True:
                db_connection_status = self._check_database_connectivity(db_engine)
                if db_connection_status:
                    break
                else:
                    self.cmn_logger.info(
                        f"Going for retry .. RETRY_INTERVAL :: {self._retry_interval} sec"
                    )
                    time.sleep(self._retry_interval)
            return db_connection_status
        except Exception as ex:
            self.cmn_logger.error(
                f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
            )
            self.cmn_logger.error(
                f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
            )

    def _check_database_connectivity(
        self, db_engine: SQLAlchemy.engine
    ) -> Union[bool, None]:
        db_connection_status = False
        self.cmn_logger.info(
            f"Current Connection status set to :: {db_connection_status} for the service :: {self.cmn_logger.name}"
        )
        try:
            self.cmn_logger.info(
                "Trying to establish the connection to the database :: [IN-PROGRESS]"
            )
            db_connection = db_engine.connect()
            self.cmn_logger.info(
                "Established the connection to the database :: [SUCCESS]"
            )
            db_connection_status = True
            self.cmn_logger.info(
                f"Current Connection status set to :: {db_connection_status} for the service :: {self.cmn_logger.name}"
            )
            db_connection.close()
            self.cmn_logger.info(
                f"Closing the Current Connection as the connection was established for the service :: {self.cmn_logger.name}"
            )
        except sqlalchemy.exc.OperationalError as ex:
            self.cmn_logger.error(
                f"Current Connection status set to :: {db_connection_status}"
            )
            self.cmn_logger.error(
                f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
            )
        return db_connection_status

    def create_tables_associated_to_db_model(
        self, db_engine: SQLAlchemy.engine
    ) -> Union[bool, None]:
        connection_status = False
        try:
            self.cmn_logger.info(
                "Trying to create the tables if not present in the database..."
            )
            # Create all the tables associated with the Base class
            self.cmn_logger.info("Going to create the tables ...")
            self.base.metadata.create_all(db_engine)
            connection_status = True
            self.cmn_logger.info("Created the tables ...")
        except sqlalchemy.exc.OperationalError as ex:
            self.cmn_logger.error(
                f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
            )
        except sqlalchemy.exc.TimeoutError as ex:
            self.cmn_logger.error(
                f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
            )
        except Exception as ex:
            self.cmn_logger.error(
                f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
            )
        return connection_status
