from src.pyportal_common.grpc_handlers.grpc_server_handler.grpc_base_server import PyPortalGrpcBaseServer


def init_pyportal_grpc_base_server(cmn_logger):
    my_grpc_server: PyPortalGrpcBaseServer = PyPortalGrpcBaseServer(
                    logger_instance=cmn_logger,
                    grpc_server_ip="127.0.0.1",
                    grpc_server_port=50051,
                    max_workers_for_service=4,
                )
    return my_grpc_server
