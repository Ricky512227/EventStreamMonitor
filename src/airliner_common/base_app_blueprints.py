from flask import Blueprint


class AppBluePrint:
    def __init__(self, blueprint_name, app_name):
        self.app_name = app_name
        self.blueprint_name = blueprint_name
        self.url_bp = None

    def create_blueprint_name(self):
        # Define/Create the blueprints
        self.blueprint_name = Blueprint(self.blueprint_name, __name__)
        print("Created Blueprint name :: {0}".format(self.blueprint_name))
        return self.blueprint_name


