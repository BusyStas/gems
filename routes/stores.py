"""
Stores and Auctions routes for Gems Hub
"""

from flask import Blueprint, render_template
import yaml
import os

bp = Blueprint('stores', __name__, url_prefix='/stores')

def load_gem_types():
    """Load gem types from YAML configuration"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config_gem_types.yaml')
    try:
        with open(config_path, 'r') as file:
            data = yaml.safe_load(file)
            return data.get('Gemstones by Mineral Group', [])
    except Exception as e:
        print(f"Error loading gem types: {e}")
        return []

def flatten_gem_list(gem_data, parent_name=None):
    """Recursively flatten the gem type hierarchy into a simple list"""
    gems = []
    
    for item in gem_data:
        if isinstance(item, str):
            # It's a simple gem name
            gem_name = item.replace(' (Protected)', '').replace(' (Bixbite)', '').strip()
            # Remove parenthetical notes for cleaner search
            if '(' in gem_name:
                gem_name = gem_name.split('(')[0].strip()
            gems.append({
                'name': gem_name,
                'display_name': item,
                'group': parent_name
            })
        elif isinstance(item, dict):
            # It's a nested structure
            for key, value in item.items():
                group_name = key.replace(' Group', '').replace(' Family', '')
                if isinstance(value, list):
                    gems.extend(flatten_gem_list(value, group_name))
    
    return gems

@bp.route('/')
def index():
    """Stores and Auctions main page"""
    page_data = {
        'title': 'Stores and Auctions',
        'description': 'Discover where to buy gems, gemstones, and jewelry from trusted sources',
        'stores': [
            {
                'name': 'Gem Rock Auctions',
                'description': 'Online auction platform for gemstones and minerals',
                'url': '/stores/gem-rock-auctions'
            }
        ]
    }
    return render_template('stores/index.html', **page_data)

@bp.route('/gem-rock-auctions')
def gem_rock_auctions():
    """Gem Rock Auctions page with searchable gem types"""
    gem_data = load_gem_types()
    gems_list = flatten_gem_list(gem_data)
    
    # Remove duplicates and sort
    unique_gems = {}
    for gem in gems_list:
        if gem['name'] not in unique_gems:
            unique_gems[gem['name']] = gem
    
    sorted_gems = sorted(unique_gems.values(), key=lambda x: x['name'])
    
    page_data = {
        'title': 'Gem Rock Auctions',
        'description': 'Search for gemstones on Gem Rock Auctions - browse by gem type',
        'gems': sorted_gems,
        'search_base_url': 'https://www.gemrockauctions.com/search?query='
    }
    return render_template('stores/gem_rock_auctions.html', **page_data)
