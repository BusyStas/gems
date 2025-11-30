"""
Jewelry routes for Gems Hub
"""

from flask import Blueprint, render_template, abort
from utils.api_client import get_jewelry_service_types, get_jewelry_service_firms
import logging

bp = Blueprint('jewelry', __name__, url_prefix='/jewelry')

logger = logging.getLogger(__name__)

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


@bp.route('/customized')
def customized():
    page_data = {
        'title': 'Customized Jewelry',
        'description': 'Bespoke jewelry design services and customization options',
        'services': [
            {'name': 'Custom Engagement Rings', 'description': 'Design your perfect ring from scratch'},
            {'name': 'Remounting', 'description': 'Update older pieces into modern settings'},
            {'name': 'Design Consultation', 'description': 'Work with our designers to create unique pieces'}
        ]
    }
    return render_template('jewelry/customized.html', **page_data)


@bp.route('/shops')
def shops():
    page_data = {
        'title': 'Shops',
        'description': 'Recommended shops for custom and ready-made jewelry',
        'shops': [
            {'name': 'Local Jewelers', 'description': 'Trusted local artisans and jewelers'},
            {'name': 'Online Bespoke Services', 'description': 'Design services and marketplaces'},
        ]
    }
    return render_template('jewelry/shops.html', **page_data)


@bp.route('/services')
def services():
    """Jewelry services overview page - lists all service types from API"""
    service_types = get_jewelry_service_types()
    page_data = {
        'title': 'Jewelry Services',
        'description': 'Find professional jewelry services including CAD design, casting, stone setting, and more',
        'intro': 'Discover trusted professionals for all your jewelry service needs.',
        'service_types': service_types
    }
    return render_template('jewelry/services.html', **page_data)


@bp.route('/services/<int:service_type_id>')
def service_type(service_type_id):
    """Page showing firms for a specific jewelry service type"""
    # Get service types to find the name
    service_types = get_jewelry_service_types()
    service_type_info = None
    for st in service_types:
        if st.get('ServiceTypeId') == service_type_id:
            service_type_info = st
            break

    if not service_type_info:
        abort(404)

    # Get firms for this service type
    firms = get_jewelry_service_firms(service_type_id)

    page_data = {
        'title': service_type_info.get('ServiceTypeName', 'Service'),
        'description': f"Find trusted {service_type_info.get('ServiceTypeName', 'jewelry service')} providers",
        'service_type': service_type_info,
        'firms': firms
    }
    return render_template('jewelry/service_type.html', **page_data)
