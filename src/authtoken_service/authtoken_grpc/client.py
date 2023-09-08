import sys
import grpc
from src.admin_grpc import token_pb2_grpc
from src.admin_grpc import token_pb2
from google.protobuf.json_format import MessageToJson
from src.authtoken_service import authtoken_app_logger
import uuid


class gRPCTokenClient:
    def __init__(self, grpc_auth_token_client_ip, grpc_auth_token_client_port):
        self.grpc_auth_token_client_ip = grpc_auth_token_client_ip
        self.grpc_auth_token_client_port = grpc_auth_token_client_port
        self.token_channel = None
        self.tokenstub = None
        self.grpc_client_status = False
        self.resp_data = None
        self.resp_status = False
        self.data_to_send =None
    def create_channel_stub(self):
        try:
            self.token_channel = grpc.insecure_channel(self.grpc_auth_token_client_ip + ":" + self.grpc_auth_token_client_port)
            authtoken_app_logger.info("Created channel :: {0}".format(self.token_channel))
            self.tokenstub = token_pb2_grpc.UserValidationForTokenGenerationStub(self.token_channel)
            authtoken_app_logger.info("Created Stub and assigned to the channel :: {0}".format(self.tokenstub))
            self.grpc_client_status = True
            return self.tokenstub, self.grpc_client_status
        except Exception as ex:
            authtoken_app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            return self.tokenstub, self.grpc_client_status

    def close_channel_stub(self):
        try:
            if self.token_channel:
                authtoken_app_logger.info("Closing channel  :: {0}".format(self.token_channel))
                self.token_channel.close()
                self.tokenstub = None
                self.grpc_client_status = False
                self.resp_data = None
                self.resp_status = False
                self.data_to_send = None
                authtoken_app_logger.info("Closed channel")
        except Exception as ex:
            authtoken_app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

    @staticmethod
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

    @staticmethod
    def generate_request_id():
        authtoken_app_logger.info("Generated a UUID as the request ID :: {0}".format(str(uuid.uuid4())))
        return str(uuid.uuid4())

    def trigger_request(self):
        try:
            if self.token_channel:
                metadata = [('x-request-id', self.generate_request_id()), ('timeout', '5000')]
                self.resp_data = self.tokenstub.ValidateUserCredentials(self.data_to_send, metadata=metadata)
                authtoken_app_logger.info("Received Response from grpc :: {0}".format(self.resp_data))
                self.resp_status = True
        except grpc.RpcError as ex:
            authtoken_app_logger.error("Sending gRPC message to Registration Service :: [FAILED]")
            authtoken_app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex.debug_error_string(), sys.exc_info()[2].tb_lineno))
        except Exception as ex:
            authtoken_app_logger.error("Sending gRPC message to Registration Service :: [FAILED]")
            authtoken_app_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return self.resp_data, self.resp_status








