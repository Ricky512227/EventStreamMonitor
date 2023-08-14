import os,sys
import jsonschema

def generate_req_missing_params(rec_req_params, aeroplane_req_headers_schema):
    missing_params_err_obj = {}
    try:
        jsonschema.validate(instance=rec_req_params, schema=aeroplane_req_headers_schema)
    except jsonschema.exceptions.ValidationError as ex:
        # Get the list of required properties from the schema
        required_properties = aeroplane_req_headers_schema.get("required", [])
        # print("Required_Properties_As_Per_Schema :: {0}".format(required_properties))
        # Get the list of missing required properties from the validation error
        missing_params = [property_name for property_name in required_properties if property_name not in ex.instance]
        print("Missing params found :: {0}".format(missing_params))
        missing_params_err_obj = {'details': {'params': missing_params}}
        print("Packing message for missing property which are found :: {0}".format(missing_params))
    except Exception as ex:
        print('Error occurred :: {0} \tLine No: {1}'.format(ex, sys.exc_info()[2].tb_lineno))
    return missing_params_err_obj