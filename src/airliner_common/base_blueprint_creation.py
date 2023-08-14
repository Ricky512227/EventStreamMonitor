from flask import Blueprint

class AirlinerBluePrint:
    def __init(self, reg_app_flask_instance, blueprint_name):
        self.reg_app_flask_instance = reg_app_flask_instance
        self.blueprint_name = blueprint_name

    @classmethod
    def create_blueprint(cls, reg_app_flask_instance, blueprint_name):
        registered_blueprint = Blueprint(blueprint_name, __name__)
        print("Created Blueprint :: {0} for the Application service ::{1}".format(registered_blueprint, reg_app_flask_instance))
        return reg_app_flask_instance, registered_blueprint

    @classmethod
    def register_blueprint(cls, reg_app_flask_instance, created_blueprint_instance):
        print("Registering blueprints to the service :: {0}".format(reg_app_flask_instance))
        return reg_app_flask_instance, reg_app_flask_instance.register_blueprint(created_blueprint_instance)


    @staticmethod
    def display_registered_blueprints_for_service(reg_app_flask_instance):
        for rule in reg_app_flask_instance.url_map.iter_rules():
            print("Added Blueprints :: {0}".format(rule))



