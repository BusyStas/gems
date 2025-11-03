"""
Jewelry routes for Gems Hub
"""

from flask import Blueprint, render_template

bp = Blueprint('jewelry', __name__, url_prefix='/jewelry')

@bp.route('/')
def index():
    """Jewelry main page"""
    page_data = {
        'title': 'Jewelry',
        'description': 'Explore beautiful jewelry pieces featuring precious and semi-precious gems',
        'intro': 'From elegant rings to stunning necklaces, discover the perfect jewelry pieces.',
        'categories': [
            {'name': 'Rings', 'description': 'Engagement, wedding, and fashion rings'},
            {'name': 'Necklaces', 'description': 'Pendants, chains, and statement necklaces'},
            {'name': 'Earrings', 'description': 'Studs, drops, and chandelier earrings'}
        ]
    }
    return render_template('jewelry/index.html', **page_data)

@bp.route('/rings')
def rings():
    """Rings page"""
    page_data = {
        'title': 'Rings',
        'description': 'Beautiful rings featuring precious gemstones',
        'types': [
            {'name': 'Engagement Rings', 'description': 'Classic and modern engagement ring designs'},
            {'name': 'Wedding Bands', 'description': 'Timeless wedding bands in various styles'},
            {'name': 'Fashion Rings', 'description': 'Statement and cocktail rings for any occasion'},
            {'name': 'Gemstone Rings', 'description': 'Rings featuring colored gemstones'}
        ]
    }
    return render_template('jewelry/rings.html', **page_data)

@bp.route('/necklaces')
def necklaces():
    """Necklaces page"""
    page_data = {
        'title': 'Necklaces',
        'description': 'Elegant necklaces and pendants with gemstones',
        'types': [
            {'name': 'Pendant Necklaces', 'description': 'Simple pendants featuring single gems'},
            {'name': 'Statement Necklaces', 'description': 'Bold designs with multiple gemstones'},
            {'name': 'Chain Necklaces', 'description': 'Classic chains in various metals'},
            {'name': 'Gemstone Strands', 'description': 'Beaded necklaces of precious stones'}
        ]
    }
    return render_template('jewelry/necklaces.html', **page_data)

@bp.route('/earrings')
def earrings():
    """Earrings page"""
    page_data = {
        'title': 'Earrings',
        'description': 'Stunning earrings adorned with beautiful gems',
        'types': [
            {'name': 'Stud Earrings', 'description': 'Classic studs featuring gemstones'},
            {'name': 'Drop Earrings', 'description': 'Elegant drops with gem accents'},
            {'name': 'Chandelier Earrings', 'description': 'Dramatic multi-tier designs'},
            {'name': 'Hoop Earrings', 'description': 'Modern hoops with gem details'}
        ]
    }
    return render_template('jewelry/earrings.html', **page_data)
