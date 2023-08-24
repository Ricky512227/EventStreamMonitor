
class AirlinerErrorDetails:
    def __init__(self, message=None, error_details=None):
        self.message = message
        self.error_details = error_details

class AirlinerError500(AirlinerErrorDetails):
    error = "INTERNAL_SERVER_ERROR"
    status_code = 500
    def __init__(self):
        super().__init__()
    def to_dict(self):
        response_500={
                        "status_code": self.status_code,
                        "error": self.error,
                        "message": self.message,
                        "errors": self.error_details
        }
        if self.message is None:
            del response_500["message"]
        if self.error_details is None:
            del response_500["errors"]
        return response_500

class AirlinerError400(AirlinerErrorDetails):
    error = "BAD_REQUEST"
    status_code = 400
    def __init__(self):
        super().__init__()

    def to_dict(self):

        response_400 = {
            "status_code": self.status_code,
            "error": self.error,
            "message": self.message,
            "error_details": self.error_details
        }

        if self.message is None:
            del response_400["message"]
        if self.error_details is None:
            del response_400["errors"]

        return response_400

class AirlinerError404(AirlinerErrorDetails):
    error = "NOT_FOUND"
    status_code = 404
    def __init__(self):
        super().__init__()
    def to_dict(self):
        response_404 = {
            "status_code": self.status_code,
            "error": self.error,
            "message": self.message,
            "errors": self.error_details
        }
        if self.message is None:
            del response_404["message"]
        if self.error_details is None:
            del response_404["errors"]
        return response_404

class AirlinerError405(AirlinerErrorDetails):
    error = "METHOD_NOT_ALLOWED"
    status_code = 405
    def __init__(self):
        super().__init__()
    def to_dict(self):
        response_404 = {
            "status_code": self.status_code,
            "error": self.error,
            "message": self.message,
            "errors": self.error_details
        }
        if self.message is None:
            del response_404["message"]
        if self.error_details is None:
            del response_404["errors"]
        return response_404




# internal_server_error = AirlinerError500()
# # internal_server_error.message = "An internal server error occurred."
# # internal_server_error.error_details = "Additional details about the error."
# error_dict = internal_server_error.to_dict()
# print(error_dict)




















# sqlalchemy.exc.IntegrityError: This exception is raised when there is a violation of the database's integrity constraints. For example, if you try to insert a record with a duplicate primary key or violate a unique constraint, an IntegrityError will be raised.
#
# sqlalchemy.exc.FlushError: This exception is raised if there is an error during the process of flushing changes to the database. The flush process is part of the commit() operation.
#
# sqlalchemy.exc.StatementError: This exception is raised when there is an error with the SQL statement being executed.
#
# sqlalchemy.exc.ResourceClosedError: This exception is raised if you try to access a closed database resource (such as a closed result set or closed connection).
#
# sqlalchemy.exc.InvalidRequestError: This exception is raised for various types of invalid requests, such as attempting to use an expired session or accessing an attribute that doesn't exist on a mapped class.
#
# sqlalchemy.exc.DBAPIError: This is a generic exception for errors raised by the underlying database API.
#
# It's important to note that the specific exception that will be raised during the add() operation can depend on various factors, including the type of database being used, the structure of the database schema, and the configuration of SQLAlchemy.
#
# To handle these exceptions, you can use a try-except block and catch sqlalchemy.exc.IntegrityError specifically if you want to handle integrity constraint violations. For other exceptions, you can catch sqlalchemy.exc.SQLAlchemyError, which is the base class for all SQLAlchemy exceptions.
#
# Here's an example of how you can handle exceptions during the add() operation:
#
#
#
#
#
#
#












#
#     "InternalServerError": {
#         "message": "Something went wrong",
#         "status": 500
#     },
#     "SchemaValidationError": {
#         "error": "BAD_REQUEST",
#         "message": "Invalid JSON request",
#         "code": 400,
#         "errors": [{'fields': ['Content-Type', 'Content-Length']}]
#     },
#     "AirlinerAlreadyExistsError": {
#         "message": "Airliner with given name already exists",
#         "status": 400
#     },
#     "UpdatingAirlinerError": {
#         "message": "Updating airliner added by other is forbidden",
#         "status": 403
#     },
#     "DeletingAirlinerError": {
#         "message": "Deleting airliner added by other is forbidden",
#         "status": 403
#     },
#     "AirlinerNotExistsError": {
#         "message": "Airliner with given id doesn't exists",
#         "status": 400
#     },
#     "UnauthorizedError": {
#         "message": "Invalid username or password",
#         "status": 401
#     }
#
# }