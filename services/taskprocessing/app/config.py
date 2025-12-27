import os

def init_app_configs(taskprocessing_app) -> None:

    taskprocessing_app.config["FLASK_ENV"] = os.environ.get("FLASK_ENV")

    taskprocessing_app.config["DEBUG"] = os.environ.get("DEBUG")

    taskprocessing_app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")

    taskprocessing_app.config["FLASK_APP"] = os.environ.get("FLASK_APP")

    taskprocessing_app.config[

        "TASKPROCESSING_SERVER_IPADDRESS"

    ] = os.environ.get(

        "TASKPROCESSING_SERVER_IPADDRESS"

    )

    taskprocessing_app.config[

        "TASKPROCESSING_SERVER_PORT"

    ] = os.environ.get(

        "TASKPROCESSING_SERVER_PORT"

    )
