import sys
import time

import grpc

from src.proto_def.token_proto_v1 import token_pb2_grpc, token_pb2
from src.usermanagement_service.utils.util_helpers import is_userid_exists
from src.usermanagement_service import user_management_logger


class UserValidationForTokenGenerationService(
    token_pb2_grpc.UserValidationForTokenGenerationServiceServicer
):
    def ValidateUserCredentials(self, request, context):
        try:
            # # Set a deadline for the entire RPC call (e.g., 10 seconds)
            # deadline = context.deadline.timestamp() if context.deadline else None
            #
            # start_time = time.time()
            # elapsed_time = 0
            #
            # while True:
            #     if deadline and time.time() > deadline:
            #         # If the deadline is exceeded, set the status code and details
            #         context.set_code(grpc.StatusCode.DEADLINE_EXCEEDED)
            #         context.set_details("Deadline exceeded")
            #         return example_pb2.MyResponse(result="")
            #
            #     # Simulate a portion of work
            #     time.sleep(1)  # Simulate 1 second of work
            #     elapsed_time = time.time() - start_time
            #
            #     # Notify the client about the progress
            #     response = token_pb2.TokenResponseMessage(
            #         result=f"Progress: {elapsed_time:.2f} seconds"
            #     )
            #
            #     yield response  # Send progress update to the client
            #
            #     if elapsed_time >= 10:
            #         # Simulating the completion of the operation after 10 seconds
            #         break
            #
            # return token_pb2.TokenResponseMessage(result="Task completed successfully")

            user_management_logger.info(
                "Received request from client ::\n{0}".format(request)
            )
            if context.deadline:
                if time.time() > context.deadline.timestamp():
                    context.set_code(grpc.StatusCode.DEADLINE_EXCEEDED)
                    context.set_details("Deadline exceeded")
                    return token_pb2.TokenResponseMessage(result="")

                request_id = context.get("request_id")
                token_res_message = token_pb2.TokenResponseMessage()
                token_res_message.user_id = request.userid
                token_res_message.isvalid_user = False
                for key, value in vars(token_res_message).items():
                    user_management_logger.info(
                        "Received token_res_message-{0}: {1}".format(key, value)
                    )
                try:
                    user_data, is_exists = is_userid_exists(
                        session_instance="xtyyy", userid=request.user_id
                    )
                    if is_exists:
                        token_res_message.user_id = user_data
                        token_res_message.isvalid_user = True
                        context.set("request_id", request_id)
                except Exception as ex:
                    user_management_logger.error(
                        "Error occurred :: {0}\tLine No:: {1}".format(
                            ex, sys.exc_info()[2].tb_lineno
                        )
                    )
                    print(
                        "Error occurred :: {0}\tLine No:: {1}".format(
                            ex, sys.exc_info()[2].tb_lineno
                        )
                    )
                user_management_logger.info(
                    "Packing and sending response back to gRPC Client :: {0}".format(
                        token_res_message
                    )
                )
                return token_res_message
        except Exception as ex:
            print(
                "Error occurred :: {0}\tLine No:: {1}".format(
                    ex, sys.exc_info()[2].tb_lineno
                )
            )
