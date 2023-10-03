
import sys
import datetime
import bcrypt
from src.usermanagement_service import user_management_logger
from src.usermanagement_service.models.user_model import UsersModel


class User:
    def __init__(self, username=None, firstname=None, lastname=None, dateofbirth=None, email=None, pwd=None):
        """
        Initialize the User instance and log initialization information.
        """
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.dateofbirth = dateofbirth
        self.email = email
        self.pwd = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())
        self.created_at = str(datetime.datetime.now())
        self.updated_at = str(datetime.datetime.now())

        # Log all parameters
        for key, value in vars(self).items():
            user_management_logger.info(f"Initialized {key} with value: {value}")

    def add_user(self):
        try:
            user_instance = self.create_user_dict()
            if user_instance is None:
                user_management_logger.error("Instance creation for User :: [FAILED] :: {0}".format(user_instance))
            else:
                user_management_logger.info("Returning :: {0} , ID :: {1}".format(user_instance, id(user_instance)))
                user_management_logger.info("Instance creation for User :: [SUCCESS] :: {0}".format(user_instance))
            return user_instance
        except Exception as ex:
            user_management_logger.error(
                "Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

    def create_user_dict(self):
        user_dict = None
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
                "updated_at": self.updated_at}
        except Exception as ex:
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return user_dict

    def map_user_instance_to_db_model(self):
        try:
            user_instance = self.create_user_dict()
            user_management_logger.info("Mapping the request data to the database model:: [STARTED]")
            user_map_db_instance = UsersModel(Username=user_instance["username"], FirstName=user_instance["firstname"],
                                              LastName=user_instance["lastname"], Email=user_instance["email"],
                                              DateOfBirth=user_instance["dateofbirth"],
                                              Password=user_instance["password"], CreatedAt=user_instance["created_at"],
                                              UpdatedAt=user_instance["updated_at"])
            if user_map_db_instance is None:
                user_management_logger.info("Mapping the request data to the database model:: [FAILED]")
                return user_map_db_instance
            user_management_logger.info("Mapping the request data to the database model:: [SUCCESS]")
            return user_map_db_instance
        except Exception as ex:
            user_management_logger.error(
                "Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
