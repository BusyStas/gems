"""
Gems Hub - Main Flask Application
A comprehensive web resource for gem information, investments, and jewelry
"""

from flask import Flask, render_template, url_for
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

# Import routes
from routes import main, gems, investments, jewelry, stores

# Register blueprints
app.register_blueprint(main.bp)
app.register_blueprint(gems.bp)
app.register_blueprint(investments.bp)
app.register_blueprint(jewelry.bp)
app.register_blueprint(stores.bp)

@app.context_processor
def inject_globals():
    """Inject global variables and functions into all templates"""
    from datetime import datetime
    return dict(current_year=lambda: datetime.now().year)

@app.context_processor
def inject_menu():
    """Inject menu structure into all templates"""
    menu_items = [
        {
            'title': 'Home',
            'icon': '🏠',
            'url': url_for('main.index')
        },
        {
            'title': 'Type of Gems',
            'icon': '💎',
            'url': url_for('gems.index'),
            'submenu': [
                {'title': 'By hardness', 'url': url_for('gems.by_hardness')},
                {'title': 'By rarity', 'url': url_for('gems.by_rarity')},
                {'title': 'By availability', 'url': url_for('gems.by_availability')},
                {'title': 'By size', 'url': url_for('gems.by_size')},
                {'title': 'By price', 'url': url_for('gems.by_price')},
                {'title': 'By colors', 'url': url_for('gems.by_colors')},
            ]
        },
        {
            'title': 'Stores and Auctions',
            'icon': '🏪',
            'url': url_for('stores.index'),
            'submenu': [
                {'title': 'Gem Rock Auctions', 'url': url_for('stores.gem_rock_auctions')},
            ]
        },
        {
            'title': 'Investments',
            'icon': '📈',
            'url': url_for('investments.index'),
            'submenu': [
                {'title': 'Market Trends', 'url': url_for('investments.market_trends')},
                {'title': 'Value Assessment', 'url': url_for('investments.value_assessment')},
            ]
        },
        {
            'title': 'Jewelry',
            'icon': '👑',
            'url': url_for('jewelry.index'),
            'submenu': [
                {'title': 'Rings', 'url': url_for('jewelry.rings')},
                {'title': 'Necklaces', 'url': url_for('jewelry.necklaces')},
                {'title': 'Earrings', 'url': url_for('jewelry.earrings')},
            ]
        }
    ]
    return dict(menu_items=menu_items)

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
