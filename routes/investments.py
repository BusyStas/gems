"""
Investment routes for Gems Hub
"""

from flask import Blueprint, render_template, url_for
import os
import yaml
import logging

# Import helpers from gems routes
from routes.gems import load_gem_types, load_gem_hardness, get_hardness_value, categorize_by_hardness

bp = Blueprint('investments', __name__, url_prefix='/investments')

# Configure logging
logger = logging.getLogger(__name__)

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
                            rarity_data[str(gem_name).strip()] = {
                                'rarity': str(props.get('rarity') or '').strip(),
                                'availability': str(props.get('availability') or '').strip(),
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
            g['tier'] = score_to_tier(g['composite'])

        gems.sort(key=lambda x: x['composite'], reverse=True)

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
