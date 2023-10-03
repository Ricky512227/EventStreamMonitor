from src.usermanagement_service import user_management_logger
from src.usermanagement_service.users.response_handlers.user_success_response import SuccessBaseResponseBody


class CreateSuccessResponse(SuccessBaseResponseBody):
    def __init__(self, response_body=None, response_message="User Created Successfully"):
        user_management_logger.info("Initializing SuccessBaseResponseBody object ID: {0}".format(id(self)))
        super().__init__(response_body)
        self.response_message = response_message
        user_management_logger.info("Received response_message: {0}".format(self.response_message))
        user_management_logger.info("Initialized SuccessBaseResponseBody object ID: {0}".format(id(self)))

    def get_assigned_resp_body(self):
        return self.response_body

    def get_assigned_resp_msg(self):
        return self.response_message

# sampledata = {'data': {'CreatedAt': '2023-09-12 08:02:02', 'UpdatedAt': '2023-09-12 08:02:02', 'DateOfBirth': '06-4-1997', 'Email': 'devarapallikama123mail.com', 'FirstName': 'kamal', 'LastName': 'devarapalli', 'ID': 1000, 'Username': '123'}}
# such = CreateSuccessResponse(response_body=sampledata)
# print(such.generate_success_response())
