"""
Gems routes for Gems Hub
"""

from flask import Blueprint, render_template, current_app
from flask_login import current_user
import yaml
import requests
import re
from utils.api_client import get_gems_from_api, build_types_structure_from_api, load_api_key
import os
import logging
import sqlite3
from utils.db_logger import log_db_exception
from utils.sqlite_utils import row_to_dict

bp = Blueprint('gems', __name__, url_prefix='/gems')

# Configure logging
logger = logging.getLogger(__name__)

def get_user_holdings(user_id, gem_type_name):
    """Get user's holdings for a specific gem type from portfolio database."""
    if not user_id or not gem_type_name:
        return []
    
    try:
        DB_PATH = os.path.join(os.getcwd(), 'gems_portfolio.db')
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, weight_carats, purchase_price, current_value, 
                   purchase_date, notes, date_added, last_updated
            FROM user_portfolio
            WHERE user_id = ? AND LOWER(gem_type_name) = LOWER(?)
            ORDER BY purchase_date DESC
        """, (user_id, gem_type_name))
        
        rows = cursor.fetchall()
        conn.close()
        
        holdings = []
        for row in rows:
            holdings.append({
                'id': row['id'],
                'weight_carats': row['weight_carats'],
                'purchase_price': row['purchase_price'],
                'current_value': row['current_value'],
                'purchase_date': row['purchase_date'],
                'notes': row['notes'],
                'date_added': row['date_added'],
                'last_updated': row['last_updated']
            })
        
        return holdings
    except Exception as e:
        logger.error(f"Error fetching user holdings for {gem_type_name}: {e}")
        return []

def load_gem_hardness():
    """Load gem hardness data from Web API only."""
    # v2 API uses PascalCase: GemTypeName, HardnessRange, HardnessLevel
    try:
        gems = get_gems_from_api()
        if gems:
            hd = {}
            for g in gems:
                name = g.get('GemTypeName')
                hr = g.get('HardnessRange') or (str(g.get('HardnessLevel')) if g.get('HardnessLevel') else '')
                if name and hr:
                    hd[name] = str(hr)
            return hd
    except Exception as e:
        logger.error(f"Failed to load hardness data from API: {e}")
    return {}

def load_gem_types():
    """Load gem types from Web API only."""
    try:
        gems_list = get_gems_from_api()
        if gems_list:
            return build_types_structure_from_api(gems_list)
    except Exception as e:
        logger.error(f"Failed to load gem types from API: {e}")
    return {}

def get_hardness_value(hardness_str):
    """Convert hardness string to numeric value for sorting with error handling"""
    try:
        if not hardness_str or not isinstance(hardness_str, str):
            return 0.0
        # Normalize common unicode dash characters to ASCII hyphen for parsing
        hardness_str = hardness_str.strip()
        hardness_str = hardness_str.replace('\u2013', '-').replace('\u2014', '-')
        
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
        
        # Follow BusinessRequirements buckets precisely
        # Very Soft (1-2.99), Soft (3-5.99), Medium-1 (6-6.99), Medium-2 (7.0-7.49),
        # Hard-1 (7.5-7.99), Hard-2 (8.0-8.49), Very Hard (8.5-9.99), Extremely Hard (10)
        if hardness_val < 3:
            return 'Very Soft (1-2.99)'
        elif hardness_val < 6:
            return 'Soft (3-5.99)'
        elif hardness_val < 7.0:
            return 'Medium-1 (6-6.99)'
        elif hardness_val < 7.5:
            return 'Medium-2 (7.0-7.49)'
        elif hardness_val < 8.0:
            return 'Hard-1 (7.5-7.99)'
        elif hardness_val < 8.5:
            return 'Hard-2 (8.0-8.49)'
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
        
        # Load gem types to map gem -> mineral group for hover text
        types_raw = load_gem_types()
        gem_to_group = {}
        try:
            for key, val in types_raw.items():
                if not isinstance(val, list):
                    continue
                for entry in val:
                    if isinstance(entry, str):
                        gem_to_group[entry] = key
                    elif isinstance(entry, dict):
                        for group_name, gems in entry.items():
                            if isinstance(gems, list):
                                for g in gems:
                                    gem_to_group[g] = group_name
                            elif isinstance(gems, str):
                                gem_to_group[gems] = group_name
        except Exception as e:
            logger.warning(f"Error mapping gem groups for hardness: {e}")

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
                    'category': category,
                    'mineral_group': gem_to_group.get(gem_name, '')
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
            'Hard-2 (8.0-8.49)',
            'Hard-1 (7.5-7.99)',
            'Medium-2 (7.0-7.49)',
            'Medium-1 (6-6.99)',
            'Soft (3-5.99)',
            'Very Soft (1-2.99)'
        ]
        
        for gem in gems_list:
            cat = gem.get('category', 'Unknown')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(gem)
        
        # Read tiers from DB for all gems in this list (prefer DB values; do not recompute)
        DB_PATH = os.path.join(os.getcwd(), 'gems_portfolio.db')
        try:
            gem_names = [g.get('name') for g in gems_list if g.get('name')]
            db_cache = {}
            if gem_names:
                try:
                    conn = sqlite3.connect(DB_PATH)
                    conn.row_factory = sqlite3.Row
                    cur = conn.cursor()
                    # build parameter placeholders
                    placeholders = ','.join('?' for _ in gem_names)
                    query = f"SELECT gem_type_name, Investment_Ranking_Tier, Investment_Ranking_Score FROM gem_attributes WHERE gem_type_name IN ({placeholders})"
                    cur.execute(query, tuple(gem_names))
                    for row in cur.fetchall():
                        r = row_to_dict(row)
                        name = (r.get('gem_type_name') or '').strip().lower()
                        db_cache[name] = {
                            'tier': r.get('Investment_Ranking_Tier'),
                            'score': r.get('Investment_Ranking_Score')
                        }
                except Exception as e:
                    log_db_exception(e, 'by_hardness: selecting gem_attributes')
                finally:
                    try:
                        conn.close()
                    except Exception:
                        pass
            # Attach cached tier/score (or Unknown) to each gem entry
            for gem in gems_list:
                name = (gem.get('name') or '').strip().lower()
                info = db_cache.get(name)
                if info:
                    gem['tier'] = info.get('tier') or 'Unknown'
                    gem['composite'] = round(info.get('score') or 0, 2)
                else:
                    gem['tier'] = 'Unknown'
        except Exception as e:
            # on any other error, log it and mark tiers unknown rather than recomputing
            log_db_exception(e, 'by_hardness: processing DB cache')
            for gem in gems_list:
                gem['tier'] = 'Unknown'

        # Create ordered list of categories
        ordered_categories = []
        for cat_name in category_order:
            if cat_name in categories:
                ordered_categories.append({
                    'name': cat_name,
                    'gems': categories[cat_name]
                })

        # No global page visibility flags set here (moved to pages which need it)

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
    """Gems by rarity page - loads rarity data from Web API only.

    Groups gems into the five rarity categories required by the business rules.
    """
    try:
        # Load rarity data from API only
        # v2 API uses PascalCase: GemTypeName, RarityLevel, AvailabilityLevel, RarityDescription
        rarity_data = {}
        gems_api = get_gems_from_api() or []
        for g in gems_api:
            name = g.get('GemTypeName')
            if not name:
                continue
            rarity_data[name] = {
                'rarity': str(g.get('RarityLevel') or '').strip(),
                'availability': str(g.get('AvailabilityLevel') or '').strip(),
                'rarity_description': str(g.get('RarityDescription') or '').strip()
            }

        # Load gem types to map gem -> mineral group for hover text
        types_raw = load_gem_types()
        gem_to_group = {}
        try:
            # types_raw expected to be a dict with keys like 'Gemstones by Mineral Group' etc.
            for key, val in types_raw.items():
                # val is typically a list; items may be strings or mappings like 'Beryl Group': [ ... ]
                if not isinstance(val, list):
                    continue
                for entry in val:
                    if isinstance(entry, str):
                        gem_to_group[entry] = key
                    elif isinstance(entry, dict):
                        for group_name, gems in entry.items():
                            # group_name like 'Beryl Group'
                            if isinstance(gems, list):
                                for g in gems:
                                    gem_to_group[g] = group_name
                            elif isinstance(gems, str):
                                gem_to_group[gems] = group_name
        except Exception as e:
            logger.warning(f"Error mapping gem groups: {e}")

        # Build list of gem entries from rarity_data
        # Map existing availability values to the project's availability groups and supply a
        # short availability_description (uses reasonable defaults). This avoids requiring
        # manual edits of the YAML while keeping the UI consistent with requirements.
        availability_map = {
            'common': 'Consistently Available',
            'consistently available': 'Consistently Available',
            'uncommon': 'Readily Available',
            'readily available': 'Readily Available',
            'rare': 'Limited Supply',
            'limited supply': 'Limited Supply',
            'very rare': 'Collectors Market',
            'collectors market': 'Collectors Market',
            'extremely rare': 'Museum Grade Rarity',
            'museum grade rarity': 'Museum Grade Rarity'
        }

        availability_description_defaults = {
            'Consistently Available': 'Consistent Deposits',
            'Readily Available': 'Readily Available',
            'Limited Supply': 'Limited Deposits',
            'Collectors Market': 'Limited Investment',
            'Museum Grade Rarity': 'Difficult Mining'
        }

        gems_list = []
        for gem_name, info in rarity_data.items():
            raw_av = (info.get('availability') or '').strip()
            av_key = raw_av.lower()
            availability_group = availability_map.get(av_key, raw_av or '')
            availability_description = availability_description_defaults.get(availability_group, '')

            gems_list.append({
                'name': gem_name,
                'rarity': info.get('rarity', 'Unknown'),
                'availability': availability_group,
                'availability_description': availability_description,
                'rarity_description': info.get('rarity_description', ''),
                'mineral_group': gem_to_group.get(gem_name, '')
            })

        # Group gems by rarity category
        categories = {}
        # Desired display order: descending rarity (rarest first)
        order = [
            'Singular Occurrence',
            'Unique Geological',
            'Localized Formation',
            'Limited Occurrence',
            'Abundant Minerals'
        ]

        for gem in gems_list:
            cat = gem.get('rarity') or 'Unknown'
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(gem)

        # Build ordered categories for template
        ordered = []
        for cat in order:
            if cat in categories:
                # sort gems alphabetically within category
                categories[cat].sort(key=lambda x: x.get('name', '').lower())
                ordered.append({'name': cat, 'gems': categories[cat]})

        # Add any other categories present
        for extra_cat, gems in categories.items():
            if extra_cat not in order:
                gems.sort(key=lambda x: x.get('name', '').lower())
                ordered.append({'name': extra_cat, 'gems': gems})

        page_data = {
            'title': 'Gems by Rarity',
            'description': 'Gemstone types grouped by geological rarity',
            'categories': ordered,
            'search_base_url': 'https://www.gemrockauctions.com/search?query='
        }

        return render_template('gems/by_rarity.html', **page_data)

    except Exception as e:
        logger.error(f"Error in by_rarity route: {e}")
        return render_template('gems/index.html',
                               title='Gems by Rarity',
                               description='Error loading rarity data')


@bp.route('/by-availability')
def by_availability():
    """Gems by market availability (groups and drivers)

    Builds a list of gems with availability, availability_driver and availability_description
    sourced from `config_gem_rarity.yaml` when present. Groups gems into the market availability
    buckets required by the business rules.
    """
    try:
        # Try to load availability/rarity data from API first
        entries = {}
        # Load availability data only from the API. Do not fallback to YAML per requirements.
        # v2 API uses PascalCase field names: GemTypeName, AvailabilityLevel, AvailabilityDriver, AvailabilityDescription
        try:
            gems_api = get_gems_from_api() or []
            for g in gems_api:
                name = g.get('GemTypeName')
                if not name:
                    continue
                props = {}
                # Use PascalCase API field names from v2 API
                props['availability'] = g.get('AvailabilityLevel') or ''
                props['availability_driver'] = g.get('AvailabilityDriver') or ''
                props['availability_description'] = g.get('AvailabilityDescription') or ''
                entries[name] = props
        except Exception as ex:
            logger.warning(f"Gems API returned error when fetching availability: {ex}")

        # Load gem types for hover mineral group
        types_raw = load_gem_types()
        gem_to_group = {}
        try:
            # Handle new nested structure: "Gemstones by Mineral Group" -> mineral groups -> gem lists
            if isinstance(types_raw, dict):
                if "Gemstones by Mineral Group" in types_raw:
                    mineral_groups = types_raw["Gemstones by Mineral Group"]
                    if isinstance(mineral_groups, dict):
                        for group_name, gems in mineral_groups.items():
                            if isinstance(gems, list):
                                for gem in gems:
                                    if isinstance(gem, str):
                                        gem_to_group[gem] = group_name
                else:
                    # Old flat structure
                    for key, val in types_raw.items():
                        if not isinstance(val, list):
                            continue
                        for entry in val:
                            if isinstance(entry, str):
                                gem_to_group[entry] = key
                            elif isinstance(entry, dict):
                                for group_name, gems in entry.items():
                                    if isinstance(gems, list):
                                        for g in gems:
                                            gem_to_group[g] = group_name
                                    elif isinstance(gems, str):
                                        gem_to_group[gems] = group_name
        except Exception as e:
            logger.warning(f"Error mapping gem groups for availability: {e}")

        # Build gems list with availability fields
        gems_list = []
        for gem_name, props in entries.items():
            try:
                # props may be dict or list
                if isinstance(props, list):
                    # convert list of small dicts to a single dict
                    merged = {}
                    for p in props:
                        if isinstance(p, dict):
                            merged.update(p)
                    props = merged

                availability = (props.get('availability') or '').strip() if isinstance(props, dict) else ''
                availability_driver = (props.get('availability_driver') or '').strip() if isinstance(props, dict) else ''
                availability_description = (props.get('availability_description') or '').strip() if isinstance(props, dict) else ''

                # Normalize availability to expected groups
                group = availability or ''
                # Map common variants
                normal_map = {
                    'consistent deposits': 'Consistently Available',
                    'consistently available': 'Consistently Available',
                    'readily available': 'Readily Available',
                    'limited supply': 'Limited Supply',
                    'collectors market': 'Collectors Market',
                    'museum grade rarity': 'Museum Grade Rarity'
                }
                group_key = normal_map.get(group.lower(), group)

                gems_list.append({
                    'name': gem_name,
                    'availability': group_key,
                    'availability_driver': availability_driver,
                    'availability_description': availability_description,
                    'mineral_group': gem_to_group.get(gem_name, '')
                })
            except Exception as e:
                logger.warning(f"Error processing availability for {gem_name}: {e}")

        # Group by availability
        categories = {}
        # Show availability groups in descending market scarcity (most scarce first)
        order = [
            'Museum Grade Rarity',
            'Collectors Market',
            'Limited Supply',
            'Readily Available',
            'Consistently Available'
        ]

        for gem in gems_list:
            cat = gem.get('availability') or 'Unknown'
            categories.setdefault(cat, []).append(gem)

        ordered = []
        for cat in order:
            if cat in categories:
                categories[cat].sort(key=lambda x: x.get('name','').lower())
                ordered.append({'name': cat, 'gems': categories[cat]})

        for extra_cat, gems in categories.items():
            if extra_cat not in order:
                gems.sort(key=lambda x: x.get('name','').lower())
                ordered.append({'name': extra_cat, 'gems': gems})

        page_data = {
            'title': 'Gems by Availability',
            'description': 'Gemstone types grouped by market availability',
            'categories': ordered,
            'search_base_url': 'https://www.gemrockauctions.com/search?query='
        }

        return render_template('gems/by_availability.html', **page_data)

    except Exception as e:
        import traceback
        logger.error(f"Error in by_availability route: {e}")
        return f"<pre>Error in by_availability:\n{e}\n\n{traceback.format_exc()}</pre>", 500

@bp.route('/by-size')
def by_size():
    """Gems by size page - loads size data from Web API only.

    Parses typical size ranges and groups gems into size buckets defined in BusinessRequirements.
    """
    try:
        # Load sizes from API only
        # v2 API uses PascalCase: GemTypeName, TypicalSize
        size_data = {}
        gems_api = get_gems_from_api() or []
        for g in gems_api:
            name = g.get('GemTypeName') or ''
            size = g.get('TypicalSize') or ''
            if name and size:
                size_data[name] = size

        # Load gem types to map gem -> mineral group for hover text
        types_raw = load_gem_types()
        gem_to_group = {}
        try:
            for key, val in types_raw.items():
                if not isinstance(val, list):
                    continue
                for entry in val:
                    if isinstance(entry, str):
                        gem_to_group[entry] = key
                    elif isinstance(entry, dict):
                        for group_name, gems in entry.items():
                            if isinstance(gems, list):
                                for g in gems:
                                    gem_to_group[g] = group_name
                            elif isinstance(gems, str):
                                gem_to_group[gems] = group_name
        except Exception as e:
            logger.warning(f"Error mapping gem groups for size: {e}")

        def parse_size_value(s):
            """Return a numeric representative (average) for a size string.

            Examples handled: '1-50+ carats', '0.5-20 carats', '50+ carats', '3 carats'
            Non-parsable values return 0.0
            """
            if not s or not isinstance(s, str):
                return 0.0
            s = s.strip()
            s = s.replace('\u2013','-')
            # extract the first numeric token or range
            import re
            m = re.search(r"(\d+(?:\.\d*)?)(?:\s*-\s*(\d+(?:\.\d*)?)(\+?)?)?", s)
            if not m:
                return 0.0
            a = float(m.group(1))
            b = m.group(2)
            plus = m.group(3)
            if b:
                try:
                    bval = float(b)
                except:
                    bval = a
                # if plus sign present (e.g., 50+), keep bval as-is
                return (a + bval) / 2.0
            else:
                # single value or value with plus
                return a

        def categorize_size(val):
            # Priority order: Very Large, Large, Medium to Large, Small to Medium, Very Small
            try:
                v = float(val)
            except:
                v = 0.0
            if v >= 50:
                return 'VERY LARGE STONES (50+ carats)'
            elif v >= 20:
                return 'LARGE STONES (20-50 carats)'
            elif v >= 10:
                return 'MEDIUM TO LARGE STONES (10-30 carats)'
            elif v >= 3:
                return 'SMALL TO MEDIUM STONES (under 10 carats)'
            else:
                return 'VERY SMALL STONES (typically under 3 carats)'

        gems_list = []
        for gem_name, size_str in size_data.items():
            try:
                if not gem_name:
                    continue
                size_val = parse_size_value(size_str)
                category = categorize_size(size_val)
                gems_list.append({
                    'name': gem_name,
                    'size_str': size_str,
                    'size_val': size_val,
                    'category': category,
                    'mineral_group': gem_to_group.get(gem_name, '')
                })
            except Exception as e:
                logger.warning(f"Error processing size for {gem_name}: {e}")

        # Sort by representative size descending
        try:
            gems_list.sort(key=lambda x: x.get('size_val', 0), reverse=True)
        except Exception as e:
            logger.error(f"Error sorting gems by size: {e}")

        # Group into ordered categories
        categories = {}
        category_order = [
            'VERY LARGE STONES (50+ carats)',
            'LARGE STONES (20-50 carats)',
            'MEDIUM TO LARGE STONES (10-30 carats)',
            'SMALL TO MEDIUM STONES (under 10 carats)',
            'VERY SMALL STONES (typically under 3 carats)'
        ]

        for gem in gems_list:
            cat = gem.get('category', 'VERY SMALL STONES (typically under 3 carats)')
            categories.setdefault(cat, []).append(gem)

        ordered = []
        for cat in category_order:
            if cat in categories:
                ordered.append({'name': cat, 'gems': categories[cat]})

        page_data = {
            'title': 'Gems by Size',
            'description': 'Gemstone types grouped by typical size',
            'categories': ordered,
            'search_base_url': 'https://www.gemrockauctions.com/search?query='
        }

        return render_template('gems/by_size.html', **page_data)

    except Exception as e:
        logger.error(f"Error in by_size route: {e}")
        return render_template('gems/index.html',
                               title='Gems by Size',
                               description='Error loading size data')

@bp.route('/by-price')
def by_price():
    """Gems by price page - loads price and rarity data from Web API only.

    Groups gems by price level using API data.
    """
    try:
        # Load price and rarity data from API only
        # v2 API uses PascalCase: GemTypeName, PriceRange, RarityLevel, AvailabilityLevel
        explicit_prices = {}
        rarity_data = {}
        gems_api = get_gems_from_api() or []
        for g in gems_api:
            name = g.get('GemTypeName')
            if not name:
                continue
            price = g.get('PriceRange')
            if price:
                explicit_prices[name] = str(price)
            rarity_data[name] = {
                'rarity': str(g.get('RarityLevel') or '').strip(),
                'availability': str(g.get('AvailabilityLevel') or '').strip()
            }

        # Load gem types to map gem -> mineral group for hover text
        types_raw = load_gem_types()
        gem_to_group = {}
        try:
            for key, val in types_raw.items():
                if not isinstance(val, list):
                    continue
                for entry in val:
                    if isinstance(entry, str):
                        gem_to_group[entry] = key
                    elif isinstance(entry, dict):
                        for group_name, gems in entry.items():
                            if isinstance(gems, list):
                                for g in gems:
                                    gem_to_group[g] = group_name
                            elif isinstance(gems, str):
                                gem_to_group[gems] = group_name
        except Exception as e:
            logger.warning(f"Error mapping gem groups for price: {e}")

        # Heuristic mapping from rarity -> price group and priority value for sorting
        # Map to the explicit buckets defined in BusinessRequirements.txt
        # Bucket order (high -> low):
        # ULTRA-LUXURY, SUPER-PREMIUM, PREMIUM, HIGH-END, MID-RANGE, AFFORDABLE, BUDGET-FRIENDLY
        rarity_to_price = {
            'Singular Occurrence': ('ULTRA-LUXURY', 7),
            'Unique Geological': ('ULTRA-LUXURY', 7),
            'Localized Formation': ('PREMIUM', 5),
            'Limited Occurrence': ('HIGH-END', 4),
            'Abundant Minerals': ('AFFORDABLE', 2)
        }

        # Default when unknown: use availability to guess, else 'MID-RANGE'
        availability_map = {
            'Museum Grade Rarity': ('ULTRA-LUXURY', 7),
            'Collectors Market': ('PREMIUM', 5),
            'Limited Supply': ('HIGH-END', 4),
            'Readily Available': ('MID-RANGE', 3),
            'Consistently Available': ('AFFORDABLE', 2)
        }

        # Price groups in descending order (exact names from requirements)
        category_order = [
            'ULTRA-LUXURY',
            'SUPER-PREMIUM',
            'PREMIUM',
            'HIGH-END',
            'MID-RANGE',
            'AFFORDABLE',
            'BUDGET-FRIENDLY'
        ]

        # Build gems list: iterate through gem types file to include all gems
        types = types_raw
        gems_list = []
        import re

        def _extract_numbers(s):
            nums = re.findall(r"[\d,]+", s)
            vals = []
            for n in nums:
                try:
                    vals.append(float(n.replace(',', '')))
                except Exception:
                    continue
            return vals

        def _infer_group_from_price_str(price_str):
            if not price_str or not isinstance(price_str, str):
                return ('MID-RANGE', 3)

            s = price_str.lower()
            nums = _extract_numbers(price_str)

            # If string contains '>' treat the first number as a lower bound
            if '>' in price_str and nums:
                lb = nums[0]
                if lb >= 50000:
                    return ('ULTRA-LUXURY', 7)
                if lb >= 10000:
                    return ('SUPER-PREMIUM', 6)
                if lb >= 1000:
                    return ('PREMIUM', 5)
                if lb >= 500:
                    return ('HIGH-END', 4)
                if lb >= 100:
                    return ('MID-RANGE', 3)
                if lb >= 50:
                    return ('AFFORDABLE', 2)
                return ('BUDGET-FRIENDLY', 1)

            # If a range or single number present, use the max value found
            if nums:
                maxv = max(nums)
                if maxv >= 50000:
                    return ('ULTRA-LUXURY', 7)
                if maxv >= 10000:
                    return ('SUPER-PREMIUM', 6)
                if maxv >= 1000:
                    return ('PREMIUM', 5)
                if maxv >= 500:
                    return ('HIGH-END', 4)
                if maxv >= 100:
                    return ('MID-RANGE', 3)
                if maxv >= 50:
                    return ('AFFORDABLE', 2)
                return ('BUDGET-FRIENDLY', 1)

            # Fall back to keyword hints
            if 'ultra' in s or 'exceed' in s:
                return ('ULTRA-LUXURY', 7)
            if 'premium' in s or 'luxury' in s:
                return ('SUPER-PREMIUM', 6)
            if 'high' in s or 'valuable' in s:
                return ('HIGH-END', 4)

            return ('MID-RANGE', 3)

        def add_gem(name):
            # Determine price_str and price_value
            price_str = explicit_prices.get(name, '')
            price_group = 'MID-RANGE'
            price_value = 3

            if price_str:
                # Try to infer a precise group from the explicit price string
                try:
                    price_group, price_value = _infer_group_from_price_str(price_str)
                except Exception:
                    price_group, price_value = ('MID-RANGE', 3)
            else:
                # infer from rarity_data
                r = rarity_data.get(name, {}).get('rarity', '')
                a = rarity_data.get(name, {}).get('availability', '')
                mapped = rarity_to_price.get(r)
                if mapped:
                    price_group, price_value = mapped
                else:
                    mapped2 = availability_map.get(a)
                    if mapped2:
                        price_group, price_value = mapped2
                    else:
                        price_group, price_value = ('MID-RANGE', 3)

                # Provide a readable typical price string based on group (if none was explicit)
                if price_group == 'ULTRA-LUXURY':
                    price_str = '>$50,000 per carat'
                elif price_group == 'SUPER-PREMIUM':
                    price_str = '$10,000 - $50,000 per carat'
                elif price_group == 'PREMIUM':
                    price_str = '$1,000 - $10,000 per carat'
                elif price_group == 'HIGH-END':
                    price_str = '$500 - $3,000 per carat'
                elif price_group == 'MID-RANGE':
                    price_str = '$100 - $500 per carat'
                elif price_group == 'AFFORDABLE':
                    price_str = '$50 - $200 per carat'
                else:
                    price_str = '$5 - $50 per carat'

            gems_list.append({
                'name': name,
                'price_str': price_str,
                'price_group': price_group,
                'price_value': price_value,
                'mineral_group': gem_to_group.get(name, '')
            })

        # Walk through types_raw and add all gems
        # Handle new nested structure: "Gemstones by Mineral Group" -> mineral groups -> gem lists
        if isinstance(types, dict):
            # Check if new structure with "Gemstones by Mineral Group"
            if "Gemstones by Mineral Group" in types:
                mineral_groups = types["Gemstones by Mineral Group"]
                # mineral_groups may be a dict of group->list or a list of {group: list}
                if isinstance(mineral_groups, dict):
                    iter_groups = mineral_groups.items()
                elif isinstance(mineral_groups, list):
                    def iter_list_groups(lst):
                        for el in lst:
                            if isinstance(el, dict):
                                for k, v in el.items():
                                    yield (k, v)
                    iter_groups = iter_list_groups(mineral_groups)
                else:
                    iter_groups = []
                for group_name, gems in iter_groups:
                    if isinstance(gems, list):
                        for gem in gems:
                            if isinstance(gem, str):
                                add_gem(gem)
            else:
                # Old flat structure
                for section, items in types.items():
                    if not isinstance(items, list):
                        continue
                    for entry in items:
                        if isinstance(entry, str):
                            add_gem(entry)
                        elif isinstance(entry, dict):
                            for grp, gems in entry.items():
                                if isinstance(gems, list):
                                    for g in gems:
                                        add_gem(g)
                                elif isinstance(gems, str):
                                    add_gem(gems)

        # Sort by price_value descending then by name
        gems_list.sort(key=lambda x: (-x.get('price_value',2), x.get('name','').lower()))

        # Group into categories
        categories = {}
        for g in gems_list:
            categories.setdefault(g['price_group'], []).append(g)

        ordered = []
        for cat in category_order:
            if cat in categories:
                ordered.append({'name': cat, 'gems': categories[cat]})

        page_data = {
            'title': 'Gems by Price',
            'description': 'Gemstone types grouped by typical price (heuristic or explicit)',
            'categories': ordered,
            'search_base_url': 'https://www.gemrockauctions.com/search?query='
        }

        return render_template('gems/by_price.html', **page_data)

    except Exception as e:
        logger.error(f"Error in by_price route: {e}")
        return render_template('gems/index.html', title='Gems by Price', description='Error loading price data')

@bp.route('/by-colors')
def by_colors():
    """Gems by colors page - loads color data from Web API only."""
    try:
        # Load color data from API only
        # v2 API uses PascalCase: GemTypeName
        colors_raw = {}
        gems_api = get_gems_from_api() or []
        for g in gems_api:
            name = g.get('GemTypeName')
            # API key may provide colors as 'Colours' or 'colors' (list/dict)
            c = g.get('Colours') or g.get('colors')
            if not name or not c:
                continue
            # If API provides a simple list of strings, convert to expected format
            if isinstance(c, list):
                # convert to list of dicts with basic fields
                entries = []
                for col in c:
                    if isinstance(col, str):
                        entries.append({'color': col, 'hex': None, 'rarity': '', 'description': ''})
                    elif isinstance(col, dict):
                        entries.append(col)
                colors_raw[name] = {'color_range': entries, 'color_primary': entries[0]['color'] if entries else None}
            elif isinstance(c, dict):
                colors_raw[name] = c

        # Normalize colors: build mapping gem_name -> list of {color, hex, rarity, description}
        # and collect primary colors (color_primary) for the top palette
        gem_colors = {}
        primary_colors = {}
        if isinstance(colors_raw, dict):
            for gem_name, props in colors_raw.items():
                try:
                    color_list = []
                    primary = None
                    if isinstance(props, dict):
                        primary = props.get('color_primary')
                        cr = props.get('color_range') or []
                        if isinstance(cr, list):
                            for entry in cr:
                                if not isinstance(entry, dict):
                                    continue
                                cname = entry.get('color')
                                chex = entry.get('hex')
                                rrar = entry.get('rarity') or entry.get('color_rarity') or ''
                                desc = entry.get('description') or ''
                                if cname:
                                    color_list.append({'color': cname, 'hex': chex or '#CCCCCC', 'rarity': rrar, 'description': desc})
                                    # if this is the primary color, record its hex for palette
                                    if primary and cname == primary and primary not in primary_colors:
                                        primary_colors[primary] = chex or '#CCCCCC'

                        # if primary declared but not matched above, try to find its hex in color_list
                        if primary and primary not in primary_colors:
                            found = next((c for c in color_list if c['color'] == primary), None)
                            primary_colors[primary] = found['hex'] if found else '#CCCCCC'

                    if color_list:
                        gem_colors[gem_name] = color_list
                except Exception as e:
                    logger.warning(f"Error parsing colors for {gem_name}: {e}")

        # Load gem types to build master gem list while preserving mineral group mapping
        types_raw = load_gem_types()
        gem_to_group = {}
        gems_master = []
        try:
            # Handle new nested structure: "Gemstones by Mineral Group" -> mineral groups -> gem lists
            if isinstance(types_raw, dict):
                if "Gemstones by Mineral Group" in types_raw:
                    mineral_groups = types_raw["Gemstones by Mineral Group"]
                    if isinstance(mineral_groups, dict):
                        for group_name, gems in mineral_groups.items():
                            if isinstance(gems, list):
                                for gem in gems:
                                    if isinstance(gem, str):
                                        gems_master.append({'name': gem, 'mineral_group': group_name})
                                        gem_to_group[gem] = group_name
                else:
                    # Old flat structure
                    for key, val in types_raw.items():
                        if not isinstance(val, list):
                            continue
                        for entry in val:
                            if isinstance(entry, str):
                                name = entry
                                gems_master.append({'name': name, 'mineral_group': key})
                                gem_to_group[name] = key
                            elif isinstance(entry, dict):
                                for group_name, items in entry.items():
                                    if isinstance(items, list):
                                        for g in items:
                                            gems_master.append({'name': g, 'mineral_group': group_name})
                                            gem_to_group[g] = group_name
                                    elif isinstance(items, str):
                                        gems_master.append({'name': items, 'mineral_group': group_name})
                                        gem_to_group[items] = group_name
        except Exception as e:
            logger.warning(f"Error mapping gem types for colors page: {e}")

        # Attach colors to each gem from gem_colors mapping (if available)
        for gem in gems_master:
            cname = gem.get('name')
            gem['colors'] = gem_colors.get(cname, [])

        # Prepare palette from primary colors sorted alphabetically
        palette = []
        try:
            for c, h in primary_colors.items():
                palette.append({'color': c, 'hex': h})
            palette = sorted(palette, key=lambda x: x['color'].lower())
        except Exception:
            # Fallback: empty palette
            palette = []

        page_data = {
            'title': 'Gems by Colors',
            'description': 'Browse gems by their common colors. Click a color swatch to filter the list below.',
            'palette': palette,
            'gems': gems_master,
            'search_base_url': 'https://www.gemrockauctions.com/search?query='
        }

        return render_template('gems/by_colors.html', **page_data)

    except Exception as e:
        logger.error(f"Error in by_colors route: {e}")
        return render_template('gems/index.html', title='Gems by Colors', description='Error loading colors data')


@bp.route('/by-investment')
def by_investment():
    """Gems by investment appropriateness - loads data from Web API only."""
    try:
        # Load investment data from API only
        # v2 API uses PascalCase: GemTypeName, InvestmentAppropriatenessLevel, InvestmentAppropriatenessDescription
        entries = {}
        gems_api = get_gems_from_api() or []
        for g in gems_api:
            name = g.get('GemTypeName')
            if not name:
                continue
            entries[name] = {
                'investment_appropriateness': g.get('InvestmentAppropriatenessLevel') or '',
                'investment_description': g.get('InvestmentAppropriatenessDescription') or ''
            }

        # Load gem types for hover mineral group
        types_raw = load_gem_types()
        gem_to_group = {}
        try:
            # Handle new nested structure: "Gemstones by Mineral Group" -> mineral groups -> gem lists
            if isinstance(types_raw, dict):
                if "Gemstones by Mineral Group" in types_raw:
                    mineral_groups = types_raw["Gemstones by Mineral Group"]
                    if isinstance(mineral_groups, dict):
                        for group_name, gems in mineral_groups.items():
                            if isinstance(gems, list):
                                for gem in gems:
                                    if isinstance(gem, str):
                                        gem_to_group[gem] = group_name
                else:
                    # Old flat structure
                    for key, val in types_raw.items():
                        if not isinstance(val, list):
                            continue
                        for entry in val:
                            if isinstance(entry, str):
                                gem_to_group[entry] = key
                            elif isinstance(entry, dict):
                                for group_name, gems in entry.items():
                                    if isinstance(gems, list):
                                        for g in gems:
                                            gem_to_group[g] = group_name
                                    elif isinstance(gems, str):
                                        gem_to_group[gems] = group_name
        except Exception as e:
            logger.warning(f"Error mapping gem groups for investment: {e}")

        # Build gems list with investment fields
        gems_list = []
        for gem_name, props in entries.items():
            try:
                # props may be dict or list
                if isinstance(props, list):
                    merged = {}
                    for p in props:
                        if isinstance(p, dict):
                            merged.update(p)
                    props = merged

                investment = (props.get('investment_appropriateness') or '').strip() if isinstance(props, dict) else ''
                investment_desc = (props.get('investment_description') or '').strip() if isinstance(props, dict) else ''

                gems_list.append({
                    'name': gem_name,
                    'investment': investment,
                    'investment_description': investment_desc,
                    'mineral_group': gem_to_group.get(gem_name, '')
                })
            except Exception as e:
                logger.warning(f"Error processing investment info for {gem_name}: {e}")

        # Group by investment appropriateness and order groups by priority
        categories = {}
        # Desired order: most-investment-worthy first
        order = [
            'Blue Chip Investment Gems',
            'Emerging Investment Gems',
            'Speculative Collector Gems',
            'Fashion/Trend Gems',
            'Jewelry Utility',
            'Non-Investment Gems'
        ]

        for gem in gems_list:
            cat = gem.get('investment') or 'Unknown Investment Appropriateness'
            categories.setdefault(cat, []).append(gem)

        ordered = []
        for cat in order:
            if cat in categories:
                categories[cat].sort(key=lambda x: x.get('name','').lower())
                ordered.append({'name': cat, 'gems': categories[cat]})

        # Add any other categories present
        for extra_cat, gems in categories.items():
            if extra_cat not in order:
                gems.sort(key=lambda x: x.get('name','').lower())
                ordered.append({'name': extra_cat, 'gems': gems})

        page_data = {
            'title': 'Gems by Investment Appropriateness',
            'description': 'Gemstone types grouped by investment appropriateness (from config)',
            'categories': ordered,
            'search_base_url': 'https://www.gemrockauctions.com/search?query='
        }

        return render_template('gems/by_investment.html', **page_data)

    except Exception as e:
        logger.error(f"Error in by_investment route: {e}")
        return render_template('gems/index.html', title='Gems by Investment Appropriateness', description='Error loading investment data')


@bp.route('/by-brilliance')
def by_brilliance():
    """Gems by brilliance level
    
    Shows gem types sorted by brilliance level (descending) based on refractive
    properties from config_gem_refraction.yaml.
    """
    try:
        # Load refraction/brilliance config
        refraction_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config_gem_refraction.yaml')
        refraction_data = {}
        if os.path.exists(refraction_path):
            with open(refraction_path, 'r', encoding='utf-8') as f:
                refraction_data = yaml.safe_load(f) or {}
        else:
            logger.warning(f"Refraction config file not found: {refraction_path}")
        
        # Load gem types for mineral group info
        types_raw = load_gem_types()
        gem_to_group = {}
        try:
            if isinstance(types_raw, dict):
                if "Gemstones by Mineral Group" in types_raw:
                    mineral_groups = types_raw["Gemstones by Mineral Group"]
                    if isinstance(mineral_groups, dict):
                        for group_name, gems in mineral_groups.items():
                            if isinstance(gems, list):
                                for gem in gems:
                                    if isinstance(gem, str):
                                        gem_to_group[gem] = group_name
        except Exception as e:
            logger.warning(f"Error mapping gem groups for brilliance: {e}")
        
        # Load investment rankings for the Investment Ranking column
        DB_PATH = os.path.join(os.getcwd(), 'gems_portfolio.db')
        investment_rankings = {}
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT gem_type_name, Investment_Ranking_Tier FROM gem_attributes")
            for row in cursor.fetchall():
                investment_rankings[row['gem_type_name']] = row['Investment_Ranking_Tier']
            conn.close()
        except Exception as e:
            log_db_exception(e, 'by_brilliance route - loading investment rankings')
        
        # Build categorized gem list with brilliance info
        brilliance_categories = refraction_data.get('brilliance_categories', {})
        
        # Define brilliance order (best to lowest)
        brilliance_order = {
            'exceptional_brilliance': 5,
            'outstanding_brilliance': 4,
            'excellent_brilliance': 3,
            'good_brilliance': 2,
            'subtle_brilliance': 1
        }
        
        categories_list = []
        for category_key, category_data in brilliance_categories.items():
            if not isinstance(category_data, dict):
                continue
            
            category_name = category_data.get('description', category_key)
            gemstones = category_data.get('gemstones', [])
            brilliance_level = brilliance_order.get(category_key, 0)
            
            gems_in_category = []
            for gem_data in gemstones:
                if not isinstance(gem_data, dict):
                    continue
                
                gem_name = gem_data.get('name', '')
                if not gem_name:
                    continue
                
                ri_range = gem_data.get('ri_range', 'N/A')
                
                gems_in_category.append({
                    'name': gem_name,
                    'ri_range': ri_range,
                    'mineral_group': gem_to_group.get(gem_name, ''),
                    'investment_ranking': investment_rankings.get(gem_name, 'Not Assessed')
                })
            
            # Sort gems within category by name
            gems_in_category.sort(key=lambda x: x['name'].lower())
            
            categories_list.append({
                'name': category_name,
                'order': brilliance_level,
                'gems': gems_in_category
            })
        
        # Sort categories by brilliance order (descending)
        categories_list.sort(key=lambda x: -x['order'])
        
        page_data = {
            'title': 'Gems by Brilliance',
            'description': 'Gemstone types grouped by brilliance level based on refractive index and optical properties',
            'categories': categories_list
        }
        
        return render_template('gems/by_brilliance.html', **page_data)
    
    except Exception as e:
        logger.error(f"Error in by_brilliance route: {e}")
        return render_template('gems/index.html', title='Gems by Brilliance', description='Error loading brilliance data')


@bp.route('/gem/<gem_slug>')
def gem_profile(gem_slug):
    """Render a profile page for a single gem type identified by slug.

    Slug format: lowercase, spaces replaced with underscores.
    """
    try:
        # Normalize mapping from config to find canonical gem name
        types_raw = load_gem_types() or {}
        
        # Check if gem data is available
        if not types_raw:
            error_msg = "Gem data is temporarily unavailable. The API connection may be down. Please try again later."
            logger.error(f"Gem types data is empty for slug '{gem_slug}' - API may be unavailable")
            return render_template('500.html', 
                error_message=error_msg,
                error_details="Unable to load gem types from API. This is a temporary issue."), 503
        
        normalized_to_name = {}
        gem_to_group = {}
        
        # Handle new nested structure: "Gemstones by Mineral Group" -> "Carbon/Beryl Group/etc" -> list or dict
        if "Gemstones by Mineral Group" in types_raw:
            mineral_groups = types_raw["Gemstones by Mineral Group"]
            # diamond: groups may be a dict of group->list or a list of {group: list}
            if isinstance(mineral_groups, dict):
                iter_groups = mineral_groups.items()
            elif isinstance(mineral_groups, list):
                def iter_list_groups(l):
                    for el in l:
                        if isinstance(el, dict):
                            for k, v in el.items():
                                yield (k, v)
                iter_groups = iter_list_groups(mineral_groups)
            else:
                iter_groups = []

            for group_name, gems in iter_groups:
                if isinstance(gems, list):
                    for gem in gems:
                        if not isinstance(gem, str):
                            continue
                        name = str(gem).strip()
                        # add both underscore and dash style slugs
                        key_us = name.lower().replace(' ', '_')
                        key_dash = name.lower().replace(' ', '-')
                        normalized_to_name[key_us] = name
                        normalized_to_name[key_dash] = name
                        gem_to_group[name] = group_name
        else:
            # Fallback to old flat structure parsing
            for section, items in (types_raw.items() if isinstance(types_raw, dict) else []):
                if not isinstance(items, list):
                    continue
                for entry in items:
                    if isinstance(entry, str):
                        name = str(entry).strip()
                        key_us = name.lower().replace(' ', '_')
                        key_dash = name.lower().replace(' ', '-')
                        normalized_to_name[key_us] = name
                        normalized_to_name[key_dash] = name
                        gem_to_group[name] = section
                    elif isinstance(entry, dict):
                        for grp, glist in entry.items():
                            if isinstance(glist, list):
                                for g in glist:
                                    name = str(g).strip()
                                    key_us = name.lower().replace(' ', '_')
                                    key_dash = name.lower().replace(' ', '-')
                                    normalized_to_name[key_us] = name
                                    normalized_to_name[key_dash] = name
                                    gem_to_group[name] = grp
                            elif isinstance(glist, str):
                                name = str(glist).strip()
                                key_us = name.lower().replace(' ', '_')
                                key_dash = name.lower().replace(' ', '-')
                                normalized_to_name[key_us] = name
                                normalized_to_name[key_dash] = name
                                gem_to_group[name] = grp

        gem_name = normalized_to_name.get(gem_slug)
        if not gem_name:
            # Try alternative key forms (dashes/underscores) and more aggressive matching
            alt_us = gem_slug.replace('-', '_')
            alt_dash = gem_slug.replace('_', '-')
            gem_name = normalized_to_name.get(alt_us) or normalized_to_name.get(alt_dash)
        if not gem_name:
            candidate = gem_slug.replace('_', ' ').replace('-', ' ')
            for k, v in normalized_to_name.items():
                # also compare normalized keys replacing separators with spaces for broader match
                k_comp = k.replace('_', ' ').replace('-', ' ')
                if k_comp.startswith(candidate) or candidate.startswith(k_comp):
                    gem_name = v
                    break

        if not gem_name:
            logger.warning(f"Gem not found for slug: {gem_slug}. Available gems: {len(normalized_to_name)}")
            error_msg = f"The gem '{gem_slug}' was not found in our database."
            error_details = "Please check the URL spelling or browse our gem catalog to find what you're looking for."
            return render_template('404.html', 
                error_message=error_msg,
                error_details=error_details), 404

        # Load all metadata from API only
        # v2 API uses PascalCase field names
        size_str = ''
        price_str = ''
        api_colors_list = []
        rarity_props = {}
        hardness_str = ''
        hardness_val = None

        gems_api = get_gems_from_api() or []
        api_props = None
        for g in gems_api:
            if str(g.get('GemTypeName')).strip().lower() == str(gem_name).strip().lower():
                api_props = g
                break

        if api_props:
            # Map API keys to the code's expected fields (using PascalCase from v2 API)
            rarity_props = {
                'rarity': api_props.get('RarityLevel') or '',
                'rarity_description': api_props.get('RarityDescription') or '',
                'availability': api_props.get('AvailabilityLevel') or '',
                'availability_driver': api_props.get('AvailabilityDriver') or '',
                'availability_description': api_props.get('AvailabilityDescription') or '',
                'investment_appropriateness': api_props.get('InvestmentAppropriatenessLevel') or '',
                'investment_description': api_props.get('InvestmentAppropriatenessDescription') or '',
            }
            size_str = api_props.get('TypicalSize') or ''
            price_str = api_props.get('PriceRange') or ''
            hardness_str = api_props.get('HardnessRange') or ''
            hardness_val = api_props.get('HardnessLevel')
            if hardness_val is None and hardness_str:
                hardness_val = get_hardness_value(hardness_str)

            # Colors
            api_colors = api_props.get('Colours') or api_props.get('colors')
            if api_colors:
                color_list = []
                if isinstance(api_colors, list):
                    for c in api_colors:
                        if isinstance(c, str):
                            color_list.append({'color': c, 'hex': None, 'rarity': '', 'description': ''})
                        elif isinstance(c, dict):
                            color_list.append(c)
                elif isinstance(api_colors, dict):
                    for k, v in api_colors.items():
                        if isinstance(v, str):
                            color_list.append({'color': k, 'hex': None, 'rarity': '', 'description': v})
                        elif isinstance(v, dict):
                            color_list.append(v)
                api_colors_list = color_list

        # Compute composite score using same mapping as investments route
        rarity_points = {
            'Singular Occurrence': 100,
            'Unique Geological': 85,
            'Limited Occurrence': 65,
            'Abundant Minerals': 35,
            'Unknown': 0,
            '': 0
        }
        availability_points = {
            'Museum Grade Rarity': 100,
            'Collectors Market': 85,
            'Limited Supply': 65,
            'Readily Available': 35,
            'Consistently Available': 10,
            '': 0
        }
        invest_appr_points = {
            'Blue Chip Investment Gems': 100,
            'Emerging Investment Gems': 75,
            'Speculative Collector Gems': 50,
            'Fashion/Trend Gems': 25,
            'Non-Investment Gems': 5,
            '': 0
        }
        hardness_points_map = {
            'Extremely Hard (10)': 100,
            'Very Hard (8.5-9.9)': 85,
            'Hard-2 (8.0-8.49)': 65,
            'Hard-1 (7.5-7.99)': 45,
            'Medium-2 (7.0-7.49)': 25,
            'Medium-1 (6-6.99)': 10,
            'Soft (3-5.99)': 5,
            'Very Soft (1-2.99)': 0,
            'Unknown': 0
        }
        price_group_points = {
            'ULTRA-LUXURY': 100,
            'SUPER-PREMIUM': 85,
            'PREMIUM': 65,
            'HIGH-END': 45,
            'MID-RANGE': 25,
            'AFFORDABLE': 10,
            'BUDGET-FRIENDLY': 5,
        }

        import re
        def _extract_numbers(s):
            nums = re.findall(r"[\d,]+", s)
            vals = []
            for n in nums:
                try:
                    vals.append(float(n.replace(',', '')))
                except Exception:
                    continue
            return vals
        def _infer_price_group(price_str_local):
            if not price_str_local:
                return 'MID-RANGE'
            nums = _extract_numbers(price_str_local)
            if '>' in price_str_local and nums:
                lb = nums[0]
                if lb >= 50000:
                    return 'ULTRA-LUXURY'
                if lb >= 10000:
                    return 'SUPER-PREMIUM'
                if lb >= 1000:
                    return 'PREMIUM'
                if lb >= 500:
                    return 'HIGH-END'
                if lb >= 100:
                    return 'MID-RANGE'
                if lb >= 50:
                    return 'AFFORDABLE'
                return 'BUDGET-FRIENDLY'
            if nums:
                maxv = max(nums)
                if maxv >= 50000:
                    return 'ULTRA-LUXURY'
                if maxv >= 10000:
                    return 'SUPER-PREMIUM'
                if maxv >= 1000:
                    return 'PREMIUM'
                if maxv >= 500:
                    return 'HIGH-END'
                if maxv >= 100:
                    return 'MID-RANGE'
                if maxv >= 50:
                    return 'AFFORDABLE'
                return 'BUDGET-FRIENDLY'
            s = (price_str_local or '').lower()
            if 'ultra' in s or 'exceed' in s:
                return 'ULTRA-LUXURY'
            if 'premium' in s or 'luxury' in s:
                return 'SUPER-PREMIUM'
            return 'MID-RANGE'

        rarity_label = str(rarity_props.get('rarity') or '').strip()
        availability_label = str(rarity_props.get('availability') or '').strip()
        invest_label = str(rarity_props.get('investment_appropriateness') or '').strip()

        gp = rarity_points.get(rarity_label, 0)
        ap = availability_points.get(availability_label, 0)
        ip = invest_appr_points.get(invest_label, 0)
        hard_cat = categorize_by_hardness(hardness_val)
        hp = hardness_points_map.get(hard_cat, 0)
        price_group = _infer_price_group(price_str)
        pp = price_group_points.get(price_group, 25)

        composite = (gp * 0.25) + (ap * 0.25) + (ip * 0.25) + (hp * 0.125) + (pp * 0.125)

        # Map composite score to ranking tier (same rules as investment rankings)
        def score_to_tier_local(s):
            try:
                s = float(s)
            except Exception:
                return 'UNKNOWN'
            if s >= 80:
                return 'VERY BULLISH'
            if s >= 70:
                return 'BULLISH'
            if s >= 50:
                return 'MODERATELY BULLISH'
            if s >= 45:
                return 'NEUTRAL'
            if s >= 30:
                return 'BEARISH'
            return 'VERY BEARISH'

        tier_label = score_to_tier_local(composite)
        # Map to simple color buckets per requirements: bullish=green, neutral=orange, bearish=red
        if tier_label in ('VERY BULLISH', 'BULLISH', 'MODERATELY BULLISH'):
            tier_color = 'green'
        elif tier_label == 'NEUTRAL':
            tier_color = 'orange'
        else:
            tier_color = 'red'

        # gem_type_id from API
        gem_type_id = api_props.get('GemTypeId') if api_props else None

        # Fetch pricing data from the pricing page API
        pricing_data = {}
        if gem_type_id:
            try:
                base = current_app.config.get('GEMDB_API_URL', 'https://api.preciousstone.info')
                token = load_api_key() or ''
                pricing_url = f"{base.rstrip('/')}/api/v2/gem-pricing-page/{gem_type_id}"
                headers = {'X-API-Key': token} if token else {}
                pricing_resp = requests.get(pricing_url, headers=headers, timeout=5)
                if pricing_resp.status_code == 200:
                    pricing_data = pricing_resp.json() or {}
                    current_app.logger.info(f"Pricing data for gem {gem_type_id}: {pricing_data}")
                else:
                    current_app.logger.warning(f"Pricing API returned {pricing_resp.status_code} for gem {gem_type_id}")
            except Exception as pe:
                current_app.logger.warning(f"Error fetching pricing data for gem {gem_type_id}: {pe}")
        else:
            current_app.logger.warning(f"No gem_type_id found for gem {gem_name}")

        # Fetch related gems pricing (same mineral group)
        related_gems = []
        if gem_type_id:
            try:
                base = current_app.config.get('GEMDB_API_URL', 'https://api.preciousstone.info')
                token = load_api_key() or ''
                related_url = f"{base.rstrip('/')}/api/v2/related-gems-pricing/{gem_type_id}"
                headers = {'X-API-Key': token} if token else {}
                related_resp = requests.get(related_url, headers=headers, timeout=5)
                if related_resp.status_code == 200:
                    related_gems = related_resp.json() or []
            except Exception as re:
                current_app.logger.warning(f"Error fetching related gems for {gem_type_id}: {re}")

        # Determine if user is authenticated. Prefer the module-level current_user
        # (which tests may monkeypatch), and fall back to the flask_login proxy.
        def _is_user_authenticated():
            try:
                import sys
                # Check multiple module names where the route code might be imported
                candidates = [__name__, 'gems.routes.gems', 'routes.gems']
                for modname in candidates:
                    mod = sys.modules.get(modname)
                    if mod is None:
                        continue
                    try:
                        if hasattr(mod, 'current_user'):
                            cu = getattr(mod, 'current_user')
                            if cu is None:
                                continue
                            # If it's a flask_login proxy, we still accept it; otherwise prefer patched objects
                            try:
                                is_flask_proxy = cu.__class__.__module__.startswith('flask_login')
                            except Exception:
                                is_flask_proxy = False
                            # If this is a patched module-level current_user (not a flask_login proxy), return its value explicitly
                            if not is_flask_proxy:
                                return bool(getattr(cu, 'is_authenticated', False))
                            # If it's a flask_login proxy, we'll evaluate it after checking all modules
                            # but if it's authenticated True return True now
                            if bool(getattr(cu, 'is_authenticated', False)):
                                return True
                    except Exception:
                        continue
            except Exception:
                pass
            try:
                from flask_login import current_user as flask_current_user
                # If flask_login proxy indicates authenticated, honor it
                if getattr(flask_current_user, 'is_authenticated', False):
                    return True
            except Exception:
                pass
            # If we reach here: no authenticated user found - do not show listings
            return False

        # Fetch user holdings if authenticated
        user_holdings = []
        if _is_user_authenticated():
            try:
                user_id = getattr(current_user, 'id', None)
                if user_id:
                    user_holdings = get_user_holdings(user_id, gem_name)
            except Exception as e:
                logger.warning(f"Error fetching user holdings: {e}")
        
        page_data = {
            'title': gem_name,
            'gem_name': gem_name,
            'mineral_group': gem_to_group.get(gem_name, ''),
            'hardness_str': hardness_str,
            'hardness_val': hardness_val,
            'typical_size': size_str,
            'typical_price': price_str,
            'rarity_label': rarity_label,
            'rarity_description': str(rarity_props.get('rarity_description') or ''),
            'availability_label': availability_label,
            'availability_driver': str(rarity_props.get('availability_driver') or ''),
            'availability_description': str(rarity_props.get('availability_description') or ''),
            'investment_label': invest_label,
            'investment_description': str(rarity_props.get('investment_description') or ''),
            'colors': api_colors_list or [],
            'price_group': price_group,
            'composite': round(composite, 2),
            'tier': tier_label,
            'tier_color': tier_color,
            'composite_components': {
                'geological_rarity': gp,
                'market_availability': ap,
                'investment_appropriateness': ip,
                'hardness': hp,
                'price': pp
            },
            'gem_type_id': gem_type_id,
            'pricing': pricing_data,
            'related_gems': related_gems,
            'user_holdings': user_holdings
        }

        # Determine whether we show listings (available to signed-in users)
        show_listings = _is_user_authenticated()

        # Server-side fetch of current listings (call upstream API from Python side so browser doesn't need API token)
        try:
            listings = []
            base = current_app.config.get('GEMDB_API_URL', 'https://api.preciousstone.info')
            token = load_api_key() or ''
            url = f"{base.rstrip('/')}/api/v2/listings-view/filtered"
            params = {}
            # Allow server-side control to avoid accidentally fetching too many listings
            max_results = current_app.config.get('GEMDB_MAX_RESULTS') or 500
            # The listings-view/filtered endpoint now accepts `limit` per requirements; keep support for 'max_results' in server config
            params['limit'] = max_results
            if gem_type_id:
                params['gem_type_id'] = gem_type_id
            else:
                params['gem'] = gem_name
            # include google id if user is logged in and has google_id on profile
            gid = None
            try:
                if getattr(current_user, 'is_authenticated', False):
                    gid = getattr(current_user, 'google_id', None)
            except Exception:
                gid = None
            if gid:
                params['google_user_id'] = gid
            headers = {}
            if token:
                headers['X-API-Key'] = token
            try:
                r = requests.get(url, params=params, headers=headers, timeout=6)
                if r.status_code == 200:
                    payload = r.json()
                    if isinstance(payload, dict) and 'items' in payload and isinstance(payload['items'], list):
                        listings = payload['items']
                    elif isinstance(payload, list):
                        listings = payload
                else:
                    current_app.logger.warning('Listings upstream returned %s: %s', r.status_code, r.text[:200])
            except Exception as e:
                current_app.logger.warning('Error fetching listings from upstream: %s', e)

            # Normalize listing fields - handle PascalCase from Azure SQL API
            normed = []
            for it in (listings or []):
                try:
                    # Map PascalCase to snake_case for template compatibility
                    if 'listing_id' not in it:
                        it['listing_id'] = it.get('ListingId') or it.get('id') or ''
                    if 'carat_weight' not in it:
                        it['carat_weight'] = it.get('Weight') or it.get('weight') or ''
                    if 'title' not in it:
                        it['title'] = it.get('ListingTitle') or it.get('listing_title') or ''
                    if 'seller' not in it:
                        it['seller'] = it.get('SellerNickname') or it.get('seller_nickname') or ''
                    if 'price' not in it:
                        it['price'] = it.get('Price') or ''
                    it.setdefault('seller_url', '')
                    it.setdefault('title_url', '')
                    # Synthesize URLs if missing
                    try:
                        def _slugify(v: str) -> str:
                            if not v:
                                return ''
                            s = str(v).strip().lower()
                            s = re.sub(r"[^\w\s-]", '', s, flags=re.U)
                            s = s.replace('_', ' ')
                            s = re.sub(r"[\s-]+", '-', s.strip())
                            return s
                        lid = it.get('listing_id')
                        if lid:
                            if it.get('title'):
                                it['title_url'] = f"https://www.gemrockauctions.com/products/{_slugify(it.get('title'))}-{lid}"
                            if it.get('seller'):
                                it['seller_url'] = f"https://www.gemrockauctions.com/stores/{_slugify(it.get('seller'))}"
                    except Exception:
                        pass
                    # Format price if numeric
                    try:
                        pv = it.get('price') or it.get('Price')
                        if isinstance(pv, (int, float)):
                            it['price'] = f"${pv:,.2f}"
                        elif isinstance(pv, str) and re.match(r"^\s*\d+(?:[.,]\d+)?\s*$", pv):
                            it['price'] = f"${float(pv.replace(',', '')):,.2f}"
                    except Exception:
                        pass
                    normed.append(it)
                except Exception:
                    continue
            page_data['current_listings'] = normed
            try:
                current_app.logger.debug('Server-side filtered listings count: %s', len(normed))
            except Exception:
                pass
        except Exception:
            # ignore listing fetch errors and continue rendering page without server-side listings
            page_data['current_listings'] = []

        # Expose whether listings are visible to the template
        page_data['show_listings'] = show_listings

        # Only show listings if user is authenticated
        if not show_listings:
            page_data['current_listings'] = []
        # finalize page rendering
        return render_template('gems/gem_profile.html', **page_data)
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Error rendering gem profile for {gem_slug}: {e}\n{error_traceback}")
        error_msg = f"An error occurred while loading the gem profile for '{gem_slug}'."
        error_details = f"Error type: {type(e).__name__}: {str(e)}. Please try again later or contact support if the problem persists."
        return render_template('500.html', 
            error_message=error_msg,
            error_details=error_details), 500
