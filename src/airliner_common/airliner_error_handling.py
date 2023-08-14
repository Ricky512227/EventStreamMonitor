import jsonschema, json
# rec_req_headers = {
#                    'Content-Type': 'application/json',
#                    'User-Agent': 'PostmanRuntime/7.32.3',
#                    'Accept': '*/*',
#                    'Postman-Token': 'e060e477-601b-4ceb-9112-84bb5fb4f5d1',
#                    'Host': '127.0.0.1:5000',
#                    'Accept-Encoding': 'gzip, deflate, br',
#                    'Connection': 'keep-alive',
#                    'Content-Length': '191'
#                    }
# rec_req_headers = { 'User-Agent': 'PostmanRuntime/7.32.3', 'Accept': '*/*', 'Postman-Token': 'e060e477-601b-4ceb-9112-84bb5fb4f5d1', 'Host': '127.0.0.1:5000', 'Accept-Encoding': 'gzip, deflate, br', 'Connection': 'keep-alive', 'Content-Length': '191'}
# rec_req_headers = {'Accept': '*/*', 'Postman-Token': 'e060e477-601b-4ceb-9112-84bb5fb4f5d1', 'Host': '127.0.0.1:5000', 'Accept-Encoding': 'gzip, deflate, br', 'Connection': 'keep-alive', 'Content-Length': '191'


class AirlinerSchemaValidationError:
    error = "BAD_REQUEST"
    status_code = 400
    def __init__(self, message, error_details):
        self.message = message
        self.error_details = error_details
        self.errors = error_details
    def to_dict(self):
        return {
            "error": self.error,
            "message": self.message,
            "status_code": self.status_code,
            "errors": self.error_details
        }










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