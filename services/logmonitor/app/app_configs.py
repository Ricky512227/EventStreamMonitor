"""

Application configuration for Log Monitoring Service

"""

import os

def init_app_configs(app):

    """

    Initialize application configuration

    Args:

        app: Flask application instance

    """

    app.config["FLASK_ENV"] = os.environ.get("FLASK_ENV", "production")

    app.config["DEBUG"] = os.environ.get("DEBUG", "false").lower() == "true"

    app.config["LOG_MONITOR_SERVER_IPADDRESS"] = os.environ.get(

        "LOG_MONITOR_SERVER_IPADDRESS", "0.0.0.0"

    )

    app.config["LOG_MONITOR_SERVER_PORT"] = int(os.environ.get(

        "LOG_MONITOR_SERVER_PORT", 9094

    ))

    app.config["KAFKA_BOOTSTRAP_SERVERS"] = os.environ.get(

        "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"

    )
