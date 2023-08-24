# ID = Column(BigInteger, Sequence('aeroplane_id_seq',start=2000), primary_key=True)
# UserID = Column(BigInteger, ForeignKey('Users.ID'), unique=True, nullable=False)
# Token = Column(String(255), nullable=False)
# Expiry = Column(String(255), nullable=False)
# CreatedAt = Column(String(255), nullable=False)
# UpdatedAt = Column(String(255), nullable=False)

import sys
import datetime,bcrypt
from flask_jwt_extended import create_access_token


class Token:
    token_type = "bearer"
    expiry =  10000
    created_at = str(datetime.datetime.now())
    updated_at = str(datetime.datetime.now())
    custom_access_token = None

    def __init__(self, user_id, user_name, pwd):
        self.user_id = user_id
        self.user_name = user_name
        self.pwd = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())

    def generate_custom_token(self):
        my_identity = self.user_id
        generated_token = create_access_token(identity=my_identity)
        return generated_token

    @classmethod
    def create_custom_token(cls, user_id, user_name, pwd):
        token_instance = cls(user_id, user_name, pwd)
        custom_access_token = token_instance.generate_custom_token()
        token_instance.custom_access_token = custom_access_token
        return token_instance

    @staticmethod
    def convert_db_model_to_response(model_instance):
        print("<<<<<>>>>>>", model_instance, type(model_instance))
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
        succ_res_dict = {}
        try:
            succ_res_dict.update({'message': 'Token  is created'})
            succ_res_dict.update(
                {
                    "token":{
                            'accessToken': token_instance['data']['Token'],
                            'expiresIn': token_instance['data']['Expiry']
                            # 'tokenType': token_instance['']
                    }
                }
            )
        except Exception as ex:
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return succ_res_dict

