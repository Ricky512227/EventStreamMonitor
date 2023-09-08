import sys
from src.admin_grpc import token_pb2_grpc
from src.admin_grpc import token_pb2
from google.protobuf.json_format import MessageToJson
from src.registration_service.controllers.user_controller import is_userid_exists
from src.registration_service import registration_app_logger


class UserValidationForTokenGenerationService(token_pb2_grpc.UserValidationForTokenGenerationServicer):
    def ValidateUserCredentials(self, request, context):
        registration_app_logger.info("Received request from client ::\n{0}".format(request))
        token_res_message = token_pb2.TokenResMessage()
        token_res_message.userid = request.userid
        token_res_message.isvalid = False
        print("Before token_res_message  :: {0}".format(token_res_message.userid))
        print("Before token_res_message  :: {0}".format(token_res_message.isvalid))
        try:
            user_data, is_exists = is_userid_exists(request.userid)
            if is_exists:
                token_res_message.userid = user_data
                token_res_message.isvalid = True
        except Exception as ex:
            registration_app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        registration_app_logger.info("Packing and sending response back to gRPC Client")
        return token_res_message
