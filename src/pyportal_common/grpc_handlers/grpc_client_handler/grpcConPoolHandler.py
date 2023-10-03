# channel1: stub1
# channel1:[stub1, stub2, stub3]
import time

import grpc

# grpcpoolCon = {
#   channel1: [stub1, stub2, stub3]
#   channel2: [stub1, stub2, stub3]
#   channel3: [stub1, stub2, stub3]
# }
from src.proto_def.token_proto_v1.token_pb2_grpc import UserValidationForTokenGenerationServiceStub
from src.pyportal_common.grpc_handlers.grpc_client_handler.grpc_base_client import PyportalGrpcBaseClient
from queue import Queue
from grpc.experimental import aio


options = [
    ('grpc.lb_policy_name', 'round_robin'),  # Specify the load balancing policy
]

class PyPortalGrpcClientConnPool(PyportalGrpcBaseClient):
    _total_number_of_channels = 0
    _num_of_stubs_per_channel = 0
    _max_queue_pool_size = 0

    def __init__(self, grpc_base_client_ip, grpc_base_client_port):
        super().__init__(grpc_base_client_ip, grpc_base_client_port)
        self.grpc_conn_queue_pool = Queue(maxsize=PyPortalGrpcClientConnPool._max_queue_pool_size)
        for key, value in vars(self).items():
            print(f"Initialized {key} with value: {value}")

    @classmethod
    def set_queue_max_pool_size(cls, value):
        cls._max_queue_pool_size = value
        print("Initialised stub queue pool with size :: {0}".format(cls._max_queue_pool_size))

    @classmethod
    def get_queue_max_pool_size(cls):
        return cls._max_queue_pool_size

    @classmethod
    def set_total_number_of_channels(cls, value):
        cls._total_number_of_channels = value
        print("Created total channels :: {0}".format(cls._total_number_of_channels))

    @classmethod
    def set_num_of_stubs_per_channel(cls, value):
        cls._num_of_stubs_per_channel = value
        print("Created stubs per each channel :: {0}".format(cls._num_of_stubs_per_channel))

    @classmethod
    def get_total_number_of_channels(cls):
        return cls._total_number_of_channels

    @classmethod
    def get_num_of_stubs_per_channel(cls):
        return cls._num_of_stubs_per_channel

    def create_channel_pool(self):
        # for chan_index in range(1, PyPortalGrpcClientConnPool.total_number_of_channels + 1):
        self.create_my_channel()
        for stub_index in range(1, PyPortalGrpcClientConnPool._num_of_stubs_per_channel + 1):
            associated_stub = self.assign_stub_to_channel(
                stub_cls_name=UserValidationForTokenGenerationServiceStub)
            self.grpc_conn_queue_pool.put(associated_stub)
        print("Created pool of stubs with the size :: {0}".format(self.grpc_conn_queue_pool.qsize()))
        return self.grpc_conn_queue_pool.queue

    def get_available_stub_from_pool(self):
        print("Queue size before acquiring the stub :: {0}".format(self.grpc_conn_queue_pool.qsize()))
        available_stub = self.grpc_conn_queue_pool.get()
        print("Queue size before acquiring the stub :: {0}".format(self.grpc_conn_queue_pool.qsize()))
        return available_stub

    def release_stub_to_pool(self, released_stub):
        print("Releasing the stub to the queue :: {0}".format(released_stub))
        self.grpc_conn_queue_pool.put(released_stub)


custom_pool = PyPortalGrpcClientConnPool("127.0.0.1", 50051)
custom_pool.set_queue_max_pool_size(10)
custom_pool.set_total_number_of_channels(1)
custom_pool.set_num_of_stubs_per_channel(10)
grpc_conn_pool = custom_pool.create_channel_pool()
print("grpc_conn_pool :: {0}".format(grpc_conn_pool))
while True:
    avail_stub = custom_pool.get_available_stub_from_pool()
    print(id(avail_stub))
    custom_pool.release_stub_to_pool(avail_stub)
    time.sleep(1)
# my_token_data = {
#     "userid": "10",
#     "username": "HP Pavilion 15-DK1056WM",
#     "passcode": "fragrances"
# }
