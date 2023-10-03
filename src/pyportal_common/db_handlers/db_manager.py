import sys
import time
from typing import Union
import flask
import sqlalchemy.exc
from sqlalchemy.pool import QueuePool
from sqlalchemy import create_engine
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus


class DataBaseHandler:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    def __init__(self, logger_instance, db_driver, db_user, db_ip_address, db_password, db_port, db_name, db_pool_size,
                 db_pool_max_overflow, db_pool_recycle, db_pool_timeout, retry_interval, max_retries, base) -> None:
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
        self.cmn_logger = logger_instance
        self.db_driver = db_driver
        self.db_user = db_user
        self.db_password = db_password
        self.db_ip_address = db_ip_address
        self.db_port = db_port
        self.db_name = db_name
        self.db_pool_size = db_pool_size
        self.db_pool_recycle = db_pool_recycle
        self.db_pool_timeout = db_pool_timeout
        self.db_pool_max_overflow = db_pool_max_overflow
        self.base = base
        self.retry_interval = retry_interval
        self.max_retries = max_retries

        # Log all parameters
        for key, value in vars(self).items():
            self.cmn_logger.info(f"Initialized {key} with value: {value}")

    def get_database_uri(self) -> str:
        try:
            self.cmn_logger.info("Preparing DatabaseURI for Service :: [{0}]  ::".format(self.cmn_logger.name))
            database_uri = self.db_driver + "://" + self.db_user + ":" + quote_plus(self.db_password) + "@" + self.db_ip_address + ":" + str(self.db_port) + "/" + self.db_name
            self.cmn_logger.info("Prepared DatabaseURI for Service :: [{0}] - {1} ::".format(self.cmn_logger.name, database_uri))
            return database_uri
        except Exception as ex:
            self.cmn_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

    def create_db_engine_for_service(self, app_instance: flask.Flask) -> tuple[object, bool]:
        try:
            retries = 0
            while retries < self.max_retries:
                try:
                    self.cmn_logger.info("Creating DB-Engine using DatabaseURI for Service :: [{0}]".format(self.cmn_logger.name))
                    app_instance.config['SQLALCHEMY_DATABASE_URI'] = self.get_database_uri()
                    db_engine = create_engine(app_instance.config['SQLALCHEMY_DATABASE_URI'])
                    self.cmn_logger.info("Created DB-Engine using DatabaseURI for Service :: [{0}]".format(db_engine))
                    return db_engine, True
                except Exception as ex:
                    print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
                    self.cmn_logger.error(
                        "Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
                    retries += 1
                    if retries < self.max_retries:
                        self.cmn_logger.info(f"Retrying in {self.retry_interval} seconds...")
                        time.sleep(self.retry_interval)
                    else:
                        return None, False
        except Exception as ex:
            self.cmn_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            return None, False

    def create_database_for_service(self) -> Union[bool, None]:
        try:
            if not database_exists(self.get_database_uri()):
                self.cmn_logger.info("Database doesn't exists :: {0}".format(self.get_database_uri().split("/")[-1]))
                create_database(self.get_database_uri())
                self.cmn_logger.info("Created the database :: {0}".format(self.get_database_uri().split("/")[-1]))
            else:
                self.cmn_logger.info("Database already exists :: {0}".format(self.get_database_uri().split("/")[-1]))
            return True
        except Exception as ex:
            self.cmn_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

    def bind_db_app(self, app_instance: flask.Flask) -> Union[SQLAlchemy, None]:
        try:
            self.cmn_logger.info("Binding SQLALCHEMY  to Application Instance for Service :: [{0}]".format(self.cmn_logger.name))
            app_db = SQLAlchemy(app=app_instance)
            self.cmn_logger.info("Bound SQLALCHEMY :: [{0}] to Application Instance for Service :: [{1}]".format(app_db, self.cmn_logger.name))
            return app_db
        except Exception as ex:
            self.cmn_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

    def migrate_db_bind_app(self, app_instance: flask.Flask, app_db: SQLAlchemy) -> Union[Migrate, None]:
        try:
            self.cmn_logger.info("Binding the db :: [{0}] to app instance :: [{1}] for migrations".format(app_db, app_instance))
            migrate_instance = Migrate(app_instance, app_db)
            self.cmn_logger.info("Bound the db :: [{0}] to app instance :: [{1}] for migrations".format(app_db, app_instance))
            return migrate_instance
        except Exception as ex:
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            self.cmn_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

    def create_pool_of_connections(self, db_engine: SQLAlchemy.engine) -> Union[QueuePool, None]:
        try:
            self.cmn_logger.info("Creating Pool of connections for Service ==>[{0}] :: [STARTED]".format(self.cmn_logger.name))
            connection_pool = QueuePool(creator=db_engine, pool_size=self.db_pool_size, recycle=self.db_pool_recycle,
                                        timeout=self.db_pool_timeout, max_overflow=self.db_pool_max_overflow)
            self.cmn_logger.info("Created Pool of connections for Service ==>[{0}] :: [SUCCESS]".format(self.cmn_logger.name))
            return connection_pool
        except Exception as ex:
            self.cmn_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

    def create_session_maker_to_connectio_pool(self, db_engine: SQLAlchemy.engine, connection_pool: QueuePool) -> Union[sessionmaker, None]:
        try:
            self.cmn_logger.info("Creating session using pool of connections  :: [STARTED]")
            self.cmn_logger.info("Creating  a session maker for database interactions")
            session_maker = sessionmaker(bind=db_engine)
            self.cmn_logger.info("Created session using Pool_info :: {0}".format(connection_pool))
            self.cmn_logger.info("Initialised a session maker for database interactions {0}".format(session_maker))
            return session_maker

        except Exception as ex:
            self.cmn_logger.error("Creating session using pool of connections  :: [FAILED]")
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

    def get_session_from_conn_pool(self, session_maker_to_get_session: sessionmaker) -> Union[sqlalchemy.orm.Session, None]:
        try:
            self.display_pool_info(connection_pool=session_maker_to_get_session.kw['bind'].pool)
            self.cmn_logger.info("Creating session using pool of connections :: [STARTED]")
            session_instance = session_maker_to_get_session()
            return session_instance
        except sqlalchemy.exc.TimeoutError as ex:
            self.cmn_logger.error("Timeout error occurred while creating a session from the connection pool")
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        except Exception as ex:
            self.cmn_logger.error("Creating session using pool of connections :: [FAILED]")
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

    def close_session(self, session_instance: sqlalchemy.orm.Session) -> Union[bool, None]:
        try:
            self.cmn_logger.info("Closing the  session  {0}:: ".format(session_instance))
            if session_instance.is_active:
                session_instance.close()
                self.cmn_logger.info("Closed session of Session-Id {0}:: ".format(session_instance))
            else:
                self.cmn_logger.info("Session of Session-Id {0} which is not active or already closed:: [SUCCESS]".format(session_instance))
            return True
        except Exception as ex:
            self.cmn_logger.info("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

    def rollback_session(self, session_instance: sqlalchemy.orm.Session) -> Union[bool, None]:
        try:
            self.cmn_logger.info("Rollback the  session  {0}:: ".format(session_instance))
            session_instance.rollback()
            self.cmn_logger.info("Rollback the  session  {0}:: ".format(session_instance))
            return True
        except Exception as ex:
            self.cmn_logger.info("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

    def display_pool_info(self, connection_pool: QueuePool) -> None:
        try:
            if connection_pool:
                self.cmn_logger.info("#---------------------------------[ POOL INFO ]----------------------------------------#")
                self.cmn_logger.info("Displaying Pool Info for Service ==>[{0}]".format(self.cmn_logger.name))
                self.cmn_logger.info("Current Pool Info :: {0} - ID: {1}".format(connection_pool, id(connection_pool)))
                self.cmn_logger.info("Current Pool Size :: {0}".format(connection_pool.size()))
                self.cmn_logger.info("Checked Out Connections from Pool: {0}".format(connection_pool.checkedin()))
                self.cmn_logger.info("Checked in Connections available in Pool: {0}".format(connection_pool.checkedout()))
                self.cmn_logger.info("Current Pool Overflow Info: {0}".format(connection_pool.overflow()))
                self.cmn_logger.info("#---------------------------------[ POOL INFO ]----------------------------------------#")
        except Exception as ex:
            self.cmn_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

    def check_db_connectivity_and_retry(self, db_engine: SQLAlchemy.engine) -> Union[bool, None]:
        try:
            # Establishing the connection to the database and create a database/table if not exists
            while True:
                db_connection_status = self.check_database_connectivity(db_engine)
                if db_connection_status:
                    break
                else:
                    self.cmn_logger.info("Going for retry .. RETRY_INTERVAL :: {0} sec".format(self.retry_interval))
                    time.sleep(self.retry_interval)
            return db_connection_status
        except Exception as ex:
            self.cmn_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

    def check_database_connectivity(self, db_engine: SQLAlchemy.engine) -> Union[bool, None]:
        db_connection_status = False
        self.cmn_logger.info("Current Connection status set to :: {0} for the service :: {1}".format(db_connection_status,
                                                                                    self.cmn_logger.name))
        try:
            self.cmn_logger.info("Trying to establish the connection to the database :: [IN-PROGRESS]")
            db_connection = db_engine.connect()
            self.cmn_logger.info("Established the connection to the database :: [SUCCESS]")
            db_connection_status = True
            self.cmn_logger.info("Current Connection status set to :: {0} for the service :: {1}".format(db_connection_status,
                                                                                        self.cmn_logger.name))
            db_connection.close()
            self.cmn_logger.info("Closing the Current Connection as the connection was established for the service :: {0}".format(
                    self.cmn_logger.name))
        except sqlalchemy.exc.OperationalError as ex:
            self.cmn_logger.error("Current Connection status set to :: {0}".format(db_connection_status))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return db_connection_status

    def create_tables_associated_to_db_model(self, db_engine: SQLAlchemy.engine) -> Union[bool, None]:
        connection_status = False
        try:
            self.cmn_logger.info("Trying to create the tables if not present in the database...")
            # Create all the tables associated with the Base class
            self.cmn_logger.info("Going to create the tables ...")
            self.base.metadata.create_all(db_engine)
            connection_status = True
            self.cmn_logger.info("Created the tables ...")
        except sqlalchemy.exc.OperationalError as ex:
            self.cmn_logger.info("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        except sqlalchemy.exc.TimeoutError as ex:
            self.cmn_logger.info("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        except Exception as ex:
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            self.cmn_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return connection_status
