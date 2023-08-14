import sys, time

from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import TimeoutError, OperationalError
from sqlalchemy_utils import database_exists, create_database
from src.airliner_service.models.airliner_model import Base

def init_airliner_database_engine(airliner_app, airliner_logger, database_uri):
    try:
        # database_uri = os.environ.get('SQLALCHEMY_DATABASE_URI')
        airliner_app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
        airliner_logger.info("DataBase URI :: {0}".format(database_uri))
        airliner_app.config['SQLALCHEMY_DATABASE_URI'] = database_uri

        airliner_logger.info("Initialising the database engine using database URI with specified pool settings")
        airliner_db_engine = create_engine(database_uri)
        airliner_logger.info("Initialised the database engine using database URI with specified pool settings:: {0}".format(airliner_db_engine))

        # Access the pool and print pool information
        airliner_pool = QueuePool(creator=airliner_db_engine, pool_size=10, max_overflow=20)
        # print(f"Pool '{airliner_pool.name}' - Size: {airliner_pool.size()}, Checked Out: {airliner_pool.checkedin()}, Checked In: {airliner_pool.checkedout()}, Overflow: {airliner_pool.overflow()}")

        airliner_logger.info("Initialising the SQLAlchemy DB instance and bind with the Application Instance")
        airliner_db = SQLAlchemy(app=airliner_app)
        airliner_logger.info("Initialised the SQLAlchemy DB instance and binded with the Application Instance :: {0}".format(airliner_db))
        return airliner_db, airliner_db_engine, airliner_pool

    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        airliner_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))







def check_database_connectivity(airliner_db_engine,  airliner_logger):
    db_connection_status = False
    airliner_logger.info("Current Connection status set to :: {0}".format(db_connection_status))
    airliner_logger.info("Trying to establish the connection to the database :: [IN-PROGRESS]")
    try:
        # Handle the connection event before_connect :: [Triggered before a connection to the database is established.]
        airliner_db_connection = airliner_db_engine.connect()
        airliner_logger.info("Established the connection to the database :: [SUCCESS]")
        airliner_logger.info("Established the connection to the database..")
        db_connection_status = True
        airliner_logger.info("Current Connection status set to :: {0}".format(db_connection_status))
        airliner_db_connection.close()
        airliner_logger.info("Closing the Current Connection as the connection was established.")
    except OperationalError as ex:
        airliner_logger.error("Current Connection status set to :: {0}".format(db_connection_status))
        airliner_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        airliner_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
    return db_connection_status



def display_pool_info(airliner_pool, airliner_logger):
    try:
        airliner_logger.info("Current airliner_pool Info :: {0} - ID: {1}".format(airliner_pool, id(airliner_pool)))
        airliner_logger.info("airliner_pool Size ::  {0}".format(airliner_pool.size()))
        airliner_logger.info("Checked Out Connections from airliner_pool  {0}".format(airliner_pool.checkedin()))
        airliner_logger.info("Checked in Connections available in airliner_pool :: {0}".format(airliner_pool.checkedout()))
        airliner_logger.info("Current airliner_pool Overflow Info :: {0}".format(airliner_pool.overflow()))
    except Exception as ex:
        airliner_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        airliner_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))





def init_create_databases(airliner_logger, database_uri):
    is_database_created = False
    try:
        if not database_exists(database_uri):
            airliner_logger.info("Database doesn't exists :: {0}".format(database_uri.split("/")[-1]))
            create_database(database_uri)
            is_database_created = True
            airliner_logger.info("Created the database :: {0}".format(database_uri.split("/")[-1]))
        else:
            is_database_created = True
            airliner_logger.info("Database already exists :: {0}".format(database_uri.split("/")[-1]))
    except Exception as ex:
        airliner_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        airliner_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
    return is_database_created

def create_tables_associated_to_db_model(airliner_logger, airliner_db_engine):
    connection_status = False
    try:
        airliner_logger.info("Trying to create the tables if not present in the database...")
        # Create all the tables associated with the Base class
        airliner_logger.info("Going to create the tables ...")
        Base.metadata.create_all(airliner_db_engine)
        connection_status = True
        airliner_logger.info("Created the tables ...")
    except OperationalError as ex:
        airliner_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        airliner_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
    except TimeoutError as ex:
        airliner_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        airliner_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
    except Exception as ex:
        airliner_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        airliner_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
    return connection_status


def connect_db_for_model_creation(airliner_logger, airliner_db_engine ):
    connection_attempt = 3
    models_created_in_DB = False
    try:
        for every_attempt in range(connection_attempt):
            connection_status = create_tables_associated_to_db_model(airliner_logger, airliner_db_engine)
            if connection_status:
                airliner_logger.error("Model creation {0} ::  SUCCESS".format(every_attempt))
                models_created_in_DB = True
                break
            else:
                models_created_in_DB = False
                airliner_logger.error("Model creation {0} ::  FAILED".format(every_attempt))
        return models_created_in_DB
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        airliner_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))




def create_airliner_session(airliner_logger, airliner_pool, airliner_db_engine):
    aero_session = None
    try:
        airliner_logger.info("Creating session using pool of connections  :: [STARTED]")
        airliner_logger.info("Creating session using Pool_info :: {0}".format(airliner_pool))
        display_pool_info(airliner_pool, airliner_logger)
        airliner_logger.info("Initialising  a session maker for database interactions")
        airliner_session = sessionmaker(bind=airliner_db_engine)
        airliner_logger.info("Initialised a session maker for database interactions {0}".format(airliner_session))
        aero_session = airliner_session()
        airliner_logger.info("Created session to store the data in to DataBase Session-Id  :: {0}".format(aero_session))
    except Exception as ex:
        airliner_logger.error("Creating session using pool of connections  :: [FAILED]")
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        airliner_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
    return aero_session

def retry_db_connectivity(airliner_db_engine):
    # Establishing the connection to the database and create a database/table if not exists
    RETRY_INTERVAL = 5
    while True:
        db_connection_status = check_database_connectivity(airliner_db_engine)
        if db_connection_status == True:
            break
        else:
            print("Going for retry .. RETRY_INTERVAL :: {0} sec".format(RETRY_INTERVAL))
            time.sleep(RETRY_INTERVAL)
    return db_connection_status




