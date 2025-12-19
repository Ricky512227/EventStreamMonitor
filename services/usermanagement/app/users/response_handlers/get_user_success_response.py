# from app.users.response_handlers.user_success_res_handler import SuccessBaseResponseBody
#
#
# class GetSuccessResponse(SuccessBaseResponseBody):
#
#     def __init__(self, response_body=None, response_message="User Retried Successfully"):
#         print(f"Object created with ID: {id(self)}")
#         super().__init__(response_body)
#         self.response_message = response_message
#
#     def get_assigned_resp_body(self):
#         return self.response_body
#
#     def get_assigned_resp_msg(self):
#         return self.response_message
