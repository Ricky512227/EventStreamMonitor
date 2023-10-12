from src.proto_def.token_proto_v1.token_pb2_grpc import (
    add_UserValidationForTokenGenerationServiceServicer_to_server,
)
from src.pyportal_common.grpc_service_handlers.grpc_server_handler.grpc_base_server_init import (
    init_pyportal_grpc_base_server,
)
from src.usermanagement_service.user_management_grpc.user_grpc_server import (
    UserValidationForTokenGenerationService,
)


def start_user_management_grpc_server(user_management_logger):
    user_management_grpc_server = init_pyportal_grpc_base_server(user_management_logger)
    if user_management_grpc_server:
        user_management_grpc_server.bind_ip_port_server()
        if user_management_grpc_server is not None:
            user_management_grpc_server.bind_rpc_method_server(
                name_service_servicer_to_server=add_UserValidationForTokenGenerationServiceServicer_to_server,
                name_service=UserValidationForTokenGenerationService,
            )
    return user_management_grpc_server
