from typing import Union, Optional, Any
from flask import make_response
from pyportal_common.error_handlers.base_error_handler import PyPortalAdminBaseError


class PyPortalAdminNotFoundError(PyPortalAdminBaseError):

    def __init__(self, logger_instance, message=None, error_details=None):
        # self.cmn_logger.info("Initializing PyPortalAdminBaseError object ID: {0}".format(id(self)))
        super().__init__(logger=logger_instance,
                         message=message,
                         error_details=error_details)
        self.error = "NOT_FOUND"
        self.status_code = 404
        # Log all parameters
        for key, value in vars(self).items():
            self.cmn_logger.info(f"Initialized {key} with value: {value}")
        self.cmn_logger.info(
            "Initialed PyPortalAdminBaseError object ID: {0}".format(id(self)))

    def get_custom_error(self):
        return self.error

    def get_custom_status_code(self):
        return self.status_code


def send_notfound_request_error_to_client(
    app_logger_name,
    message_data: Optional[str] = None,
    err_details: Optional[Any] = None,
) -> Union[make_response, None]:
    not_found_error_obj = PyPortalAdminNotFoundError(
        logger_instance=app_logger_name,
        message=message_data,
        error_details=err_details)
    return not_found_error_obj.send_response_to_client
