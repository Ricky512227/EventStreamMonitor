import sys
import grpc
from src.airliner_grpc import token_pb2_grpc
from src.airliner_grpc import token_pb2
from src.authtoken_service import authtoken_app_logger

def TokenGrpcRequestPreparation(userid, username, passcode):
    token_req_message = None
    try:
        token_req_message = token_pb2.TokenReqMessage()
        token_req_message.userid = userid
        token_req_message.username = username
        token_req_message.passcode = passcode
        authtoken_app_logger.info("Request Created  :: {0}".format(token_req_message))
    except Exception as ex:
        authtoken_app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
    return token_req_message

def init_grpc_token_client():
    grpc_client_status = False
    tokenstub = None
    try:
        grpc_auth_token_client_ip = "127.0.0.1"
        grpc_auth_token_client_port = "8081"
        tokenchannel = grpc.insecure_channel(grpc_auth_token_client_ip + ":" + grpc_auth_token_client_port)
        authtoken_app_logger.info("Created channel :: {0}".format(tokenchannel))
        tokenstub = token_pb2_grpc.UserValidationForTokenGenerationStub(tokenchannel)
        authtoken_app_logger.info("Created Stub and assigned to the channel :: {0}".format(tokenstub))
        grpc_client_status = True
    except Exception as ex:
        authtoken_app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
    return tokenstub, grpc_client_status


def trigger_request(tokenstub, data_to_send):
    resp_status = False
    resp_data = None
    try:
        resp_data = tokenstub.ValidateUserCredentials(data_to_send)
        authtoken_app_logger.info("Received Response from grpc :: {0}".format(resp_data))
        resp_status= True
    except grpc.RpcError as ex:
        authtoken_app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex.debug_error_string(), sys.exc_info()[2].tb_lineno))
    except Exception as ex:
        authtoken_app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
    return resp_data, resp_status




