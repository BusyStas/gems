"""
Investment routes for Gems Hub
"""

from flask import Blueprint, render_template

bp = Blueprint('investments', __name__, url_prefix='/investments')

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
