"""
Portfolio routes - User's gem portfolio management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
import os
from datetime import datetime
from utils.db_logger import log_db_exception

bp = Blueprint('portfolio', __name__, url_prefix='/portfolio')

DB_PATH = os.path.join(os.getcwd(), 'gems_portfolio.db')

def get_db():
    """Get database connection"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        log_db_exception(e, 'portfolio.get_db: connecting to DB')
        raise

def load_current_user():
    """Load current user from Flask-Login"""
    try:
        from flask_login import current_user
        if getattr(current_user, 'is_authenticated', False):
            return current_user
    except Exception:
        pass
    return None

@bp.route('/')
def index():
    """Portfolio main page"""
    user = load_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get user's portfolio items
        cursor.execute("""
            SELECT * FROM user_portfolio 
            WHERE user_id = ?
            ORDER BY date_added DESC
        """, (user.id,))
        
        portfolio_items = cursor.fetchall()
        conn.close()
        
        return render_template('portfolio/index.html', portfolio_items=portfolio_items)
    except Exception as e:
        log_db_exception(e, 'portfolio.index: fetching portfolio items')
        return render_template('portfolio/index.html', portfolio_items=[])
    finally:
        try:
            conn.close()
        except:
            pass

@bp.route('/add', methods=['GET', 'POST'])
def add_gem():
    """Add a gem to portfolio"""
    user = load_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        try:
            gem_type = request.form.get('gem_type')
            weight = request.form.get('weight')
            purchase_price = request.form.get('purchase_price')
            purchase_date = request.form.get('purchase_date')
            notes = request.form.get('notes')
            
            conn = get_db()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_portfolio 
                (user_id, gem_type_name, weight_carats, purchase_price, purchase_date, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user.id, gem_type, weight, purchase_price, purchase_date, notes))
            
            conn.commit()
            conn.close()
            
            flash('Gem added to your portfolio!', 'success')
            return redirect(url_for('portfolio.index'))
            
        except Exception as e:
            log_db_exception(e, 'portfolio.add_gem: adding gem')
            flash('Error adding gem to portfolio', 'error')
            return redirect(url_for('portfolio.add_gem'))
        finally:
            try:
                conn.close()
            except:
                pass
    
    # GET request - show form
    return render_template('portfolio/add.html')

@bp.route('/edit/<int:portfolio_id>', methods=['GET', 'POST'])
def edit_gem(portfolio_id):
    """Edit a gem in portfolio"""
    user = load_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        try:
            weight = request.form.get('weight')
            purchase_price = request.form.get('purchase_price')
            current_value = request.form.get('current_value')
            notes = request.form.get('notes')
            
            conn = get_db()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE user_portfolio 
                SET weight_carats = ?, purchase_price = ?, current_value = ?, notes = ?
                WHERE id = ? AND user_id = ?
            """, (weight, purchase_price, current_value, notes, portfolio_id, user.id))
            
            conn.commit()
            conn.close()
            
            flash('Portfolio item updated!', 'success')
            return redirect(url_for('portfolio.index'))
            
        except Exception as e:
            log_db_exception(e, 'portfolio.edit_gem: updating gem')
            flash('Error updating portfolio item', 'error')
        finally:
            try:
                conn.close()
            except:
                pass
    
    # GET request - show form with current data
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM user_portfolio 
            WHERE id = ? AND user_id = ?
        """, (portfolio_id, user.id))
        
        portfolio_item = cursor.fetchone()
        conn.close()
        
        if not portfolio_item:
            flash('Portfolio item not found', 'error')
            return redirect(url_for('portfolio.index'))
        
        return render_template('portfolio/edit.html', item=portfolio_item)
        
    except Exception as e:
        log_db_exception(e, 'portfolio.edit_gem: fetching gem')
        flash('Error loading portfolio item', 'error')
        return redirect(url_for('portfolio.index'))
    finally:
        try:
            conn.close()
        except:
            pass

@bp.route('/delete/<int:portfolio_id>', methods=['POST'])
def delete_gem(portfolio_id):
    """Delete a gem from portfolio"""
    user = load_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM user_portfolio 
            WHERE id = ? AND user_id = ?
        """, (portfolio_id, user.id))
        
        conn.commit()
        conn.close()
        
        flash('Gem removed from portfolio', 'success')
        
    except Exception as e:
        log_db_exception(e, 'portfolio.delete_gem: deleting gem')
        flash('Error removing gem from portfolio', 'error')
    finally:
        try:
            conn.close()
        except:
            pass
    
    return redirect(url_for('portfolio.index'))

@bp.route('/stats')
def portfolio_stats():
    """Portfolio statistics and analytics"""
    user = load_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Total portfolio value
        cursor.execute("""
            SELECT 
                COUNT(*) as total_items,
                SUM(purchase_price) as total_invested,
                SUM(current_value) as total_current_value,
                SUM(weight_carats) as total_carats
            FROM user_portfolio 
            WHERE user_id = ?
        """, (user.id,))
        
        stats = cursor.fetchone()
        
        # Top gems by value
        cursor.execute("""
            SELECT gem_type_name, SUM(current_value) as total_value
            FROM user_portfolio 
            WHERE user_id = ?
            GROUP BY gem_type_name
            ORDER BY total_value DESC
            LIMIT 10
        """, (user.id,))
        
        top_gems = cursor.fetchall()
        conn.close()
        
        return render_template('portfolio/stats.html', stats=stats, top_gems=top_gems)
        
    except Exception as e:
        log_db_exception(e, 'portfolio.portfolio_stats: fetching stats')
        return render_template('portfolio/stats.html', stats=None, top_gems=[])
    finally:
        try:
            conn.close()
        except:
            pass
