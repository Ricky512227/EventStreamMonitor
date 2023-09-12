import sys
from src.admin_grpc import token_pb2_grpc
from src.admin_grpc import token_pb2
from src.usermanagement_service.utils.util_helpers import is_userid_exists
from src.usermanagement_service import user_management_app_logger


class UserValidationForTokenGenerationService(token_pb2_grpc.UserValidationForTokenGenerationServicer):
    def ValidateUserCredentials(self, request, context):
        user_management_app_logger.info("Received request from client ::\n{0}".format(request))
        token_res_message = token_pb2.TokenResMessage()
        token_res_message.userid = request.userid
        token_res_message.isvalid = False
        user_management_app_logger.info("Before token_res_message  :: {0}".format(token_res_message.userid))
        user_management_app_logger.info("Before token_res_message  :: {0}".format(token_res_message.isvalid))
        try:
            user_data, is_exists = is_userid_exists(request.userid)
            if is_exists:
                token_res_message.userid = user_data
                token_res_message.isvalid = True
        except Exception as ex:
            user_management_app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        user_management_app_logger.info("Packing and sending response back to gRPC Client")
        return token_res_message
