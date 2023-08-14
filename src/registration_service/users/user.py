import sys
import datetime,bcrypt
class User:
    created_at = str(datetime.datetime.now())
    updated_at = str(datetime.datetime.now())

    def __init__(self, username=None, firstname=None, lastname=None, dateofbirth=None, email=None, pwd=None):
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.dateofbirth = dateofbirth
        self.email = email
        self.pwd = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())

    @classmethod
    def add_user(cls, username, firstname, lastname, dateofbirth, email, pwd):
        user_obj = None
        try:
            print("Received :: username :: {0}, firstname :: {1}, lastname :: {2}, emailaddress :: {3}, password :: {4}, dateofbirth :: {5}".format(username, firstname, lastname, email, pwd, dateofbirth))
            user_obj = cls(username, firstname, lastname, dateofbirth, email, pwd)
            print("Returning :: {0} , ID :: {1}".format(user_obj, id(user_obj)))
        except Exception as ex:
            # user_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex,sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return user_obj

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
    def generate_success_response(user_instance):
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
        except Exception as ex:
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            # user_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return succ_res_dict

    def __repr__(self):
        return f"UserName :: {self.username},FirstName :: {self.firstname}," \
               f" LastName :: {self.lastname}, Emailaddress :: {self.email} , Password :: {self.pwd}," \
               f" CreatedAt :: {self.created_at}, UpdatedAt :: {self.updated_at}"
