import os


def init_app_configs(booking_app) -> None:
    booking_app.config["FLASK_ENV"] = os.environ.get("FLASK_ENV")
    booking_app.config["DEBUG"] = os.environ.get("DEBUG")
    booking_app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
    booking_app.config["FLASK_APP"] = os.environ.get("FLASK_APP")

    booking_app.config[
        "BOOKING_SERVER_IPADDRESS"
    ] = os.environ.get(
        "BOOKING_SERVER_IPADDRESS"
    )
    booking_app.config[
        "BOOKING_SERVER_PORT"
    ] = os.environ.get(
        "BOOKING_SERVER_PORT"
    )

