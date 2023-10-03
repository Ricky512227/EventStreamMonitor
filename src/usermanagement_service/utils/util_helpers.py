import sys
from sqlalchemy import or_
import sqlalchemy.orm.exc
from src.usermanagement_service.models.user_model import UsersModel
from src.usermanagement_service import user_management_logger


def is_userid_exists(session_instance: sqlalchemy.orm.Session, userid) -> tuple[int, bool]:
    user_management_logger.info("Querying Userid in the Database to check the if user exists :: {0}".format(userid))
    is_user_exists_status = False
    try:
        user_row = session_instance.query(UsersModel).get(userid)
        if user_row is not None:
            is_user_exists_status = True
            user_management_logger.info("Result for the Query Response :: {0} - {1}".format(userid, is_user_exists_status))
        else:
            user_management_logger.info("Result for the Query Response :: {0} - {1}".format(userid, is_user_exists_status))
    except sqlalchemy.orm.exc.NoResultFound as ex:
        user_management_logger.error("Result for the Query Response :: {0}".format(False))
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
    return userid, is_user_exists_status


def is_username_email_already_exists_in_db(session_instance, uname: str, email: str) -> bool:
    is_username_email_already_exists_status = False
    user_management_logger.info("Querying UserName :: {0} , Email :: {1} in the Database to check the if already exists :: ".format(uname, email))
    try:
        user_row = session_instance.query(UsersModel).filter(or_(UsersModel.Username == uname, UsersModel.Email == email)).first()
        if user_row is not None:
            is_username_email_already_exists_status = True
            user_management_logger.info("Result for the Query Response :: {0}".format(is_username_email_already_exists_status))
            return is_username_email_already_exists_status
        else:
            user_management_logger.info("Result for the Query Response :: {0}".format(is_username_email_already_exists_status))
    except sqlalchemy.orm.exc.NoResultFound as ex:
        user_management_logger.error("Result for the Query Response :: {0}".format(False))
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
    return is_username_email_already_exists_status


def convert_db_model_to_resp(model_instance):
    user_management_logger.info("Converting db model to response obj :: [STARTED]")
    model_dict = {}
    try:
        model_dict['data'] = {col.name: getattr(model_instance, col.name) for col in model_instance.__table__.columns}
        if 'CreatedAtTime' in model_dict['data'].keys():
            model_dict['data']['CreatedAtTime'] = model_dict['data']['CreatedAtTime']
        if 'UpdatedAtTime' in model_dict['data'].keys():
            model_dict['data']['UpdatedAtTime'] = model_dict['data']['UpdatedAtTime']
        model_dict.update({"message": ""})
        user_management_logger.info("Converting db model to response obj :: [SUCCESS]")
    except Exception as ex:
        user_management_logger.error("Converting db model to response obj :: [FAILED]")
        user_management_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
    return model_dict


