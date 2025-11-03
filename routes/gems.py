"""
Gems routes for Gems Hub
"""

from flask import Blueprint, render_template

bp = Blueprint('gems', __name__, url_prefix='/gems')

@bp.route('/')
def index():
    """Gems main page"""
    page_data = {
        'title': 'Type of Gems',
        'description': 'Explore different types of gems including precious, semi-precious, and organic gemstones',
        'sections': [
            {
                'name': 'Precious Gems',
                'description': 'The four precious gemstones: Diamond, Ruby, Sapphire, and Emerald',
                'image': 'precious-gems.jpg'
            },
            {
                'name': 'Semi-Precious Gems',
                'description': 'Beautiful gemstones including Amethyst, Topaz, Garnet, and more',
                'image': 'semi-precious-gems.jpg'
            },
            {
                'name': 'Organic Gems',
                'description': 'Natural organic materials like Pearl, Amber, and Coral',
                'image': 'organic-gems.jpg'
            }
        ]
    }
    return render_template('gems/index.html', **page_data)

@bp.route('/precious')
def precious():
    """Precious gems page"""
    page_data = {
        'title': 'Precious Gems',
        'description': 'Learn about the four precious gemstones',
        'gems': [
            {'name': 'Diamond', 'description': 'The hardest natural material, known for brilliance'},
            {'name': 'Ruby', 'description': 'The red variety of corundum, symbol of passion'},
            {'name': 'Sapphire', 'description': 'Blue corundum, representing wisdom and royalty'},
            {'name': 'Emerald', 'description': 'Green beryl, the gem of spring and rebirth'}
        ]
    }
    return render_template('gems/precious.html', **page_data)

@bp.route('/semi-precious')
def semi_precious():
    """Semi-precious gems page"""
    page_data = {
        'title': 'Semi-Precious Gems',
        'description': 'Discover beautiful semi-precious gemstones',
        'gems': [
            {'name': 'Amethyst', 'description': 'Purple quartz, stone of spirituality'},
            {'name': 'Topaz', 'description': 'Available in many colors, known for clarity'},
            {'name': 'Garnet', 'description': 'Deep red stone, symbol of energy'},
            {'name': 'Aquamarine', 'description': 'Blue-green beryl, calming and serene'}
        ]
    }
    return render_template('gems/semi_precious.html', **page_data)

@bp.route('/organic')
def organic():
    """Organic gems page"""
    page_data = {
        'title': 'Organic Gems',
        'description': 'Natural organic gemstones formed by living organisms',
        'gems': [
            {'name': 'Pearl', 'description': 'Formed by mollusks, symbol of purity'},
            {'name': 'Amber', 'description': 'Fossilized tree resin, preserving ancient life'},
            {'name': 'Coral', 'description': 'Marine organism structures, vibrant colors'}
        ]
    }
    return render_template('gems/organic.html', **page_data)
