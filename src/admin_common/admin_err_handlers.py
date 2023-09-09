# from src.admin_common.admin_error_handling import PyPortalAdminBaseError
# import sys
# import json

#
# def prepare_bad_request_and_send_response(error_data):
#     try:
#         print("Preparing Err_response :: [STARTED]")
#         error_res_obj = PyPortalAdminBadRequest()
#         error_res_obj.message = error_data['message']
#         print("Error_res_obj.message :: {0}".format(error_res_obj.message))
#         if "details" in error_data.keys():
#             error_res_obj.error_details = error_data['details']
#             print("Error_res_obj.error_details :: {0}".format(error_res_obj.error_details))
#         print("Before Serializing the error response body :: {0}".format(error_res_obj.to_dict()))
#         error_response_body = json.dumps(error_res_obj.to_dict())
#         print("After Serializing the error response body :: {0}".format(error_response_body))
#         err_response_400 = make_response(error_response_body)
#         err_response_400.headers['Content-Type'] = 'application/problem+json'
#         err_response_400.headers['Cache-Control'] = 'no-cache'
#         err_response_400.status_code = 400
#         print("Packed Response headers:: {0}".format(err_response_400.headers))
#         print("Packed Response response:: {0}".format(err_response_400.data))
#         print("Prepared Err_response :: [SUCCESS]:: {0}".format(err_response_400))
#         return err_response_400
#
#     except Exception as ex:
#         print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
#         return jsonify({"status": 500, "message": "INTERNAL_SERVER_ERROR"}), 500
#
#
# def prepare_method_not_allowed_and_send_response(error_data):
#     try:
#         print("Preparing Err_response :: [STARTED]")
#         error_res_obj = PyPortalAdminMethodNotAllowed()
#         error_res_obj.message = error_data['message']
#         print("Error_res_obj.message :: {0}".format(error_res_obj.message))
#         if "details" in error_data.keys():
#             error_res_obj.error_details = error_data['details']
#             print("Error_res_obj.error_details :: {0}".format(error_res_obj.error_details))
#         error_response_body = json.dumps(error_res_obj.to_dict())
#         print("Serializing the error response body :: {0}".format(error_response_body))
#         err_response_405 = make_response(error_response_body)
#         err_response_405.headers['Content-Type'] = 'application/problem+json'
#         err_response_405.headers['Cache-Control'] = 'no-cache'
#         err_response_405.status_code = 405
#         print("Packed Response headers:: {0}".format(err_response_405.headers))
#         print("Packed Response response:: {0}".format(err_response_405.data))
#         print("Prepared Err_response :: [SUCCESS]:: {0}".format(err_response_405))
#         return err_response_405
#     except Exception as ex:
#         print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
#         return jsonify({"status": 500, "message": "INTERNAL_SERVER_ERROR"}), 500
#
#
# def prepare_internal_server_error_and_send_response(error_data):
#     try:
#         print("Preparing Err_response :: [STARTED]")
#         error_res_obj = PyPortalAdminInternalError()
#         error_res_obj.message = error_data['message']
#         print("Error_res_obj.message :: {0}".format(error_res_obj.message))
#         if "details" in error_data.keys():
#             error_res_obj.error_details = error_data['details']
#             print("Error_res_obj.error_details :: {0}".format(error_res_obj.error_details))
#         error_response_body = json.dumps(error_res_obj.to_dict())
#         print("Serializing the error response body :: {0}".format(error_response_body))
#         err_response_500 = make_response(error_response_body)
#         err_response_500.headers['Content-Type'] = 'application/problem+json'
#         err_response_500.headers['Cache-Control'] = 'no-cache'
#         err_response_500.status_code = 500
#         print("Packed Response headers:: {0}".format(err_response_500.headers))
#         print("Packed Response response:: {0}".format(err_response_500.data))
#         print("Prepared Err_response :: [SUCCESS]:: {0}".format(err_response_500))
#         return err_response_500
#     except Exception as ex:
#         print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
#         return jsonify({"status": 500, "message": "INTERNAL_SERVER_ERROR"}), 500
#
#
# def prepare_not_found_and_send_response(error_data):
#     try:
#         print("Preparing Err_response :: [STARTED]")
#         error_res_obj = PyPortalAdminNotFound()
#         error_res_obj.message = error_data['message']
#         print("Error_res_obj.message :: {0}".format(error_res_obj.message))
#         if "details" in error_data.keys():
#             error_res_obj.error_details = error_data['details']
#             print("Error_res_obj.error_details :: {0}".format(error_res_obj.error_details))
#         error_response_body = json.dumps(error_res_obj.to_dict())
#         print("Serializing the error response body :: {0}".format(error_response_body))
#         err_response_404 = make_response(error_response_body)
#         err_response_404.headers['Content-Type'] = 'application/problem+json'
#         err_response_404.headers['Cache-Control'] = 'no-cache'
#         err_response_404.status_code = 404
#         print("Packed Response headers:: {0}".format(err_response_404.headers))
#         print("Packed Response response:: {0}".format(err_response_404.data))
#         print("Prepared Err_response :: [SUCCESS]:: {0}".format(err_response_404))
#         return err_response_404
#     except Exception as ex:
#         print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
#         return jsonify({"status": 500, "message": "INTERNAL_SERVER_ERROR"}), 500
