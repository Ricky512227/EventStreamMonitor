from src.airliner_service.aeroplane.aeroplane import AeroPlane
from src.app import airliner_logger
import sys


def add_aeroplane(airlines_name, airlines_type, maker, model, seating_capacity, fuel_capacity):
    airplane_obj = None
    try:
        airliner_logger.info("Received :: airlines_name :: {0}, airlines_type :: {1}, maker :: {2}, model :: {3}, seating_capacity :: {4}, fuel_capacity :: {5}".format(airlines_name, airlines_type, maker, model, seating_capacity, fuel_capacity))
        airplane_obj = AeroPlane(airlines_name, airlines_type, maker, model, seating_capacity, fuel_capacity)
        airliner_logger.info("Returning :: {0} , ID :: {1}".format(airplane_obj, id(airplane_obj)))
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        airliner_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
    return airplane_obj





def generate_success_aero_response(aero_map_db_instance):
    succ_aero_res_dict = {}
    try:
        succ_aero_res_dict.update({'message': 'AeroPlane  is created'})
        succ_aero_res_dict.update(
            {
                'data': {
                    'AirlineID': aero_map_db_instance.AeroPlaneID,
                    'AirlinesName': aero_map_db_instance.AeroPlaneName,
                    'AirlineType': aero_map_db_instance.AeroPlaneType,
                    'Maker': aero_map_db_instance.AeroPlaneMaker,
                    'Model': aero_map_db_instance.AeroPlaneModel,
                    'SeatingCapacity': aero_map_db_instance.SeatingCapacity,
                    'FuelCapacity': aero_map_db_instance.FuelCapacity,
                    'CreatedAt': aero_map_db_instance.CreatedAtTime,
                    'UpdatedAt':aero_map_db_instance.UpdatedAtTime,
                }
            }
        )
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        airliner_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
    return succ_aero_res_dict
#

def convert_db_model_to_response(model_instance):
    model_dict= {}
    model_dict['data'] = {col.name: getattr(model_instance, col.name) for col in model_instance.__table__.columns}
    if 'CreatedAtTime' in model_dict['data'].keys():
        model_dict['data']['CreatedAtTime'] = str(model_dict['data']['CreatedAtTime'])
    if 'UpdatedAtTime' in model_dict['data'].keys():
        model_dict['data']['UpdatedAtTime'] = str(model_dict['data']['UpdatedAtTime'])
    model_dict.update({"message": ""})
    return model_dict



