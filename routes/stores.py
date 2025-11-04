"""
Stores and Auctions routes for Gems Hub
"""

from flask import Blueprint, render_template
import yaml
import os

bp = Blueprint('stores', __name__, url_prefix='/stores')

def load_gem_types():
    """Load all gem sections from YAML configuration"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config_gem_types.yaml')
    try:
        with open(config_path, 'r') as file:
            data = yaml.safe_load(file)
            # Return all sections
            all_sections = {}
            all_sections['Gemstones by Mineral Group'] = data.get('Gemstones by Mineral Group', [])
            all_sections['Organic Gemstones'] = data.get('Organic Gemstones', [])
            all_sections['Other Important Gemstones'] = data.get('Other Important Gemstones', [])
            all_sections['Rare and Collector Gemstones'] = data.get('Rare and Collector Gemstones', [])
            return all_sections
    except Exception as e:
        print(f"Error loading gem types: {e}")
        return {}

def parse_gem_hierarchy(gem_data):
    """Parse gem hierarchy maintaining the group structure"""
    gem_groups = []
    
    for item in gem_data:
        if isinstance(item, str):
            # It's a top-level gem (like Diamond)
            gem_name = item.replace(' (Protected)', '').replace(' (Bixbite)', '').strip()
            if '(' in gem_name:
                clean_name = gem_name.split('(')[0].strip()
            else:
                clean_name = gem_name
            
            gem_groups.append({
                'group_name': gem_name,
                'group_search_name': clean_name,
                'gems': []
            })
        elif isinstance(item, dict):
            # It's a group with sub-gems
            for key, value in item.items():
                group_name = key
                group_search_name = key.replace(' Group', '').replace(' Family', '').strip()
                
                gems_list = []
                if isinstance(value, list):
                    for gem in value:
                        if isinstance(gem, str):
                            gem_name = gem
                            clean_name = gem.replace(' (Protected)', '').replace(' (Bixbite)', '').strip()
                            if '(' in clean_name:
                                clean_name = clean_name.split('(')[0].strip()
                            
                            gems_list.append({
                                'display_name': gem_name,
                                'search_name': clean_name
                            })
                
                gem_groups.append({
                    'group_name': group_name,
                    'group_search_name': group_search_name,
                    'gems': gems_list
                })
    
    return gem_groups

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
    all_sections = load_gem_types()
    
    # Parse each section
    sections_data = []
    for section_name, gem_data in all_sections.items():
        if gem_data:  # Only include non-empty sections
            gem_groups = parse_gem_hierarchy(gem_data)
            sections_data.append({
                'section_name': section_name,
                'gem_groups': gem_groups
            })
    
    page_data = {
        'title': 'Gem Rock Auctions',
        'description': 'Search for gemstones on Gem Rock Auctions - browse by gem type',
        'sections': sections_data,
        'search_base_url': 'https://www.gemrockauctions.com/search?query='
    }
    return render_template('stores/gem_rock_auctions.html', **page_data)
