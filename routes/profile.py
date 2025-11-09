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


@bp.route('/')
def show_profile():
    user = load_current_user()
    if not user:
        # redirect to login
        return redirect(url_for('auth.login'))
    return render_template('profile/profile.html', user=user)


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
