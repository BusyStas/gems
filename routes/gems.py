"""
Gems routes for Gems Hub
"""

from flask import Blueprint, render_template, current_app
import yaml
import os
import logging

bp = Blueprint('gems', __name__, url_prefix='/gems')

# Configure logging
logger = logging.getLogger(__name__)

def load_gem_hardness():
    """Load gem hardness data from config file with error handling"""
    hardness_data = {}
    
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config_gem_hardness.txt')
        
        if not os.path.exists(config_path):
            logger.error(f"Hardness config file not found: {config_path}")
            return hardness_data
        
        with open(config_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                if '=' not in line:
                    logger.warning(f"Invalid line format in {config_path} at line {line_num}: {line}")
                    continue
                
                try:
                    gem_name, hardness = line.split('=', 1)
                    gem_name = gem_name.strip()
                    hardness = hardness.strip()
                    
                    if gem_name and hardness:
                        hardness_data[gem_name] = hardness
                except ValueError as e:
                    logger.warning(f"Error parsing line {line_num} in {config_path}: {e}")
                    continue
                    
    except IOError as e:
        logger.error(f"Error reading hardness config file: {e}")
    except Exception as e:
        logger.error(f"Unexpected error loading hardness data: {e}")
    
    return hardness_data

def load_gem_types():
    """Load gem types from YAML config with error handling"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config_gem_types.yaml')
        
        if not os.path.exists(config_path):
            logger.error(f"Gem types config file not found: {config_path}")
            return {}
        
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        if not isinstance(data, dict):
            logger.error("Invalid YAML format: expected dictionary")
            return {}
            
        return data
        
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing error: {e}")
        return {}
    except IOError as e:
        logger.error(f"Error reading gem types config file: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error loading gem types: {e}")
        return {}

def get_hardness_value(hardness_str):
    """Convert hardness string to numeric value for sorting with error handling"""
    try:
        if not hardness_str or not isinstance(hardness_str, str):
            return 0.0
            
        hardness_str = hardness_str.strip()
        
        if '-' in hardness_str:
            # Take the average of the range
            parts = hardness_str.split('-', 1)
            if len(parts) == 2:
                try:
                    val1 = float(parts[0].strip())
                    val2 = float(parts[1].strip())
                    return (val1 + val2) / 2
                except ValueError:
                    logger.warning(f"Invalid hardness range format: {hardness_str}")
                    return 0.0
        
        return float(hardness_str)
        
    except ValueError as e:
        logger.warning(f"Cannot convert hardness to float: {hardness_str} - {e}")
        return 0.0
    except Exception as e:
        logger.error(f"Unexpected error in get_hardness_value: {e}")
        return 0.0

def categorize_by_hardness(hardness_val):
    """Categorize gem by hardness level"""
    try:
        if not isinstance(hardness_val, (int, float)):
            hardness_val = 0.0
            
        if hardness_val < 3:
            return 'Very Soft (1-2.99)'
        elif hardness_val < 6:
            return 'Soft (3-5.99)'
        elif hardness_val < 7.5:
            return 'Medium (6-7.49)'
        elif hardness_val < 8.5:
            return 'Hard (7.5-8.49)'
        elif hardness_val < 10:
            return 'Very Hard (8.5-9.99)'
        else:
            return 'Extremely Hard (10)'
    except Exception as e:
        logger.error(f"Error categorizing hardness: {e}")
        return 'Unknown'

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

@bp.route('/by-hardness')
def by_hardness():
    """Gems by hardness page with defensive coding"""
    try:
        hardness_data = load_gem_hardness()
        
        if not hardness_data:
            logger.warning("No hardness data loaded")
            return render_template('gems/by_hardness.html', 
                                 title='Gems by Hardness (Mohs Scale)',
                                 description='No gem data available',
                                 categories=[],
                                 search_base_url='https://www.gemrockauctions.com/search?query=')
        
        # Create list of gems with their hardness
        gems_list = []
        for gem_name, hardness_str in hardness_data.items():
            try:
                if not gem_name or not hardness_str:
                    continue
                    
                hardness_val = get_hardness_value(hardness_str)
                category = categorize_by_hardness(hardness_val)
                
                gems_list.append({
                    'name': gem_name,
                    'hardness': hardness_str,
                    'hardness_val': hardness_val,
                    'category': category
                })
            except Exception as e:
                logger.warning(f"Error processing gem {gem_name}: {e}")
                continue
        
        if not gems_list:
            logger.warning("No valid gems found in hardness data")
        
        # Sort by hardness descending
        try:
            gems_list.sort(key=lambda x: x.get('hardness_val', 0), reverse=True)
        except Exception as e:
            logger.error(f"Error sorting gems list: {e}")
        
        # Group by category
        categories = {}
        category_order = [
            'Extremely Hard (10)',
            'Very Hard (8.5-9.99)',
            'Hard (7.5-8.49)',
            'Medium (6-7.49)',
            'Soft (3-5.99)',
            'Very Soft (1-2.99)'
        ]
        
        for gem in gems_list:
            cat = gem.get('category', 'Unknown')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(gem)
        
        # Create ordered list of categories
        ordered_categories = []
        for cat_name in category_order:
            if cat_name in categories:
                ordered_categories.append({
                    'name': cat_name,
                    'gems': categories[cat_name]
                })
        
        page_data = {
            'title': 'Gems by Hardness (Mohs Scale)',
            'description': 'Explore gemstones organized by their hardness on the Mohs scale',
            'categories': ordered_categories,
            'search_base_url': 'https://www.gemrockauctions.com/search?query='
        }
        return render_template('gems/by_hardness.html', **page_data)
        
    except Exception as e:
        logger.error(f"Error in by_hardness route: {e}")
        return render_template('gems/by_hardness.html', 
                             title='Gems by Hardness (Mohs Scale)',
                             description='Error loading gem data',
                             categories=[],
                             search_base_url='https://www.gemrockauctions.com/search?query=')

@bp.route('/by-rarity')
def by_rarity():
    """Gems by rarity page - placeholder"""
    page_data = {
        'title': 'Gems by Rarity',
        'description': 'Coming soon: Gemstones organized by rarity'
    }
    return render_template('gems/index.html', **page_data)

@bp.route('/by-size')
def by_size():
    """Gems by size page - placeholder"""
    page_data = {
        'title': 'Gems by Size',
        'description': 'Coming soon: Gemstones organized by typical size'
    }
    return render_template('gems/index.html', **page_data)

@bp.route('/by-price')
def by_price():
    """Gems by price page - placeholder"""
    page_data = {
        'title': 'Gems by Price',
        'description': 'Coming soon: Gemstones organized by price range'
    }
    return render_template('gems/index.html', **page_data)

@bp.route('/by-colors')
def by_colors():
    """Gems by colors page - placeholder"""
    page_data = {
        'title': 'Gems by Colors',
        'description': 'Coming soon: Gemstones organized by color'
    }
    return render_template('gems/index.html', **page_data)
