import json
import sys
import datetime
import bcrypt
from src.usermanagement_service import user_management_app_logger


class User:
    def __init__(self, username=None, firstname=None, lastname=None, dateofbirth=None, email=None, pwd=None):
        user_management_app_logger.info("Initialising User object ...")
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.dateofbirth = dateofbirth
        self.email = email
        self.pwd = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())
        self.created_at = str(datetime.datetime.now())
        self.updated_at = str(datetime.datetime.now())
        user_management_app_logger.info("Initialised User object ...")

    def create_user(self):
        user_obj = None
        try:
            user_management_app_logger.info("Received :: username :: {0}, firstname :: {1}, lastname :: {2}, emailaddress :: {3}, dateofbirth :: {4}".format(
                    self.username, self.firstname, self.lastname, self.email, self.dateofbirth))
            user_obj = {
                "username": self.username,
                "firstname": self.firstname,
                "lastname": self.lastname,
                "password": self.pwd,
                "email": self.email,
                "dateofbirth": self.dateofbirth,
                "created_at": self.created_at,
                "updated_at": self.updated_at
            }
            user_management_app_logger.info("Returning :: {0} , ID :: {1}".format(user_obj, id(user_obj)))
            user_management_app_logger.info("Instance creation for User :: [SUCCESS] :: {0}".format(user_obj))
        except Exception as ex:
            user_management_app_logger.error("Instance creation for User :: [FAILED] :: {0}".format(user_obj))
            user_management_app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return user_obj

    @staticmethod
    def convert_db_model_to_resp(model_instance):
        user_management_app_logger.info("Converting db model to response obj :: [STARTED]")
        model_dict = {}
        try:
            model_dict['data'] = {col.name: getattr(model_instance, col.name) for col in
                                  model_instance.__table__.columns}
            if 'CreatedAtTime' in model_dict['data'].keys():
                model_dict['data']['CreatedAtTime'] = model_dict['data']['CreatedAtTime']
            if 'UpdatedAtTime' in model_dict['data'].keys():
                model_dict['data']['UpdatedAtTime'] = model_dict['data']['UpdatedAtTime']
            model_dict.update({"message": ""})
            user_management_app_logger.info("Converting db model to response obj :: [SUCCESS]")
        except Exception as ex:
            user_management_app_logger.error("Converting db model to response obj :: [FAILED]")
            user_management_app_logger.error(
                "Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return model_dict

    @staticmethod
    def generate_custom_response_body(user_instance, messagedata):
        user_management_app_logger.info("Generating Success response  :: [STARTED] :: {0}".format(user_instance))
        succ_res_dict = {}
        try:
            if len(user_instance.keys()) < 0:
                succ_res_dict.update({'message': messagedata})
                succ_res_dict.update(
                    {
                        'user': {
                            'userId': user_instance['data']['ID'],
                            'username': user_instance['data']['Username'],
                            'email': user_instance['data']['Email'],
                            'dateOfBirth': user_instance['data']['DateOfBirth'],
                            'firstName': user_instance['data']['FirstName'],
                            'lastName': user_instance['data']['LastName'],
                            'CreatedAt': user_instance['data']['CreatedAt'].strftime("%Y-%m-%d %H:%M:%S"),
                            'UpdatedAt': user_instance['data']['UpdatedAt'].strftime("%Y-%m-%d %H:%M:%S"),
                        }
                    }
                )
                succ_res_json_obj = json.dumps(succ_res_dict)
                user_management_app_logger.info("Generating Success response  :: [SUCCESS] :: {0}".format(succ_res_json_obj))
        except Exception as ex:
            user_management_app_logger.error("Generating Success response  :: [FAILED]")
            user_management_app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return succ_res_dict
