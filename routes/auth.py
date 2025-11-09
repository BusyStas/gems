from flask import Blueprint, render_template, redirect, url_for, request, current_app, flash, session
import os
import sqlite3
from datetime import datetime
import secrets

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Try to import optional libraries
try:
    from authlib.integrations.flask_client import OAuth
    OAUTH_AVAILABLE = True
except Exception:
    OAUTH_AVAILABLE = False

try:
    from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
    FLASK_LOGIN_AVAILABLE = True
except Exception:
    FLASK_LOGIN_AVAILABLE = False

DB_PATH = os.path.join(os.getcwd(), 'gems_portfolio.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS table_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            google_id TEXT UNIQUE,
            email TEXT,
            name TEXT,
            profile_pic TEXT,
            preferred_store TEXT,
            minimal_investment_tier TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()


class User(UserMixin if FLASK_LOGIN_AVAILABLE else object):
    def __init__(self, id, google_id, email, name, profile_pic, preferred_store=None, minimal_investment_tier=None, created_at=None):
        self.id = str(id)
        self.google_id = google_id
        self.email = email
        self.name = name
        self.profile_pic = profile_pic
        self.preferred_store = preferred_store
        self.minimal_investment_tier = minimal_investment_tier
        self.created_at = created_at or datetime.utcnow().isoformat()


@bp.record_once
def on_register(state):
    # Ensure database exists when blueprint is registered
    try:
        init_db()
    except Exception:
        current_app.logger.warning('Could not initialize auth DB')


def load_user_by_id(uid):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM table_users WHERE id = ?', (int(uid),))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        return User(row['id'], row['google_id'], row['email'], row['name'], row['profile_pic'], row['preferred_store'], row['minimal_investment_tier'], row['created_at'])
    except Exception:
        return None


# If Flask-Login is available, register user_loader
if FLASK_LOGIN_AVAILABLE:
    try:
        from flask import current_app
        lm = current_app.login_manager if hasattr(current_app, 'login_manager') else None
    except Exception:
        lm = None

    # We cannot call login_manager.user_loader at import time reliably because app may initialize later.
    # Instead, provide a helper the app can use to register the loader if needed.

def register_login_loader(login_manager):
    if not FLASK_LOGIN_AVAILABLE or not login_manager:
        return

    @login_manager.user_loader
    def _user_loader(user_id):
        return load_user_by_id(user_id)


@bp.route('/login')
def login():
    # If OAuth available and credentials configured, start OAuth flow
    oauth_configured = OAUTH_AVAILABLE and bool(os.environ.get('GOOGLE_CLIENT_ID')) and bool(os.environ.get('GOOGLE_CLIENT_SECRET'))
    # If configured, attempt to start OAuth flow, but catch and surface errors to the user
    if oauth_configured:
        try:
            oauth = OAuth(current_app)
            # Register google with explicit server metadata so jwks_uri is available for ID token parsing
            oauth.register(
                'google',
                client_id=os.environ.get('GOOGLE_CLIENT_ID'),
                client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
                access_token_url='https://oauth2.googleapis.com/token',
                authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
                api_base_url='https://www.googleapis.com/oauth2/v1/',
                client_kwargs={'scope': 'openid email profile'},
                server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
            )
            # Allow overriding redirect URI via env var (helps Cloud Run / proxies)
            redirect_uri = os.environ.get('OAUTH_REDIRECT_URI') or url_for('auth.callback', _external=True)
            # generate a nonce and store in session so we can validate ID token in the callback
            try:
                nonce = secrets.token_urlsafe(16)
                session['oidc_nonce'] = nonce
            except Exception:
                nonce = None
            # pass nonce to the provider so it is echoed into the id_token
            if nonce:
                return oauth.google.authorize_redirect(redirect_uri, nonce=nonce)
            return oauth.google.authorize_redirect(redirect_uri)
        except Exception as e:
            # surface error to the user and render diagnostics
            current_app.logger.exception('OAuth authorize_redirect failed')
            flash('Failed to start OAuth sign-in: {}'.format(str(e)), 'danger')
            # fall through to render login page with diagnostics

    # Fallback: show a simple login page; do not offer demo login in production
    # Provide diagnostics to help the developer configure OAuth
    diagnostics = {
        'authlib_installed': OAUTH_AVAILABLE,
        'google_client_id_present': bool(os.environ.get('GOOGLE_CLIENT_ID')),
        'google_client_secret_present': bool(os.environ.get('GOOGLE_CLIENT_SECRET')),
        'redirect_uri': os.environ.get('OAUTH_REDIRECT_URI') or url_for('auth.callback', _external=True),
    }
    return render_template('auth/login.html', oauth_available=OAUTH_AVAILABLE, diagnostics=diagnostics)


@bp.route('/callback')
def callback():
    if not OAUTH_AVAILABLE or not os.environ.get('GOOGLE_CLIENT_ID') or not os.environ.get('GOOGLE_CLIENT_SECRET'):
        flash('OAuth is not configured correctly on this server.', 'warning')
        return redirect(url_for('auth.login'))

    oauth = OAuth(current_app)
    # Register the google client with explicit endpoints so token endpoint is available
    try:
        oauth.register(
            'google',
            client_id=os.environ.get('GOOGLE_CLIENT_ID'),
            client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
            access_token_url='https://oauth2.googleapis.com/token',
            authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
            api_base_url='https://www.googleapis.com/oauth2/v1/',
            client_kwargs={'scope': 'openid email profile'},
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
        )
    except Exception:
        current_app.logger.exception('Failed to register Google OAuth client on callback')
        flash('Internal error during OAuth processing', 'danger')
        return redirect(url_for('auth.login'))

    try:
        token = oauth.google.authorize_access_token()
    except Exception as e:
        current_app.logger.exception('Error fetching access token')
        flash('Failed to obtain access token: {}'.format(str(e)), 'danger')
        return redirect(url_for('auth.login'))

    # Validate/parse id_token using nonce stored in session. If nonce is missing for any reason,
    # fall back to userinfo endpoint. Authlib's parse_id_token requires the original nonce.
    userinfo = None
    nonce = session.pop('oidc_nonce', None)
    try:
        if nonce:
            userinfo = oauth.google.parse_id_token(token, nonce=nonce)
        else:
            # attempt parse without nonce (may raise TypeError) and let except handle fallback
            try:
                userinfo = oauth.google.parse_id_token(token)
            except TypeError:
                userinfo = None
    except TypeError:
        # missing nonce or parse error - fallback
        current_app.logger.warning('parse_id_token failed due to missing nonce; falling back to userinfo endpoint')
        userinfo = None
    except Exception:
        current_app.logger.exception('Unexpected error parsing id_token')
        userinfo = None

    if not userinfo:
        try:
            resp = oauth.google.get('userinfo')
            userinfo = resp.json()
        except Exception:
            current_app.logger.exception('Failed to fetch userinfo fallback')
            flash('Could not retrieve user information from provider.', 'danger')
            return redirect(url_for('auth.login'))
    # userinfo should contain 'sub' as google id
    gid = userinfo.get('sub')
    email = userinfo.get('email')
    name = userinfo.get('name')
    picture = userinfo.get('picture')

    # persist to DB
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT id FROM table_users WHERE google_id = ?', (gid,))
    row = cur.fetchone()
    if row:
        user_id = row['id']
    else:
        cur.execute('INSERT INTO table_users (google_id, email, name, profile_pic, created_at) VALUES (?, ?, ?, ?, ?)', (gid, email, name, picture, datetime.utcnow().isoformat()))
        conn.commit()
        user_id = cur.lastrowid
    conn.close()

    user = load_user_by_id(user_id)
    if FLASK_LOGIN_AVAILABLE:
        from flask_login import login_user
        login_user(user)
    return redirect(url_for('profile.show_profile'))


# Demo login removed: no demo endpoints are provided in production.


@bp.route('/logout')
def logout():
    if FLASK_LOGIN_AVAILABLE:
        from flask_login import logout_user
        logout_user()
    # otherwise nothing to clear; redirect to home
    return redirect(url_for('main.index'))


@bp.route('/inspect', methods=['GET', 'POST'])
def inspect_callback():
    """Debug endpoint to inspect incoming OAuth callbacks. Enabled only when app.debug is True."""
    try:
        from flask import jsonify
        if not current_app.debug:
            return ('Not available', 404)
        info = {
            'method': request.method,
            'args': request.args.to_dict(flat=True),
            'form': request.form.to_dict(flat=True),
            'headers': {k: v for k, v in request.headers.items() if k.lower() in ['host', 'user-agent', 'referer', 'origin']}
        }
        current_app.logger.info('Inspect callback hit: %s', info)
        return jsonify(info)
    except Exception as e:
        current_app.logger.exception('Inspect callback error')
        return ('error', 500)


@bp.route('/login/callback')
def legacy_login_callback():
    """Compatibility route: some OAuth clients (or embedded hosts) use /login/callback.
    Redirect to the canonical /auth/callback preserving the query string so the app can handle it.
    """
    qs = request.query_string.decode('utf-8') if request.query_string else ''
    target = url_for('auth.callback', _external=True)
    if qs:
        target = f"{target}?{qs}"
    current_app.logger.info('Redirecting legacy /login/callback -> %s', target)
    return redirect(target)
