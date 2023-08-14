from flask import Blueprint
from src.airliner_service.controllers.aeroplane_controller import create_aeroplane, get_Aeroplane
aero_blueprint = Blueprint('aero_blueprint', __name__)





aero_blueprint.route('/api/v1/airliner/createAeroplane', methods=['POST'])(create_aeroplane)

aero_blueprint.route('/api/v1/airliner/getAeroplanes/<int:aeroplane_id>', methods=['GET'])(get_Aeroplane)
