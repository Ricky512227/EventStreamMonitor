import logging
import os
import sys
import datetime

# class LogMonitor:
#     log_file_path = None
#     log_time_format = "%Y-%m-%d %H:%M:%S"
#     log_file_format ='%(asctime)s - %(levelname)s - [%(filename)s : %(funcName)s - %(lineno)d] :: %(message)s'
#     log_level = logging.DEBUG
#     log_file_mode = 'w'
#     project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#     log_file_name = datetime.datetime.now().strftime("%Y%m%d_%H") + ".log"
#     def __init__(self, service_name):
#         self.service_name = service_name
#     @classmethod
#     def create_logger_for_service(cls, service_name):
#         try:
#             service_dir = os.path.join(cls.project_dir, 'logs', service_name)
#             if not os.path.exists(service_dir):
#                 os.makedirs(service_dir)
#             log_file_path = os.path.join(service_dir, cls.log_file_name)
#             logger = logging.getLogger(service_name)
#             formatter = logging.Formatter(cls.log_file_format, datefmt=cls.log_time_format)
#             file_handler = logging.FileHandler(log_file_path, mode=cls.log_file_mode)
#             file_handler.setFormatter(formatter)
#             logger.setLevel(cls.log_level)
#             logger.addHandler(file_handler)
#             logger.info("Initialized logger for the service [{0}] :: [SUCCESS]".format(service_name))
#             return logger
#         except Exception as ex:
#             print("Initialized logger for the service [{0}] :: [FAILED]".format(service_name))
#             print(f'Error occurred :: {ex} \tLine No: {sys.exc_info()[2].tb_lineno}')
#             return logging.getLogger(__name__)

import logging
import os
import sys
import datetime


class LogMonitor:
    _instance = None  # Class variable to store the instance

    log_file_path = None
    log_time_format = "%Y-%m-%d %H:%M:%S"
    log_file_format = "%(asctime)s - %(levelname)s - [%(filename)s : %(funcName)s - %(lineno)d] :: %(message)s"
    log_level = logging.DEBUG
    log_file_mode = "w"
    project_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    log_file_name = datetime.datetime.now().strftime("%Y%m%d_%H") + ".log"

    def __new__(cls, service_name):
        # Implement the Singleton pattern: return the existing instance if it exists
        if cls._instance is None:
            cls._instance = super(LogMonitor, cls).__new__(cls)
            cls._instance.service_name = service_name
            cls._instance.initialize_logger()
        return cls._instance

    def initialize_logger(self):
        try:
            service_dir = os.path.join(self.project_dir, "logs",
                                       self.service_name)
            if not os.path.exists(service_dir):
                os.makedirs(service_dir)
            log_file_path = os.path.join(service_dir, self.log_file_name)
            self.logger = logging.getLogger(self.service_name)
            formatter = logging.Formatter(self.log_file_format,
                                          datefmt=self.log_time_format)
            file_handler = logging.FileHandler(log_file_path,
                                               mode=self.log_file_mode)
            file_handler.setFormatter(formatter)
            self.logger.setLevel(self.log_level)
            self.logger.addHandler(file_handler)
            self.logger.info(
                "Initialized logger for the service [{0}] :: [SUCCESS]".format(
                    self.service_name))
        except Exception as ex:
            print(
                "Initialized logger for the service [{0}] :: [FAILED]".format(
                    self.service_name))
            print(
                f"Error occurred :: {ex} \tLine No: {sys.exc_info()[2].tb_lineno}"
            )
            self.logger = logging.getLogger(__name__)
