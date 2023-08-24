import sys
import datetime,bcrypt
from src.registration_service import registration_app_logger
class User:
    def __init__(self, username=None, firstname=None, lastname=None, dateofbirth=None, email=None, pwd=None):
        registration_app_logger.info("Initialising User object ...")
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.dateofbirth = dateofbirth
        self.email = email
        self.pwd = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())
        self.created_at = str(datetime.datetime.now())
        self.updated_at = str(datetime.datetime.now())
        self.user_obj = None
        registration_app_logger.info("Initialised User object ...")

    def add_user(self):
        try:
            registration_app_logger.info("Received :: username :: {0}, firstname :: {1}, lastname :: {2}, emailaddress :: {3}, dateofbirth :: {4}".format(self.username, self.firstname, self.lastname, self.email, self.dateofbirth))
            self.user_obj = {
                "username": self.username,
                "firstname": self.firstname,
                "lastname": self.lastname,
                "password": self.pwd,
                "email": self.email,
                "dateofbirth": self.dateofbirth,
                "created_at" : self.created_at,
                "updated_at" : self.updated_at
            }
            registration_app_logger.info("Returning :: {0} , ID :: {1}".format(self.user_obj, id(self.user_obj)))
            registration_app_logger.info("Instance creation for User :: [SUCCESS] :: {0}".format(self.user_obj))
        except Exception as ex:
            registration_app_logger.info("Instance creation for User :: [FAILED] :: {0}".format(self.user_obj))
            registration_app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return self.user_obj

    @staticmethod
    def convert_db_model_to_response(model_instance):
        registration_app_logger.info("Converting db model to response obj :: [STARTED]")
        model_dict = {}
        try:
            model_dict['data'] = {col.name: getattr(model_instance, col.name) for col in model_instance.__table__.columns}
            if 'CreatedAtTime' in model_dict['data'].keys():
                model_dict['data']['CreatedAtTime'] = str(model_dict['data']['CreatedAtTime'])
            if 'UpdatedAtTime' in model_dict['data'].keys():
                model_dict['data']['UpdatedAtTime'] = str(model_dict['data']['UpdatedAtTime'])
            model_dict.update({"message": ""})
            registration_app_logger.info("Converting db model to response obj :: [SUCCESS]")
        except Exception as ex:
            registration_app_logger.info("Converting db model to response obj :: [FAILED]")
            registration_app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return model_dict

    @staticmethod
    def generate_success_response(user_instance):
        registration_app_logger.info("Generating Success response  :: [STARTED]")
        succ_res_dict = {}
        try:
            succ_res_dict.update({'message': 'User  is created'})
            succ_res_dict.update(
                {
                    'user': {
                        'userId': user_instance['data']['ID'],
                        'username': user_instance['data']['Username'],
                        'email': user_instance['data']['Email'],
                        'dateOfBirth': user_instance['data']['DateOfBirth'],
                        'firstName': user_instance['data']['FirstName'],
                        'lastName': user_instance['data']['LastName'],
                        'CreatedAt': user_instance['data']['CreatedAt'],
                        'UpdatedAt': user_instance['data']['UpdatedAt'],
                    }
                }
            )
            registration_app_logger.info("Generating Success response  :: [SUCCESS]")
        except Exception as ex:
            registration_app_logger.info("Generating Success response  :: [FAILED]")
            registration_app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return succ_res_dict
