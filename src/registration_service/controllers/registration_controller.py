import sys
from sqlalchemy.exc import SQLAlchemyError
from flask import jsonify, request, abort
from src.registration_service import user_logger,req_headers_schema, reg_user_req_schema, User, UsersModel, create_session_for_service
from src.airliner_common.req_header_validation import generate_req_missing_params

def add_user():
    user_logger.info('REQUEST ==> Received Endpoint :: {0}'.format(request.endpoint))
    rec_req_headers = dict(request.headers)
    user_logger.info("Received Headers from the request :: {0}".format(rec_req_headers))
    user_logger.info("Validation for Request-Header is  :: [STARTED]")
    err_result = generate_req_missing_params(rec_req_headers, req_headers_schema)
    if len(err_result.keys()) == 0:
        user_logger.info("Validation for Request-Header is  :: [SUCCESS]")
        for header_key, header_value in rec_req_headers.items():
            user_logger.debug("REQUEST <==> HEADER.params ==> Param :: {0} :: Value :: {1} :: Type ::{2} ".format(header_key,header_value, type(header_value)))
            if request.method == 'POST':
                rec_req_data = request.get_json()
                user_logger.info("Validation for Request-Body is  :: [STARTED]")
                err_result = generate_req_missing_params(rec_req_data, reg_user_req_schema)
                user_logger.info("Validation for Request-body is  :: [SUCCESS]")
                for data_key, data_value in rec_req_data.items():
                    user_logger.debug("REQUEST <==> BODY.params ==> Param :: {0} :: Value :: {1} :: Type ::{2} ".format(data_key,data_value,type(data_value)))
                username = rec_req_data['username']
                firstname = rec_req_data['firstName']
                lastname = rec_req_data['lastName']
                emailaddress = rec_req_data['email']
                password = rec_req_data['password']
                dataofbirth = rec_req_data['dateOfBirth']
                try:
                    user_logger.info("Processing the request data... :: [STARTED]")
                    user_obj: User = User.add_user(username, firstname, lastname, dataofbirth, emailaddress, password)
                    user_logger.info("Instance creation for User :: [SUCCESS] :: {0}".format(user_obj))
                    user_logger.info("Mapping the request data to the database model:: [STARTED]")
                    user_map_db_instance = UsersModel(Username = user_obj.username,
                                                      FirstName = user_obj.firstname,
                                                      LastName = user_obj.lastname,
                                                      Email = user_obj.email,
                                                      DateOfBirth = user_obj.dateofbirth,
                                                      Password = user_obj.pwd,
                                                      CreatedAt = user_obj.created_at,
                                                      UpdatedAt = user_obj.updated_at)
                    user_logger.info("Mapping the request data to the database model:: [SUCCESS]")
                    from src.registration_service import user_connection_pool, user_db_engine, USER_SERVICE_NAME
                    user_session = create_session_for_service(user_connection_pool, user_db_engine, USER_SERVICE_NAME.lower())
                    if user_session is not None:
                        try:
                            user_session.add(user_map_db_instance)
                            user_logger.info("Data added into  DataBase session {0}:: SUCCESS".format(user_map_db_instance))
                            user_session.commit()  # Commit the change
                            user_logger.info("Added Data is committed into  DataBase {0}:: SUCCESS".format(user_session))
                            #print("Commit the  changes  {0}:: SUCCESS".format(user_session))
                            user_logger.info("Generating Success response  :: [STARTED]")
                            user_instance = User.convert_db_model_to_response(user_map_db_instance)
                            success_user_response = User.generate_success_response(user_instance)
                            user_logger.info("Generating Success response  :: [STARTED] :: {0}".format(success_user_response))
                            return jsonify(success_user_response), 201

                        except SQLAlchemyError as ex:
                            user_session.rollback()
                            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
                            abort(500, description={'message': 'Create User Failed', 'details': {'params': ex}})

                        except Exception as ex:
                            user_session.rollback()
                            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
                            abort(500, description={'message': 'Create User Failed', 'details': {'params': str(ex)}})
                        finally:
                            print("Closing the  session  {0}:: [STARTED]".format(user_session))
                            user_session.close()  # Close the change
                            print("Closed the  session  {0}:: [SUCCESS]".format(user_session))
                except Exception as ex:
                    user_logger.error("Instance creation for User :: [FAILED] :: {0}".format(ex))
                    abort(500, description={'message': 'Create User Failed', 'details': {'params': str(ex)}})

            else:
                user_logger.error("Validation for Request-Data is  :: [FAILED]")
                err_result["message"] = 'Request data of params missing'
                user_logger.info("Sending Error response back to client :: {0}".format(err_result))
                abort(400, description=err_result)

    else:
        user_logger.error("Validation for Request-Header is  :: [FAILED]")
        err_result["message"] = "Request Header Missing"
        user_logger.info("Sending Error response back to client :: {0}".format(err_result))
        abort(400, description=err_result)

def check_user_credentails(userID):
    try:
        print("%%%%%%%%%>> check_user_credentails")
        from src.registration_service import user_connection_pool, user_db_engine, USER_SERVICE_NAME
        print(user_connection_pool, user_db_engine, USER_SERVICE_NAME)
        user_session = create_session_for_service(user_connection_pool, user_db_engine, USER_SERVICE_NAME.lower())
        print("user_session :: {0}".format(user_session))
        if user_session is not None:
            try:
                row = user_session.query(UsersModel).filter_by(ID=userID).first()
                return row.ID, True
            except Exception as ex:
                print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))