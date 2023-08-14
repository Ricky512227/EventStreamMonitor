from src.airliner_grpc import token_pb2_grpc
from src.airliner_grpc import token_pb2


class UserValidationForTokenGenerationService(token_pb2_grpc.UserValidationForTokenGenerationServicer):
    def ValidateUserCredentials(self, request, context):
        print("Received request from client ::\n{0}".format(request))
        metadata = dict(context.invocation_metadata())
        print(metadata)
        token_res_message = token_pb2.TokenResMessage()
        from src.registration_service.controllers.registration_controller import check_user_credentails
        data = check_user_credentails(request.userid)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", data)
        token_res_message.userid = "1"
        token_res_message.isvalid = True
        print("Sending response back to gRPC client ::{0}".format(token_res_message))
        return token_res_message




# if __name__=="__main__":
#     server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
#     print("Created GRPC server with the workers of max :: {0}".format(10))
#     token_pb2_grpc.add_UserValidationForTokenGenerationServicer_to_server(UserValidationForTokenGenerationService(), server)
#     print("Registered GRPC server to the server :: {0}".format("UserValidationForTokenGenerationService"))
#     server.add_insecure_port('127.0.0.1:8081')
#     print("Registering GRPC server for the Token-User service with the IP & PORT:: {0}:{1}".format("localhost", "8081"))
#     server.start()
#     print("Started the grpc server ...")
#     server.wait_for_termination()