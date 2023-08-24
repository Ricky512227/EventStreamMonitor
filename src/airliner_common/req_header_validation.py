import sys
import jsonschema


def generate_req_missing_params(rec_req_params, schema_data):
    missing_params_err_obj = {}
    try:
        for key, value in rec_req_params.items():
            print("REQUEST <==> params ==> Param :: {0} :: Value :: {1} :: Type ::{2} ".format(key, value, type(value)))
        try:
            jsonschema.validate(instance=rec_req_params, schema=schema_data)
        except jsonschema.exceptions.ValidationError as ex:
            print("Checking the data and do validations...")
            # Get the list of required properties from the schema
            required_properties = schema_data.get("required", [])
            print("Required_Properties_As_Per_Schema :: {0}".format(required_properties))
            # Get the list of missing required properties from the validation error
            missing_params = [property_name for property_name in required_properties if property_name not in ex.instance]
            print("Missing params found :: {0}".format(missing_params))
            missing_params_err_obj = {'details': {'params': missing_params}}
            print("Packing message for missing property which are found :: {0}".format(missing_params))
        return missing_params_err_obj
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return missing_params_err_obj

