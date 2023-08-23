import sys
import jsonschema
from src.registration_service import registration_app_logger

def generate_req_missing_params(rec_req_params, schema_data):
    missing_params_err_obj = {}
    for key, value in rec_req_params.items():
        registration_app_logger.debug("REQUEST <==> params ==> Param :: {0} :: Value :: {1} :: Type ::{2} ".format(key, value, type(value)))
    try:
        jsonschema.validate(instance=rec_req_params, schema=schema_data)
    except jsonschema.exceptions.ValidationError as ex:
        registration_app_logger.info("Checking the data and do validations...")
        # Get the list of required properties from the schema
        required_properties = schema_data.get("required", [])
        registration_app_logger.info("Required_Properties_As_Per_Schema :: {0}".format(required_properties))
        # Get the list of missing required properties from the validation error
        missing_params = [property_name for property_name in required_properties if property_name not in ex.instance]
        registration_app_logger.info("Missing params found :: {0}".format(missing_params))
        missing_params_err_obj = {'details': {'params': missing_params}}
        registration_app_logger.info("Packing message for missing property which are found :: {0}".format(missing_params))
    return missing_params_err_obj

