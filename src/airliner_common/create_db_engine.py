import sys,time
import sqlalchemy.exc
from sqlalchemy import create_engine, QueuePool
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
from create_app import CreatFlaskApp


class CreateDbEngine(CreatFlaskApp):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    def __init__(self, service_name, db_driver, db_user, db_password, db_ip_address, db_port, db_name):
        super().__init__(service_name)
        self.db_driver = db_driver
        self.db_user = db_user
        self.db_password = db_password
        self.db_ip_address = db_ip_address
        self.db_port = db_port
        self.db_name = db_name
        self.database_uri = None
        self.app_db_engine = None


    def get_database_uri(self):
        self.app_logger.info("Preparing DatabaseURI for Service :: [{0}]".format(self.service_name))
        database_uri = self.db_driver + "://" + self.db_user + ":" + self.db_password + "@" + self.db_ip_address + ":" + self.db_port + "/" + self.db_name
        self.app_logger.info("Prepared DatabaseURI for Service :: [{0}] - {1}".format(self.service_name, database_uri))
        return database_uri
    def create_db_engine(self):
        database_uri = self.get_database_uri()
        self.app_logger.info("Creating DB-Engine using DatabaseURI :: {1} for Service :: [{0}]".format(self.service_name, database_uri))
        app_db_engine = create_engine(database_uri)
        self.app_logger.info("Created DB-Engine using DatabaseURI :: {0} for Service :: [{1}]".format(app_db_engine, self.service_name))
        return app_db_engine

class BindSQLALCHEMY(CreatFlaskApp):
    def __init__(self, service_name, app_name, databaseuri):
        self.app_name = app_name
        self.databaseuri = databaseuri
        self.app_db = None
        self.service_name = service_name


    def bind_db_app(self):
        self.app_name.config['SQLALCHEMY_DATABASE_URI'] = self.databaseuri
        self.app_logger.info("Binding SQLALCHEMY using DatabaseURI:: [{1}] to Application Instance for Service :: [{0}]".format(self.service_name, self.databaseuri))
        app_db = SQLAlchemy(app=self.app_name)
        self.app_logger.info("Binded SQLALCHEMY :: [{0}] to Application Instance for Service :: [{1}]".format(app_db, self.service_name))
        return app_db

class QueuePool_To_Target_DB(CreatFlaskApp):
    def __init__(self, service_name, app_db_engine, db_pool_size, db_pool_max_overflow):
        self.service_name = service_name
        self.app_db_engine= app_db_engine
        self.db_pool_size= db_pool_size
        self.db_pool_max_overflow= db_pool_max_overflow
        self.connection_pool=None

    def create_pool(self):
        self.app_logger.info("Initialized Pool for Service ==>[{0}] :: [SUCCESS]".format(self.service_name))
        self.connection_pool = QueuePool(creator=self.app_db_engine,pool_size=self.db_pool_size, max_overflow=self.db_pool_max_overflow)
        return self.connection_pool


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





def create_session_for_service(app_pool, airliner_db_engine, service_name):
    aero_session = None
    try:
        print("Creating session using pool of connections  :: [STARTED]")
        print("Creating session using Pool_info :: {0}".format(app_pool))
        print("Initialising  a session maker for database interactions")
        airliner_session = sessionmaker(bind=airliner_db_engine)
        print("Initialised a session maker for database interactions {0}".format(airliner_session))
        aero_session = airliner_session()
        print("Created session to store the data in to DataBase Session-Id  :: {0}".format(aero_session))
    except Exception as ex:
        print("Creating session using pool of connections  :: [FAILED]")
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
    return aero_session

def init_databases_for_service(database_uri):
    is_databases_created = False
    try:
        is_databases_created = True
        if not database_exists(database_uri):
            print("Database doesn't exists :: {0}".format(database_uri.split("/")[-1]))
            create_database(database_uri)
            print("Created the database :: {0}".format(database_uri.split("/")[-1]))
        else:
            print("Database already exists :: {0}".format(database_uri.split("/")[-1]))
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
    return is_databases_created

def check_database_connectivity(service_name, airliner_db_engine):
    db_connection_status = False
    print("Current Connection status set to :: {0} for the service :: {1}".format(db_connection_status, service_name))
    print("Trying to establish the connection to the database :: [IN-PROGRESS]")
    try:
        # Handle the connection event before_connect :: [Triggered before a connection to the database is established.]
        airliner_db_connection = airliner_db_engine.connect()
        print("Established the connection to the database :: [SUCCESS]")
        db_connection_status = True
        print("Current Connection status set to :: {0} for the service :: {1}".format(db_connection_status, service_name))
        airliner_db_connection.close()
        print("Closing the Current Connection as the connection was established for the service :: {0}".format(service_name))
    except sqlalchemy.exc.OperationalError as ex:
        print("Current Connection status set to :: {0}".format(db_connection_status))
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
    return db_connection_status

def create_tables_associated_to_db_model(Base, airliner_db_engine):
    connection_status = False
    try:
        print("Trying to create the tables if not present in the database...")
        # Create all the tables associated with the Base class
        print("Going to create the tables ...")
        Base.metadata.create_all(airliner_db_engine)
        connection_status = True
        print("Created the tables ...")
    except sqlalchemy.exc.OperationalError as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
    except sqlalchemy.exc.TimeoutError as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
    return connection_status

def check_db_connectivity_and_retry(USER_SERVICE_NAME, airliner_db_engine):
    # Establishing the connection to the database and create a database/table if not exists
    RETRY_INTERVAL = 5
    while True:
        db_connection_status = check_database_connectivity(USER_SERVICE_NAME, airliner_db_engine)
        if db_connection_status == True:
            break
        else:
            print("Going for retry .. RETRY_INTERVAL :: {0} sec".format(RETRY_INTERVAL))
            time.sleep(RETRY_INTERVAL)
    return db_connection_status




# if check_db_connectivity_and_retry(SERVICE_NAME, registration_db_engine):
#     database_uri = registration_db_obj.get_database_uri()
#     if init_databases_for_service(database_uri):
#         if create_tables_associated_to_db_model(Base, airliner_db_engine=registration_db_engine):
#             registration_db_bind_obj = BindSQLALCHEMY(SERVICE_NAME, registration_app, database_uri)
#             registration_db_sqlalchemy = registration_db_bind_obj.bind_db_app()
#             registration_pool_obj = QueuePool_To_Target_DB(SERVICE_NAME, registration_db_engine, 100, 20)
#             registration_connection_pool = registration_pool_obj.create_pool()
