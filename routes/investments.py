"""
Investment routes for Gems Hub
"""

from flask import Blueprint, render_template, url_for
import os
import yaml
import logging
import sqlite3

# Import helpers from gems routes
from routes.gems import load_gem_types, load_gem_hardness, get_hardness_value, categorize_by_hardness
from utils.db_logger import log_db_exception

bp = Blueprint('investments', __name__, url_prefix='/investments')

# Configure logging
logger = logging.getLogger(__name__)

# Database used by auth/profile; ensure we use the same DB path
DB_PATH = os.path.join(os.getcwd(), 'gems_portfolio.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@bp.route('/')
def index():
    """Investments main page"""
    page_data = {
        'title': 'Gem Investments',
        'description': 'Learn about investing in gems and gemstones',
        'intro': 'Gems have been a store of value for centuries. Learn how to invest wisely in precious stones.',
        'topics': [
            {
                'name': 'Market Trends',
                'description': 'Current market analysis and price trends for various gemstones',
                'icon': 'chart'
            },
            {
                'name': 'Value Assessment',
                'description': 'Understanding the 4Cs and how to evaluate gem quality',
                'icon': 'assessment'
            }
        ]
    }
    return render_template('investments/index.html', **page_data)

@bp.route('/market-trends')
def market_trends():
    """Market trends page"""
    page_data = {
        'title': 'Gem Market Trends',
        'description': 'Current trends and analysis in the gemstone market',
        'trends': [
            {
                'gem': 'Diamonds',
                'trend': 'Stable',
                'description': 'Lab-grown diamonds increasing market share'
            },
            {
                'gem': 'Colored Gemstones',
                'trend': 'Growing',
                'description': 'Increased demand for unique colored stones'
            },
            {
                'gem': 'Rare Gems',
                'trend': 'Strong',
                'description': 'Premium pricing for rare and exotic gemstones'
            }
        ]
    }
    return render_template('investments/market_trends.html', **page_data)

@bp.route('/value-assessment')
def value_assessment():
    """Value assessment page"""
    page_data = {
        'title': 'Gem Value Assessment',
        'description': 'How to assess and determine the value of gemstones',
        'criteria': [
            {
                'name': 'Color',
                'description': 'Hue, tone, and saturation affect value significantly'
            },
            {
                'name': 'Clarity',
                'description': 'Fewer inclusions generally mean higher value'
            },
            {
                'name': 'Cut',
                'description': 'Quality of cut affects brilliance and value'
            },
            {
                'name': 'Carat Weight',
                'description': 'Larger stones are rarer and more valuable'
            },
            {
                'name': 'Origin',
                'description': 'Provenance can significantly impact value'
            },
            {
                'name': 'Treatment',
                'description': 'Natural, untreated gems command premium prices'
            }
        ]
    }
    return render_template('investments/value_assessment.html', **page_data)


@bp.route('/investment-rankings')
def investment_rankings():
    """Compute composite investment ranking for all gem types and render table

    Uses weights and mappings defined in BusinessRequirements.txt. Reads:
    - config/config_gem_rarity.yaml (rarity, availability, investment_appropriateness)
    - config/config_gem_hardness.txt (hardness numeric values)
    - config/config_gem_pricerange.txt (typical price strings)
    """
    try:
        # Try to load persisted gem attributes from DB for performance.
        gems = []
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT gem_type_name AS name, Mineral_Group AS mineral_group, Investment_Ranking_Score AS composite, Investment_Ranking_Tier AS tier, Price_Range AS price_text, Hardness_Level AS hardness_val, Hardness_Range AS hardness_str, Rarity_Level AS rarity_label, Availability_Level AS availability_label, Investment_Appropriateness_Level AS investment_label FROM gem_attributes")
            rows = cur.fetchall()
            if rows and len(rows) > 0:
                for r in rows:
                    gems.append({
                        'name': r['name'],
                        'mineral_group': r['mineral_group'],
                        'composite': round(r['composite'] or 0, 2),
                        'tier': r['tier'] or 'UNKNOWN',
                        'price_text': r['price_text'] or '',
                        'hardness_val': r['hardness_val'],
                        'hardness_str': r['hardness_str'] or '',
                        'rarity_label': r['rarity_label'] or '',
                        'availability_label': r['availability_label'] or '',
                        'investment_label': r['investment_label'] or ''
                    })
                # Sort and return page using persisted data
                gems.sort(key=lambda x: x['composite'], reverse=True)
                page_data = {
                    'title': 'Investment Rankings',
                    'description': 'Composite investment rankings for gemstones (cached)',
                    'methodology': 'Composite score from Geological Rarity (25%), Market Availability (25%), Investment Appropriateness (25%), Hardness (12.5%), Price Range (12.5%)',
                    'gems': gems
                }
                try:
                    conn.close()
                except Exception:
                    pass
                return render_template('investments/investment_rankings.html', **page_data)
        except Exception as e:
            # If DB read fails, log and fall back to computing live
            log_db_exception(e, 'investment_rankings: selecting gem_attributes')
            try:
                conn.close()
            except Exception:
                pass

        # Load gem types
        types = load_gem_types() or {}

        # Load rarity/investment metadata
        rarity_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config_gem_rarity.yaml')
        rarity_data = {}
        if os.path.exists(rarity_path):
            try:
                with open(rarity_path, 'r', encoding='utf-8') as f:
                    raw = yaml.safe_load(f) or {}
                # Normalize entries into mapping gem->props
                if isinstance(raw, dict):
                    items = raw.items()
                elif isinstance(raw, list):
                    items = []
                    for el in raw:
                        if isinstance(el, dict):
                            for k, v in el.items():
                                items.append((k, v))
                else:
                    items = []

                for gem_name, props in items:
                    try:
                        if isinstance(props, list):
                            merged = {}
                            for p in props:
                                if isinstance(p, dict):
                                    merged.update(p)
                            props = merged
                        if isinstance(props, dict):
                            # preserve several optional descriptive fields if present
                            rarity_data[str(gem_name).strip()] = {
                                'rarity': str(props.get('rarity') or '').strip(),
                                'rarity_description': str(props.get('rarity_description') or props.get('description') or '').strip(),
                                'availability': str(props.get('availability') or '').strip(),
                                'availability_driver': str(props.get('availability_driver') or '').strip(),
                                'availability_description': str(props.get('availability_description') or '').strip(),
                                'investment_appropriateness': str(props.get('investment_appropriateness') or '').strip(),
                                'investment_description': str(props.get('investment_description') or '').strip()
                            }
                        else:
                            rarity_data[str(gem_name).strip()] = {'rarity': '', 'availability': '', 'investment_appropriateness': ''}
                    except Exception:
                        continue
            except Exception as e:
                logger.warning(f"Error loading rarity metadata: {e}")

        # Load hardness values
        hardness_map = load_gem_hardness() or {}

        # Load explicit price strings from txt
        price_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config_gem_pricerange.txt')
        explicit_prices = {}
        if os.path.exists(price_path):
            try:
                with open(price_path, 'r', encoding='utf-8') as f:
                    for raw_line in f:
                        line = raw_line.strip()
                        if not line or line.startswith('#'):
                            continue
                        key = None
                        val = None
                        if '=' in line:
                            key, val = line.split('=', 1)
                        elif ':' in line:
                            key, val = line.split(':', 1)
                        elif '\t' in line:
                            key, val = line.split('\t', 1)
                        else:
                            continue
                        key = key.strip()
                        val = val.strip()
                        if key:
                            explicit_prices[key] = val
            except Exception as e:
                logger.warning(f"Error reading price range config: {e}")

        # Scoring maps from requirements
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

        # Hardness category points
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

        # Price group points per requirements
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

        def _infer_price_group(price_str):
            if not price_str or not isinstance(price_str, str):
                return 'MID-RANGE'
            nums = _extract_numbers(price_str)
            if '>' in price_str and nums:
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
            s = price_str.lower()
            if 'ultra' in s or 'exceed' in s:
                return 'ULTRA-LUXURY'
            if 'premium' in s or 'luxury' in s:
                return 'SUPER-PREMIUM'
            if 'high' in s or 'valuable' in s:
                return 'HIGH-END'
            return 'MID-RANGE'

        # Build gem list
        gems = []
        def add_from_entry(name, group_name=''):
            name = str(name).strip()
            mg = group_name
            rprops = rarity_data.get(name, {})
            rarity_label = rprops.get('rarity','')
            availability_label = rprops.get('availability','')
            invest_label = rprops.get('investment_appropriateness','')

            # Points
            gp = rarity_points.get(rarity_label, 0)
            ap = availability_points.get(availability_label, 0)
            ip = invest_appr_points.get(invest_label, 0)

            # Hardness
            hard_str = hardness_map.get(name, '')
            hard_val = get_hardness_value(hard_str)
            hard_cat = categorize_by_hardness(hard_val)
            hp = hardness_points_map.get(hard_cat, 0)

            # Price group from explicit mapping if present
            price_text = explicit_prices.get(name, '')
            price_group = _infer_price_group(price_text) if price_text else 'MID-RANGE'
            pp = price_group_points.get(price_group, 25)

            composite = (gp * 0.25) + (ap * 0.25) + (ip * 0.25) + (hp * 0.125) + (pp * 0.125)

            gems.append({
                'name': name,
                'mineral_group': mg,
                'rarity_label': rarity_label,
                'availability_label': availability_label,
                'investment_label': invest_label,
                'hardness_val': hard_val,
                'hardness_str': hard_str,
                'hardness_cat': hard_cat,
                'price_text': price_text,
                'price_group': price_group,
                'composite': round(composite, 2)
            })

        # Walk through types to collect gems
        for section, items in (types.items() if isinstance(types, dict) else []):
            if not isinstance(items, list):
                continue
            for entry in items:
                if isinstance(entry, str):
                    add_from_entry(entry, section)
                elif isinstance(entry, dict):
                    for grp, glist in entry.items():
                        if isinstance(glist, list):
                            for g in glist:
                                add_from_entry(g, grp)
                        elif isinstance(glist, str):
                            add_from_entry(glist, grp)

        # Map composite score to ranking tiers
        def score_to_tier(s):
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

        for g in gems:
            tier_full = score_to_tier(g['composite'])
            # Keep and expose the full tier label as requested by requirements
            g['tier'] = tier_full

        gems.sort(key=lambda x: x['composite'], reverse=True)

        # Persist computed attributes into the SQLite table for performance
        # Create table if needed and upsert each gem's computed data
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS gem_attributes (
                    gem_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gem_type_name TEXT NOT NULL UNIQUE,
                    Mineral_Group TEXT,
                    Hardness_Level REAL,
                    Hardness_Range TEXT,
                    Price_Range TEXT,
                    Typical_Size TEXT,
                    Rarity_Level TEXT,
                    Rarity_Description TEXT,
                    Availability_Level TEXT,
                    Availability_Driver TEXT,
                    Availability_Description TEXT,
                    Investment_Appropriateness_Level TEXT,
                    Investment_Appropriateness_Description TEXT,
                    Investment_Ranking_Score REAL,
                    Investment_Ranking_Tier TEXT
                )
            ''')
            # Upsert each gem
            for g in gems:
                try:
                    cur.execute('''
                        INSERT INTO gem_attributes (
                            gem_type_name, Mineral_Group, Hardness_Level, Hardness_Range,
                            Price_Range, Typical_Size, Rarity_Level, Rarity_Description,
                            Availability_Level, Availability_Driver, Availability_Description,
                            Investment_Appropriateness_Level, Investment_Appropriateness_Description,
                            Investment_Ranking_Score, Investment_Ranking_Tier
                        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                        ON CONFLICT(gem_type_name) DO UPDATE SET
                            Mineral_Group=excluded.Mineral_Group,
                            Hardness_Level=excluded.Hardness_Level,
                            Hardness_Range=excluded.Hardness_Range,
                            Price_Range=excluded.Price_Range,
                            Typical_Size=excluded.Typical_Size,
                            Rarity_Level=excluded.Rarity_Level,
                            Rarity_Description=excluded.Rarity_Description,
                            Availability_Level=excluded.Availability_Level,
                            Availability_Driver=excluded.Availability_Driver,
                            Availability_Description=excluded.Availability_Description,
                            Investment_Appropriateness_Level=excluded.Investment_Appropriateness_Level,
                            Investment_Appropriateness_Description=excluded.Investment_Appropriateness_Description,
                            Investment_Ranking_Score=excluded.Investment_Ranking_Score,
                            Investment_Ranking_Tier=excluded.Investment_Ranking_Tier
                    ''', (
                        g.get('name'),
                        g.get('mineral_group'),
                        g.get('hardness_val'),
                        g.get('hardness_str'),
                        g.get('price_text'),
                        None,
                        g.get('rarity_label'),
                        rarity_data.get(g.get('name'), {}).get('rarity_description', ''),
                        g.get('availability_label'),
                        rarity_data.get(g.get('name'), {}).get('availability_driver', ''),
                        rarity_data.get(g.get('name'), {}).get('availability_description', ''),
                        g.get('investment_label'),
                        rarity_data.get(g.get('name'), {}).get('investment_description', ''),
                        g.get('composite'),
                        g.get('tier')
                    ))
                except Exception as e:
                    # best-effort: do not fail the whole page if DB write fails
                    log_db_exception(e, f"investment_rankings: upsert gem_attributes for {g.get('name')}")
                    logger.debug(f"Failed to upsert gem_attributes for {g.get('name')}")
            conn.commit()
        except Exception as e:
            log_db_exception(e, 'investment_rankings: creating/upserting gem_attributes')
            logger.exception('Failed to persist gem attributes to DB')
        finally:
            try:
                conn.close()
            except Exception:
                pass

        page_data = {
            'title': 'Investment Rankings',
            'description': 'Composite investment rankings for gemstones',
            'methodology': 'Composite score from Geological Rarity (25%), Market Availability (25%), Investment Appropriateness (25%), Hardness (12.5%), Price Range (12.5%)',
            'gems': gems
        }

        return render_template('investments/investment_rankings.html', **page_data)

    except Exception as e:
        logger.error(f"Error building investment rankings: {e}")
        return render_template('investments/index.html', title='Investment Rankings', description='Error computing rankings')
