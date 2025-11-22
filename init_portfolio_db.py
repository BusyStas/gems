"""
Database initialization script for portfolio table
"""
import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), 'gems_portfolio.db')

def init_portfolio_table():
    """Create the user_portfolio table if it doesn't exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create user_portfolio table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            gem_type_name TEXT NOT NULL,
            weight_carats REAL,
            purchase_price REAL,
            current_value REAL,
            purchase_date DATE,
            notes TEXT,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES table_users(id)
        )
    """)
    
    # Create index on user_id for faster lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_portfolio_user_id ON user_portfolio(user_id)
    """)
    
    conn.commit()
    conn.close()
    print("Portfolio table initialized successfully!")

if __name__ == '__main__':
    init_portfolio_table()
