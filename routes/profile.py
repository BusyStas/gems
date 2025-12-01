from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
import os
import requests
from utils.db_logger import log_db_exception
from utils.api_client import load_api_key

bp = Blueprint('profile', __name__, url_prefix='/profile')


def get_gemdb_url():
    """Get the gemdb API URL from config."""
    return current_app.config.get('GEMDB_API_URL', 'https://api.preciousstone.info')


def get_gemdb_headers():
    """Get headers for gemdb API calls."""
    token = load_api_key() or ''
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['X-API-Key'] = token
    return headers


def load_current_user():
    # Prefer Flask-Login current_user if available
    try:
        from flask_login import current_user
        if getattr(current_user, 'is_authenticated', False):
            return current_user
    except Exception:
        pass
    # No demo/session fallback — require real logged-in user (Flask-Login)
    return None


@bp.route('/')
def show_profile():
    user = load_current_user()
    if not user:
        # redirect to login
        return redirect(url_for('auth.login'))

    # Load all gem types for the preferences tab (need both id and name)
    try:
        from utils.api_client import get_gems_from_api
        gems_api = get_gems_from_api() or []
        # v2 API uses PascalCase: GemTypeId, GemTypeName
        gem_types = sorted(
            [{'id': g.get('GemTypeId'), 'name': g.get('GemTypeName')}
             for g in gems_api if g.get('GemTypeName') and g.get('GemTypeId')],
            key=lambda x: x['name']
        )
    except Exception:
        gem_types = []

    return render_template('profile/profile.html', user=user, gem_types=gem_types)


@bp.route('/api/v1/users/<google_id>/gem-preferences/', methods=['GET'])
def api_list_user_gem_preferences(google_id):
    """Return a list of preferences for the given user (by google_id) - proxies to gemdb API"""
    try:
        base_url = get_gemdb_url()
        headers = get_gemdb_headers()
        url = f"{base_url}/api/v2/users/{google_id}/gem-preferences"

        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            prefs = resp.json()
            # Return in expected format for frontend
            return jsonify({'user_google_id': google_id, 'preferences': prefs})
        elif resp.status_code == 404:
            return jsonify({'user_google_id': google_id, 'preferences': []})
        else:
            return jsonify({'error': 'API error', 'status': resp.status_code}), resp.status_code
    except Exception as e:
        log_db_exception(e, f'api_list_user_gem_preferences: {google_id}')
        return jsonify({'error': str(e)}), 500


@bp.route('/api/v1/users/<google_id>/gem-preferences/<int:gem_type_id>', methods=['GET', 'POST'])
def api_user_gem_preference(google_id, gem_type_id):
    """GET: retrieve preference for specified gem for this user.
       POST: create or update the preference.
       Proxies to gemdb API using gem_type_id.
    """
    try:
        base_url = get_gemdb_url()
        headers = get_gemdb_headers()
        url = f"{base_url}/api/v2/users/{google_id}/gem-preferences/{gem_type_id}"

        if request.method == 'GET':
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                return jsonify(resp.json())
            elif resp.status_code == 404:
                return jsonify({'error': 'Preference not found'}), 404
            else:
                return jsonify({'error': 'API error'}), resp.status_code

        # POST: create or update
        data = request.get_json() or {}
        # Build payload for gemdb API
        payload = {
            'is_ignored': bool(data.get('is_ignored')),
            'is_hunted': bool(data.get('is_hunted')),
            'max_hunt_price_per_ct': float(data.get('max_hunt_price_per_ct') or 0) if data.get('max_hunt_price_per_ct') else None,
            'max_hunt_total_cost': float(data.get('max_hunt_total_cost') or 0) if data.get('max_hunt_total_cost') else None,
            'max_premium_price_per_ct': float(data.get('max_premium_price_per_ct') or 0) if data.get('max_premium_price_per_ct') else None,
            'max_premium_total_cost': float(data.get('max_premium_total_cost') or 0) if data.get('max_premium_total_cost') else None,
            'min_hunt_weight': float(data.get('min_hunt_weight') or 0) if data.get('min_hunt_weight') else None,
            'min_premium_weight': float(data.get('min_premium_weight') or 0) if data.get('min_premium_weight') else None,
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if resp.status_code in (200, 201):
            return jsonify(resp.json())
        else:
            return jsonify({'error': 'API error', 'detail': resp.text}), resp.status_code

    except Exception as e:
        log_db_exception(e, f'api_user_gem_preference: {google_id} {gem_type_id}')
        return jsonify({'error': str(e)}), 500
