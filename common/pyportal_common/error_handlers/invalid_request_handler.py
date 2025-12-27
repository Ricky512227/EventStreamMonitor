from typing import Union, Optional, Any
from flask import make_response
from common.pyportal_common.error_handlers.base_error_handler import EventStreamMonitorBaseError


class EventStreamMonitorInvalidRequestError(EventStreamMonitorBaseError):

    def __init__(self, logger_instance, message=None, error_details=None):
        super().__init__(logger=logger_instance,
                         message=message,
                         error_details=error_details)
        self.error = "BAD_REQUEST"
        self.status_code = 400
        # Log all parameters
        for key, value in vars(self).items():
            self.cmn_logger.info(f"Initialized {key} with value: {value}")
        self.cmn_logger.info("Initialed EventStreamMonitorInvalidRequestError object ID: %s", id(self))

    def get_custom_error(self):
        return self.error

    def get_custom_status_code(self):
        return self.status_code


def send_invalid_request_error_to_client(
    app_logger_name,
    message_data: Optional[str] = None,
    err_details: Optional[Any] = None,
) -> Union[make_response, None]:
    invalid_request_error_obj = EventStreamMonitorInvalidRequestError(
        logger_instance=app_logger_name,
        message=message_data,
        error_details=err_details)
    return invalid_request_error_obj.send_response_to_client

#
# user_management_logger = LogMonitor("usermanagement").logger
# message = "Invalid JSON request"
# errors = [{'fields': ['Content-Type', 'Content-Length']}]
# print(send_invalid_request_error_to_client(app_logger_name=user_management_logger, message_data=message,
#                                            err_details=errors))
#
#
# user_management_logger = LogMonitor("usermanagement").logger
# errors = [{'fields': ['Content-Type', 'Content-Length']}]
# print(send_invalid_request_error_to_client(app_logger_name=user_management_logger,err_details=errors))
