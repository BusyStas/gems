from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
from datetime import datetime

bp = Blueprint('profile', __name__, url_prefix='/profile')

DB_PATH = os.path.join(os.getcwd(), 'gems_portfolio.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def load_current_user():
    # Prefer Flask-Login current_user if available
    try:
        from flask_login import current_user
        if getattr(current_user, 'is_authenticated', False):
            return current_user
    except Exception:
        pass
    # Fallback to demo session user
    uid = session.get('demo_user_id')
    if uid:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM table_users WHERE id = ?', (int(uid),))
        row = cur.fetchone()
        conn.close()
        if row:
            from routes.auth import User
            return User(row['id'], row['google_id'], row['email'], row['name'], row['profile_pic'], row['preferred_store'], row['minimal_investment_tier'], row['created_at'])
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
    conn = get_db()
    cur = conn.cursor()
    cur.execute('UPDATE table_users SET preferred_store = ?, minimal_investment_tier = ? WHERE id = ?', (pref, tier, int(user.id)))
    conn.commit()
    conn.close()
    flash('Profile updated', 'success')
    return redirect(url_for('profile.show_profile'))
