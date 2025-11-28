"""
Main routes for Gems Hub
"""

from flask import Blueprint, render_template
from utils.api_client import get_api_health, get_api_key_info, load_api_key
from datetime import datetime

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Home page"""
    page_data = {
        'title': 'Welcome to Gems Hub',
        'description': 'Your comprehensive resource for everything about gems, gemstones, investments, and jewelry',
        'hero_title': 'Discover the World of Gems',
        'hero_text': 'Explore precious and semi-precious stones, learn about gem investments, and find the perfect jewelry pieces.'
    }
    return render_template('home.html', **page_data)


@bp.route('/health')
def health():
    """Site health page (not linked from any menu). Shows API health and API key presence/length.
    This is intentionally not linked in the menu per requirements.
    """
    try:
        api_health = get_api_health()
    except Exception:
        api_health = None

    try:
        token, key_source = get_api_key_info()
    except Exception:
        token = None
        key_source = None

    key_ok = False
    key_len = 0
    if token and isinstance(token, str):
        key_len = len(token)
        if key_len > 100:
            key_ok = True

    page_data = {
        'title': 'Health Check',
        'description': 'Internal health check for the site and external API',
        'api_health': api_health,
    'api_key_present_long_enough': key_ok,
    'api_key_len': key_len,
    'api_key_source': key_source,
        'checked_at': datetime.utcnow().isoformat() + 'Z'
    }
    return render_template('health.html', **page_data)


@bp.route('/privacy-policy')
@bp.route('/privacy')
def privacy():
    """Privacy Policy page"""
    page_data = {
        'title': 'Privacy Policy',
        'description': 'Our privacy policy and data handling practices'
    }
    return render_template('privacy-policy.html', **page_data)


@bp.route('/terms-of-service')
@bp.route('/terms')
def terms():
    """Terms of Service page"""
    page_data = {
        'title': 'Terms of Service',
        'description': 'Terms and conditions for using our website'
    }
    return render_template('terms-of-service.html', **page_data)
