import sys
from flask import make_response, json
from abc import ABC, abstractmethod
from typing import Union


class PyPortalAdminBaseError(ABC):

    def __init__(self, logger, message=None, error_details=None) -> None:
        self.message = message
        self.error_details = error_details
        self.cmn_logger = logger
        self.cmn_logger.info(f"Initializing PyPortalAdminBaseError object ID: {id(self)}")

    @abstractmethod
    def get_custom_status_code(self) -> int:
        pass

    @abstractmethod
    def get_custom_error(self) -> str:
        pass

    @property
    def prepare_error_response(self) -> Union[dict, None]:
        try:
            error_res = {}
            self.cmn_logger.info("Preparing Err_response :: [STARTED]")
            error_res.update({"error": self.get_custom_error()})
            if self.message is not None:
                error_res.update({"message": self.message})
            if self.error_details is not None:
                error_res.update({"error_details": self.error_details})
            self.cmn_logger.info(
                "Prepared Err_response :: [SUCCESS] : {0}".format(error_res))
            return error_res
        except Exception as ex:
            self.cmn_logger.error(
                "Error occurred :: {0}\tLine No:: {1}".format(
                    ex,
                    sys.exc_info()[2].tb_lineno))

    def serialize_prepared_error_response(
            self, prep_error_res: dict) -> Union[make_response, None]:

        try:
            self.cmn_logger.debug(
                f"Before Serializing the error response body :: {prep_error_res}")
            serialized_err_res = json.dumps(prep_error_res)
            self.cmn_logger.debug(
                f"After Serializing the error response body :: {serialized_err_res}")
            err_response = make_response(serialized_err_res)
            err_response.headers["Content-Type"] = "application/problem+json"
            err_response.headers["Cache-Control"] = "no-cache"
            err_response.status_code = self.get_custom_status_code()
            self.cmn_logger.debug(f"Packed Response headers:: {err_response.headers}")
            self.cmn_logger.debug(f"Packed Response response:: {err_response.data}")
            self.cmn_logger.debug(
                f"Prepared Err_response :: [SUCCESS]:: {err_response}")
            return err_response
        except Exception as ex:
            self.cmn_logger.error(
                f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}")

    @property
    def send_response_to_client(self) -> Union[make_response, None]:
        prepared_error = self.prepare_error_response
        final_error_response = self.serialize_prepared_error_response(
            prepared_error)
        return final_error_response


#
# # sqlalchemy.exc.IntegrityError: This exception is raised when there is a violation of the database's integrity constraints. For example, if you try to insert a record with a duplicate primary key or violate a unique constraint, an IntegrityError will be raised.
# #
# # sqlalchemy.exc.FlushError: This exception is raised if there is an error during the process of flushing changes to the database. The flush process is part of the commit() operation.
# #
# # sqlalchemy.exc.StatementError: This exception is raised when there is an error with the SQL statement being executed.
# #
# # sqlalchemy.exc.ResourceClosedError: This exception is raised if you try to access a closed database resource (such as a closed result set or closed connection).
# #
# # sqlalchemy.exc.InvalidRequestError: This exception is raised for various types of invalid requests, such as attempting to use an expired session or accessing an attribute that doesn't exist on a mapped class.
# #
# # sqlalchemy.exc.DBAPIError: This is a generic exception for errors raised by the underlying database API.
# #
# # It's important to note that the specific exception that will be raised during the add() operation can depend on various factors, including the type of database being used, the structure of the database schema, and the configuration of SQLAlchemy.
# #
# # To handle these exceptions, you can use a try-except block and catch sqlalchemy.exc.IntegrityError specifically if you want to handle integrity constraint violations. For other exceptions, you can catch sqlalchemy.exc.SQLAlchemyError, which is the base class for all SQLAlchemy exceptions.
# #
# # Here's an example of how you can handle exceptions during the add() operation:
# #
#
# #
# #     "InternalServerError": {
# #         "message": "Something went wrong",
# #         "status": 500
# #     },
# #     "SchemaValidationError": {
# #         "error": "BAD_REQUEST",
# #         "message": "Invalid JSON request",
# #         "code": 400,
# #         "errors": [{'fields': ['Content-Type', 'Content-Length']}]
# #     },
# #     "AirlinerAlreadyExistsError": {
# #         "message": "Airliner with given name already exists",
# #         "status": 400
# #     },
# #     "UpdatingAirlinerError": {
# #         "message": "Updating airliner added by other is forbidden",
# #         "status": 403
# #     },
# #     "DeletingAirlinerError": {
# #         "message": "Deleting airliner added by other is forbidden",
# #         "status": 403
# #     },
# #     "AirlinerNotExistsError": {
# #         "message": "Airliner with given id doesn't exists",
# #         "status": 400
# #     },
# #     "UnauthorizedError": {
# #         "message": "Invalid username or password",
# #         "status": 401
# #     }
# #
# }
