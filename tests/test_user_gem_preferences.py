import os
import sqlite3
import json
import pytest

from app import app

# Ensure database path is the same as the app uses
DB_PATH = os.path.join(os.getcwd(), 'gems_portfolio.db')

@pytest.fixture(autouse=True)
def setup_db(monkeypatch):
    # Ensure any existing test DB is removed to start fresh for each test
    try:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
    except Exception:
        pass
    # Initialize users table and preferences table
    from routes import auth as auth_bp
    auth_bp.init_db()
    from init_user_gem_preferences_db import init_user_gem_preferences_table
    init_user_gem_preferences_table()
    yield


def create_user(google_id, email='test@example.com', name='Test User'):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('INSERT INTO table_users (google_id, email, name, created_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)', (google_id, email, name))
    conn.commit()
    last = cur.lastrowid
    conn.close()
    return last


def test_create_and_read_user_gem_preference():
    client = app.test_client()
    # Create user
    gid = 'test-google-123'
    uid = create_user(gid)

    # POST a preference
    payload = {
        'is_ignored': True,
        'is_hunted': True,
        'max_hunt_total_cost': 200.0,
        'max_premium_total_cost': 500.0,
        'min_hunt_weight': 1.2,
        'min_premium_weight': 2.5
    }

    r = client.post(f'/profile/api/v1/users/{gid}/gem-preferences/Emerald', data=json.dumps(payload), content_type='application/json')
    assert r.status_code == 200
    body = r.get_json()
    assert body['user_id'] == uid
    assert body['gem_type_name'] == 'Emerald'
    assert body['is_hunted'] == 1
    assert float(body['max_hunt_total_cost']) == 200.0

    # GET to retrieve
    r2 = client.get(f'/profile/api/v1/users/{gid}/gem-preferences/Emerald')
    assert r2.status_code == 200
    body2 = r2.get_json()
    assert body2['gem_type_name'] == 'Emerald'
    assert body2['is_ignored'] == 1

    # Update using POST again
    update_payload = {'max_hunt_total_cost': 300.0}
    r3 = client.post(f'/profile/api/v1/users/{gid}/gem-preferences/Emerald', data=json.dumps(update_payload), content_type='application/json')
    assert r3.status_code == 200
    body3 = r3.get_json()
    assert float(body3['max_hunt_total_cost']) == 300.0

    # List all preferences
    r4 = client.get(f'/profile/api/v1/users/{gid}/gem-preferences/')
    assert r4.status_code == 200
    body4 = r4.get_json()
    assert 'preferences' in body4
    assert len(body4['preferences']) >= 1
