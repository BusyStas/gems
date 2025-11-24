"""
Stores and Auctions routes for Gems Hub
"""

from flask import Blueprint, render_template, current_app
import yaml
import requests
from utils.api_client import get_gems_from_api, build_types_structure_from_api
import os
import logging

bp = Blueprint('stores', __name__, url_prefix='/stores')

# Configure logging
logger = logging.getLogger(__name__)

def load_gem_types():
    """Load all gem sections from YAML configuration with error handling"""
    # Try to get types from API
    try:
        gems_list = get_gems_from_api()
        if gems_list:
            return build_types_structure_from_api(gems_list)
    except Exception as e:
        logger.warning(f"Gems API not available: {e}")

    # Fallback to file-based types
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config_gem_types.yaml')
        
        if not os.path.exists(config_path):
            logger.error(f"Gem types config file not found: {config_path}")
            return {}
        
        with open(config_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            
        if not isinstance(data, dict):
            logger.error("Invalid YAML format: expected dictionary")
            return {}
        
        # Return all sections with safe get
        all_sections = {}
        section_names = [
            'Gemstones by Mineral Group',
            'Organic Gemstones', 
            'Other Important Gemstones',
            'Rare and Collector Gemstones'
        ]
        
        for section_name in section_names:
            all_sections[section_name] = data.get(section_name, [])
            
        return all_sections
        
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing error: {e}")
        return {}
    except IOError as e:
        logger.error(f"Error reading gem types config file: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error loading gem types: {e}")
        return {}

def parse_gem_hierarchy(gem_data):
    """Parse gem hierarchy maintaining the group structure with error handling"""
    gem_groups = []
    
    try:
        if not gem_data or not isinstance(gem_data, list):
            return gem_groups
        
        for item in gem_data:
            try:
                if isinstance(item, str):
                    # It's a top-level gem (like Diamond)
                    gem_name = item.replace(' (Protected)', '').replace(' (Bixbite)', '').strip()
                    if '(' in gem_name:
                        clean_name = gem_name.split('(')[0].strip()
                    else:
                        clean_name = gem_name
                    
                    if clean_name:  # Only add if we have a valid name
                        gem_groups.append({
                            'group_name': gem_name,
                            'group_search_name': clean_name,
                            'gems': []
                        })
                        
                elif isinstance(item, dict):
                    # It's a group with sub-gems
                    for key, value in item.items():
                        if not key or not isinstance(value, list):
                            logger.warning(f"Invalid group structure for key: {key}")
                            continue
                            
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
                                    
                                    if clean_name:  # Only add if valid
                                        gems_list.append({
                                            'display_name': gem_name,
                                            'search_name': clean_name
                                        })
                        
                        if group_name:  # Only add if we have a group name
                            gem_groups.append({
                                'group_name': group_name,
                                'group_search_name': group_search_name,
                                'gems': gems_list
                            })
                            
            except Exception as e:
                logger.warning(f"Error parsing gem item: {e}")
                continue
    
    except Exception as e:
        logger.error(f"Error in parse_gem_hierarchy: {e}")
    
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
            },
            {
                'name': 'Best In Gems',
                'description': 'Online marketplace and listings for loose gemstones',
                'url': '/stores/best-in-gems'
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


@bp.route('/best-in-gems')
def best_in_gems():
    """Best In Gems page with searchable gem types"""
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
        'title': 'Best In Gems',
        'description': 'Search for gemstones on Best In Gems - browse by gem type',
        'sections': sections_data,
        'search_base_url': 'https://www.bestingems.com/listing/buy-gemstones-online/?filter=gemsname:'
    }
    return render_template('stores/best_in_gems.html', **page_data)
