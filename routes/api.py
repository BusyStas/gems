from flask import Blueprint, request, jsonify, current_app
import os
import json
import re
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
    google_user_id = request.args.get('google_user_id')

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
        # Forward google_user_id to upstream API to apply user preferences filtering
        if google_user_id:
            params['google_user_id'] = google_user_id
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
            # map 'id' -> 'listing_id'
            if 'listing_id' not in row and 'id' in row:
                row['listing_id'] = row.get('id')
            # map 'weight' -> 'carat_weight'
            if 'carat_weight' not in row and 'weight' in row:
                row['carat_weight'] = row.get('weight')
            # map 'listing_title' -> 'title'
            if 'title' not in row and 'listing_title' in row:
                row['title'] = row.get('listing_title')
            # map 'listing_url' -> 'title_url'
            if 'title_url' not in row and 'listing_url' in row:
                row['title_url'] = row.get('listing_url')
            # map 'seller' fields: seller / seller_nickname
            if 'seller' not in row and 'seller_nickname' in row:
                row['seller'] = row.get('seller_nickname')
            # map 'seller_profile' or 'seller_url' to seller_url
            if 'seller_url' not in row and 'seller_profile' in row:
                row['seller_url'] = row.get('seller_profile')
            # map 'seller_url' if listing_url exists and seller_url is missing
            if 'seller_url' not in row and 'seller' in row:
                # don't invent seller_url, just ensure key presence
                row.setdefault('seller_url', '')
            # Synthesize gemrock URLs for title and seller if missing
            try:
                def _slugify(value: str) -> str:
                    if not value:
                        return ''
                    v = str(value).strip().lower()
                    # remove punctuation except spaces and hyphens
                    v = re.sub(r"[^\w\s-]", '', v, flags=re.U)
                    # normalize spaces/hyphens
                    v = v.replace('_', ' ')
                    v = re.sub(r"[\s-]+", '-', v.strip())
                    return v

                # Ensure listing_id exists from 'id' or 'listing_id'
                lid = row.get('listing_id') or row.get('id')
                if lid:
                    title = row.get('title') or row.get('listing_title') or ''
                    if title:
                        slug = _slugify(title)
                        # Always prefer gemrock product URL pattern per requirements
                        row['title_url'] = f"https://www.gemrockauctions.com/products/{slug}-{lid}"

                seller = row.get('seller') or row.get('seller_nickname') or ''
                if seller:
                    seller_slug = _slugify(seller)
                    if seller_slug:
                        # Always prefer gemrock store URL pattern per requirements
                        row['seller_url'] = f"https://www.gemrockauctions.com/stores/{seller_slug}"

                # Price formatting: ensure price includes '$' prefix for numeric values
                price_val = row.get('price')
                if price_val is not None:
                    try:
                        # if numeric, format
                        if isinstance(price_val, (int, float)):
                            row['price'] = f"${price_val:,.2f}"
                        elif isinstance(price_val, str) and re.match(r"^\s*\d+(?:[.,]\d+)?\s*$", price_val):
                            pv = float(price_val.replace(',', ''))
                            row['price'] = f"${pv:,.2f}"
                        else:
                            # leave price as-is (could contain '$' already)
                            pass
                    except Exception:
                        pass
            except Exception:
                # move on; don't break the whole loop
                pass
        except Exception:
            continue

    # Debug sample item
    try:
        if filtered:
            current_app.logger.debug('listings_view sample item: %s', json.dumps(filtered[0]))
    except Exception:
        pass

    return jsonify({'items': filtered})
