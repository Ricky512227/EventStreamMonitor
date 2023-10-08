import sys
import datetime
import bcrypt
from src.usermanagement_service import user_management_logger
from src.usermanagement_service.models.user_model import UsersModel


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

        self.user_instance=None

        # Log all parameters
        for key, value in vars(self).items():
            user_management_logger.info("Initialized %s with value: %s", key, value)

    def add_user(self):
        try:
            self.user_instance: dict = self.create_user_dict()
            if self.user_instance is None:
                user_management_logger.error(
                    "Instance creation for User :: [FAILED] :: %s", self.user_instance
                )
            else:
                user_management_logger.info(
                    "Returning :: %s , ID :: %s", self.user_instance, id(self.user_instance)
                )
                user_management_logger.info(
                    "Instance creation for User :: [SUCCESS] :: %s", self.user_instance
                )
            return self.user_instance
        except Exception as ex:
            user_management_logger.exception(
                "Error occurred :: %s\tLine No:: %s", ex, sys.exc_info()[2].tb_lineno
            )
            print("Error occurred :: %s\tLine No:: %s", ex, sys.exc_info()[2].tb_lineno)
            return None

    def create_user_dict(self):
        """
        Create a dictionary representation of the user object.

        Returns:
            dict: A dictionary containing user data.
        """
        try:
            user_dict = {
                "username": self.username,
                "firstname": self.firstname,
                "lastname": self.lastname,
                "password": self.pwd,
                "email": self.email,
                "dateofbirth": self.dateofbirth,
                "created_at": self.created_at,
                "updated_at": self.updated_at,
            }
            return user_dict
        except Exception as ex:
            print("Error occurred :: %s\tLine No:: %s", ex, sys.exc_info()[2].tb_lineno)
            return None

    def map_user_instance_to_db_model(self):
        try:
            user_management_logger.info(
                "Mapping the request data to the database model:: [STARTED]"
            )
            user_map_db_instance: UsersModel = UsersModel(
                Username=self.user_instance["username"],
                FirstName=self.user_instance["firstname"],
                LastName=self.user_instance["lastname"],
                Email=self.user_instance["email"],
                DateOfBirth=self.user_instance["dateofbirth"],
                Password=self.user_instance["password"],
                CreatedAt=self.user_instance["created_at"],
                UpdatedAt=self.user_instance["updated_at"],
            )
            if user_map_db_instance is None:
                user_management_logger.info(
                    "Mapping the request data to the database model:: [FAILED]"
                )
                return user_map_db_instance
            user_management_logger.info(
                "Mapping the request data to the database model:: [SUCCESS]"
            )
            return user_map_db_instance
        except Exception as ex:
            user_management_logger.exception(
                "Error occurred :: %s\tLine No:: %s", ex, sys.exc_info()[2].tb_lineno
            )
            print("Error occurred :: %s\tLine No:: %s", ex, sys.exc_info()[2].tb_lineno)
            return None
