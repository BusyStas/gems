import pdfplumber
import re
import io

with open('unneededcontent/invoice-gem-rock-auctions-siamesegems-bizzik-standard-shipping-tracked-30296573031161303116830311723031966.pdf', 'rb') as f:
    pdf_bytes = f.read()

pdf_stream = io.BytesIO(pdf_bytes)
with pdfplumber.open(pdf_stream) as pdf:
    full_text = ''
    for page in pdf.pages:
        full_text += page.extract_text() + '\n'
    
    # Test date parsing
    date_match = re.search(r'Order date\s+(\d{1,2})(?:st|nd|rd|th)?\s+(\w+)\s+(\d{4})', full_text)
    if date_match:
        print(f'Date: {date_match.group(1)} {date_match.group(2)} {date_match.group(3)}')
    else:
        print('Date not found')
    
    # Test seller parsing - get seller email
    seller_email_match = re.search(r'SOLD BY.*?([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', full_text, re.DOTALL)
    if seller_email_match:
        print(f'Seller Email: {seller_email_match.group(1).strip()}')
    else:
        print('Seller email not found')
    
    # Test item parsing
    product_id_matches = list(re.finditer(r'Product ID:\s*(\d+)', full_text))
    print(f'Found {len(product_id_matches)} products')
    
    for i, pid_match in enumerate(product_id_matches):
        product_id = pid_match.group(1)
        start_pos = product_id_matches[i-1].end() if i > 0 else 0
        end_pos = pid_match.start()
        block = full_text[start_pos:end_pos]
        
        title_match = re.search(r'(\d+\.?\d*)\s+Ct\s+(.+?)(?=\n|$)', block, re.IGNORECASE)
        price_match = re.search(r'\$(\d+\.?\d*)\s+USD', block)
        
        if title_match and price_match:
            print(f'Product {product_id}: {title_match.group(1)} Ct - {title_match.group(2).strip()} - ${price_match.group(1)}')
        else:
            print(f'Product {product_id}: title_match={title_match is not None}, price_match={price_match is not None}')
            if not title_match:
                # Show block for debugging
                print(f'  Block excerpt: {block[:200]}...')

