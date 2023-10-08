import sys
from typing import Union
from sqlalchemy.exc import (
    SQLAlchemyError,
    ArgumentError,
    UnboundExecutionError,
    OperationalError,
    TimeoutError,
    DatabaseError,
)
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import QueuePool

from src.pyportal_common.db_handlers.db_conn_manager import (
    DataBaseConnectionHandler,
)


class DataBasePoolHandler(DataBaseConnectionHandler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_pool_size = kwargs.get("db_pool_size")
        self.db_pool_recycle = kwargs.get("db_pool_recycle")
        self.db_pool_timeout = kwargs.get("db_pool_timeout")
        self.db_pool_max_overflow = kwargs.get("db_pool_max_overflow")

        # Log all parameters
        for key, value in vars(self).items():
            self.cmn_logger.info(f"Initialized {key} with value: {value}")

    def create_pool_of_connections(
        self, db_engine: SQLAlchemy.engine
    ) -> Union[QueuePool, None]:
        try:
            self.cmn_logger.info(
                f"Creating Pool of connections for Service ==>[{self.cmn_logger.name}] :: [STARTED]"
            )
            if not db_engine:
                self.cmn_logger.info(
                    f"Created Pool of connections for Service ==>[{self.cmn_logger.name}] :: [FAILED]"
                )
                return None
            else:
                pool_of_db_connections: QueuePool = QueuePool(
                    creator=db_engine,
                    pool_size=self.db_pool_size,
                    recycle=self.db_pool_recycle,
                    timeout=self.db_pool_timeout,
                    max_overflow=self.db_pool_max_overflow,
                )
                self.cmn_logger.info(
                    f"Created Pool of connections for Service ==>[{self.cmn_logger.name}] :: [SUCCESS]"
                )
                return pool_of_db_connections
        except SQLAlchemyError as ex:
            self.cmn_logger.error(
                f"{ex} error occurred while Creating Pool of connections for Service \tLine No:: {sys.exc_info()[2].tb_lineno}"
            )
            return None

    def create_session_maker_to_connectio_pool(
        self, db_engine: SQLAlchemy.engine, connection_pool: QueuePool
    ) -> Union[sessionmaker, None]:
        try:
            if not db_engine:
                self.cmn_logger.info(
                    "Creating session using pool of connections  :: [FAILED]"
                )
                return None
            else:
                self.cmn_logger.info(
                    "Creating session maker for managing database sessions/interactions  :: [STARTED]"
                )
                session_maker = sessionmaker(bind=db_engine)
                self.cmn_logger.info(
                    f"Created session using Pool_info :: {connection_pool}"
                )
                self.cmn_logger.info(
                    f"Created a session maker for database interactions {session_maker} :: [SUCCESS]"
                )
                return session_maker
        except (
            ArgumentError,
            UnboundExecutionError,
            OperationalError,
            TimeoutError,
            DatabaseError,
        ) as ex:
            self.cmn_logger.error(
                f"{ex} error occurred while Creating session using pool of connections  \tLine No:: {sys.exc_info()[2].tb_lineno}"
            )
            return None



        # def rollback_session(self, session_instance: sqlalchemy.orm.Session) -> Union[bool, None]:
        #     try:
        #         if session_instance:
        #             self.cmn_logger.info(f"Rollback the  session  {session_instance}:: ")
        #             session_instance.rollback()
        #             self.cmn_logger.info(f"Rollback the  session  {session_instance}:: ")
        #             return True
        #     except Exception as ex:
        #         self.cmn_logger.info(f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}")
        #         print(f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}")
        #         return False
