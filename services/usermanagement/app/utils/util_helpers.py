import sys
from typing import Union
from sqlalchemy import or_
import sqlalchemy.orm.exc
from app.models.user_model import UsersModel
from app import user_management_logger


def is_userid_exists_in_db(session_instance, userid) -> tuple[int, Union[bool, None]]:
    user_management_logger.info(f"Querying Userid in the Database to check the if user exists :: {userid}")
    is_user_exists = False
    try:
        user_row = session_instance.query(UsersModel).get(userid)
        if user_row is not None:
            is_user_exists = True
        else:
            is_user_exists = False
        user_management_logger.info(f"Result for the Query Response :: {userid} - {is_user_exists}")
        return userid, is_user_exists
    except sqlalchemy.orm.exc.NoResultFound as ex:
        user_management_logger.error(f"Result for the Query Response :: {userid} - {is_user_exists}")
        user_management_logger.exception(f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}")
        return userid, None


def is_username_email_already_exists_in_db(session_instance, uname: str, email: str) -> Union[bool, None]:
    user_management_logger.info(f"Querying UserName :: %s , Email :: %s in the Database to check the if already exists :: ",uname, email)
    try:
        user_row = (session_instance.query(UsersModel).filter(or_(UsersModel.Username == uname, UsersModel.Email == email)).first())
        if user_row is None:
            is_username_email_already_exists = False
        else:
            is_username_email_already_exists = True
        user_management_logger.info(f"Result for the Query Response %s :: ",is_username_email_already_exists)
        return is_username_email_already_exists
    except sqlalchemy.orm.exc.NoResultFound as ex:
        user_management_logger.error(f"Result for the Query Response :: {False}")
        return None



def convert_db_model_to_resp(model_instance: object) -> dict:
    user_management_logger.info("Converting db model to response obj :: [STARTED]")
    model_dict = {}
    try:
        model_dict["data"] = {
            col.name: getattr(model_instance, col.name)
            for col in model_instance.__table__.columns
        }
        if "CreatedAtTime" in model_dict["data"].keys():
            model_dict["data"]["CreatedAtTime"] = model_dict["data"]["CreatedAtTime"]
        if "UpdatedAtTime" in model_dict["data"].keys():
            model_dict["data"]["UpdatedAtTime"] = model_dict["data"]["UpdatedAtTime"]
        model_dict.update({"message": ""})
        user_management_logger.info("Converting db model to response obj :: [SUCCESS]")
    except Exception as ex:
        user_management_logger.error("Converting db model to response obj :: [FAILED]")
        user_management_logger.error(
            f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
        )
        user_management_logger.error(
            f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}"
        )
    return model_dict
