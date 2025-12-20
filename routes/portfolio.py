"""
Portfolio routes - User's gem portfolio management
Uses Azure SQL via gemdb API for data storage.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import requests
import logging
from utils.api_client import load_api_key
from utils.db_logger import log_db_exception

bp = Blueprint('portfolio', __name__, url_prefix='/portfolio')
logger = logging.getLogger(__name__)


class BypassUser:
    """Mock user for local development when bypass_google_user_id is set"""
    def __init__(self, google_id):
        self.google_id = google_id
        self.is_authenticated = True


def load_current_user():
    """Load current user from Flask-Login, or use bypass ID for local dev"""
    try:
        from flask_login import current_user
        if getattr(current_user, 'is_authenticated', False):
            return current_user
    except Exception:
        pass

    # For local development: use bypass_google_user_id if configured
    bypass_id = current_app.config.get('BYPASS_GOOGLE_USER_ID')
    if bypass_id:
        return BypassUser(bypass_id)

    return None


def get_api_base():
    """Get API base URL from config"""
    return current_app.config.get('GEMDB_API_URL', 'https://api.preciousstone.info')


def get_api_headers():
    """Get API headers with auth token"""
    token = load_api_key() or ''
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['X-API-Key'] = token
    return headers


def api_get_holdings(google_user_id):
    """Get gem holdings for a user from API"""
    try:
        token = load_api_key()
        if not token:
            logger.error("api_get_holdings: No API key configured. Cannot call holdings API.")
            return []

        url = f"{get_api_base()}/api/v2/users/{google_user_id}/gem-holdings"
        headers = get_api_headers()
        logger.info(f"api_get_holdings: calling {url}")
        r = requests.get(url, headers=headers, timeout=10)
        logger.info(f"api_get_holdings: status={r.status_code}, response={r.text[:500] if r.text else 'empty'}")
        if r.status_code == 200:
            return r.json()
        logger.warning(f"Holdings API returned {r.status_code}: {r.text}")
        return []
    except Exception as e:
        logger.error(f"Error calling holdings API: {e}")
        return []


def api_get_holding(asset_id):
    """Get a specific gem holding from API"""
    try:
        url = f"{get_api_base()}/api/v2/gem-holdings/{asset_id}"
        r = requests.get(url, headers=get_api_headers(), timeout=10)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception as e:
        logger.error(f"Error getting holding {asset_id}: {e}")
        return None


def api_create_holding(google_user_id, data):
    """Create a new gem holding via API"""
    try:
        url = f"{get_api_base()}/api/v2/gem-holdings"
        params = {'google_user_id': google_user_id, **data}
        logger.info(f"Creating holding with params: {params}")
        r = requests.post(url, headers=get_api_headers(), params=params, timeout=10)
        logger.info(f"Create holding API response: {r.status_code} - {r.text[:500]}")
        if r.status_code == 200:
            return r.json()
        error_msg = f"API returned {r.status_code}: {r.text}"
        logger.warning(f"Create holding API error: {error_msg}")
        raise Exception(error_msg)
    except Exception as e:
        logger.error(f"Error creating holding: {e}")
        raise


def api_update_holding(asset_id, data):
    """Update an existing gem holding via API"""
    try:
        url = f"{get_api_base()}/api/v2/gem-holdings/{asset_id}"
        r = requests.put(url, headers=get_api_headers(), params=data, timeout=10)
        if r.status_code == 200:
            return r.json()
        logger.warning(f"Update holding API returned {r.status_code}: {r.text}")
        return None
    except Exception as e:
        logger.error(f"Error updating holding {asset_id}: {e}")
        return None


def api_delete_holding(asset_id, google_user_id=None):
    """Delete a gem holding via API"""
    try:
        url = f"{get_api_base()}/api/v2/gem-holdings/{asset_id}"
        params = {}
        if google_user_id:
            params['google_user_id'] = google_user_id
        r = requests.delete(url, headers=get_api_headers(), params=params, timeout=10)
        return r.status_code == 200
    except Exception as e:
        logger.error(f"Error deleting holding {asset_id}: {e}")
        return False


def api_get_gem_types():
    """Get all gem types for dropdown selection, sorted alphabetically"""
    try:
        url = f"{get_api_base()}/api/v2/gems"
        r = requests.get(url, headers=get_api_headers(), params={'limit': 500}, timeout=10)
        if r.status_code == 200:
            gem_types = r.json()
            # Sort alphabetically by GemTypeName
            gem_types.sort(key=lambda x: (x.get('GemTypeName') or '').lower())
            return gem_types
        return []
    except Exception as e:
        logger.error(f"Error getting gem types: {e}")
        return []


@bp.route('/')
def index():
    """Portfolio main page"""
    user = load_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    try:
        logger.info(f"Portfolio index: user.google_id = {user.google_id}")

        # Check if API key is configured
        if not load_api_key():
            logger.error("Portfolio index: API key not configured")
            return render_template('portfolio/index.html', holdings=[], error="API key not configured. Please contact administrator.")

        holdings = api_get_holdings(user.google_id)
        logger.info(f"Portfolio index: got {len(holdings)} holdings: {holdings}")
        return render_template('portfolio/index.html', holdings=holdings)
    except Exception as e:
        log_db_exception(e, 'portfolio.index: fetching holdings')
        return render_template('portfolio/index.html', holdings=[], error=f"Error loading portfolio: {str(e)}")


@bp.route('/add', methods=['GET', 'POST'])
def add_gem():
    """Add a gem to portfolio"""
    user = load_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        try:
            data = {
                'gem_type_id': int(request.form.get('gem_type_id')),
                'parcel_size': int(request.form.get('parcel_size') or 1),
                'weight_carats': float(request.form.get('weight_carats')) if request.form.get('weight_carats') else None,
                'purchase_date': request.form.get('purchase_date') or None,
                'purchase_cost': float(request.form.get('purchase_cost')) if request.form.get('purchase_cost') else None,
                'shipping_cost': float(request.form.get('shipping_cost')) if request.form.get('shipping_cost') else None,
                'insurance_cost': float(request.form.get('insurance_cost')) if request.form.get('insurance_cost') else None,
                'taxes_cost': float(request.form.get('taxes_cost')) if request.form.get('taxes_cost') else None,
                'gem_form': request.form.get('gem_form') or None,
                'original_listing_url': request.form.get('original_listing_url') or None,
                'notes': request.form.get('notes') or None,
            }
            # Remove None values
            data = {k: v for k, v in data.items() if v is not None}

            result = api_create_holding(user.google_id, data)
            if result:
                flash('Gem added to your portfolio!', 'success')
                return redirect(url_for('portfolio.index'))

        except Exception as e:
            error_msg = f"Error adding gem to portfolio: {str(e)}"
            logger.error(error_msg)
            flash(error_msg, 'error')

    # GET request - show form with gem types
    try:
        gem_types = api_get_gem_types()
        if not gem_types:
            logger.warning("No gem types returned from API")
            gem_types = []
        return render_template('portfolio/add.html', gem_types=gem_types)
    except Exception as e:
        logger.error(f"Error loading add gem form: {e}")
        return render_template('portfolio/add.html', gem_types=[], error=f"Error loading gem types: {str(e)}")

@bp.route('/edit/<int:asset_id>', methods=['GET', 'POST'])
def edit_gem(asset_id):
    """Edit a gem in portfolio"""
    user = load_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        try:
            data = {
                'gem_type_id': int(request.form.get('gem_type_id')) if request.form.get('gem_type_id') else None,
                'parcel_size': int(request.form.get('parcel_size')) if request.form.get('parcel_size') else None,
                'weight_carats': float(request.form.get('weight_carats')) if request.form.get('weight_carats') else None,
                'purchase_date': request.form.get('purchase_date') or None,
                'shipping_date': request.form.get('shipping_date') or None,
                # Costs
                'purchase_cost': float(request.form.get('purchase_cost')) if request.form.get('purchase_cost') else None,
                'shipping_cost': float(request.form.get('shipping_cost')) if request.form.get('shipping_cost') else None,
                'insurance_cost': float(request.form.get('insurance_cost')) if request.form.get('insurance_cost') else None,
                'taxes_cost': float(request.form.get('taxes_cost')) if request.form.get('taxes_cost') else None,
                'upfront_tariffs_cost': float(request.form.get('upfront_tariffs_cost')) if request.form.get('upfront_tariffs_cost') else None,
                'additional_tariffs_cost': float(request.form.get('additional_tariffs_cost')) if request.form.get('additional_tariffs_cost') else None,
                'seller_certification_cost': float(request.form.get('seller_certification_cost')) if request.form.get('seller_certification_cost') else None,
                'total_certification_cost': float(request.form.get('total_certification_cost')) if request.form.get('total_certification_cost') else None,
                # Gem details
                'holding_display_name': request.form.get('holding_display_name') or None,
                'original_listing_title': request.form.get('original_listing_title') or None,
                'origination_country': request.form.get('origination_country') or None,
                'clarity': request.form.get('clarity') or None,
                'gem_form': request.form.get('gem_form') or None,
                'cut_shape': request.form.get('cut_shape') or None,
                'color': request.form.get('color') or None,
                'treatment': request.form.get('treatment') or None,
                'dimensions': request.form.get('dimensions') or None,
                # Seller/Purchase details
                'seller_platform_id': int(request.form.get('seller_platform_id')) if request.form.get('seller_platform_id') else None,
                'seller_id': int(request.form.get('seller_id')) if request.form.get('seller_id') else None,
                'invoice_number': request.form.get('invoice_number') or None,
                'product_number': request.form.get('product_number') or None,
                'seller_internal_sku': request.form.get('seller_internal_sku') or None,
                'original_listing_url': request.form.get('original_listing_url') or None,
                'payment_method': request.form.get('payment_method') or None,
                'shipping_provider': request.form.get('shipping_provider') or None,
                'tracking_number': request.form.get('tracking_number') or None,
                'notes': request.form.get('notes') or None,
            }
            # Remove None values
            data = {k: v for k, v in data.items() if v is not None}

            result = api_update_holding(asset_id, data)
            if result:
                flash('Portfolio item updated!', 'success')
                return redirect(url_for('portfolio.index'))
            else:
                flash('Error updating portfolio item', 'error')

        except Exception as e:
            log_db_exception(e, 'portfolio.edit_gem: updating gem')
            flash('Error updating portfolio item', 'error')

    # GET request - show form with current data
    try:
        holding = api_get_holding(asset_id)
        if not holding:
            flash('Portfolio item not found', 'error')
            return redirect(url_for('portfolio.index'))

        gem_types = api_get_gem_types()
        if not gem_types:
            logger.warning("No gem types returned from API")
            gem_types = []
        return render_template('portfolio/edit.html', item=holding, gem_types=gem_types)
    except Exception as e:
        logger.error(f"Error loading edit gem form: {e}")
        flash(f"Error loading form: {str(e)}", 'error')
        return redirect(url_for('portfolio.index'))


@bp.route('/delete/<int:asset_id>', methods=['POST'])
def delete_gem(asset_id):
    """Delete a gem from portfolio"""
    user = load_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    success = api_delete_holding(asset_id, user.google_id)
    if success:
        flash('Gem removed from portfolio', 'success')
    else:
        flash('Error removing gem from portfolio', 'error')

    return redirect(url_for('portfolio.index'))


@bp.route('/add-gra-invoice', methods=['GET', 'POST'])
def add_gra_invoice():
    """Add multiple gem holdings from a single GRA invoice"""
    user = load_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        try:
            # Get header info
            invoice_number = request.form.get('invoice_number') or None
            purchase_date = request.form.get('purchase_date') or None
            seller_name = request.form.get('seller_name') or None
            total_amount = request.form.get('total_amount') or None

            # Get header-level costs to split across all holdings
            header_insurance = float(request.form.get('insurance_cost')) if request.form.get('insurance_cost') else 0
            header_taxes = float(request.form.get('taxes_cost')) if request.form.get('taxes_cost') else 0
            header_shipping = float(request.form.get('shipping_cost')) if request.form.get('shipping_cost') else 0
            header_tariffs = float(request.form.get('tariffs_cost')) if request.form.get('tariffs_cost') else 0

            # Get gem rows - form fields are arrays with indices
            gem_type_ids = request.form.getlist('gem_type_id[]')
            weights = request.form.getlist('weight_carats[]')
            prices = request.form.getlist('purchase_cost[]')
            gem_forms = request.form.getlist('gem_form[]')
            product_numbers = request.form.getlist('product_number[]')
            seller_skus = request.form.getlist('seller_internal_sku[]')
            listing_titles = request.form.getlist('original_listing_title[]')

            if not gem_type_ids:
                flash('At least one gem is required', 'error')
                gem_types = api_get_gem_types()
                return render_template('portfolio/add_gra_invoice.html', gem_types=gem_types)

            # Count valid gem rows for splitting costs
            valid_gem_count = sum(1 for gid in gem_type_ids if gid)

            # Calculate per-holding split of costs (rounded to 2 decimals)
            insurance_per_holding = round(header_insurance / valid_gem_count, 2) if valid_gem_count > 0 and header_insurance > 0 else None
            taxes_per_holding = round(header_taxes / valid_gem_count, 2) if valid_gem_count > 0 and header_taxes > 0 else None
            shipping_per_holding = round(header_shipping / valid_gem_count, 2) if valid_gem_count > 0 and header_shipping > 0 else None
            tariffs_per_holding = round(header_tariffs / valid_gem_count, 2) if valid_gem_count > 0 and header_tariffs > 0 else None

            created_count = 0
            errors = []

            for i, gem_type_id in enumerate(gem_type_ids):
                if not gem_type_id:
                    continue

                try:
                    # Build notes with seller name
                    notes_parts = []
                    if seller_name:
                        notes_parts.append(f"Seller: {seller_name}")

                    data = {
                        'gem_type_id': int(gem_type_id),
                        'parcel_size': 1,
                        'weight_carats': float(weights[i]) if i < len(weights) and weights[i] else None,
                        'purchase_date': purchase_date,
                        'purchase_cost': float(prices[i]) if i < len(prices) and prices[i] else None,
                        'insurance_cost': insurance_per_holding,
                        'taxes_cost': taxes_per_holding,
                        'shipping_cost': shipping_per_holding,
                        'upfront_tariffs_cost': tariffs_per_holding,
                        'gem_form': gem_forms[i] if i < len(gem_forms) and gem_forms[i] else None,
                        'product_number': product_numbers[i] if i < len(product_numbers) and product_numbers[i] else None,
                        'seller_internal_sku': seller_skus[i] if i < len(seller_skus) and seller_skus[i] else None,
                        'original_listing_title': listing_titles[i] if i < len(listing_titles) and listing_titles[i] else None,
                        'invoice_number': invoice_number,
                        'notes': '; '.join(notes_parts) if notes_parts else None,
                    }
                    # Remove None values
                    data = {k: v for k, v in data.items() if v is not None}

                    result = api_create_holding(user.google_id, data)
                    if result:
                        created_count += 1
                except Exception as e:
                    errors.append(f"Row {i+1}: {str(e)}")

            if created_count > 0:
                flash(f'Successfully added {created_count} gem(s) to your portfolio!', 'success')
            if errors:
                for err in errors:
                    flash(err, 'error')

            return redirect(url_for('portfolio.index'))

        except Exception as e:
            error_msg = f"Error processing invoice: {str(e)}"
            logger.error(error_msg)
            flash(error_msg, 'error')

    # GET request - show form with gem types
    try:
        gem_types = api_get_gem_types()
        if not gem_types:
            logger.warning("No gem types returned from API")
            gem_types = []
        return render_template('portfolio/add_gra_invoice.html', gem_types=gem_types)
    except Exception as e:
        logger.error(f"Error loading add GRA invoice form: {e}")
        return render_template('portfolio/add_gra_invoice.html', gem_types=[], error=f"Error loading gem types: {str(e)}")


def api_get_listing_details(listing_id):
    """Fetch listing details from the API by listing ID (product number)"""
    try:
        base_url = current_app.config.get('GEMDB_API_URL', 'https://api.preciousstone.info')
        token = load_api_key() or ''
        headers = {'X-API-Key': token} if token else {}

        url = f"{base_url.rstrip('/')}/api/v2/listings/{listing_id}"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"Failed to fetch listing {listing_id}: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error fetching listing details: {e}")
        return None


def api_derive_gem_type_from_title(title):
    """
    Derive gem type ID from title by calling the PUT listings endpoint.
    The API has DeriveGemTypeIdFromTitle built-in and returns gem_type_id.
    Since there's no dedicated endpoint, we use the local gem_type_map as fallback.
    """
    if not title:
        return None, None

    # Get gem types from API for local matching (as fallback)
    gem_types = api_get_gem_types()
    title_lower = title.lower()

    # Sort by name length descending to match more specific types first
    sorted_gems = sorted(gem_types, key=lambda x: len(x.get('GemTypeName', '')), reverse=True)

    for gt in sorted_gems:
        name = gt.get('GemTypeName', '')
        if name.lower() in title_lower:
            return gt.get('GemTypeId'), name

    return None, None


@bp.route('/parse-gra-pdf', methods=['POST'])
def parse_gra_pdf():
    """Parse a GRA invoice PDF and return extracted data as JSON"""
    import re
    from flask import jsonify

    user = load_current_user()
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401

    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No PDF file provided'}), 400

    pdf_file = request.files['pdf_file']
    if pdf_file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not pdf_file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'File must be a PDF'}), 400

    try:
        import pdfplumber
        import io

        # Read PDF from uploaded file
        pdf_bytes = pdf_file.read()
        pdf_stream = io.BytesIO(pdf_bytes)

        invoice_data = {
            'invoice_number': None,
            'order_date': None,
            'seller_invoice_name': None,
            'totals': {},
            'shipping_info': {},
            'items': []
        }

        # Debug logging to file
        import os
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        debug_log_path = os.path.join(log_dir, 'pdf_parse_debug.txt')

        with pdfplumber.open(pdf_stream) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() + "\n"

            # Write debug info to file
            with open(debug_log_path, 'w', encoding='utf-8') as debug_file:
                debug_file.write("=== FULL TEXT ===\n")
                debug_file.write(full_text)
                debug_file.write("\n\n")

            # Parse header information
            invoice_match = re.search(r'Invoice #(\d+)', full_text)
            # Date format: "Order date 11th Dec 2025" - need to handle ordinal suffixes
            date_match = re.search(r'Order date\s+(\d{1,2})(?:st|nd|rd|th)?\s+(\w+)\s+(\d{4})', full_text)

            if invoice_match:
                invoice_data['invoice_number'] = invoice_match.group(1)
            if date_match:
                # Convert date to YYYY-MM-DD format
                try:
                    from datetime import datetime
                    day = date_match.group(1)
                    month = date_match.group(2)
                    year = date_match.group(3)
                    date_str = f"{day} {month} {year}"
                    # Try parsing with full month name first, then abbreviated
                    for fmt in ['%d %B %Y', '%d %b %Y']:
                        try:
                            parsed_date = datetime.strptime(date_str, fmt)
                            invoice_data['order_date'] = parsed_date.strftime('%Y-%m-%d')
                            break
                        except ValueError:
                            continue
                except Exception as e:
                    logger.warning(f"Could not parse date: {e}")

            # Parse seller info from "SOLD BY" section
            # The PDF merges both columns, so both seller and buyer names appear on same line
            # We extract the seller email (first email on the email line) and get the username part
            # Format: ...lines...\n seller@email.com buyer@email.com \n...
            seller_email_match = re.search(r'SOLD BY.*?([a-zA-Z0-9_.+-]+)@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', full_text, re.DOTALL)
            if seller_email_match:
                # Extract just the username part before @ (e.g., "preciouscarats" from "preciouscarats@gmail.com")
                invoice_data['seller_invoice_name'] = seller_email_match.group(1).strip()

            # Parse totals
            totals_patterns = {
                'subtotal': r'Subtotal\s+\$(\d+\.?\d*)\s+USD',
                'shipping': r'Shipping\s+\$(\d+\.?\d*)\s+USD',
                'insurance': r'Insurance\s+\$(\d+\.?\d*)\s+USD',
                'taxes': r'Taxes\s+\$(\d+\.?\d*)\s+USD',
                'total': r'\bTotal\s+\$(\d+\.?\d*)\s+USD'
            }

            for key, pattern in totals_patterns.items():
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    invoice_data['totals'][key] = float(match.group(1))

            # Parse shipping and delivery information
            shipping_patterns = {
                'shipping_provider': r'Shipping Provider\s+(.+?)(?:\n|$)',
                'tracking_number': r'Tracking Number\s+(.+?)(?:\n|$)'
            }

            for key, pattern in shipping_patterns.items():
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    invoice_data['shipping_info'][key] = match.group(1).strip()

            # Parse items - GRA PDF format:
            # Line 1: "0.07 Ct World Rarest Vayrynenite Top Quality Luster VR16"
            # Line 2: "1 SKU: $13.00 USD" or "1 $13.00 USD" (SKU may be on next line)
            # Line 3: "Product ID: 3029657"
            # Sometimes SKU is on a separate line: "SKU:"
            # We need to find Product ID and look BACKWARDS for the title

            # Find all Product IDs first
            product_id_matches = list(re.finditer(r'Product ID:\s*(\d+)', full_text))

            for i, pid_match in enumerate(product_id_matches):
                product_id = pid_match.group(1)

                # Find the text between previous Product ID (or start) and this Product ID
                start_pos = product_id_matches[i-1].end() if i > 0 else 0
                end_pos = pid_match.start()
                block = full_text[start_pos:end_pos]

                # Debug: log each block
                with open(debug_log_path, 'a', encoding='utf-8') as debug_file:
                    debug_file.write(f"=== PRODUCT {product_id} BLOCK ===\n")
                    debug_file.write(f"start_pos={start_pos}, end_pos={end_pos}\n")
                    debug_file.write(block)
                    debug_file.write("\n---\n")

                # Extract price - look for "$X.XX USD" pattern
                price_match = re.search(r'\$(\d+\.?\d*)\s+USD', block)
                if not price_match:
                    with open(debug_log_path, 'a', encoding='utf-8') as debug_file:
                        debug_file.write(f"NO PRICE FOUND for {product_id}, skipping\n\n")
                    continue

                price = float(price_match.group(1))

                # Initialize item data
                original_url = f"https://www.gemrockauctions.com/auctions/{product_id}"
                item_data = {
                    'product_id': product_id,
                    'sku': None,
                    'gem_type_id': None,
                    'gem_type_name': '',
                    'carat': None,
                    'price': price,
                    'title': '',
                    'holding_name': '',
                    'description': '',
                    'clarity': None,
                    'treatment': None,
                    'gem_form': None,
                    'original_url': original_url
                }

                # Extract SKU - can be "SKU: ABC123" or just on its own line
                sku_match = re.search(r'SKU:\s*([A-Z0-9-]+)', block, re.IGNORECASE)
                if sku_match:
                    item_data['sku'] = sku_match.group(1).strip()

                # Extract title - format: "X.XX Ct <title>" at the start of the block
                # The title line typically starts with weight in Ct
                title_match = re.search(r'(\d+\.?\d*)\s+Ct\s+(.+?)(?=\n|$)', block, re.IGNORECASE)

                # Debug: log title match attempt
                with open(debug_log_path, 'a', encoding='utf-8') as debug_file:
                    debug_file.write(f"title_match result: {title_match}\n")

                if title_match:
                    item_data['carat'] = float(title_match.group(1))
                    # Title is everything after "X.XX Ct " up to end of line
                    raw_title = title_match.group(2).strip()
                    # Clean up the title - remove SKU suffix if present (e.g., "VR16" at end)
                    item_data['title'] = re.sub(r'\s+', ' ', raw_title)
                    with open(debug_log_path, 'a', encoding='utf-8') as debug_file:
                        debug_file.write(f"TITLE FOUND: {item_data['title']}\n\n")
                else:
                    # Try alternate format: "NO RESERVE X CARAT <gem>"
                    alt_match = re.search(r'NO RESERVE\s+(\d+\.?\d*)\s+CARAT\s+(.+?)(?=\n|$)', block, re.IGNORECASE)
                    if alt_match:
                        item_data['carat'] = float(alt_match.group(1))
                        item_data['title'] = re.sub(r'\s+', ' ', alt_match.group(2).strip())
                        with open(debug_log_path, 'a', encoding='utf-8') as debug_file:
                            debug_file.write(f"TITLE FOUND (alt): {item_data['title']}\n\n")
                    else:
                        with open(debug_log_path, 'a', encoding='utf-8') as debug_file:
                            debug_file.write(f"NO TITLE FOUND\n\n")

                # Try to fetch listing details from the API to enrich with additional data
                listing_details = api_get_listing_details(product_id)

                if listing_details:
                    # Use API data for fields not available in PDF
                    # Only use API title if PDF parsing didn't find one
                    if not item_data['title']:
                        item_data['title'] = listing_details.get('ListingTitle') or listing_details.get('listing_title') or ''

                    # Use API weight if PDF parsing didn't find carat
                    if not item_data['carat']:
                        item_data['carat'] = listing_details.get('Weight') or listing_details.get('weight')

                    # These fields are only available from API
                    item_data['clarity'] = listing_details.get('Clarity') or listing_details.get('clarity')
                    item_data['treatment'] = listing_details.get('Treatment') or listing_details.get('treatment')
                    item_data['gem_form'] = listing_details.get('Shape') or listing_details.get('shape') or listing_details.get('Type') or listing_details.get('type')
                    item_data['gem_type_id'] = listing_details.get('GemTypeId') or listing_details.get('gem_type_id')

                    # Get SKU from API if not in PDF
                    if not item_data['sku']:
                        item_data['sku'] = listing_details.get('Sku') or listing_details.get('sku')

                    # Derive gem type name if we have gem_type_id
                    if item_data['gem_type_id']:
                        gem_types = api_get_gem_types()
                        for gt in gem_types:
                            if gt.get('GemTypeId') == item_data['gem_type_id']:
                                item_data['gem_type_name'] = gt.get('GemTypeName', '')
                                break

                # If we still don't have gem_type_id, derive it from title
                if not item_data['gem_type_id'] and item_data['title']:
                    gem_type_id, gem_type_name = api_derive_gem_type_from_title(item_data['title'])
                    item_data['gem_type_id'] = gem_type_id
                    item_data['gem_type_name'] = gem_type_name or ''

                item_data['description'] = item_data['title']
                item_data['holding_name'] = item_data['title']  # Default holding name to title
                invoice_data['items'].append(item_data)

        return jsonify(invoice_data)

    except ImportError:
        return jsonify({'error': 'PDF parsing library (pdfplumber) not installed'}), 500
    except Exception as e:
        logger.error(f"Error parsing GRA PDF: {e}")
        return jsonify({'error': f'Error parsing PDF: {str(e)}'}), 500


@bp.route('/stats')
def portfolio_stats():
    """Portfolio statistics and analytics"""
    user = load_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    holdings = api_get_holdings(user.google_id)

    # Calculate stats from holdings
    total_items = len(holdings)
    total_invested = sum(h.get('PurchaseCost', 0) or 0 for h in holdings)
    total_shipping = sum(h.get('ShippingCost', 0) or 0 for h in holdings)
    total_carats = sum(h.get('WeightCarats', 0) or 0 for h in holdings)

    stats = {
        'total_items': total_items,
        'total_invested': total_invested,
        'total_shipping': total_shipping,
        'total_cost': total_invested + total_shipping,
        'total_carats': total_carats
    }

    # Group holdings by gem type
    gem_totals = {}
    for h in holdings:
        gem_name = h.get('GemTypeName', 'Unknown')
        cost = (h.get('PurchaseCost', 0) or 0) + (h.get('ShippingCost', 0) or 0)
        gem_totals[gem_name] = gem_totals.get(gem_name, 0) + cost

    # Sort by value descending
    top_gems = sorted(gem_totals.items(), key=lambda x: x[1], reverse=True)[:10]

    return render_template('portfolio/stats.html', stats=stats, top_gems=top_gems, holdings=holdings)
