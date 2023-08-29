from src.registration_service.registration_service import registration_app_logger
import sys

def generate_success_user_response(user_map_db_instance):
    succ_user_res_dict = {}
    try:
        succ_user_res_dict.update({'message': 'User  is created'})
        succ_user_res_dict.update(
            {
                'user': {
                    'userId': user_map_db_instance.UserID,
                    'username': user_map_db_instance.UserName,
                    'email': user_map_db_instance.EmailAddress,
                    'firstName': user_map_db_instance.FirstName,
                    'lastName': user_map_db_instance.LastName,
                    'CreatedAt': user_map_db_instance.CreatedAtTime,
                    'UpdatedAt':user_map_db_instance.UpdatedAtTime,
                }
            }
        )
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        registration_app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
    return succ_user_res_dict
#

def convert_db_model_to_response(model_instance):
    model_dict= {}
    try:
        model_dict['data'] = {col.name: getattr(model_instance, col.name) for col in model_instance.__table__.columns}
        if 'CreatedAtTime' in model_dict['data'].keys():
            model_dict['data']['CreatedAtTime'] = str(model_dict['data']['CreatedAtTime'])
        if 'UpdatedAtTime' in model_dict['data'].keys():
            model_dict['data']['UpdatedAtTime'] = str(model_dict['data']['UpdatedAtTime'])
        model_dict.update({"message": ""})
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        registration_app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
    return model_dict


