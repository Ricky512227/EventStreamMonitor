import sys
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
from flask import jsonify, request, abort
from src.registration_service.users.user import User
from src.registration_service.models.user_model import UsersModel
from src.registration_service import registration_app_logger, req_headers_schema, getuser_headers_schema, \
    del_user_headers_schema, reg_user_req_schema, reg_app_obj


def register_user():
    try:
        registration_app_logger.info('REQUEST ==> Received Endpoint :: {0}'.format(request.endpoint))
        rec_req_headers = dict(request.headers)
        registration_app_logger.info("Received Headers from the request :: {0}".format(rec_req_headers))
        header_result = reg_app_obj.generate_req_missing_params(rec_req_headers, req_headers_schema)
        if len(header_result.keys()) != 0:
            header_result["message"] = "Request Header Missing"
            registration_app_logger.info("Sending Error response back to client :: {0}".format(header_result))
            abort(400, description=header_result)
        if request.method == 'POST':
            rec_req_data = request.get_json()
            body_result = reg_app_obj.generate_req_missing_params(rec_req_data, reg_user_req_schema)
            if len(body_result.keys()) != 0:
                body_result["message"] = "Request Params Missing"
                registration_app_logger.info("Sending Error response back to client :: {0}".format(body_result))
                abort(400, description=body_result)
            username = rec_req_data['username']
            firstname = rec_req_data['firstName']
            lastname = rec_req_data['lastName']
            emailaddres = rec_req_data['email']
            password = rec_req_data['password']
            dateofbirth = rec_req_data['dateOfBirth']
            registration_app_logger.info("Processing the request data... :: [STARTED]")
            # Doing the pre-validation checks before procession the request.
            if is_username_email_already_exists(uname=username, email=emailaddres):
                return jsonify({"message":"Username or EmailAddress already exists"}), 400

            user_obj = User(username=username, firstname=firstname, lastname=lastname, dateofbirth=dateofbirth,
                            email=emailaddres, pwd=password)
            if user_obj is None:
                abort(500, description={'message': 'Create User Failed'})
            user_instance = user_obj.create_user()
            registration_app_logger.info("Mapping the request data to the database model:: [STARTED]")
            user_map_db_instance = UsersModel(Username=user_instance["username"],
                                              FirstName=user_instance["firstname"],
                                              LastName=user_instance["lastname"],
                                              Email=user_instance["email"],
                                              DateOfBirth=user_instance["dateofbirth"],
                                              Password=user_instance["password"],
                                              CreatedAt=user_instance["created_at"],
                                              UpdatedAt=user_instance["updated_at"])
            registration_app_logger.info("Mapping the request data to the database model:: [SUCCESS]")
            registration_session = reg_app_obj.get_session_for_service()
            if registration_session is None:
                abort(500, description={'message': 'Create Session Failed'})

            try:
                registration_app_logger.info("Data adding into  DataBase session {0}:: [STARTED]".format(user_map_db_instance))
                registration_session.add(user_map_db_instance)
                registration_app_logger.info("Data added into  DataBase session {0}:: [SUCCESS]".format(user_map_db_instance))
                registration_session.commit()  # Commit the change
                registration_app_logger.info("Added Data is committed into  DataBase {0}:: [SUCCESS]".format(registration_session))
                user_instance = User.convert_db_model_to_response(user_map_db_instance)
                success_user_response = User.generate_success_response(user_instance=user_instance, messagedata="User Created")
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
                reg_app_obj.close_session_for_service(registration_session)  # Close the session

    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return jsonify({"message": "Internal Server Error"}), 500


def is_userid_exists(userid):
    is_user_exists_status = False
    try:
        registration_session = reg_app_obj.get_session_for_service()
        if registration_session is not None:
            registration_app_logger.info("Querying Userid in the Database to check the if user exists :: {0}".format(userid))
            user_row = registration_session.query(UsersModel).get(userid)
            if user_row is not None:
                is_user_exists_status = True
                registration_app_logger.info("1 Result for the Query Response :: {0} - {1}".format(userid, is_user_exists_status))
            else:
                registration_app_logger.info("2 Result for the Query Response :: {0} - {1}".format(userid, is_user_exists_status))
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
    registration_app_logger.info("3 Result for the Query Response :: {0} - {1}".format(userid, is_user_exists_status))
    return userid, is_user_exists_status


def is_username_email_already_exists(uname, email):
    try:
        registration_session = reg_app_obj.get_session_for_service()
        if registration_session is not None:
            registration_app_logger.info("Querying UserName :: {0} , Email :: {1} in the Database to check the if already exists :: ".format(uname, email))
            user_row = registration_session.query(UsersModel).filter(or_(UsersModel.Username ==uname, UsersModel.Email == email)).first()
            if user_row is not None:
                registration_app_logger.info("Result for the Query Response :: {0}".format(True))
                return True
            else:
                registration_app_logger.info("Result for the Query Response :: {0}".format(False))
                return False
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        registration_app_logger.info("Result for the Query Response :: {0}".format(False))
        return False

def get_user_info(userid):
    try:
        registration_app_logger.info('REQUEST ==> Received Endpoint :: {0}'.format(request.endpoint))
        rec_req_headers = dict(request.headers)
        registration_app_logger.info("Received Headers from the request :: {0}".format(rec_req_headers))
        header_result = reg_app_obj.generate_req_missing_params(rec_req_headers, getuser_headers_schema)
        if len(header_result.keys()) != 0:
            header_result["message"] = "Request Header Missing"
            registration_app_logger.info("Sending Error response back to client :: {0}".format(header_result))
            abort(400, description=header_result)
        if request.method == 'GET':
            registration_app_logger.info("Received userid from the url :: {0}".format(userid))
            registration_app_logger.info("Processing the request data... :: [STARTED]")
            registration_app_logger.info("Mapping the request data to the database model:: [STARTED]")

            user_id, is_exists = is_userid_exists(userid)
            if is_exists:
                getuser_session = reg_app_obj.get_session_for_service()
                try:
                    '''Fetching the user record from the database using the primary key userid'''
                    get_user_map_db_instance = getuser_session.query(UsersModel).get(userid)
                    print(get_user_map_db_instance)
                    '''Converting the database model of user to defined user object'''
                    user_instance = User.convert_db_model_to_response(get_user_map_db_instance)
                    '''Using the user object, Generating the success response object'''
                    success_get_user_response = User.generate_success_response(user_instance=user_instance,
                                                                               messagedata="Retrieved User")
                    registration_app_logger.info(
                        "Generating Success response  :: [STARTED] :: {0}".format(success_get_user_response))
                    return jsonify(success_get_user_response), 200
                except SQLAlchemyError as ex:
                    getuser_session.rollback()
                    print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
                    return jsonify({"message": "Internal Server Error"}), 500
                except Exception as ex:
                    getuser_session.rollback()
                    print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
                    return jsonify({"message": "Internal Server Error"}), 500
                finally:
                    reg_app_obj.close_session_for_service(getuser_session)  # Close the change
            else:
                return jsonify({"message": "Retrieved user not Found"}), 404
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return jsonify({"message": "Internal Server Error"}), 500


def remove_user(userid):
    try:
        registration_app_logger.info('REQUEST ==> Received Endpoint :: {0}'.format(request.endpoint))
        rec_req_headers = dict(request.headers)
        registration_app_logger.info("Received Headers from the request :: {0}".format(rec_req_headers))
        header_result = reg_app_obj.generate_req_missing_params(rec_req_headers, del_user_headers_schema)
        if len(header_result.keys()) != 0:
            header_result["message"] = "Request Header Missing"
            registration_app_logger.info("Sending Error response back to client :: {0}".format(header_result))
            abort(400, description=header_result)
        if request.method == 'DELETE':
            registration_app_logger.info("Received userid from the url :: {0}".format(userid))
            registration_app_logger.info("Processing the request data... :: [STARTED]")
            registration_app_logger.info("Mapping the request data to the database model:: [STARTED]")

            user_id, is_exists = is_userid_exists(userid)
            if is_exists:
                delete_user_session = reg_app_obj.get_session_for_service()
                try:
                    '''Delete the user record from the database using the primary key userid'''
                    delete_user_session.query(UsersModel).filter(UsersModel.ID == user_id).delete()
                    delete_user_session.commit()
                    return jsonify({"message": "User deleted Successfully"}), 200
                except SQLAlchemyError as ex:
                    delete_user_session.rollback()
                    print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
                    return jsonify({"message": "Internal Server Error"}), 500
                except Exception as ex:
                    delete_user_session.rollback()
                    print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
                    return jsonify({"message": "Internal Server Error"}), 500
                finally:
                    reg_app_obj.close_session_for_service(delete_user_session)  # Close the change
            else:
                return jsonify({"message": "User not found"}), 404
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return jsonify({"message": "Internal Server Error"}), 500
