from flask import Blueprint, render_template, redirect, url_for, request, current_app, flash
import os
import sqlite3
from datetime import datetime

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
    if OAUTH_AVAILABLE and os.environ.get('GOOGLE_CLIENT_ID') and os.environ.get('GOOGLE_CLIENT_SECRET'):
        oauth = OAuth(current_app)
        oauth.register('google', client_id=os.environ.get('GOOGLE_CLIENT_ID'), client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'), access_token_url='https://oauth2.googleapis.com/token', authorize_url='https://accounts.google.com/o/oauth2/v2/auth', api_base_url='https://www.googleapis.com/oauth2/v1/', client_kwargs={'scope': 'openid email profile'})
        redirect_uri = url_for('auth.callback', _external=True)
        return oauth.google.authorize_redirect(redirect_uri)

    # Fallback: show a simple login page with a demo-login button for local testing
    return render_template('auth/login.html', oauth_available=OAUTH_AVAILABLE)


@bp.route('/callback')
def callback():
    if not OAUTH_AVAILABLE:
        flash('OAuth not configured on server', 'warning')
        return redirect(url_for('main.index'))
    oauth = OAuth(current_app)
    oauth.register('google')
    token = oauth.google.authorize_access_token()
    userinfo = oauth.google.parse_id_token(token)
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


@bp.route('/demo-login')
def demo_login():
    """Create or reuse a local demo user for development when OAuth isn't configured."""
    demo_google_id = 'demo-google-1'
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT id FROM table_users WHERE google_id = ?', (demo_google_id,))
    row = cur.fetchone()
    if row:
        user_id = row['id']
    else:
        cur.execute('INSERT INTO table_users (google_id, email, name, profile_pic, created_at) VALUES (?, ?, ?, ?, ?)', (demo_google_id, 'demo@example.org', 'Demo User', '', datetime.utcnow().isoformat()))
        conn.commit()
        user_id = cur.lastrowid
    conn.close()

    user = load_user_by_id(user_id)
    if FLASK_LOGIN_AVAILABLE:
        from flask_login import login_user
        login_user(user)
        return redirect(url_for('profile.show_profile'))
    else:
        # Set a lightweight session flag if flask-login is not available
        from flask import session
        session['demo_user_id'] = user.id
        return redirect(url_for('profile.show_profile'))


@bp.route('/logout')
def logout():
    if FLASK_LOGIN_AVAILABLE:
        from flask_login import logout_user
        logout_user()
    else:
        from flask import session
        session.pop('demo_user_id', None)
    return redirect(url_for('main.index'))
