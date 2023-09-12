import json
import sys
import time
import jsonschema
from flask import Flask
from flask import Blueprint
import sqlalchemy.exc
from sqlalchemy.pool import QueuePool
from sqlalchemy import create_engine
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
from src.admin_common.base_logger import LogMonitor
from flask_jwt_extended import JWTManager
from urllib.parse import quote_plus


# noinspection PyMissingConstructor
class CreatFlaskApp(LogMonitor):
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    def __init__(self, service_name, db_driver, db_user, db_ip_address, db_password, db_port, db_name, db_pool_size,
                 db_pool_max_overflow, db_pool_recycle, db_pool_timeout, retry_interval, max_retries,  base):
        self.service_name = service_name
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
        self.app_logger = super().create_logger_for_service(self.service_name)
        self.app_instance = None
        self.blueprint_instance = None
        self.migrate_instance = None
        self.jwt_instance = None
        self.database_uri = None
        self.airliner_db_connection = None
        self.db_connection_status = False
        self.app_db_engine = None
        self.is_engine_created = False
        self.app_db = None
        self.connection_pool = None
        self.Session = None
        self.session_instance = None
        self.loaded_status = False
        self.loaded_schema = None
        self.SQLALCHEMY_DATABASE_URI = None
        self.rec_req_params = None
        self.required_properties = []
        self.schema_file_path = None
        self.schema_file = None

    def create_app_instance(self):
        try:
            self.app_logger.info("Received Service [{0}]".format(self.service_name))
            self.app_instance = Flask(self.service_name)
            self.app_logger.info("Flask of Application Instance created for service [{0}] ,  App Name :: [{1}] ==> SUCCESS".format(
                    self.service_name, self.app_instance))
        except Exception as ex:
            self.app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return self.app_instance

    def init_jwt_manger(self):
        try:
            self.jwt_instance = JWTManager(self.app_instance)
            return self.jwt_instance
        except Exception as ex:
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            self.app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            return None

    def create_blueprint(self):
        try:
            self.blueprint_instance = Blueprint(self.service_name + "_bp", __name__)
            self.app_logger.info(
                "Created Blueprint :: {0} for the Application service ::{1}".format(self.blueprint_instance,
                                                                                    self.service_name))
        except Exception as ex:
            self.app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return self.blueprint_instance

    def register_blueprint(self):
        try:
            self.app_logger.info("Registering blueprints to the service :: {0}".format(self.app_instance))
            return self.app_instance.register_blueprint(self.blueprint_instance)
        except Exception as ex:
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return None

    def register_err_handler(self, status_code, err_handler_func_name):
        try:
            self.app_logger.info(
                "Registering Error Handler {1}-{2} to the service :: {0}".format(self.app_instance, status_code,
                                                                                 err_handler_func_name))
            return self.app_instance.register_error_handler(status_code, err_handler_func_name)
        except Exception as ex:
            self.app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return None

    def display_registered_err_handlers(self):
        try:
            for error_code, handler_info in self.app_instance.error_handler_spec.items():
                self.app_logger.info(f"Error Code: {error_code}, Handler Function: {handler_info[0]}")
        except Exception as ex:
            self.app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return None

    def display_registered_blueprints_for_service(self):
        try:
            for rule in self.app_instance.url_map.iter_rules():
                self.app_logger.info("Added Blueprints :: {0}".format(rule))
        except Exception as ex:
            self.app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return None

    def get_database_uri(self):
        try:
            # connection_string = 'postgresql://username:password@localhost/dbname'
            self.app_logger.info("Preparing DatabaseURI for Service :: [{0}]".format(self.service_name))
            self.database_uri = self.db_driver + "://" + self.db_user + ":" + quote_plus(
                self.db_password) + "@" + self.db_ip_address + ":" + str(self.db_port) + "/" + self.db_name
            self.app_logger.info("Prepared DatabaseURI for Service :: [{0}] - {1}".format(self.service_name, self.database_uri))
        except Exception as ex:
            self.app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return self.database_uri

    def create_db_engine(self):
        try:
            retries = 0
            while retries < self.max_retries:
                try:
                    self.app_logger.info("Creating DB-Engine using DatabaseURI for Service :: [{0}]".format(self.service_name))
                    self.SQLALCHEMY_DATABASE_URI = self.get_database_uri()
                    self.app_instance.config['SQLALCHEMY_DATABASE_URI'] = self.SQLALCHEMY_DATABASE_URI
                    self.app_db_engine = create_engine(self.app_instance.config['SQLALCHEMY_DATABASE_URI'])
                    self.is_engine_created = True
                    self.app_logger.info(
                        "Created DB-Engine using DatabaseURI for Service :: [{0}]".format(self.app_db_engine))
                    return self.app_db_engine, self.is_engine_created
                except Exception as ex:
                    print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
                    self.app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
                    retries += 1
                    if retries < self.max_retries:
                        self.app_logger.info(f"Retrying in {self.retry_interval} seconds...")
                        time.sleep(self.retry_interval)
                    else:
                        self.is_engine_created = False  # Set the flag to False on max retries
                        self.app_db_engine = None  # Set the engine to None in case of an error
                        return self.app_db_engine, self.is_engine_created
        except Exception as ex:
            self.app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

    def bind_db_app(self):
        try:
            self.app_instance.config['SQLALCHEMY_DATABASE_URI'] = self.database_uri
            self.app_logger.info(
                "Binding SQLALCHEMY using DatabaseURI:: [{1}] to Application Instance for Service :: [{0}]".format(
                    self.service_name, self.database_uri))
            self.app_db = SQLAlchemy(app=self.app_instance)
            self.app_logger.info(
                "Bound SQLALCHEMY :: [{0}] to Application Instance for Service :: [{1}]".format(self.app_db,
                                                                                                self.service_name))
        except Exception as ex:
            self.app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return self.app_db

    def migrate_db_bind_app(self):
        try:
            self.app_logger.info("Binding the db :: [{0}] to app instance :: [{1}] for migrations".format(self.app_db,
                                                                                                          self.app_instance))
            self.migrate_instance = Migrate(self.app_instance, self.app_db)
            self.app_logger.info(
                "Bound the db :: [{0}] to app instance :: [{1}] for migrations".format(self.app_db, self.app_instance))
        except Exception as ex:
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            self.app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return self.migrate_instance

    def create_pool_of_connections(self):
        try:
            self.app_logger.info(
                "Creating Pool of connections for Service ==>[{0}] :: [STARTED]".format(self.service_name))
            self.connection_pool = QueuePool(creator=self.app_db_engine, pool_size=self.db_pool_size, recycle=self.db_pool_recycle, timeout=self.db_pool_timeout,max_overflow=self.db_pool_max_overflow)
            self.app_logger.info(
                "Created Pool of connections for Service ==>[{0}] :: [SUCCESS]".format(self.service_name))
            self.app_logger.info("Creating session using pool of connections  :: [STARTED]")
            self.app_logger.info("Creating  a session maker for database interactions")
            self.Session = sessionmaker(bind=self.app_db_engine)
            self.app_logger.info("Created session using Pool_info :: {0}".format(self.connection_pool))
            self.app_logger.info("Initialised a session maker for database interactions {0}".format(self.Session))
        except Exception as ex:
            self.app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return self.connection_pool, self.Session

    def get_session_from_conn_pool(self):
        try:
            self.app_logger.error("Creating session using pool of connections  :: [STARTED]")
            self.session_instance = self.Session()
            self.app_logger.info("Using session  to DataBase Session-Id  :: {0}".format(self.session_instance))
        except Exception as ex:
            self.app_logger.error("Creating session using pool of connections  :: [FAILED]")
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return self.session_instance

    def close_session(self, sessionname):
        is_session_closed = False
        try:
            self.app_logger.info("Closing the  session  {0}:: [STARTED]".format(sessionname))
            sessionname.close()
            is_session_closed = True
            self.app_logger.info("Closed session of Session-Id {0}:: [SUCCESS]".format(sessionname))
        except Exception as ex:
            self.app_logger.info("Closing the  session  {0}:: [FAILED]".format(sessionname))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return is_session_closed

    def rollback_session(self, sessionname):
        is_session_rollbacked = False
        try:
            self.app_logger.info("Rollback the  session  {0}:: [STARTED]".format(sessionname))
            sessionname.rollback()
            is_session_rollbacked = True
            self.app_logger.info("Rollback the  session  {0}:: [SUCCESS]".format(sessionname))
            # app_name.close_session_for_service(session_name)
            # err_response = PyPortalAdminInternalServerError(message=error_message)
            # user_management_app_logger.info("Sending Error response back to client :: {0}".format(err_response))
            # return err_response
        except Exception as ex:
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return is_session_rollbacked

    def display_pool_info(self):
        try:
            if self.connection_pool:
                self.app_logger.info("#---------------------------------[ POOL - INFO ]----------------------------------------#")
                self.app_logger.info("Displaying Pool_Info for Service ==>[{0}] ".format(self.service_name))
                self.app_logger.info("Current Pool Info :: {0} - ID: {1}".format(self.connection_pool, id(self.connection_pool)))
                self.app_logger.info("Current Pool Size ::  {0}".format(self.connection_pool.size()))
                self.app_logger.info("Checked Out Connections from Pool  {0}".format(self.connection_pool.checkedin()))
                self.app_logger.info("Checked in Connections available in Pool :: {0}".format(self.connection_pool.checkedout()))
                self.app_logger.info("Current Pool Overflow Info :: {0}".format(self.connection_pool.overflow()))
                self.app_logger.info("#---------------------------------[ POOL - INFO ]----------------------------------------#")
        except Exception as ex:
            self.app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

    def check_db_connectivity_and_retry(self):
        try:
            # Establishing the connection to the database and create a database/table if not exists
            while True:
                self.db_connection_status = self.check_database_connectivity()
                if self.db_connection_status:
                    break
                else:
                    self.app_logger.info("Going for retry .. RETRY_INTERVAL :: {0} sec".format(self.retry_interval))
                    time.sleep(self.retry_interval)
            return self.db_connection_status
        except Exception as ex:
            self.app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

    def check_database_connectivity(self):
        self.app_logger.info(
            "Current Connection status set to :: {0} for the service :: {1}".format(self.db_connection_status,
                                                                                    self.service_name))
        self.app_logger.info("Trying to establish the connection to the database :: [IN-PROGRESS]")
        try:
            # Handle the connection event before_connect :: [Triggered before a connection to the database is established.]
            self.airliner_db_connection = self.app_db_engine.connect()
            self.app_logger.info("Established the connection to the database :: [SUCCESS]")
            self.db_connection_status = True
            self.app_logger.info(
                "Current Connection status set to :: {0} for the service :: {1}".format(self.db_connection_status,
                                                                                        self.service_name))
            self.airliner_db_connection.close()
            self.app_logger.info(
                "Closing the Current Connection as the connection was established for the service :: {0}".format(
                    self.service_name))
        except sqlalchemy.exc.OperationalError as ex:
            self.app_logger.error("Current Connection status set to :: {0}".format(self.db_connection_status))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return self.db_connection_status

    def create_tables_associated_to_db_model(self):
        connection_status = False
        try:
            self.app_logger.info("Trying to create the tables if not present in the database...")
            # Create all the tables associated with the Base class
            self.app_logger.info("Going to create the tables ...")
            self.base.metadata.create_all(self.app_db_engine)
            connection_status = True
            self.app_logger.info("Created the tables ...")
        except sqlalchemy.exc.OperationalError as ex:
            self.app_logger.info("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        except sqlalchemy.exc.TimeoutError as ex:
            self.app_logger.info("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        except Exception as ex:
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            self.app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return connection_status

    def init_databases_for_service(self):
        is_databases_created = False
        try:
            is_databases_created = True
            if not database_exists(self.database_uri):
                self.app_logger.info("Database doesn't exists :: {0}".format(self.database_uri.split("/")[-1]))
                create_database(self.database_uri)
                self.app_logger.info("Created the database :: {0}".format(self.database_uri.split("/")[-1]))
            else:
                self.app_logger.info("Database already exists :: {0}".format(self.database_uri.split("/")[-1]))
        except Exception as ex:
            self.app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return is_databases_created

    def read_json_schema(self, schema_file_path):
        try:
            self.app_logger.info("Received Schema File Path : {0}".format(schema_file_path))
            with open(schema_file_path, "r") as self.schema_file:
                self.loaded_status = True
                self.loaded_schema = dict(json.load(self.schema_file))
        except FileNotFoundError as ex:
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            self.app_logger.error(f"Schema file not found: {schema_file_path}")
        except json.JSONDecodeError as ex:
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            self.app_logger.error(f"Invalid JSON syntax in the schema file: {ex}")
        except Exception as ex:
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            self.app_logger.error('Error occurred :: {0} \tLine No: {1}'.format(ex, sys.exc_info()[2].tb_lineno))
        self.app_logger.info("Schema Validation {0}".format(self.loaded_status))
        return self.loaded_status, self.loaded_schema

    def generate_req_missing_params(self, rec_req_params, loaded_schema):
        try:
            missing_params_err_obj = {}
            self.app_logger.info("Validation for Request is  :: [STARTED]")
            for key, value in rec_req_params.items():
                self.app_logger.info("REQUEST <==> params ==> Param :: {0} :: Value :: {1} :: Type ::{2} ".format(key, value, type(value)))

            try:
                jsonschema.validate(instance=rec_req_params, schema=loaded_schema)
            except jsonschema.exceptions.ValidationError as ex:
                self.app_logger.info("Checking the data and doing validations...")
                # Get the list of required properties from the schema
                self.required_properties = loaded_schema.get("required", [])
                self.app_logger.info("Required_Properties_As_Per_Schema :: {0}".format(self.required_properties))
                # Get the list of missing required properties from the validation error
                missing_params = [property_name for property_name in self.required_properties if property_name not in ex.instance]
                self.app_logger.error("Missing params found :: {0}".format(missing_params))
                missing_params_err_obj = {'details': {'params': missing_params}}
                self.app_logger.error("Packing message for missing property which are found :: {0}".format(missing_params))
                self.app_logger.info("Validation for Request is  :: [SUCCESS]")
        except Exception as ex:
            missing_params_err_obj = {}
            self.app_logger.info("Validation for Request is  :: [FAILED]")
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            self.app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return missing_params_err_obj
