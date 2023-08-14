import configparser, os, sys
import json



def init_airliner_configs(configuration_file_path):
    try:
        configuration_file_path = os.path.join(configuration_file_path, "configs.ini")
        print("Configuration File Path :: {0}".format(configuration_file_path))
        print("Initializing Read configurations ...")
        config = configparser.ConfigParser()
        config.read(configuration_file_path)
        database_type = config.get('DATABASE', 'DATABASE_TYPE')
        database_user_name = config.get('DATABASE', 'DATABASE_USER_NAME')
        database_password = config.get('DATABASE', 'DATABASE_PASSWORD')
        database_ip_address = config.get('DATABASE', 'DATABASE_IP_ADDRESS')
        database_ip_port = config.get('DATABASE', 'DATABASE_PORT')
        database_name = config.get('DATABASE', 'DATABASE_NAME')
        sqlalchemy_track_modifications = config.get('DATABASE', 'SQLALCHEMY_TRACK_MODIFICATIONS')
        print("DATABASE_TYPE :: {0}".format(database_type))
        print("DATABASE_USER_NAME :: {0}".format(database_user_name))
        print("DATABASE_PASSWORD :: {0}".format(database_password))
        print("DATABASE_IP_ADDRESS :: {0}".format(database_ip_address))
        print("DATABASE_PORT :: {0}".format(database_ip_port))
        print("DATABASE_NAME :: {0}".format(database_name))
        print("SQLALCHEMY_TRACK_MODIFICATIONS :: {0}".format(sqlalchemy_track_modifications))

        airliner_configs = {
                'DATABASE_TYPE': database_type, 'DATABASE_USER_NAME':database_user_name,
                'DATABASE_PASSWORD':database_password , 'DATABASE_IP_ADDRESS':database_ip_address ,
                'DATABASE_PORT': database_ip_port , 'database_name': database_name}
        return airliner_configs
    except Exception as ex:
        print('Error occurred :: {0} \tLine No: {1}'.format(ex, sys.exc_info()[2].tb_lineno))
        #airliner_logger.error('Error occurred :: {0} \tLine No: {1}'.format(ex, sys.exc_info()[2].tb_lineno))



def read_json_schema(schema_file_path):
    loaded_status = False
    loaded_schema = None
    try:
        print("Received Schema File Path : {0}".format(schema_file_path))
        with open(schema_file_path, "r") as schema_file:
            loaded_status = True
            loaded_schema = dict(json.load(schema_file))
    except FileNotFoundError as ex:
        print(f"Schema file not found: {schema_file_path}")
    except json.JSONDecodeError as ex:
        print(f"Invalid JSON syntax in the schema file: {ex}")
    except Exception as ex:
        print('Error occurred :: {0} \tLine No: {1}'.format(ex, sys.exc_info()[2].tb_lineno))
    print("Schema Validation {0}".format(loaded_status))
    return loaded_status, loaded_schema



