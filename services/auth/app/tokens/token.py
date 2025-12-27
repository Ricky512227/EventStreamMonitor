import sys
import datetime,bcrypt
from flask_jwt_extended import create_access_token
from app import token_management_logger
from common.pyportal_common.utils import sanitize_sensitive_data


class Token:
    token_type = "bearer"
    expiry = 10000
    def __init__(self, user_id=None, user_name=None, pwd=None):
        self.user_id = user_id
        self.user_name = user_name
        self.pwd = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())
        self.created_at = str(datetime.datetime.now())
        self.updated_at = str(datetime.datetime.now())
        self.user_cus_token = None
        self.token_obj = None

    def generate_custom_token(self):
        try:
            self.user_cus_token = create_access_token(identity=self.user_id)
        except Exception as ex:
            token_management_logger.error(f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}")
        return self.user_cus_token

    def add_token(self):
        try:
            token_management_logger.info(f"Received :: userid :: {self.user_id}, username :: {self.user_name}, created_at :: {self.created_at}, updated_at :: {self.updated_at}")

            self.token_obj = {
                            "userid": self.user_id,
                            "username": self.user_name,
                            "token" :  self.generate_custom_token(),
                            "created_at": self.created_at,
                            "updated_at": self.updated_at,
                            "token_type" : "bearer",
                            "expiry" : 10000
            }
            # Security: Sanitize token object before logging
            sanitized_token_obj = sanitize_sensitive_data(self.token_obj)
            token_management_logger.info(f"Returning :: {sanitized_token_obj} , ID :: {id(self.token_obj)}")
            token_management_logger.info(f"Instance creation for User :: [SUCCESS] :: {sanitized_token_obj}")
        except Exception as ex:
            # Security: Sanitize token object before logging even on failure
            sanitized_token_obj = sanitize_sensitive_data(self.token_obj) if self.token_obj else None
            token_management_logger.info(f"Instance creation for Token :: [FAILED] :: {sanitized_token_obj}")
            token_management_logger.error(f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}")
        return self.token_obj

    @staticmethod
    def convert_db_model_to_response(model_instance):
        token_management_logger.info("Converting db model to response obj :: [STARTED]")
        model_dict = {}
        try:
            model_dict['data'] = {col.name: getattr(model_instance, col.name) for col in model_instance.__table__.columns}
            if 'CreatedAtTime' in model_dict['data'].keys():
                model_dict['data']['CreatedAtTime'] = str(model_dict['data']['CreatedAtTime'])
            if 'UpdatedAtTime' in model_dict['data'].keys():
                model_dict['data']['UpdatedAtTime'] = str(model_dict['data']['UpdatedAtTime'])
            model_dict.update({"message": ""})
            token_management_logger.info("Converting db model to response obj :: [SUCCESS]")
        except Exception as ex:
            token_management_logger.info("Converting db model to response obj :: [FAILED]")
            token_management_logger.error(f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}")
        return model_dict

    @staticmethod
    def generate_success_response(token_instance, token_message):
        token_management_logger.info("Generating Success response  :: [STARTED]")
        succ_res_dict = {}
        try:
            succ_res_dict.update({'message': token_message})
            succ_res_dict.update(
                {
                    "token":{
                            'accessToken': token_instance['data']['Token'],
                            'expiresIn': token_instance['data']['Expiry']
                            # 'tokenType': token_instance['']
                    }
                }
            )
            token_management_logger.info("Generating Success response  :: [SUCCESS]")
        except Exception as ex:
            token_management_logger.info("Generating Success response  :: [FAILED]")
            token_management_logger.error(f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}")
        return succ_res_dict

