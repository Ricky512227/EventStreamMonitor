import os

def init_app_configs(notification_app) -> None:

    notification_app.config["FLASK_ENV"] = os.environ.get("FLASK_ENV")

    notification_app.config["DEBUG"] = os.environ.get("DEBUG")

    notification_app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")

    notification_app.config["FLASK_APP"] = os.environ.get("FLASK_APP")

    notification_app.config[

        "NOTIFICATION_SERVER_IPADDRESS"

    ] = os.environ.get(

        "NOTIFICATION_SERVER_IPADDRESS"

    )

    notification_app.config[

        "NOTIFICATION_SERVER_PORT"

    ] = os.environ.get(

        "NOTIFICATION_SERVER_PORT"

    )
