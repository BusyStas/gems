"""
Portfolio routes - User's gem portfolio management
Uses Azure SQL via gemdb API for data storage.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import requests
import logging
from utils.api_client import load_api_key
from utils.db_logger import log_db_exception

bp = Blueprint('portfolio', __name__, url_prefix='/portfolio')
logger = logging.getLogger(__name__)


def load_current_user():
    """Load current user from Flask-Login"""
    try:
        from flask_login import current_user
        if getattr(current_user, 'is_authenticated', False):
            return current_user
    except Exception:
        pass
    return None


def get_api_base():
    """Get API base URL from config"""
    return current_app.config.get('GEMDB_API_URL', 'https://api.preciousstone.info')


def get_api_headers():
    """Get API headers with auth token"""
    token = load_api_key() or ''
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['X-API-Key'] = token
    return headers


def api_get_holdings(google_user_id):
    """Get gem holdings for a user from API"""
    try:
        url = f"{get_api_base()}/api/v2/users/{google_user_id}/gem-holdings"
        logger.info(f"api_get_holdings: calling {url}")
        r = requests.get(url, headers=get_api_headers(), timeout=10)
        logger.info(f"api_get_holdings: status={r.status_code}, response={r.text[:500] if r.text else 'empty'}")
        if r.status_code == 200:
            return r.json()
        logger.warning(f"Holdings API returned {r.status_code}: {r.text}")
        return []
    except Exception as e:
        logger.error(f"Error calling holdings API: {e}")
        return []


def api_get_holding(asset_id):
    """Get a specific gem holding from API"""
    try:
        url = f"{get_api_base()}/api/v2/gem-holdings/{asset_id}"
        r = requests.get(url, headers=get_api_headers(), timeout=10)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception as e:
        logger.error(f"Error getting holding {asset_id}: {e}")
        return None


def api_create_holding(google_user_id, data):
    """Create a new gem holding via API"""
    try:
        url = f"{get_api_base()}/api/v2/gem-holdings"
        params = {'google_user_id': google_user_id, **data}
        r = requests.post(url, headers=get_api_headers(), params=params, timeout=10)
        if r.status_code == 200:
            return r.json()
        logger.warning(f"Create holding API returned {r.status_code}: {r.text}")
        return None
    except Exception as e:
        logger.error(f"Error creating holding: {e}")
        return None


def api_update_holding(asset_id, data):
    """Update an existing gem holding via API"""
    try:
        url = f"{get_api_base()}/api/v2/gem-holdings/{asset_id}"
        r = requests.put(url, headers=get_api_headers(), params=data, timeout=10)
        if r.status_code == 200:
            return r.json()
        logger.warning(f"Update holding API returned {r.status_code}: {r.text}")
        return None
    except Exception as e:
        logger.error(f"Error updating holding {asset_id}: {e}")
        return None


def api_delete_holding(asset_id, google_user_id=None):
    """Delete a gem holding via API"""
    try:
        url = f"{get_api_base()}/api/v2/gem-holdings/{asset_id}"
        params = {}
        if google_user_id:
            params['google_user_id'] = google_user_id
        r = requests.delete(url, headers=get_api_headers(), params=params, timeout=10)
        return r.status_code == 200
    except Exception as e:
        logger.error(f"Error deleting holding {asset_id}: {e}")
        return False


def api_get_gem_types():
    """Get all gem types for dropdown selection"""
    try:
        url = f"{get_api_base()}/api/v2/gems"
        r = requests.get(url, headers=get_api_headers(), params={'limit': 500}, timeout=10)
        if r.status_code == 200:
            return r.json()
        return []
    except Exception as e:
        logger.error(f"Error getting gem types: {e}")
        return []


@bp.route('/')
def index():
    """Portfolio main page"""
    user = load_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    try:
        logger.info(f"Portfolio index: user.google_id = {user.google_id}")
        holdings = api_get_holdings(user.google_id)
        logger.info(f"Portfolio index: got {len(holdings)} holdings: {holdings}")
        return render_template('portfolio/index.html', holdings=holdings)
    except Exception as e:
        log_db_exception(e, 'portfolio.index: fetching holdings')
        return render_template('portfolio/index.html', holdings=[])


@bp.route('/add', methods=['GET', 'POST'])
def add_gem():
    """Add a gem to portfolio"""
    user = load_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        try:
            data = {
                'gem_type_id': int(request.form.get('gem_type_id')),
                'parcel_size': int(request.form.get('parcel_size') or 1),
                'weight_carats': float(request.form.get('weight_carats')) if request.form.get('weight_carats') else None,
                'purchase_date': request.form.get('purchase_date') or None,
                'purchase_cost': float(request.form.get('purchase_cost')) if request.form.get('purchase_cost') else None,
                'shipping_cost': float(request.form.get('shipping_cost')) if request.form.get('shipping_cost') else None,
                'notes': request.form.get('notes') or None,
            }
            # Remove None values
            data = {k: v for k, v in data.items() if v is not None}

            result = api_create_holding(user.google_id, data)
            if result:
                flash('Gem added to your portfolio!', 'success')
                return redirect(url_for('portfolio.index'))
            else:
                flash('Error adding gem to portfolio', 'error')

        except Exception as e:
            log_db_exception(e, 'portfolio.add_gem: adding gem')
            flash('Error adding gem to portfolio', 'error')

    # GET request - show form with gem types
    gem_types = api_get_gem_types()
    return render_template('portfolio/add.html', gem_types=gem_types)

@bp.route('/edit/<int:asset_id>', methods=['GET', 'POST'])
def edit_gem(asset_id):
    """Edit a gem in portfolio"""
    user = load_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        try:
            data = {
                'gem_type_id': int(request.form.get('gem_type_id')) if request.form.get('gem_type_id') else None,
                'parcel_size': int(request.form.get('parcel_size')) if request.form.get('parcel_size') else None,
                'weight_carats': float(request.form.get('weight_carats')) if request.form.get('weight_carats') else None,
                'purchase_date': request.form.get('purchase_date') or None,
                'shipping_date': request.form.get('shipping_date') or None,
                'purchase_cost': float(request.form.get('purchase_cost')) if request.form.get('purchase_cost') else None,
                'shipping_cost': float(request.form.get('shipping_cost')) if request.form.get('shipping_cost') else None,
                'notes': request.form.get('notes') or None,
            }
            # Remove None values
            data = {k: v for k, v in data.items() if v is not None}

            result = api_update_holding(asset_id, data)
            if result:
                flash('Portfolio item updated!', 'success')
                return redirect(url_for('portfolio.index'))
            else:
                flash('Error updating portfolio item', 'error')

        except Exception as e:
            log_db_exception(e, 'portfolio.edit_gem: updating gem')
            flash('Error updating portfolio item', 'error')

    # GET request - show form with current data
    holding = api_get_holding(asset_id)
    if not holding:
        flash('Portfolio item not found', 'error')
        return redirect(url_for('portfolio.index'))

    gem_types = api_get_gem_types()
    return render_template('portfolio/edit.html', item=holding, gem_types=gem_types)


@bp.route('/delete/<int:asset_id>', methods=['POST'])
def delete_gem(asset_id):
    """Delete a gem from portfolio"""
    user = load_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    success = api_delete_holding(asset_id, user.google_id)
    if success:
        flash('Gem removed from portfolio', 'success')
    else:
        flash('Error removing gem from portfolio', 'error')

    return redirect(url_for('portfolio.index'))


@bp.route('/stats')
def portfolio_stats():
    """Portfolio statistics and analytics"""
    user = load_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    holdings = api_get_holdings(user.google_id)

    # Calculate stats from holdings
    total_items = len(holdings)
    total_invested = sum(h.get('PurchaseCost', 0) or 0 for h in holdings)
    total_shipping = sum(h.get('ShippingCost', 0) or 0 for h in holdings)
    total_carats = sum(h.get('WeightCarats', 0) or 0 for h in holdings)

    stats = {
        'total_items': total_items,
        'total_invested': total_invested,
        'total_shipping': total_shipping,
        'total_cost': total_invested + total_shipping,
        'total_carats': total_carats
    }

    # Group holdings by gem type
    gem_totals = {}
    for h in holdings:
        gem_name = h.get('GemTypeName', 'Unknown')
        cost = (h.get('PurchaseCost', 0) or 0) + (h.get('ShippingCost', 0) or 0)
        gem_totals[gem_name] = gem_totals.get(gem_name, 0) + cost

    # Sort by value descending
    top_gems = sorted(gem_totals.items(), key=lambda x: x[1], reverse=True)[:10]

    return render_template('portfolio/stats.html', stats=stats, top_gems=top_gems, holdings=holdings)
