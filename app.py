"""
Gems Hub - Main Flask Application
A comprehensive web resource for gem information, investments, and jewelry
"""

from flask import Flask, render_template, url_for
from config import Config
import os
# Load .env for local development (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # python-dotenv not installed; environment variables should be set externally
    # Try a very small fallback loader so .env works even without python-dotenv
    env_path = os.path.join(os.getcwd(), '.env')
    try:
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' not in line:
                        continue
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    # Only set when not already present in environment
                    if key and not os.environ.get(key):
                        os.environ[key] = val
    except Exception:
        # if fallback fails, continue without raising — env must be set externally
        pass

app = Flask(__name__)
app.config.from_object(Config)

# Legacy compatibility route: some OAuth clients redirect to /login/callback (root).
from flask import request, redirect


@app.route('/login/callback')
def legacy_login_callback_root():
    qs = request.query_string.decode('utf-8') if request.query_string else ''
    target = url_for('auth.callback', _external=True)
    if qs:
        target = f"{target}?{qs}"
    app.logger.info('Redirecting legacy root /login/callback -> %s', target)
    return redirect(target)

# Import routes
from routes import main, gems, investments, jewelry, stores, labs
# auth and profile blueprints are optional - import if present
try:
    from routes import auth
    has_auth_blueprint = True
except Exception:
    auth = None
    has_auth_blueprint = False

try:
    from routes import profile
    has_profile_blueprint = True
except Exception:
    profile = None
    has_profile_blueprint = False

# Register blueprints
app.register_blueprint(main.bp)
app.register_blueprint(gems.bp)
app.register_blueprint(investments.bp)
app.register_blueprint(jewelry.bp)
app.register_blueprint(stores.bp)
app.register_blueprint(labs.bp)
if has_auth_blueprint:
    try:
        app.register_blueprint(auth.bp)
    except Exception:
        # register attempt failed; continue without auth
        pass

if has_profile_blueprint:
    try:
        app.register_blueprint(profile.bp)
    except Exception:
        pass

# Initialize Flask-Login if available
try:
    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    app.login_manager = login_manager
except Exception:
    # Flask-Login not installed; auth routes will provide fallbacks
    login_manager = None

# If auth module provides helper to register user_loader, do it now
try:
    if login_manager and auth and hasattr(auth, 'register_login_loader'):
        auth.register_login_loader(login_manager)
except Exception:
    pass

@app.context_processor
def inject_globals():
    """Inject global variables and functions into all templates"""
    from datetime import datetime
    # Determine simple logged-in state for templates.
    # Prefer Flask-Login's current_user when available; otherwise fall back to session keys.
    try:
        from flask import session
        try:
            from flask_login import current_user as _current_user
            logged_in = getattr(_current_user, 'is_authenticated', False)
            current_user_obj = _current_user if logged_in else None
        except Exception:
            # Flask-Login not available; check session for known user keys
            logged_in = bool(session.get('user_id') or session.get('google_id'))
            current_user_obj = None
    except Exception:
        logged_in = False
        current_user_obj = None

    return dict(
        current_year=lambda: datetime.now().year,
        user_logged_in=logged_in,
        current_user=current_user_obj,
    )

@app.context_processor
def inject_menu():
    """Inject menu structure into all templates"""
    menu_items = [
        {
            'title': 'Home',
            'icon': 'home',
            'url': url_for('main.index')
        },
        {
            'title': 'Type of Gems',
            'icon': 'gems',
            'url': url_for('gems.index'),
            'submenu': [
                {'title': 'By hardness', 'url': url_for('gems.by_hardness')},
                {'title': 'By rarity', 'url': url_for('gems.by_rarity')},
                {'title': 'By availability', 'url': url_for('gems.by_availability')},
                {'title': 'By size', 'url': url_for('gems.by_size')},
                {'title': 'By investment appropriateness', 'url': url_for('gems.by_investment')},
                {'title': 'By price', 'url': url_for('gems.by_price')},
                {'title': 'By colors', 'url': url_for('gems.by_colors')},
            ]
        },
        {
            'title': 'Stores and Auctions',
            'icon': 'stores',
            'url': url_for('stores.index'),
            'submenu': [
                {'title': 'Gem Rock Auctions', 'url': url_for('stores.gem_rock_auctions')},
                        {'title': 'Best In Gems', 'url': url_for('stores.best_in_gems')},
            ]
        },
        {
            'title': 'Investments',
            'icon': 'investments',
            'url': url_for('investments.index'),
            'submenu': [
                {'title': 'Market Trends', 'url': url_for('investments.market_trends')},
                {'title': 'Value Assessment', 'url': url_for('investments.value_assessment')},
                        {'title': 'Investment Rankings', 'url': url_for('investments.investment_rankings')},
            ]
        },
        {
            'title': 'Jewelry',
            'icon': 'jewelry',
            'url': url_for('jewelry.index'),
            'submenu': [
                {'title': 'Customized Jewelry', 'url': url_for('jewelry.customized')},
                {'title': 'Shopes', 'url': url_for('jewelry.shops')},
            ]
        }
        ,
        {
            'title': 'Certification Labs',
            'icon': 'labs',
            'url': url_for('labs.index'),
            'submenu': [
                {'title': 'GIA', 'url': url_for('labs.gia')},
                {'title': 'AGS', 'url': url_for('labs.ags')},
                {'title': 'IGI', 'url': url_for('labs.igi')},
                {'title': 'EGL', 'url': url_for('labs.egl')},
            ]
        }
    ]
    return dict(menu_items=menu_items)

# -- Accessibility helpers: contrast helpers for templates --
def _hex_to_rgb(hexstr):
    h = (hexstr or '').lstrip('#')
    if len(h) == 3:
        h = ''.join([c*2 for c in h])
    try:
        r = int(h[0:2], 16) / 255.0
        g = int(h[2:4], 16) / 255.0
        b = int(h[4:6], 16) / 255.0
        return (r, g, b)
    except Exception:
        return (1.0, 1.0, 1.0)

def _linearize(c):
    if c <= 0.03928:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4

def _relative_luminance(hexstr):
    r, g, b = _hex_to_rgb(hexstr)
    return 0.2126 * _linearize(r) + 0.7152 * _linearize(g) + 0.0722 * _linearize(b)

def contrast_ratio(hex1, hex2='#ffffff'):
    l1 = _relative_luminance(hex1)
    l2 = _relative_luminance(hex2)
    L1, L2 = max(l1, l2), min(l1, l2)
    try:
        return (L1 + 0.05) / (L2 + 0.05)
    except Exception:
        return 1.0

def contrast_fg(hexbg, light='#ffffff', dark='#000000'):
    # return the foreground color (light or dark) that gives better contrast against hexbg
    try:
        cr_light = contrast_ratio(hexbg, light)
        cr_dark = contrast_ratio(hexbg, dark)
        return light if cr_light >= cr_dark else dark
    except Exception:
        return '#000000'

def contrast_label(hexbg, threshold=4.5, light='#ffffff', dark='#000000'):
    # Determine whether best contrast meets WCAG threshold (4.5 for normal text)
    try:
        best = contrast_fg(hexbg, light, dark)
        cr = contrast_ratio(hexbg, best)
        return 'sufficient' if cr >= threshold else 'low'
    except Exception:
        return 'unknown'

# register filters
app.jinja_env.filters['contrast_fg'] = contrast_fg
app.jinja_env.filters['contrast_label'] = contrast_label

@app.route('/robots.txt')
def robots_txt():
    """Serve robots.txt"""
    return app.send_static_file('robots.txt')

@app.route('/sitemap.xml')
def sitemap_xml():
    """Serve sitemap.xml"""
    return app.send_static_file('sitemap.xml')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
