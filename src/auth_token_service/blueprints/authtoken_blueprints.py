from src.airliner_common.base_app_blueprints import AppBluePrint
from src.auth_token_service import auth_server_app


blueprint_obj = AppBluePrint("authtoken_blueprint", auth_server_app)
authtoken_blueprint = blueprint_obj.create_blueprint_name()