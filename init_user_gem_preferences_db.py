import sqlite3
import os
from utils.db_logger import log_db_exception

DB_PATH = os.path.join(os.getcwd(), 'gems_portfolio.db')


def init_user_gem_preferences_table():
    """Create user_gem_preferences table if not exists

    Fields:
    - id
    - user_id
    - gem_type_name
    - is_ignored
    - is_hunted
    - max_hunt_total_cost
    - max_premium_total_cost
    - min_hunt_weight
    - min_premium_weight
    - created_at
    - last_updated
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS user_gem_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                gem_type_name TEXT NOT NULL,
                is_ignored INTEGER DEFAULT 0,
                is_hunted INTEGER DEFAULT 0,
                max_hunt_total_cost REAL DEFAULT 0,
                max_premium_total_cost REAL DEFAULT 0,
                min_hunt_weight REAL DEFAULT 0,
                min_premium_weight REAL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, gem_type_name),
                FOREIGN KEY (user_id) REFERENCES table_users(id)
            )
        ''')
        conn.commit()
    except Exception as e:
        log_db_exception(e, 'init_user_gem_preferences_table')
    finally:
        try:
            conn.close()
        except Exception:
            pass


if __name__ == '__main__':
    init_user_gem_preferences_table()
    print('Initialized user_gem_preferences table')
