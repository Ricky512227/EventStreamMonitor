from src.airliner_common.base_app_blueprints import AppBluePrint
from src.registration_service import user_app


blueprint_obj = AppBluePrint("user_blueprint", user_app)
user_blueprint = blueprint_obj.create_blueprint_name()
