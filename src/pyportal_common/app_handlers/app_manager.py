import logging
from typing import Union, Any
from flask import Flask
from flask import Blueprint
from flask_jwt_extended import JWTManager
import sys
import json
import jsonschema


class AppHandler:
    def __init__(self, logger_instance: logging.Logger) -> None:
        self.cmn_logger = logger_instance
        # Log all parameters
        for key, value in vars(self).items():
            self.cmn_logger.info(f"Initialized {key} with value: {value}")

    def create_app_instance(self) -> Union[Flask, None]:
        try:
            self.cmn_logger.info("Received Service [{0}]".format(self.cmn_logger.name))
            app_instance = Flask(self.cmn_logger.name)
            self.cmn_logger.info(
                "Created of Flask Application Instance for service [{0}]".format(self.cmn_logger.name))
            return app_instance
        except ImportError as ex:
            self.cmn_logger.error("ImportError occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("ImportError occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        except TypeError as ex:
            self.cmn_logger.error("TypeError occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("TypeError occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        except Exception as ex:
            self.cmn_logger.error("Exception occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Exception occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

    def bind_jwt_manger_to_app_instance(self, app_instance: Flask) -> Union[JWTManager, None]:
        try:
            jwt_instance = JWTManager(app_instance)
            return jwt_instance
        except Exception as ex:
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            self.cmn_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

    def create_blueprint_instance(self) -> Union[Blueprint, None]:
        try:
            blueprint_instance = Blueprint(self.cmn_logger.name + "_bp", __name__)
            self.cmn_logger.info("Created Blueprint :: {0} for the Application service ::{1}".format(blueprint_instance,
                                                                                                     self.cmn_logger.name))
            return blueprint_instance
        except Exception as ex:
            self.cmn_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

    def register_blueprint_for_service(self, app_instance: Flask, blueprint_instance: Blueprint) -> Union[Flask, None]:
        try:
            self.cmn_logger.info("Registering blueprints to the service :: {0}".format(app_instance))
            return app_instance.register_blueprint(blueprint_instance)
        except Exception as ex:
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

    def display_registered_blueprints_for_service(self, app_instance: Flask):
        try:
            for rule in app_instance.url_map.iter_rules():
                self.cmn_logger.info("Added Blueprints :: {0}".format(rule))
        except Exception as ex:
            self.cmn_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

    def read_json_schema(self, schema_file_path: str) -> tuple[bool, Union[dict[Any, Any], dict[str, Any], dict[str, str]]]:
        try:
            self.cmn_logger.info("Received Schema File Path : {0}".format(schema_file_path))
            with open(schema_file_path, "r") as schema_file:
                loaded_status = True
                loaded_schema = dict(json.load(schema_file))
        except FileNotFoundError as ex:
            self.cmn_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print(f"Schema file not found: {schema_file_path}")
        except json.JSONDecodeError as ex:
            self.cmn_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print(f"Invalid JSON syntax in the schema file: {ex}")
        except Exception as ex:
            self.cmn_logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            print('Error occurred :: {0} \tLine No: {1}'.format(ex, sys.exc_info()[2].tb_lineno))
        self.cmn_logger.info("Schema Validation {0}".format(loaded_status))
        return loaded_status, loaded_schema

    def generate_req_missing_params(self, rec_req_params, loaded_schema):
        try:
            missing_params_err_obj = {}
            self.cmn_logger.info("Validation for Request is  :: [STARTED]")
            for key, value in rec_req_params.items():
                self.cmn_logger.info(
                    "REQUEST <==> params ==> Param :: {0} :: Value :: {1} :: Type ::{2} ".format(key, value,
                                                                                                 type(value)))

            try:
                jsonschema.validate(instance=rec_req_params, schema=loaded_schema)
            except jsonschema.exceptions.ValidationError as ex:
                self.cmn_logger.info("Checking the data and doing validations...")
                # Get the list of required properties from the schema
                required_properties = loaded_schema.get("required", [])
                self.cmn_logger.info("Required_Properties_As_Per_Schema :: {0}".format(required_properties))
                # Get the list of missing required properties from the validation error
                missing_params = [property_name for property_name in required_properties if
                                  property_name not in ex.instance]
                self.cmn_logger.info("Missing params found :: {0}".format(missing_params))
                missing_params_err_obj = {'details': {'params': missing_params}}
                self.cmn_logger.info(
                    "Packing message for missing property which are found :: {0}".format(missing_params))
                self.cmn_logger.info("Validation for Request is  :: [SUCCESS]")
        except Exception as ex:
            missing_params_err_obj = {}
            self.cmn_logger.error("Validation for Request is  :: [FAILED]")
            print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
            # print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
        return missing_params_err_obj
