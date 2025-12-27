import sys

import datetime

import bcrypt

from app import user_management_logger

from app.models.user_model import UsersModel

class User:

    username: str

    email: str

    password: str

    dateOfBirth: str

    firstName: str

    lastName: str

    def __init__(self, **kwargs):

        """

        Initialize the User instance and log initialization information.

        """

        self.user_dict = {}

        self.user_map_db_instance = None

        self.username = kwargs.get("username", None)

        self.firstname = kwargs.get("firstname", None)

        self.lastname = kwargs.get("lastname", None)

        self.dateofbirth = kwargs.get("dateofbirth", None)

        self.email = kwargs.get("email", None)

        if "pwd" in kwargs:

            self.pwd = bcrypt.hashpw(kwargs["pwd"].encode("utf-8"), bcrypt.gensalt())

        else:

            self.pwd = None

        self.created_at = str(datetime.datetime.now())

        self.updated_at = str(datetime.datetime.now())

        # Log all parameters

        for key, value in vars(self).items():

            user_management_logger.info("Initialized %s with value: %s", key, value)

    def add_user(self):

        try:

            if len(self.user_dict.keys()) == 0:

                self.user_dict = {

                    "username": self.username,

                    "firstname": self.firstname,

                    "lastname": self.lastname,

                    "password": self.pwd,

                    "email": self.email,

                    "dateofbirth": self.dateofbirth,

                    "created_at": self.created_at,

                    "updated_at": self.updated_at,

                }

                user_management_logger.info(

                    "Instance creation for User :: %s [SUCCESS] :: ID :: %s", self.user_dict, id(self.user_dict)

                )

            else:

                user_management_logger.error("Instance creation for User :: %s [FAILED]", self.user_dict,)

            return self.user_dict

        except Exception as ex:

            user_management_logger.exception(

                "Error occurred :: %s\tLine No:: %s", ex, sys.exc_info()[2].tb_lineno

            )

            return self.user_dict

    def map_user_instance_to_db_model(self):

        try:

            user_management_logger.info(

                "Mapping the request data to the database model:: [STARTED]"

            )

            if self.user_map_db_instance is None:

                self.user_map_db_instance: UsersModel = UsersModel(

                    Username=self.user_dict["username"],

                    FirstName=self.user_dict["firstname"],

                    LastName=self.user_dict["lastname"],

                    Email=self.user_dict["email"],

                    DateOfBirth=self.user_dict["dateofbirth"],

                    Password=self.user_dict["password"],

                    CreatedAt=self.user_dict["created_at"],

                    UpdatedAt=self.user_dict["updated_at"],

                )

                user_management_logger.info(

                    "Mapping the request data to the database model:: [SUCCESS]"

                )

                return self.user_map_db_instance

            else:

                user_management_logger.info(

                    "Mapping the request data to the database model:: [FAILED]"

                )

                return self.user_map_db_instance

        except Exception as ex:

            user_management_logger.exception(

                "Error occurred :: %s\tLine No:: %s", ex, sys.exc_info()[2].tb_lineno

            )

            return self.user_map_db_instance
