# pylint: disable=line-too-long

"""

Module: user_success_response.py

Description:

This module defines a success base response class.

Classes:

- SuccessBaseResponseBody: Represents a success base response.

"""

import json

from typing import Union

from abc import ABC, abstractmethod

from app import user_management_logger

class SuccessBaseResponseBody(ABC):

    """

    Base class for generating success response bodies.

    Subclasses should implement the abstract methods `get_assigned_resp_body`

    and `get_assigned_resp_msg`.

    """

    def __init__(self, response_body):

        """

        Initialize a new instance of SuccessBaseResponseBody.

        Args:

            response_body (dict): The response body to work with.

        """

        self._response_body = response_body

        self._serialized_response = None

        self._success_response_body = {}

        self._user_instance = {}

        self._prepared_success_response_body = {}

    @abstractmethod

    def get_assigned_resp_body(self):

        """

        Abstract method to get the assigned response body.

        Subclasses should implement this method.

        Returns:

            dict: The assigned response body.

        """

    @abstractmethod

    def get_assigned_resp_msg(self):

        """

        Abstract method to get the assigned response message.

        Subclasses should implement this method.

        Returns:

            str: The assigned response message.

        """

    def _prepare_success_response_body(self) -> Union[dict, None]:

        """

        Prepare the success response body based on the assigned response body.

        Returns:

            dict or None: The prepared success response body or None if no data is available.

        """

        self._user_instance = self.get_assigned_resp_body()

        user_management_logger.info(

            "Generating Success response :: [STARTED] :: %s ", type(self._user_instance)

        )

        if self._user_instance:

            self._success_response_body = {

                "user": {

                    "userId": self._user_instance["data"]["ID"],

                    "username": self._user_instance["data"]["Username"],

                    "email": self._user_instance["data"]["Email"],

                    "dateOfBirth": self._user_instance["data"]["DateOfBirth"],

                    "firstName": self._user_instance["data"]["FirstName"],

                    "lastName": self._user_instance["data"]["LastName"],

                    "CreatedAt": self._user_instance["data"]["CreatedAt"],

                    # .strftime("%Y-%m-%d %H:%M:%S"),

                    "UpdatedAt": self._user_instance["data"]["UpdatedAt"]

                    # .strftime("%Y-%m-%d %H:%M:%S"

                }

            }

            user_management_logger.info(

                "Generated Success response :: [SUCCESS] :: %s ",

                self._success_response_body,

            )

        return self._success_response_body

    def _serialize_response_data(self) -> Union[str, None]:

        """

        Serialize the prepared success response body into a JSON string.

        Returns:

            str: The serialized response data.

        """

        self._prepared_success_response_body = self._prepare_success_response_body()

        if self._prepared_success_response_body is not None:

            user_management_logger.info(

                "Serializing the response data :: %s , %s [STARTED]",

                self._prepared_success_response_body,

                type(self._prepared_success_response_body),

            )

            self._serialized_response = json.dumps(self._prepared_success_response_body)

            user_management_logger.info(

                "Serializing the response data :: %s , %s [SUCCESS]",

                self._prepared_success_response_body,

                type(self._prepared_success_response_body),

            )

        return self._serialized_response

    def generate_response(self) -> Union[str, None]:

        """

        Generate the success response as a JSON string.

        Returns:

            str: The generated success response.

        """

        return self._serialize_response_data()
