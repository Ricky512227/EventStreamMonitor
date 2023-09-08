from src.admin_common.admin_error_handling import AirlinerError404, AirlinerError400, AirlinerError405, AirlinerError500
from flask import jsonify
import sys


def bad_request(error_data):
    try:
        print("Preparing Err_response :: {0}".format(error_data))
        error_res_obj = AirlinerError400()
        error_res_obj.message = error_data.description['message']
        print("error_res_obj.message :: {0}".format(error_res_obj.message))
        if "details" in error_data.description.keys():
            error_res_obj.error_details = error_data.description['details']
        print("Response ID of Final Response:: {0}".format(id(error_res_obj.to_dict())))
        print("Prepared Final Response  and sent to Client:: {0}".format(error_res_obj.to_dict()))
        return jsonify(error_res_obj.to_dict()), 400
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return jsonify({"status": 500, "message": "INTERNAL_SERVER_ERROR"}), 500


def method_not_allowed(error_data):
    try:
        print("Preparing Err_response :: {0}".format(error_data))
        error_res_obj = AirlinerError405()
        error_res_obj.message = error_data.description['message']
        print("error_res_obj.message :: {0}".format(error_res_obj.message))
        if "details" in error_data.description.keys():
            error_res_obj.error_details = error_data.description['details']
        print("Response ID of Final Response:: {0}".format(id(error_res_obj.to_dict())))
        print("Prepared Final Response  and sent to Client:: {0}".format(error_res_obj.to_dict()))
        return jsonify(error_res_obj.to_dict()), 405
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return jsonify({"status": 500, "message": "INTERNAL_SERVER_ERROR"}), 500


def internal_server_error(error_data):
    try:
        print("Preparing Err_response :: {0}".format(error_data))
        error_res_obj = AirlinerError500()
        error_res_obj.message = error_data.description['message']
        if "details" in error_data.description.keys():
            error_res_obj.err_details = error_data.description['details']
        print("Response ID of Final Response:: {0}".format(id(error_res_obj.to_dict())))
        print("Prepared Final Response  and sent to Client:: {0}".format(error_res_obj.to_dict()))
        return jsonify(error_res_obj.to_dict()), 500
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return jsonify({"status": 500, "message": "INTERNAL_SERVER_ERROR"}), 500


def not_found(error_data):
    try:
        print("Preparing Err_response :: {0}".format(error_data))
        error_res_obj = AirlinerError404()
        error_res_obj.message = error_data.description['message']
        if "details" in error_data.description.keys():
            error_res_obj.err_details = error_data.description['details']
        print("Response ID of Final Response:: {0}".format(id(error_res_obj.to_dict())))
        print("Prepared Final Response  and sent to Client:: {0}".format(error_res_obj.to_dict()))
        return jsonify(error_res_obj.to_dict()), 404
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return jsonify({"status": 500, "message": "INTERNAL_SERVER_ERROR"}), 500
