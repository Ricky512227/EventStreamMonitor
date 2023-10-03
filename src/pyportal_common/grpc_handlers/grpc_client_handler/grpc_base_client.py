import sys
from datetime import datetime, timedelta

import grpc


class PyportalGrpcBaseClient:
    def __init__(self, grpc_base_client_ip, grpc_base_client_port) -> None:
        self.grpc_base_client_ip = grpc_base_client_ip
        self.grpc_base_client_port = str(grpc_base_client_port)
        self.base_grpc_channel = None
        self.base_stub = None
        for key, value in vars(self).items():
            print(f"Initialized {key} with value: {value}")

    def create_my_channel(self):
        print("Creating channel .")
        self.base_grpc_channel = grpc.insecure_channel(self.grpc_base_client_ip + ":" + self.grpc_base_client_port)
        self.base_grpc_channel.subscribe(self.handle_channel_state)
        print("Created channel :: {0}".format(self.base_grpc_channel))

    def assign_stub_to_channel(self, stub_cls_name):
        try:
            if self.base_grpc_channel:
                print("Assigning Stub and to the channel :: {0}".format(self.base_grpc_channel))
                self.base_stub = stub_cls_name(self.base_grpc_channel)
                print("Created Stub is :: {0} and assigned to the channel :: {1}".format(self.base_stub,
                                                                                         self.base_grpc_channel))
                return self.base_stub
        except Exception as ex:
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

    def close_my_channal(self):
        if self.base_grpc_channel:
            print("Close the channel :: {0}".format(self.base_grpc_channel))
            self.base_grpc_channel.close()

    def handle_channel_state(self, state):
        if state == grpc.ChannelConnectivity.IDLE:
            print("\nChannel  {1} is :: {0}\n".format("IDLE", self.base_grpc_channel))
        elif state == grpc.ChannelConnectivity.CONNECTING:
            print("\nChannel  {1} is :: {0}\n".format("CONNECTING", self.base_grpc_channel))
        elif state == grpc.ChannelConnectivity.READY:
            print("\nChannel  {1} is :: {0}\n".format("READY", self.base_grpc_channel))
        elif state == grpc.ChannelConnectivity.SHUTDOWN:
            print("\nChannel  {1} is :: {0}\n".format("SHUTDOWN", self.base_grpc_channel))
        elif state == grpc.ChannelConnectivity.TRANSIENT_FAILURE:
            print("\nChannel  {1} is :: {0}\n".format("TRANSIENT_FAILURE", self.base_grpc_channel))


#     def trigger_rpc_request(self, data_to_send):
#         try:
#             if self.base_grpc_channel:
#                 # Create a gRPC context
#                 context = grpc.metadata_call_credentials([('request_id', '12345')]).call(grpc.SecureChannelCredentials(None).empty_call(), None)
#
#                 # Set the request ID in the context
#
#                 # Set a deadline for the context (5 seconds from the current time)
#                 my_base_deadline = datetime.now() + timedelta(seconds=5)
#                 my_base_context = context.with_deadline(my_base_deadline)
#
#                 # Use the context when making an RPC call (assuming 'base_stub' is defined)
#                 resp_data = self.base_stub.ValidateUserCredentials(data_to_send, context=my_base_context)
#                 print("Received Response from the gRPC Server :: {0}".format(resp_data))
#                 print("Unpacking the received response from the gRPC Server userid :: {0} - isvalid :: {1}".format(
#                     resp_data.userid, resp_data.isvalid))
#                 return resp_data
#         except grpc.RpcError as ex:
#             print("Message Failed to send to teh gRPC Server")
#             print("Error occurred :: {0}\tLine No:: {1}".format(ex.debug_error_string(), sys.exc_info()[2].tb_lineno))
#         except Exception as ex:
#             print("Message Failed to send to teh gRPC Server")
#             print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
# #             print("Closed channel")
# #             return  True
# #     except Exception as ex:
# #         print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
