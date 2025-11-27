from flask import Blueprint, request, jsonify, current_app
import os
import json

bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Import profile module lazily to avoid circular imports
from routes import profile as profile_bp


@bp.route('/users/<google_id>/gem-preferences/', methods=['GET'])
def list_user_gem_preferences(google_id):
    return profile_bp.api_list_user_gem_preferences(google_id)


@bp.route('/users/<google_id>/gem-preferences/<gem_type_name>', methods=['GET', 'POST'])
def user_gem_preference(google_id, gem_type_name):
    return profile_bp.api_user_gem_preference(google_id, gem_type_name)


@bp.route('/listings-view/', methods=['GET'])
def listings_view():
    """Return listings for a gem or gem_type_id.

    Query params supported:
      - gem (string) : match against `gem` field in listing
      - gem_type_id (int|string) : exact match against `gem_type_id` field in listing

    Returns JSON: { items: [...] }
    """
    gem = str(request.args.get('gem') or '').strip()
    gem_type_id = request.args.get('gem_type_id')

    data_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'listings_sample.json')
    items = []
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r', encoding='utf-8') as fh:
                items = json.load(fh) or []
        except Exception as e:
            current_app.logger.error('Error reading listings sample file: %s', e)

    if not isinstance(items, list):
        items = []

    filtered = []
    for it in items:
        try:
            # Skip closed listings
            if str(it.get('is_closed', False)).lower() in ('true', '1'):
                continue

            if gem_type_id:
                # require exact match when filtering by id
                if str(it.get('gem_type_id') or '') != str(gem_type_id):
                    continue
            elif gem:
                if gem.lower() not in str(it.get('gem') or '').lower() and gem.lower() not in str(it.get('title') or '').lower():
                    continue

            filtered.append(it)
        except Exception:
            continue

    # sort by carat_weight descending
    try:
        filtered.sort(key=lambda x: float(x.get('carat_weight') or 0), reverse=True)
    except Exception:
        pass

    return jsonify({'items': filtered})
