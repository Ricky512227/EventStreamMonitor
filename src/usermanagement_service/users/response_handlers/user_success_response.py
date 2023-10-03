from src.usermanagement_service import user_management_logger
import json
from abc import ABC, abstractmethod


class SuccessBaseResponseBody(ABC):
    def __init__(self, response_body):
        self.response_body = response_body
        user_management_logger.info("Initialised response_body: {0}".format(self.response_body))

    @abstractmethod
    def get_assigned_resp_body(self):
        pass

    @abstractmethod
    def get_assigned_resp_msg(self):
        pass

    def prepare_success_response_body(self):
        user_instance = self.get_assigned_resp_body()
        user_management_logger.info("Generating Success response  :: [STARTED] :: {0}".format(user_instance))
        success_response_body = {
            'user': {
                'userId': user_instance['data']['ID'],
                'username': user_instance['data']['Username'],
                'email': user_instance['data']['Email'],
                'dateOfBirth': user_instance['data']['DateOfBirth'],
                'firstName': user_instance['data']['FirstName'],
                'lastName': user_instance['data']['LastName'],
                'CreatedAt': user_instance['data']['CreatedAt'].strftime("%Y-%m-%d %H:%M:%S"),
                'UpdatedAt': user_instance['data']['UpdatedAt'].strftime("%Y-%m-%d %H:%M:%S")
                # 'CreatedAt': user_instance['data']['CreatedAt'],
                # 'UpdatedAt': user_instance['data']['UpdatedAt']
            }
        }
        user_management_logger.info("Generating Success response  :: [SUCCESS] :: {0}".format(success_response_body))
        return success_response_body

    def serialize_prepared_success_response_body(self):
        prepare_success_response_body = self.prepare_success_response_body()
        user_management_logger.info(
            "Serializing the response data :: [STARTED] :: {0} :: {1}".format(prepare_success_response_body,
                                                                              type(prepare_success_response_body)))
        user_serialized_response_data = json.dumps(prepare_success_response_body)
        user_management_logger.info(
            "Serialized the response data  :: [SUCCESS] :: {0} :: {1}".format(user_serialized_response_data,
                                                                              type(user_serialized_response_data)))
        return user_serialized_response_data

    def generate_success_response(self):
        if self.response_body is None:
            user_serialized_response_data = None
            return user_serialized_response_data
        success_response_body = self.serialize_prepared_success_response_body()
        return success_response_body
