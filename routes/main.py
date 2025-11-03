"""
Main routes for Gems Hub
"""

from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Home page"""
    page_data = {
        'title': 'Welcome to Gems Hub',
        'description': 'Your comprehensive resource for everything about gems, gemstones, investments, and jewelry',
        'hero_title': 'Discover the World of Gems',
        'hero_text': 'Explore precious and semi-precious stones, learn about gem investments, and find the perfect jewelry pieces.'
    }
    return render_template('home.html', **page_data)
