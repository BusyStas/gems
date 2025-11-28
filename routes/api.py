from flask import Blueprint, request, jsonify, current_app
import os
import json
import requests
from utils.api_client import load_api_key

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

    # First, try to fetch listings from the upstream Gems API using the same pattern
    items = []
    try:
        base = current_app.config.get('GEMDB_API_URL', 'https://api.preciousstone.info')
        token = load_api_key() or ''
        url = f"{base.rstrip('/')}/api/v1/listings-view/"
        params = {}
        if gem_type_id:
            params['gem_type_id'] = gem_type_id
        elif gem:
            params['gem'] = gem
        headers = {}
        if token:
            headers['X-API-Key'] = token
        r = requests.get(url, params=params, headers=headers, timeout=8)
        if r.status_code == 200:
            try:
                payload = r.json()
                # support both top-level array or {items: [...]} shapes
                if isinstance(payload, dict) and 'items' in payload and isinstance(payload['items'], list):
                    items = payload['items']
                elif isinstance(payload, list):
                    items = payload
            except Exception:
                current_app.logger.warning('Listings API returned non-JSON payload')
        else:
            current_app.logger.warning('Listings API returned %s: %s', r.status_code, r.text[:200])
    except Exception as e:
        current_app.logger.warning('Error calling upstream Listings API: %s', e)

    # Fallback: read local sample file if upstream returned nothing
    if not isinstance(items, list) or not items:
        data_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'listings_sample.json')
        if os.path.exists(data_file):
            try:
                with open(data_file, 'r', encoding='utf-8') as fh:
                    items = json.load(fh) or []
            except Exception as e:
                current_app.logger.error('Error reading listings sample file: %s', e)

    if not isinstance(items, list):
        items = []

    # Server-side safety filtering: exclude closed listings and enforce gem_type_id / gem filter
    # log incoming params for diagnosis
    current_app.logger.debug('listings_view called with gem=%s gem_type_id=%s', gem, gem_type_id)

    filtered = []
    for it in items:
        try:
            # Normalize closed flag
            if str(it.get('is_closed', False)).lower() in ('true', '1'):
                continue

            if gem_type_id:
                if str(it.get('gem_type_id') or '') != str(gem_type_id):
                    continue
            elif gem:
                # Accept both 'gem' and 'gem_type_name' keys and check listing_title as fallback
                candidate_name = str(it.get('gem') or it.get('gem_type_name') or '')
                candidate_title = str(it.get('title') or it.get('listing_title') or '')
                if gem.lower() not in candidate_name.lower() and gem.lower() not in candidate_title.lower():
                    continue

            filtered.append(it)
        except Exception:
            continue

    # sort by carat_weight descending (defensive)
    try:
        filtered.sort(key=lambda x: float(x.get('carat_weight') or 0), reverse=True)
    except Exception:
        pass

    # Log counts so we can diagnose issues with filtering
    current_app.logger.debug('listings_view: upstream_count=%s filtered_count=%s', len(items), len(filtered))

    # Normalize fields that the UI expects: carat_weight and title
    for row in filtered:
        try:
            # map 'weight' -> 'carat_weight'
            if 'carat_weight' not in row and 'weight' in row:
                row['carat_weight'] = row.get('weight')
            # map 'listing_title' -> 'title'
            if 'title' not in row and 'listing_title' in row:
                row['title'] = row.get('listing_title')
            # map 'seller' fields: seller / seller_nickname
            if 'seller' not in row and 'seller_nickname' in row:
                row['seller'] = row.get('seller_nickname')
            # map 'seller_url' if listing_url exists and seller_url is missing
            if 'seller_url' not in row and 'seller_url' not in row and 'seller' in row:
                # don't invent seller_url, just ensure key presence
                row.setdefault('seller_url', '')
        except Exception:
            continue

    return jsonify({'items': filtered})
