import os

def init_app_configs(usermanager_app) -> None:

    usermanager_app.config["FLASK_ENV"] = os.environ.get("FLASK_ENV")

    usermanager_app.config["DEBUG"] = os.environ.get("DEBUG")

    usermanager_app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")

    usermanager_app.config["FLASK_APP"] = os.environ.get("FLASK_APP")

    usermanager_app.config[

        "USER_MANAGEMENT_SERVER_IPADDRESS"

    ] = os.environ.get(

        "USER_MANAGEMENT_SERVER_IPADDRESS"

    )

    usermanager_app.config[

        "USER_MANAGEMENT_SERVER_PORT"

    ] = os.environ.get(

        "USER_MANAGEMENT_SERVER_PORT"

    )

    usermanager_app.config[

        "USER_MANAGEMENT_GRPC_MAX_WORKERS"

    ] = int(

        os.environ.get("USER_MANAGEMENT_GRPC_MAX_WORKERS", "10")

    )
