import sys
import time

import grpc

from src.proto_def.token_proto_v1 import token_pb2_grpc, token_pb2
from src.usermanagement_service.utils.util_helpers import is_userid_exists_in_db
from src.usermanagement_service import user_management_logger, app_manager_db_obj


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

            user_management_logger.info("Received request from client ::\n{0}".format(request))
            ctx_metadata = context.invocation_metadata()
            for ctx_metadata_id, ctx_metadata_data in ctx_metadata.itertems():
                user_management_logger.info(f"Received context {ctx_metadata_id} from client :: {ctx_metadata_data}")
            deadline_remaining = context.time_remaining()
            user_management_logger.info("Time remaining to process the request ::\n{0}".format(deadline_remaining))
            token_res_message = token_pb2.TokenResponseMessage()
            token_res_message.user_id = request.user_id
            token_res_message.isvalid_user = False
            if context.deadline:
                print("time.time()", time.time())
                print("context.deadline.timestamp()", context.deadline.timestamp())
                if time.time() > context.deadline.timestamp():
                    context.set_code(grpc.StatusCode.DEADLINE_EXCEEDED)
                    context.set_details("Deadline exceeded")
                    return token_res_message
                try:
                    userid, is_exists = is_userid_exists_in_db(session_instance=app_manager_db_obj.get_session_from_session_maker() , userid=request.user_id)
                    if is_exists:
                        token_res_message.isvalid_user = is_exists
                        context.set_code(grpc.StatusCode.OK)
                except Exception as ex:
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details("Internal DB error")
                    user_management_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
                    print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
                user_management_logger.info("Packing and sending response back to gRPC Client :: {0}".format(token_res_message))
                return token_res_message
        except Exception as ex:
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
