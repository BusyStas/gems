from flask import Blueprint, request

bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Import profile module lazily to avoid circular imports
from routes import profile as profile_bp


@bp.route('/users/<google_id>/gem-preferences/', methods=['GET'])
def list_user_gem_preferences(google_id):
    return profile_bp.api_list_user_gem_preferences(google_id)


@bp.route('/users/<google_id>/gem-preferences/<gem_type_name>', methods=['GET', 'POST'])
def user_gem_preference(google_id, gem_type_name):
    return profile_bp.api_user_gem_preference(google_id, gem_type_name)
