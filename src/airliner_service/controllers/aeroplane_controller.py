import sys
import jsonschema
from sqlalchemy.exc import SQLAlchemyError
from flask import jsonify, request, abort
from src.airliner_common.common_utility import generate_req_missing_params
from src.airliner_common.database import create_airliner_session
from src.airliner_service.utils.aeroservices import add_aeroplane, generate_success_aero_response,convert_db_model_to_response
from src.airliner_service.models.airliner_model import AerPlaneDBModel
from src.app import airliner_logger, airliner_app, airliner_db_engine,airliner_pool, loaded_req_headers_schema,\
    loaded_aero_create_req_body_schema, loaded_aero_res_body_schema
from src.airliner_cls.ailiner_error_handling import AirlinerSchemaValidationError

@airliner_app.errorhandler(400)
def bad_request(error_data):
    airliner_logger.info("Preparing Err_response :: {0}".format(error_data))
    err_message = error_data.description['message']
    err_details = error_data.description['details']
    error_res_obj = AirlinerSchemaValidationError(message=err_message, error_details=err_details)
    airliner_logger.debug("Response ID of Final Response:: {0}".format(id(error_res_obj.to_dict())))
    airliner_logger.info("Prepared Final Response  and sent to Client:: {0}".format(error_res_obj.to_dict()))
    return jsonify(error_res_obj.to_dict()), 400

@airliner_app.errorhandler(500)
def internal_server_error(error_data):
    airliner_logger.info("Preparing Err_response :: {0}".format(error_data))
    err_message = error_data.description['message']
    err_details = error_data.description['details']
    error_res_obj = AirlinerSchemaValidationError(message=err_message, error_details=err_details)
    airliner_logger.debug("Response ID of Final Response:: {0}".format(id(error_res_obj.to_dict())))
    airliner_logger.info("Prepared Final Response  and sent to Client:: {0}".format(error_res_obj.to_dict()))
    return jsonify(error_res_obj.to_dict()), 500

# Event listener to display pool info before creating a session
@airliner_app.errorhandler(404)
def not_found(error_data):
    return jsonify({"status": 404, "message": "Not Found"}), 404



def create_aeroplane():
    airliner_logger.info('REQUEST ==> Received Endpoint :: /api/v1/airliner/aeroplane')
    rec_req_headers = dict(request.headers)
    airliner_logger.info("Received Headers from the request :: {0}".format(rec_req_headers))
    airliner_logger.info("Validation for Request-Header is  :: [STARTED]")
    err_result = generate_req_missing_params(rec_req_headers, loaded_req_headers_schema)
    if len(err_result.keys()) == 0:
        airliner_logger.info("Validation for Request-Header is  :: [SUCCESS]")
        for header_key, header_value in rec_req_headers.items():
            airliner_logger.debug("REQUEST <==> HEADER.params ==> Param :: {0} :: Value :: {1} :: Type ::{2} ".format(header_key, header_value,type(header_value)))
        if request.method == 'POST':
            rec_req_data = request.get_json()
            airliner_logger.info("Validation for Request-Body is  :: [STARTED]")
            err_result = generate_req_missing_params(rec_req_data, loaded_aero_create_req_body_schema)
            if len(err_result.keys()) == 0:
                airliner_logger.info("Validation for Request-body is  :: [SUCCESS]")
                for data_key, data_value in rec_req_data.items():
                    airliner_logger.debug("REQUEST <==> BODY.params ==> Param :: {0} :: Value :: {1} :: Type ::{2} ".format(data_key, data_value, type(data_value)))
                airlines_name = rec_req_data['AeroPlaneName']
                airlines_type = rec_req_data['AeroPlaneType']
                maker = rec_req_data['AeroPlaneMaker']
                model = rec_req_data['AeroPlaneModel']
                seating_capacity = rec_req_data['SeatingCapacity']
                fuel_capacity = rec_req_data['FuelCapacity']
                try:
                    airliner_logger.info("Processing the request data... :: [STARTED]")
                    airplane_obj = add_aeroplane(airlines_name, airlines_type, maker, model, seating_capacity,fuel_capacity)
                    airliner_logger.info("Instance creation for Aeroplane :: [SUCCESS] :: {0}".format(airplane_obj))
                    airliner_logger.info("Mapping the request data to the database model:: [STARTED]")
                    aero_map_db_instance = AerPlaneDBModel(
                                                            AeroPlaneName= airplane_obj.airlines_name,
                                                            AeroPlaneType= airplane_obj.airlines_type,
                                                            AeroPlaneMaker= airplane_obj.maker,
                                                            AeroPlaneModel= airplane_obj.model,
                                                            SeatingCapacity= airplane_obj.seating_capacity,
                                                            FuelCapacity= airplane_obj.fuel_capacity,
                                                            CreatedAtTime= airplane_obj.created_at,
                                                            UpdatedAtTime= airplane_obj.updated_at)
                    airliner_logger.info("Mapping the request data to the database model:: [SUCCESS]")
                    aero_session = create_airliner_session(airliner_logger, airliner_pool, airliner_db_engine)
                    if aero_session is not None:
                        try:
                            aero_session.add(aero_map_db_instance)
                            airliner_logger.info("Data added into  DataBase session {0}:: SUCCESS".format(aero_map_db_instance))
                            aero_session.commit()  # Commit the change
                            airliner_logger.info("Added Data is committed into  DataBase {0}:: SUCCESS".format(aero_session))
                            #print("Commit the  changes  {0}:: SUCCESS".format(aero_session))
                            airliner_logger.info("Generating Success response  :: [STARTED]")
                            success_aero_response = generate_success_aero_response(aero_map_db_instance)
                            airliner_logger.info("Generating Success response  :: [STARTED] :: {0}".format(success_aero_response))
                            return jsonify(success_aero_response), 201

                        except SQLAlchemyError as ex:
                            aero_session.rollback()
                            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
                            abort(500, description={'message': 'Create AeroPlane Failed', 'details': {'params': ex}})

                        except Exception as ex:
                            aero_session.rollback()
                            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
                            abort(500, description={'message': 'Create AeroPlane Failed', 'details': {'params': str(ex)}})
                        finally:
                            print("Closing the  session  {0}:: [STARTED]".format(aero_session))
                            aero_session.close()  # Close the change
                            print("Closed the  session  {0}:: [SUCCESS]".format(aero_session))
                except Exception as ex:
                    airliner_logger.error("Instance creation for Aeroplane :: [FAILED] :: {0}".format(ex))
                    abort(500, description={'message': 'Create AeroPlane Failed', 'details': {'params': str(ex)}})
            else:
                airliner_logger.error("Validation for Request-Data is  :: [FAILED]")
                err_result["message"] = 'Request data of params missing'
                airliner_logger.info("Sending Error response back to client :: {0}".format(err_result))
                abort(400, description=err_result)
    else:
        airliner_logger.error("Validation for Request-Header is  :: [FAILED]")
        err_result["message"]= "Request Header Missing"
        airliner_logger.info("Sending Error response back to client :: {0}".format(err_result))
        abort(400, description=err_result)


def get_Aeroplane(aeroplane_id):
    airliner_logger.info('Received Endpoint :: /api/v1/airliner/getAeroplanes/{0}'.format(aeroplane_id))
    airliner_logger.info('Received Header :: {0}'.format(request.method))
    airliner_logger.info('Received Value in the URL :: {0}'.format(aeroplane_id))
    rec_req_headers = dict(request.headers)
    err_result = generate_req_missing_params(rec_req_headers, loaded_req_headers_schema)
    if len(err_result.keys()) == 0:
        airliner_logger.info("Validation for Request-Header is  :: [SUCCESS]")
        for header_key, header_value in rec_req_headers.items():
            airliner_logger.debug("REQUEST <==> HEADER.params ==> Param :: {0} :: Value :: {1} :: Type ::{2} ".format(header_key,header_value,type(header_value)))
        if request.method == 'GET':
            aero_session = create_airliner_session(airliner_logger, airliner_pool, airliner_db_engine)
            if aero_session is not None:
                try:
                    aero_map_db_instance = aero_session.query(AerPlaneDBModel).get(aeroplane_id)
                    obj = convert_db_model_to_response(aero_map_db_instance)
                    obj["message"] = "Retrevied the AeroPlane"
                    jsonschema.validate(obj, loaded_aero_res_body_schema)
                    airliner_logger.info("Generating Success response  :: [STARTED] :: {0}".format(obj))

                    success_aero_response = obj
                    airliner_logger.info("Generating Success response  :: [STARTED] :: {0}".format(success_aero_response))
                    return jsonify(success_aero_response), 200



                except SQLAlchemyError as ex:
                    aero_session.rollback()
                    print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
                    abort(500, description={'message': 'Create AeroPlane Failed', 'details': {'params': ex}})

                except Exception as ex:
                    aero_session.rollback()
                    print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
                    abort(500, description={'message': 'Retrived AeroPlane Failed', 'details': {'params': str(ex)}})
                finally:
                    print("Closing the  session  {0}:: [STARTED]".format(aero_session))
                    aero_session.close()  # Close the change
                    print("Closed the  session  {0}:: [SUCCESS]".format(aero_session))

    else:
        airliner_logger.error("Validation for Request-Header is  :: [FAILED]")
        err_result["message"]= "Request Header Missing"
        airliner_logger.info("Sending Error response back to client :: {0}".format(err_result))
        abort(400, description=err_result)


