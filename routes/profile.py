from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
import os
from datetime import datetime
from utils.db_logger import log_db_exception

bp = Blueprint('profile', __name__, url_prefix='/profile')

DB_PATH = os.path.join(os.getcwd(), 'gems_portfolio.db')

def get_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        # Log DB connection error and re-raise so callers can handle gracefully
        log_db_exception(e, 'profile.get_db: connecting to DB')
        raise


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


# Initialize user_gem_preferences table when blueprint or app registers
@bp.record_once
def _ensure_user_gem_prefs_table(state):
    try:
        from init_user_gem_preferences_db import init_user_gem_preferences_table
        init_user_gem_preferences_table()
    except Exception:
        # Just log; do not raise during app start
        try:
            import logging
            logging.getLogger(__name__).warning('Could not initialize user_gem_preferences table')
        except Exception:
            pass


@bp.route('/')
def show_profile():
    user = load_current_user()
    if not user:
        # redirect to login
        return redirect(url_for('auth.login'))
    
    # Load all gem types for the preferences tab
    try:
        from utils.api_client import get_gems_from_api
        gems_api = get_gems_from_api() or []
        gem_types = sorted([g.get('gem_type_name') for g in gems_api if g.get('gem_type_name')])
    except Exception:
        gem_types = []
    
    return render_template('profile/profile.html', user=user, gem_types=gem_types)


@bp.route('/edit', methods=['POST'])
def edit_profile():
    user = load_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    pref = request.form.get('preferred_store')
    tier = request.form.get('minimal_investment_tier')
    
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('UPDATE table_users SET preferred_store = ?, minimal_investment_tier = ? WHERE id = ?', 
                   (pref, tier, int(user.id)))
        conn.commit()
        flash('Profile updated successfully', 'success')
    except Exception as e:
        log_db_exception(e, f'profile.edit_profile: updating user {user.id}')
        flash('Error updating profile. Please try again.', 'error')
    finally:
        try:
            conn.close()
        except Exception:
            pass
    
    return redirect(url_for('profile.show_profile'))


@bp.route('/api/v1/users/<google_id>/gem-preferences/', methods=['GET'])
def api_list_user_gem_preferences(google_id):
    """Return a list of preferences for the given user (by google_id)"""
    try:
        # translate google_id to user_id
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT id FROM table_users WHERE google_id = ?', (google_id,))
        row = cur.fetchone()
        if not row:
            return ("User not found", 404)
        uid = int(row['id'])
        cur.execute('SELECT * FROM user_gem_preferences WHERE user_id = ?', (uid,))
        res = [dict(r) for r in cur.fetchall()]
        conn.close()
        return {'user_google_id': google_id, 'preferences': res}
    except Exception as e:
        try:
            log_db_exception(e, f'api_list_user_gem_preferences: {google_id}')
        except Exception:
            pass
        return ({'error': 'internal'}, 500)


@bp.route('/api/v1/users/<google_id>/gem-preferences/<gem_type_name>', methods=['GET', 'POST'])
def api_user_gem_preference(google_id, gem_type_name):
    """GET: retrieve preference for specified gem for this user.
       POST: create or update the preference.
    """
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT id FROM table_users WHERE google_id = ?', (google_id,))
        row = cur.fetchone()
        if not row:
            return ("User not found", 404)
        uid = int(row['id'])
        # GET
        if request.method == 'GET':
            cur.execute('SELECT * FROM user_gem_preferences WHERE user_id = ? AND gem_type_name = ?', (uid, gem_type_name))
            r = cur.fetchone()
            conn.close()
            if not r:
                return ("Preference not found", 404)
            return dict(r)

        # POST: upsert
        data = request.get_json() or {}
        # normalize booleans and numbers
        def to_int_bool(val):
            return 1 if str(val).lower() in ('1', 'true', 't', 'yes', 'y') else 0
        is_ignored = to_int_bool(data.get('is_ignored'))
        is_hunted = to_int_bool(data.get('is_hunted'))
        try:
            max_hunt_total_cost = float(data.get('max_hunt_total_cost') or 0)
        except Exception:
            max_hunt_total_cost = 0.0
        try:
            max_premium_total_cost = float(data.get('max_premium_total_cost') or 0)
        except Exception:
            max_premium_total_cost = 0.0
        try:
            min_hunt_weight = float(data.get('min_hunt_weight') or 0)
        except Exception:
            min_hunt_weight = 0.0
        try:
            min_premium_weight = float(data.get('min_premium_weight') or 0)
        except Exception:
            min_premium_weight = 0.0

        # Try update first
        cur.execute('SELECT id FROM user_gem_preferences WHERE user_id = ? AND gem_type_name = ?', (uid, gem_type_name))
        exists = cur.fetchone()
        if exists:
            cur.execute('''
                UPDATE user_gem_preferences
                SET is_ignored = ?, is_hunted = ?, max_hunt_total_cost = ?, max_premium_total_cost = ?, min_hunt_weight = ?, min_premium_weight = ?, last_updated = CURRENT_TIMESTAMP
                WHERE user_id = ? AND gem_type_name = ?
            ''', (is_ignored, is_hunted, max_hunt_total_cost, max_premium_total_cost, min_hunt_weight, min_premium_weight, uid, gem_type_name))
            conn.commit()
            cur.execute('SELECT * FROM user_gem_preferences WHERE id = ?', (exists['id'],))
            r = cur.fetchone()
            conn.close()
            return dict(r)
        else:
            cur.execute('''
                INSERT INTO user_gem_preferences (user_id, gem_type_name, is_ignored, is_hunted, max_hunt_total_cost, max_premium_total_cost, min_hunt_weight, min_premium_weight)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (uid, gem_type_name, is_ignored, is_hunted, max_hunt_total_cost, max_premium_total_cost, min_hunt_weight, min_premium_weight))
            conn.commit()
            cur.execute('SELECT * FROM user_gem_preferences WHERE id = ?', (cur.lastrowid,))
            r = cur.fetchone()
            conn.close()
            return dict(r)

    except Exception as e:
        try:
            log_db_exception(e, f'api_user_gem_preference: {google_id} {gem_type_name}')
        except Exception:
            pass
        return ({'error': str(e)}, 500)
