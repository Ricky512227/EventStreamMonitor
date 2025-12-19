# pylint: disable=line-too-long

import sys
from typing import Union

import sqlalchemy
from sqlalchemy.exc import (
    SQLAlchemyError,
    ArgumentError,
    UnboundExecutionError,
    OperationalError,
    TimeoutError,
    DatabaseError,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import QueuePool

from src.pyportal_common.db_handlers.db_conn_manager import (
    DataBaseConnectionHandler,
)

# from sqlalchemy.exc import (
#     SQLAlchemyError,
#     ArgumentError,
#     UnboundExecutionError,
#     OperationalError,
#     TimeoutError,
#     DatabaseError,
# )
from sqlalchemy.orm import sessionmaker


class DataBasePoolHandler(DataBaseConnectionHandler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session_maker = None
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

    def create_session_maker_bind_to_db_engine(
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
                self.session_maker = sessionmaker(bind=db_engine)
                self.cmn_logger.info(
                    f"Created session using Pool_info :: {connection_pool}"
                )
                self.cmn_logger.info(
                    f"Created a session maker for database interactions {self.session_maker} :: [SUCCESS]"
                )
                return self.session_maker
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

    def get_session_from_session_maker(self) -> Union[sqlalchemy.orm.Session, None]:
        try:
            if self.session_maker is None:
                self.cmn_logger.info(
                    "Fetching session from sessions of connections  :: [FAILED]"
                )
                return None
            else:
                self.display_pool_info(
                    connection_pool=self.session_maker.kw["bind"].pool
                )
                self.cmn_logger.info(
                    "Fetching session from sessions of connections :: [STARTED]"
                )
                session_instance = self.session_maker()

                self.cmn_logger.info(
                    "Fetching session %s from sessions of connections:: [SUCCESS]",
                    session_instance,
                )
                return session_instance
        except (
            ArgumentError,
            UnboundExecutionError,
            OperationalError,
            TimeoutError,
            DatabaseError,
        ) as ex:
            self.cmn_logger.error(
                f"{ex} error occurred while Fetching session from sessions of connections \tLine No:: {sys.exc_info()[2].tb_lineno}"
            )
            return None

    def close_session(
        self, session_instance: sqlalchemy.orm.Session
    ) -> Union[bool, None]:
        try:
            self.cmn_logger.info(f"Closing the  session  {session_instance}:: ")
            if not session_instance.is_active:
                pass
                self.cmn_logger.info(
                    f"Session of Session-Id {session_instance} which is not active or already closed:: [SUCCESS]"
                )
            else:
                session_instance.close()
                self.cmn_logger.info(
                    f"Closed session of Session-Id {session_instance}:: "
                )
            return True
        except Exception as ex:
            self.cmn_logger.error(
                f"{ex} error occurred while Closing the  session \tLine No:: {sys.exc_info()[2].tb_lineno}"
            )
            return None
