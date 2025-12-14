#!/usr/bin/env python3
"""
Comprehensive Gem Rock Auctions Invoice Parser
Extracts ALL fields: SKU, totals, shipping, tracking, etc.
"""

import json
import re
from pathlib import Path
import pdfplumber
from datetime import datetime

def parse_gemrock_invoice_complete(pdf_path):
    """
    Parse complete invoice with all fields
    """
    invoice_data = {
        "invoice_number": None,
        "order_date": None,
        "order_time": None,
        "seller": {},
        "buyer": {},
        "items": [],
        "totals": {},
        "shipping_info": {},
        "raw_text_sample": None
    }
    
    with pdfplumber.open(pdf_path) as pdf:
        # Extract all text from all pages
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
        
        # Store sample for debugging
        invoice_data["raw_text_sample"] = full_text[:500]
        
        # Parse header information
        invoice_match = re.search(r'Invoice #(\d+)', full_text)
        date_match = re.search(r'Order date (.+?)(?:\n|ticket)', full_text)
        time_match = re.search(r'Order time (.+?)(?:\n| invoice)', full_text)
        
        if invoice_match:
            invoice_data["invoice_number"] = invoice_match.group(1)
        if date_match:
            invoice_data["order_date"] = date_match.group(1).strip()
        if time_match:
            invoice_data["order_time"] = time_match.group(1).strip()
        
        # Parse seller info
        seller_match = re.search(
            r'SOLD BY.*?\n(.+?)\n(\+\d+)\n([\w@.]+)',
            full_text,
            re.DOTALL
        )
        if seller_match:
            invoice_data["seller"] = {
                "name": seller_match.group(1).strip(),
                "phone": seller_match.group(2).strip(),
                "email": seller_match.group(3).strip()
            }
        
        # Parse buyer info
        buyer_match = re.search(
            r'SOLD TO.*?\n(.+?)\n(\+\d+)\n([\w@.]+)',
            full_text,
            re.DOTALL
        )
        if buyer_match:
            invoice_data["buyer"] = {
                "name": buyer_match.group(1).strip(),
                "phone": buyer_match.group(2).strip(),
                "email": buyer_match.group(3).strip()
            }
        
        # Parse items with SKU
        invoice_data["items"] = parse_items_with_sku(full_text)
        
        # Parse ALL totals fields
        totals_patterns = {
            "subtotal": r'Subtotal\s+\$(\d+\.?\d*)\s+USD',
            "shipping": r'Shipping\s+\$(\d+\.?\d*)\s+USD',
            "insurance": r'Insurance\s+\$(\d+\.?\d*)\s+USD',
            "taxes": r'Taxes\s+\$(\d+\.?\d*)\s+USD',
            "tariffs_duties": r'Tari(?:ff|[^\s])s?\s*&\s*Duties\s+\$(\d+\.?\d*)\s+USD',
            "total": r'\bTotal\s+\$(\d+\.?\d*)\s+USD'  # \b prevents matching "Subtotal"
        }
        
        for key, pattern in totals_patterns.items():
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                invoice_data["totals"][key] = float(match.group(1))
        
        # Parse shipping and delivery information
        shipping_patterns = {
            "payment_method": r'Payment Method\s+(.+?)(?:\n|$)',
            "shipping_provider": r'Shipping Provider\s+(.+?)(?:\n|$)',
            "estimated_delivery": r'Estimated Delivery\s+(.+?)(?:\n|$)',
            "tracking_number": r'Tracking Number\s+(.+?)(?:\n|$)'
        }
        
        for key, pattern in shipping_patterns.items():
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                invoice_data["shipping_info"][key] = match.group(1).strip()
    
    return invoice_data


def parse_items_with_sku(text):
    """
    Parse items including SKU field - handles both formats
    """
    items = []
    
    # Split by Product ID to identify item blocks
    item_blocks = re.split(r'(?=Product ID:\s*\d+)', text)
    
    for block in item_blocks:
        if 'Product ID:' not in block:
            continue
        
        # Extract common fields
        product_id_match = re.search(r'Product ID:\s*(\d+)', block)
        # SKU can be: "SKU: BNG7171" or just "SKU:" (empty)
        sku_match = re.search(r'SKU:\s*([A-Z0-9]+)', block)
        price_match = re.search(r'\$(\d+\.?\d*)\s+USD', block)
        
        if not product_id_match or not price_match:
            continue
        
        product_id = product_id_match.group(1)
        sku = sku_match.group(1) if sku_match else None
        price = float(price_match.group(1))
        
        # Try Format 1: "0.07 Ct <description>"
        format1_match = re.search(
            r'(\d+\.?\d*)\s+Ct\s+(.+?)(?:\n|SKU:)',
            block,
            re.DOTALL
        )
        
        if format1_match:
            carat = float(format1_match.group(1))
            description = format1_match.group(2).strip()
            description = re.sub(r'\s+', ' ', description)
            gem_type = extract_gem_type(description)
            
            items.append({
                "product_id": product_id,
                "sku": sku,
                "carat": carat,
                "description": description,
                "gem_type": gem_type,
                "price_usd": price
            })
            continue
        
        # Try Format 2: "NO RESERVE 125 CARAT <gem> <rest>"
        format2_match = re.search(
            r'NO RESERVE\s+(\d+)\s+CARAT\s+(.+?)(?:\n.*?SKU:|SKU:)',
            block,
            re.DOTALL | re.IGNORECASE
        )
        
        if format2_match:
            carat = float(format2_match.group(1))
            description = format2_match.group(2).strip()
            description = re.sub(r'\s+', ' ', description)
            gem_type = extract_gem_type(description)
            
            items.append({
                "product_id": product_id,
                "sku": sku,
                "carat": carat,
                "description": description,
                "gem_type": gem_type,
                "price_usd": price
            })
    
    return items


def extract_gem_type(description):
    """Extract gem type from description with priority ordering"""
    gem_mapping = {
        # Specific varieties first (longer matches)
        'almandine garnet': 'Almandine Garnet',
        'rhodolite garnet': 'Rhodolite Garnet',
        'hessonite garnet': 'Hessonite Garnet',
        'white garnet': 'White Garnet',
        'green tourmaline': 'Green Tourmaline',
        
        # Then general types
        'vayrynenite': 'Vayrynenite',
        'grandidierite': 'Grandidierite',
        'hackmanite': 'Hackmanite',
        'scapolite': 'Scapolite',
        'garnet': 'Garnet',
        'quartz': 'Quartz',
        'tourmaline': 'Tourmaline',
        'spinel': 'Spinel',
        'peridot': 'Peridot',
        'apatite': 'Apatite',
        'ruby': 'Ruby',
        'emerald': 'Emerald',
        'sapphire': 'Sapphire',
        'alexandrite': 'Alexandrite',
        'topaz': 'Topaz',
        'aquamarine': 'Aquamarine',
        'tanzanite': 'Tanzanite'
    }
    
    description_lower = description.lower()
    
    # Check for specific types first (longest matches first)
    for gem_key in sorted(gem_mapping.keys(), key=lambda x: -len(x)):
        if gem_key in description_lower:
            return gem_mapping[gem_key]
    
    return "Unknown"


def format_invoice_for_display(invoice_data):
    """Format invoice data for readable display"""
    output = []
    output.append("=" * 80)
    output.append(f"INVOICE #{invoice_data['invoice_number']}")
    output.append("=" * 80)
    output.append(f"Date: {invoice_data['order_date']} at {invoice_data['order_time']}")
    output.append(f"Seller: {invoice_data['seller'].get('name', 'N/A')}")
    output.append(f"Buyer: {invoice_data['buyer'].get('name', 'N/A')}")
    output.append("")
    
    # Items
    output.append("ITEMS:")
    output.append("-" * 80)
    for i, item in enumerate(invoice_data['items'], 1):
        output.append(f"{i}. {item['gem_type']} - {item['carat']} ct")
        output.append(f"   SKU: {item['sku']}")
        output.append(f"   Product ID: {item['product_id']}")
        output.append(f"   Price: ${item['price_usd']:.2f}")
        output.append(f"   Description: {item['description'][:60]}...")
        output.append("")
    
    # Totals
    output.append("TOTALS:")
    output.append("-" * 80)
    totals = invoice_data['totals']
    if 'subtotal' in totals:
        output.append(f"Subtotal:        ${totals['subtotal']:.2f}")
    if 'shipping' in totals:
        output.append(f"Shipping:        ${totals['shipping']:.2f}")
    if 'insurance' in totals:
        output.append(f"Insurance:       ${totals['insurance']:.2f}")
    if 'taxes' in totals:
        output.append(f"Taxes:           ${totals['taxes']:.2f}")
    if 'tariffs_duties' in totals:
        output.append(f"Tariffs & Duties: ${totals['tariffs_duties']:.2f}")
    if 'total' in totals:
        output.append(f"TOTAL:           ${totals['total']:.2f}")
    output.append("")
    
    # Shipping info
    output.append("SHIPPING INFORMATION:")
    output.append("-" * 80)
    shipping = invoice_data['shipping_info']
    if 'payment_method' in shipping:
        output.append(f"Payment Method:      {shipping['payment_method']}")
    if 'shipping_provider' in shipping:
        output.append(f"Shipping Provider:   {shipping['shipping_provider']}")
    if 'estimated_delivery' in shipping:
        output.append(f"Estimated Delivery:  {shipping['estimated_delivery']}")
    if 'tracking_number' in shipping:
        output.append(f"Tracking Number:     {shipping['tracking_number']}")
    
    return "\n".join(output)


def main():
    # Parse all THREE invoices with complete data
    invoices = [
        {
            "name": "Siamese Gems",
            "path": "/mnt/user-data/uploads/invoice-gem-rock-auctions-siamesegems-bizzik-standard-shipping-tracked-30296573031161303116830311723031966.pdf"
        },
        {
            "name": "Spinghar Minerals",
            "path": "/mnt/user-data/uploads/invoice-gem-rock-auctions-spingharminerals-bizzik-standard-shipping-tracked-302887230288743028882302888830288913028894302890330289093028932302902230290253029027302903030305403030547303059730306013030630.pdf"
        },
        {
            "name": "InterGemCorp",
            "path": "/mnt/user-data/uploads/invoice-gem-rock-auctions-intergemcorp-bizzik-standard-shipping-tracked-284245928425672843140.pdf"
        }
    ]
    
    all_results = {}
    
    for invoice_info in invoices:
        if not Path(invoice_info["path"]).exists():
            print(f"❌ Skipping {invoice_info['name']} - file not found")
            continue
        
        print(f"\n{'=' * 80}")
        print(f"PARSING: {invoice_info['name']}")
        print('=' * 80)
        
        data = parse_gemrock_invoice_complete(invoice_info["path"])
        
        # Display formatted output
        print(format_invoice_for_display(data))
        
        # Store for JSON export
        # Remove raw_text_sample from JSON output
        export_data = {k: v for k, v in data.items() if k != 'raw_text_sample'}
        all_results[invoice_info['name']] = export_data
    
    # Save complete results
    output_path = "/home/claude/invoices_complete.json"
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'=' * 80}")
    print("EXTRACTION SUMMARY")
    print('=' * 80)
    print("""
Extracted fields per invoice:
✅ Invoice number
✅ Order date & time
✅ Seller info (name, phone, email)
✅ Buyer info (name, phone, email)
✅ Items with:
   - Product ID
   - SKU
   - Carat weight
   - Description
   - Gem type (extracted)
   - Price
✅ Totals:
   - Subtotal
   - Shipping
   - Insurance
   - Taxes
   - Tariffs & Duties
   - Total
✅ Shipping info:
   - Payment method
   - Shipping provider
   - Estimated delivery
   - Tracking number (when available)
    """)
    
    print(f"✅ Complete data saved to: {output_path}\n")
    
    return all_results


if __name__ == "__main__":
    main()