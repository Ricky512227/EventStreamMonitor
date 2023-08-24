import sys
from sqlalchemy.exc import SQLAlchemyError
from flask import jsonify, request, abort
from src.registration_service.users.user import User
from src.registration_service.models.user_model import UsersModel
from src.airliner_common.req_header_validation import generate_req_missing_params
from src.registration_service import registration_app_logger, req_headers_schema, reg_user_req_schema, res_app_obj

def add_user():
    registration_app_logger.info('REQUEST ==> Received Endpoint :: {0}'.format(request.endpoint))
    rec_req_headers = dict(request.headers)
    registration_app_logger.info("Received Headers from the request :: {0}".format(rec_req_headers))
    registration_app_logger.info("Validation for Request-Header is  :: [STARTED]")
    result = generate_req_missing_params(rec_req_headers, req_headers_schema)
    if len(result.keys()) == 0:
        registration_app_logger.info("Validation for Request-Header is  :: [SUCCESS]")
        if request.method == 'POST':
            rec_req_data = request.get_json()
            registration_app_logger.info("Validation for Request-Body is  :: [STARTED]")
            result = generate_req_missing_params(rec_req_data, reg_user_req_schema)
            if len(result.keys()) == 0:
                registration_app_logger.info("Validation for Request-body is  :: [SUCCESS]")
                username = rec_req_data['username']
                firstname = rec_req_data['firstName']
                lastname = rec_req_data['lastName']
                emailaddress = rec_req_data['email']
                password = rec_req_data['password']
                dataofbirth = rec_req_data['dateOfBirth']
                try:
                    registration_app_logger.info("Processing the request data... :: [STARTED]")
                    user_obj: User = User.add_user(username= username, firstname= firstname, lastname= lastname, dateofbirth= dataofbirth, email= emailaddress, pwd= password)
                    registration_app_logger.info("Instance creation for User :: [SUCCESS] :: {0}".format(user_obj))
                    registration_app_logger.info("Mapping the request data to the database model:: [STARTED]")
                    user_map_db_instance = UsersModel(Username = user_obj.username,
                                                      FirstName = user_obj.firstname,
                                                      LastName = user_obj.lastname,
                                                      Email = user_obj.email,
                                                      DateOfBirth = user_obj.dateofbirth,
                                                      Password = user_obj.pwd,
                                                      CreatedAt = user_obj.created_at,
                                                      UpdatedAt = user_obj.updated_at)
                    registration_app_logger.info("Mapping the request data to the database model:: [SUCCESS]")
                    registration_session = res_app_obj.create_session_for_service()
                    if registration_session is not None:
                        try:
                            registration_session.add(user_map_db_instance)
                            registration_app_logger.info("Data added into  DataBase session {0}:: SUCCESS".format(user_map_db_instance))
                            registration_session.commit()  # Commit the change
                            registration_app_logger.info("Added Data is committed into  DataBase {0}:: SUCCESS".format(registration_session))
                            registration_app_logger.info("Generating Success response  :: [STARTED]")
                            user_instance = User.convert_db_model_to_response(user_map_db_instance)
                            success_user_response = User.generate_success_response(user_instance)
                            registration_app_logger.info("Generating Success response  :: [STARTED] :: {0}".format(success_user_response))
                            return jsonify(success_user_response), 201

                        except SQLAlchemyError as ex:
                            registration_session.rollback()
                            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
                            return jsonify({"message": "Internal Server Error"}), 500

                        except Exception as ex:
                            registration_session.rollback()
                            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
                            return jsonify({"message": "Internal Server Error"}), 500
                        finally:
                            print("Closing the  session  {0}:: [STARTED]".format(registration_session))
                            registration_session.close()  # Close the change
                            print("Closed the  session  {0}:: [SUCCESS]".format(registration_session))


                except Exception as ex:
                    registration_app_logger.error("Instance creation for User :: [FAILED] :: {0}".format(ex))
                    abort(500, description={'message': 'Create User Failed', 'details': {'params': str(ex)}})

            else:
                registration_app_logger.error("Validation for Request-Body is  :: [FAILED]")
                result["message"] = "Request Params Missing"
                registration_app_logger.info("Sending Error response back to client :: {0}".format(result))
                abort(400, description=result)

    else:
        registration_app_logger.error("Validation for Request-Header is  :: [FAILED]")
        result["message"] = "Request Header Missing"
        registration_app_logger.info("Sending Error response back to client :: {0}".format(result))
        abort(400, description=result)






def check_user_credentails(userID):
    try:
        registration_session = res_app_obj.create_session_for_service()
        if registration_session is not None:
            row = registration_session.query(UsersModel).get(ID=userID)
            if row is not None:
                return row.ID, True
            else:
                return userID, False
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return userID, False
