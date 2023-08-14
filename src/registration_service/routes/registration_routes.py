from src.registration_service.blueprints.user_blueprints import user_blueprint
from src.registration_service.controllers.registration_controller import add_user


# Create a blueprint
# add route to the blueprint
# register the blueprint to the app.

def bind_reg_blueprints(app_name, blueprint_name):
    print("Register Blueprint :: {0} to the APP :: {1}".format(blueprint_name, app_name))
    app_name.register_blueprint(blueprint_name)
    return app_name


def display_reg_blueprints_per_service(app_name):
    for url_bp in app_name.url_map.iter_rules():
        print("Registered BluePrints {0} for the APP :: {1}".format(url_bp, app_name))


user_blueprint.route('/api/v1/airliner/registerUser', methods=['POST'])(add_user)
# # user_blueprint.route('/api/v1/airliner/generateToken', methods=['POST'])(create_token)
# # user_blueprint.route('/api/v1/airliner/deregisterUser', methods=['DELETE'])(remove_user)
