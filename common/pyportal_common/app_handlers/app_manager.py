# pylint: disable=line-too-long
import logging
import sys
import json
from logging import Logger
from typing import Union, Any
import jsonschema
from flask import Flask
from flask import Blueprint
from flask_jwt_extended import JWTManager


class AppHandler:
    cmn_logger: Logger

    def __init__(self, logger_instance: logging.Logger) -> None:
        """
        Initialize an instance of AppHandler.

        Args:
            logger_instance (logging.Logger): The logger instance for logging.

        Returns:
            None
        """
        self.cmn_logger = logger_instance
        # Log all parameters
        for key, value in vars(self).items():
            self.cmn_logger.info(f"Initialized {key} with value: {value}")

    def create_app_instance(self) -> Union[Flask, None]:
        """
        Create a Flask application instance.

        Returns:
            Union[Flask, None]: The Flask application instance or None
                if an exception occurs.
        """
        try:
            self.cmn_logger.info(
                f"Received Service [{self.cmn_logger.name}]"
            )
            app_instance = Flask(self.cmn_logger.name)
            self.cmn_logger.info(
                f"Created Flask Application Instance for service "
                f"[{self.cmn_logger.name}]"
            )
            return app_instance
        except ImportError as ex:
            self.cmn_logger.error(
                f"ImportError occurred :: {ex}\t"
                f"Line No:: {sys.exc_info()[2].tb_lineno}"
            )
            return None
        except TypeError as ex:
            self.cmn_logger.error(
                f"TypeError occurred :: {ex}\t"
                f"Line No:: {sys.exc_info()[2].tb_lineno}"
            )
            return None
        except Exception as ex:
            self.cmn_logger.exception(
                f"Exception occurred :: {ex}\t"
                f"Line No:: {sys.exc_info()[2].tb_lineno}"
            )
            return None

    def bind_jwt_manger_to_app_instance(
            self, app_instance: Flask) -> Union[JWTManager, None]:
        """
        Bind JWTManager to a Flask application instance.

        Args:
            app_instance (Flask): The Flask application instance.

        Returns:
            Union[JWTManager, None]: The JWTManager instance or None
                if an exception occurs.
        """
        try:
            jwt_instance = JWTManager(app_instance)
            return jwt_instance
        except Exception as ex:
            self.cmn_logger.exception(
                f"Error occurred :: {ex}\t"
                f"Line No:: {sys.exc_info()[2].tb_lineno}"
            )
            return None

    def create_blueprint_instance(self) -> Union[Blueprint, None]:
        """
        Create a Blueprint instance.

        Returns:
            Union[Blueprint, None]: The Blueprint instance or None
                if an exception occurs.
        """
        try:
            # Replace dots with underscores in logger name for blueprint
            blueprint_name = self.cmn_logger.name.replace(".", "_") + "_bp"
            blueprint_instance = Blueprint(
                blueprint_name, __name__
            )
            self.cmn_logger.info(
                f"Created Blueprint :: {blueprint_instance} "
                f"for the Application service ::{self.cmn_logger.name}"
            )
            return blueprint_instance
        except Exception as ex:
            self.cmn_logger.exception(
                f"Error occurred :: {ex}\t"
                f"Line No:: {sys.exc_info()[2].tb_lineno}"
            )
            return None

    def register_blueprint_for_service(
            self, app_instance: Flask,
            blueprint_instance: Blueprint) -> Union[Flask, None]:
        """
        Register a Blueprint for a Flask service.

        Args:
            app_instance (Flask): The Flask application instance.
            blueprint_instance (Blueprint): The Blueprint instance to register.

        Returns:
            Union[Flask, None]: The Flask application instance or None
                if an exception occurs.
        """
        try:
            self.cmn_logger.info(
                f"Registering blueprints to the service :: {app_instance}"
            )
            return app_instance.register_blueprint(blueprint_instance)
        except Exception as ex:
            self.cmn_logger.error(
                f"Error occurred :: {ex}\t"
                f"Line No:: {sys.exc_info()[2].tb_lineno}"
            )
            return None

    def display_registered_blueprints_for_service(self, app_instance: Flask):
        """
        Display registered blueprints for a Flask service.

        Args:
            app_instance (Flask): The Flask application instance.

        Returns:
            None
        """
        try:
            for rule in app_instance.url_map.iter_rules():
                self.cmn_logger.info(f"Added Blueprints :: {rule}")
        except Exception as ex:
            self.cmn_logger.exception(
                f"Error occurred :: {ex}\t"
                f"Line No:: {sys.exc_info()[2].tb_lineno}"
            )

    def read_json_schema(
        self, schema_file_path: str
    ) -> tuple[bool, Union[dict[Any, Any], dict[str, Any], dict[str, str]]]:
        """
        Read a JSON schema file and load its contents.

        Args:
            schema_file_path (str): The path to the JSON schema file.

        Returns:
            tuple[bool, Union[dict[Any, Any], dict[str, Any], dict[str, str]]]:
                A tuple containing a boolean indicating success or failure
                of schema loading and the loaded schema.
        """
        loaded_status = False
        loaded_schema = {}
        try:
            self.cmn_logger.info(
                f"Received Schema File Path : {schema_file_path}"
            )
            with open(schema_file_path, "r", encoding="utf-8") as schema_file:
                loaded_status = True
                loaded_schema = dict(json.load(schema_file))
        except FileNotFoundError as ex:
            self.cmn_logger.error(
                f"Error occurred :: {ex}\t"
                f"Line No:: {sys.exc_info()[2].tb_lineno}"
            )
        except json.JSONDecodeError as ex:
            self.cmn_logger.error(
                f"Error occurred :: {ex}\t"
                f"Line No:: {sys.exc_info()[2].tb_lineno}"
            )
        except Exception as ex:
            self.cmn_logger.exception(
                f"Error occurred :: {ex}\t"
                f"Line No:: {sys.exc_info()[2].tb_lineno}"
            )
        self.cmn_logger.info(f"Schema Validation {loaded_status}")
        return loaded_status, loaded_schema

    def generate_req_missing_params(self, rec_req_params, loaded_schema):
        """
        Generate a dictionary of missing required parameters in a request
        based on a JSON schema.

        Args:
            rec_req_params (dict): The received request parameters.
            loaded_schema (dict): The loaded JSON schema.

        Returns:
            dict: A dictionary containing missing required parameters,
                if any.
        """
        missing_params_err_obj = {}
        try:
            self.cmn_logger.info("Validation for Request is  :: [STARTED]")
            for key, value in rec_req_params.items():
                self.cmn_logger.info(
                    f"REQUEST <==> params ==> Param :: {key} :: "
                    f"Value :: {value} :: Type ::{type(value)} "
                )

            try:
                jsonschema.validate(
                    instance=rec_req_params, schema=loaded_schema
                )
            except jsonschema.exceptions.ValidationError as ex:
                self.cmn_logger.info(
                    "Checking the data and doing validations..."
                )
                # Get the list of required properties from the schema
                required_properties = loaded_schema.get("required", [])
                self.cmn_logger.info(
                    f"Required_Properties_As_Per_Schema :: "
                    f"{required_properties}"
                )
                # Get the list of missing required properties
                # from the validation error
                missing_params = [
                    property_name for property_name in required_properties
                    if property_name not in ex.instance
                ]
                self.cmn_logger.info(
                    f"Missing params found :: {missing_params}"
                )
                missing_params_err_obj = {
                    "details": {"params": missing_params}
                }
                self.cmn_logger.info(
                    f"Packing message for missing property which are "
                    f"found :: {missing_params}"
                )
                self.cmn_logger.info("Validation for Request is  :: [SUCCESS]")
        except Exception:
            missing_params_err_obj = {}
            self.cmn_logger.exception("Validation for Request is  :: [FAILED]")
        return missing_params_err_obj
