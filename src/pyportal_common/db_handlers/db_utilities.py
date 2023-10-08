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
from sqlalchemy.orm import sessionmaker

def get_session_from_pool(session_maker_to_get_session: sessionmaker) -> Union[sqlalchemy.orm.Session, None]:
    try:
        if not session_maker_to_get_session:
            # self.cmn_logger.info(
            #     "Fetching session using pool of connections  :: [FAILED]"
            # )
            return None
        else:
            # self.display_pool_info(
            #     connection_pool=session_maker_to_get_session.kw["bind"].pool
            # )
            # self.cmn_logger.info(
            #     "Fetching session using pool of connections :: [STARTED]"
            # )
            session_instance = session_maker_to_get_session()
            # self.cmn_logger.info(
            #     "Fetching session using pool of connections :: [SUCCESS]"
            # )
            return session_instance
    except (ArgumentError, UnboundExecutionError, OperationalError, TimeoutError, DatabaseError) as ex:
        print (f"{ex} error occurred while Fetching session using pool of connections \tLine No:: {sys.exc_info()[2].tb_lineno}")
        return None

def close_session(session_instance: sqlalchemy.orm.Session) -> Union[bool, None]:
    try:
        # self.cmn_logger.info(f"Closing the  session  {session_instance}:: ")
        if not session_instance.is_active:
            pass
            # self.cmn_logger.info(
            #     f"Session of Session-Id {session_instance} which is not active or already closed:: [SUCCESS]"
            # )
        else:
            session_instance.close()
            # self.cmn_logger.info(
            #     f"Closed session of Session-Id {session_instance}:: "
            # )
        return True
    except Exception as ex:
        # self.cmn_logger.error(
        #     f"{ex} error occurred while Closing the  session \tLine No:: {sys.exc_info()[2].tb_lineno}"
        # )
        return None

