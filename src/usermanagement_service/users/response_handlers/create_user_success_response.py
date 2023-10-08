"""
Module: create_user_success_response.py

Description:
This module defines a success response class for user creation.

Classes:
- CreateSuccessResponse: Represents a success response for user creation.
"""
from src.usermanagement_service import user_management_logger
from src.usermanagement_service.users.response_handlers.user_success_response import (
    SuccessBaseResponseBody, )


class CreateSuccessResponse(SuccessBaseResponseBody):
    """
    Represents a success response for user creation.

    Attributes:
        response_body (dict): The response data containing user information.
        response_message (str): The message associated with the success response.

    Methods:
        get_assigned_resp_body(): Get the assigned response body.
        get_assigned_resp_msg(): Get the assigned response message.
    """

    def __init__(self,
                 response_body=None,
                 response_message="User Created Successfully"):
        """
        Initialize a CreateSuccessResponse instance.

        Args:
            response_body (dict, optional): The response data containing user information.
            response_message (str, optional): The message associated with the success response.
        """
        user_management_logger.info(
            "Initializing SuccessBaseResponseBody object ID: %s", id(self))
        super().__init__(response_body)
        self.response_message = response_message
        user_management_logger.info(
            "Received response_message: %s", self.response_message)
        user_management_logger.info(
            "Initialized SuccessBaseResponseBody object ID: %s", id(self))

    def get_assigned_resp_body(self):
        """
        Get the assigned response body.

        Returns:
            dict: The response data containing user information.
        """
        return self.response_body

    def get_assigned_resp_msg(self):
        """
        Get the assigned response message.

        Returns:
            str: The message associated with the success response.
        """
        return self.response_message
