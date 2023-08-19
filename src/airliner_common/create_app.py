import json
import sys
import time
from flask import Flask
from flask import Blueprint
import sqlalchemy.exc
from sqlalchemy import create_engine, QueuePool
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
from src.airliner_common.base_logger import LogMonitor


class CreatFlaskApp(LogMonitor):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    def __init__(self, service_name, db_driver, db_user, db_ip_address, db_password,  db_port, db_name, db_pool_size, db_pool_max_overflow, base):
        self.service_name = service_name
        self.app_logger = super().create_logger_for_service(self.service_name)
        self.app_instance = None
        self.blueprint_instance = None
        self.database_uri = None
        self.app_db_engine = None
        self.app_db= None
        self.connection_pool = None
        self.app_db_engine= None
        self.session_ = None
        self.session_instance = None

        self.db_driver = db_driver
        self.db_user = db_user
        self.db_password = db_password
        self.db_ip_address = db_ip_address
        self.db_port = db_port
        self.db_name = db_name
        self.db_pool_size= db_pool_size
        self.db_pool_max_overflow= db_pool_max_overflow
        self.base = base


    def create_app_instance(self):
        self.app_logger.info("Received Service [{0}]".format(self.service_name))
        self.app_instance = Flask(self.service_name)
        self.app_logger.info("Flask of Application Instance created for service [{0}] ,  App Name :: [{1}] ==> SUCCESS".format(self.service_name, self.app_instance))
        return self.app_instance

    def create_blueprint(self):
        self.blueprint_instance = Blueprint(self.service_name+"_bp", __name__)
        self.app_logger.info("Created Blueprint :: {0} for the Application service ::{1}".format(self.blueprint_instance, self.service_name))
        return self.blueprint_instance

    def register_blueprint(self):
        self.app_logger.info("Registering blueprints to the service :: {0}".format(self.app_instance))
        return self.app_instance.register_blueprint(self.blueprint_instance)

    #
    def display_registered_blueprints_for_service(self):
        for rule in self.app_instance.url_map.iter_rules():
            self.app_logger.info("Added Blueprints :: {0}".format(rule))


    def get_database_uri(self):
        self.app_logger.info("Preparing DatabaseURI for Service :: [{0}]".format(self.service_name))
        self.database_uri = self.db_driver + "://" + self.db_user + ":" + self.db_password + "@" + self.db_ip_address + ":" + self.db_port + "/" + self.db_name
        self.app_logger.info("Prepared DatabaseURI for Service :: [{0}] - {1}".format(self.service_name, self.database_uri))
        return self.database_uri

    def create_db_engine(self):
        self.app_logger.info("Creating DB-Engine using DatabaseURI for Service :: [{0}]".format(self.service_name))
        self.app_db_engine = create_engine(self.get_database_uri())
        self.app_logger.info("Created DB-Engine using DatabaseURIfor Service :: [{0}]".format(self.app_db_engine))
        return self.app_db_engine

    def bind_db_app(self):
        self.app_instance.config['SQLALCHEMY_DATABASE_URI'] = self.database_uri
        self.app_logger.info("Binding SQLALCHEMY using DatabaseURI:: [{1}] to Application Instance for Service :: [{0}]".format(self.service_name, self.database_uri))
        self.app_db = SQLAlchemy(app=self.app_instance)
        self.app_logger.info("Binded SQLALCHEMY :: [{0}] to Application Instance for Service :: [{1}]".format(self.app_db, self.service_name))
        return self.app_db

    def create_pool(self):
        self.app_logger.info("Initialized Pool for Service ==>[{0}] :: [SUCCESS]".format(self.service_name))
        self.connection_pool = QueuePool(creator=self.app_db_engine,pool_size=self.db_pool_size, max_overflow=self.db_pool_max_overflow)
        return self.connection_pool

    def check_db_connectivity_and_retry(self):
        # Establishing the connection to the database and create a database/table if not exists
        RETRY_INTERVAL = 5
        while True:
            db_connection_status = self.check_database_connectivity()
            if db_connection_status:
                break
            else:
                self.app_logger.info("Going for retry .. RETRY_INTERVAL :: {0} sec".format(RETRY_INTERVAL))
                time.sleep(RETRY_INTERVAL)
        return db_connection_status

    def check_database_connectivity(self):
        db_connection_status = False
        self.app_logger.info("Current Connection status set to :: {0} for the service :: {1}".format(db_connection_status, self.service_name))
        self.app_logger.info("Trying to establish the connection to the database :: [IN-PROGRESS]")
        try:
            # Handle the connection event before_connect :: [Triggered before a connection to the database is established.]
            airliner_db_connection = self.app_db_engine.connect()
            self.app_logger.info("Established the connection to the database :: [SUCCESS]")
            db_connection_status = True
            self.app_logger.info("Current Connection status set to :: {0} for the service :: {1}".format(db_connection_status,self.service_name))
            airliner_db_connection.close()
            self.app_logger.info("Closing the Current Connection as the connection was established for the service :: {0}".format(self.service_name))
        except sqlalchemy.exc.OperationalError as ex:
            self.app_logger.error("Current Connection status set to :: {0}".format(db_connection_status))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return db_connection_status

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
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

    def create_session_for_service(self):
        try:
            self.app_logger.info("Creating session using pool of connections  :: [STARTED]")
            self.app_logger.info("Creating session using Pool_info :: {0}".format(self.connection_pool))
            self.app_logger.info("Initialising  a session maker for database interactions")
            self.session_ = sessionmaker(bind=self.app_db_engine)
            self.app_logger.info("Initialised a session maker for database interactions {0}".format(self.session_))
            self.session_instance = self.session_()
            self.app_logger.info("Created session to store the data in to DataBase Session-Id  :: {0}".format(self.session_instance))
            self.display_pool_info()
        except Exception as ex:
            self.app_logger.error("Creating session using pool of connections  :: [FAILED]")
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return self.session_instance

    @staticmethod
    def read_json_schema(schema_file_path):
        loaded_status = False
        loaded_schema = None
        try:
            print("Received Schema File Path : {0}".format(schema_file_path))
            with open(schema_file_path, "r") as schema_file:
                loaded_status = True
                loaded_schema = dict(json.load(schema_file))
        except FileNotFoundError as ex:
            print(f"Schema file not found: {schema_file_path}")
        except json.JSONDecodeError as ex:
            print(f"Invalid JSON syntax in the schema file: {ex}")
        except Exception as ex:
            print('Error occurred :: {0} \tLine No: {1}'.format(ex, sys.exc_info()[2].tb_lineno))
        print("Schema Validation {0}".format(loaded_status))
        return loaded_status, loaded_schema







