import grpc
import sys
from concurrent import futures


class PyPortalGrpcBaseServer:
    def __init__(self, logger_instance, grpc_server_ip, grpc_server_port, max_workers_for_service):
        self.cmn_logger = logger_instance
        self.grpc_server_ip = grpc_server_ip
        self.grpc_server_port = grpc_server_port
        self.max_workers_for_service = max_workers_for_service
        self.base_grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.max_workers_for_service))
        for key, value in vars(self).items():
            self.cmn_logger.info(f"Initialized {key} with value: {value}")

    def bind_ip_port_server(self):
        try:
            server_address = f"{self.grpc_server_ip}:{self.grpc_server_port}"
            self.base_grpc_server.add_insecure_port(server_address)
            self.cmn_logger.info("Registered GRPC server :: {0}".format(server_address))
        except Exception as ex:
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            self.cmn_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

    def bind_rpc_method_server(self, name_service_servicer_to_server, name_service):
        if self.base_grpc_server is not None:
            name_service_servicer_to_server(name_service, self.base_grpc_server)
            self.cmn_logger.info("Registered RPC call to the server of :: {0} :: {1}".format(self.base_grpc_server, name_service))

    def start_base_server(self):
        self.cmn_logger.info("Started GRPC Server")
        self.base_grpc_server.start()

    def block_base_server(self):
        self.base_grpc_server.wait_for_termination()
        self.cmn_logger.info("Terminated GRPC Server")

# if __name__ == "__main__":
#     # Example for UserValidationForTokenGenerationService
#
#     my_grpc_server = PyPortalGrpcBaseServer("127.0.0.1", "50051", 4)
#
#     my_grpc_server.bind_rpc_method_server(
#         name_service_servicer_to_server=add_UserValidationForTokenGenerationServiceServicer_to_server,
#         name_service=UserValidationForTokenGenerationService
#     )
#     my_grpc_server.start_grpc_server()
