# pylint: disable=line-too-long

"""

Module: create_user_success_response.py

Description:

This module defines a success response class for user creation.

Classes:

- CreateSuccessResponse: Represents a success response for user creation.

"""

from app import user_management_logger

from app.users.response_handlers.user_success_response import (

    SuccessBaseResponseBody,

)

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

    def __init__(

        self, response_body=None, response_message="User Created Successfully"

    ):

        """

        Initialize a CreateSuccessResponse instance.

        Args:

            response_body (dict, optional): The response data containing user information.

            response_message (str, optional): The message associated with the success response.

        """

        user_management_logger.info(

            "Initializing CreateSuccessResponse object ID: %s", id(self)

        )

        super().__init__(response_body)

        self._response_message = response_message

        # Log all parameters

        for key, value in vars(self).items():

            user_management_logger.info("Initialized %s with value: %s", key, value)

    def get_assigned_resp_body(self):

        """

        Get the assigned response body.

        Returns:

            dict: The response data containing user information.

        """

        return self._response_body

    def get_assigned_resp_msg(self):

        """

        Get the assigned response message.

        Returns:

            str: The message associated with the success response.

        """

        return self._response_message

def generate_success_response(user_instance):

    suc_res_obj = CreateSuccessResponse(response_body=user_instance)

    custom_user_response_body = suc_res_obj.generate_response()

    return custom_user_response_body