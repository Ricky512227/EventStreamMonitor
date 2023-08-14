import sys
import datetime,bcrypt
from flask_jwt_extended import create_access_token
class Token:
    token_type = "bearer"
    expiry = 3500000
    created_at = str(datetime.datetime.now())
    updated_at = str(datetime.datetime.now())
    custom_access_token = None

    def __init__(self, user_id, user_name, pwd):
        self.user_id = user_id
        self.user_name = user_name
        self.pwd = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())


    @classmethod
    def create_custom_token(cls, user_id, user_name, pwd):
        token_instance = cls(user_id, user_name, pwd)
        custom_access_token = token_instance.generate_custom_token()
        token_instance.custom_access_token = custom_access_token
        return token_instance


    def generate_custom_token(self):
        my_identity = self.user_id
        generated_token = create_access_token(identity=my_identity)
        return generated_token

    @staticmethod
    def convert_db_model_to_response(model_instance):
        model_dict = {}
        model_dict['data'] = {col.name: getattr(model_instance, col.name) for col in model_instance.__table__.columns}
        if 'CreatedAtTime' in model_dict['data'].keys():
            model_dict['data']['CreatedAtTime'] = str(model_dict['data']['CreatedAtTime'])
        if 'UpdatedAtTime' in model_dict['data'].keys():
            model_dict['data']['UpdatedAtTime'] = str(model_dict['data']['UpdatedAtTime'])
        model_dict.update({"message": ""})
        return model_dict

    @staticmethod
    def generate_success_response(token_instance):
        print(token_instance)
        succ_res_dict = {}
        try:
            succ_res_dict.update({'message': 'Token  is created'})
            succ_res_dict.update(
                {
                    'accessToken': token_instance['TokenID'],
                    'expiresIn': token_instance['Expiry']
                    # 'tokenType': token_instance['']
                }
            )
        except Exception as ex:
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return succ_res_dict

