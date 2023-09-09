from flask import make_response, json
import sys
from abc import ABC, abstractmethod

class PyPortalAdminBaseError(ABC):
    def __init__(self, message=None, error_details=None, logger=None):
        super().__init__()
        self.message = message
        self.error_details = error_details
        self.err_response = None
        self.serialized_err_res = None
        self.error_res = {}
        self.logger = logger


    @abstractmethod
    def get_custom_status_code(self):
        pass
    @abstractmethod
    def get_custom_error(self):
        pass

    def prepare_error_response(self):
        try:
            self.logger.debug("Preparing Err_response :: [STARTED]")
            self.error_res.update({"error": self.get_custom_error()})
            if self.message is not None:
                self.error_res.update({"message": self.message})
            if self.error_details is not None:
                self.error_res.update({"error_details": self.error_details})
            self.logger.debug("Preparing Err_response :: [SUCCESS]")
            return self.error_res
        except Exception as ex:
            self.logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

    def serialize_prepared_error_response(self):
        try:
            self.logger.debug("Before Serializing the error response body :: {0}".format(self.error_res))
            self.serialized_err_res = json.dumps(self.error_res)
            self.logger.debug("After Serializing the error response body :: {0}".format(self.serialized_err_res))
            self.err_response = make_response(self.serialized_err_res)
            self.err_response.headers['Content-Type'] = 'application/problem+json'
            self.err_response.headers['Cache-Control'] = 'no-cache'
            self.err_response.status_code = self.get_custom_status_code()
            self.logger.debug("Packed Response headers:: {0}".format(self.err_response.headers))
            self.logger.debug("Packed Response response:: {0}".format(self.err_response.data))
            self.logger.debug("Prepared Err_response :: [SUCCESS]:: {0}".format(self.err_response))
            return self.err_response
        except Exception as ex:
            self.logger.error("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))


class PyPortalAdminInvalidRequestError(PyPortalAdminBaseError):
    error = "BAD_REQUEST"
    status_code = 400

    def __init__(self, message=None, error_details=None, logger=None):
        super().__init__(message=message, error_details=error_details)
        self.logger = logger
        self.final_error_resposne = None
        self.error_data_prepared = None

    def get_custom_error(self):
        return self.error

    def get_custom_status_code(self):
        return self.status_code



    def send_resposne_to_client(self):
        self.error_data_prepared = self.prepare_error_response()
        self.final_error_resposne = self.serialize_prepared_error_response()
        return self.final_error_resposne



class PyPortalAdminInternalServerError(PyPortalAdminBaseError):
    error = "INTERNAL_SERVER_ERROR"
    status_code = 500


    def __init__(self, message=None, error_details=None, logger=None):
        super().__init__(message=message, error_details=error_details)
        self.final_error_resposne = None
        self.error_data_prepared = None
        self.logger= logger
    def get_custom_error(self):
        return self.error

    def get_custom_status_code(self):
        return self.status_code

    def send_response_to_client(self):
        self.error_data_prepared = self.prepare_error_response()
        self.final_error_resposne = self.serialize_prepared_error_response()
        return self.final_error_resposne

class PyPortalAdminNotFoundError(PyPortalAdminBaseError):
    error = "NOT_FOUND"
    status_code = 404

    def __init__(self, message=None, error_details=None, logger=None):
        super().__init__(message=message, error_details=error_details)
        self.final_error_resposne = None
        self.error_data_prepared = None
        self.logger = logger

    def get_custom_error(self):
        return self.error

    def get_custom_status_code(self):
        return self.status_code

    def send_response_to_client(self):
        self.error_data_prepared = self.prepare_error_response()
        self.final_error_resposne = self.serialize_prepared_error_response()
        return self.final_error_resposne





#
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
