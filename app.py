"""
Flask application for precious stones/gems website with SEO optimization.
Designed for deployment on Google Cloud App Engine.
"""

from flask import Flask, render_template, url_for, make_response, Response
from datetime import datetime

app = Flask(__name__)


def get_seo_data(page='home'):
    """
    Centralized SEO data for different pages.
    """
    seo_data = {
        'home': {
            'title': 'Precious Stones & Gems - Your Complete Guide to Gemstones',
            'description': 'Discover the world of precious stones and gems. Learn about different types of gemstones, their properties, and meanings.',
            'keywords': 'precious stones, gems, gemstones, crystals, minerals, jewelry',
            'og_type': 'website',
            'canonical': url_for('index', _external=True),
        },
        'about': {
            'title': 'About Us - Precious Stones Information',
            'description': 'Learn more about our precious stones and gems information portal.',
            'keywords': 'about gems, gemstone information, precious stones guide',
            'og_type': 'website',
            'canonical': url_for('about', _external=True),
        }
    }
    return seo_data.get(page, seo_data['home'])


def get_structured_data():
    """
    Generate JSON-LD structured data for SEO.
    """
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "Precious Stones Info",
        "url": "https://preciousstone.info",
        "description": "Your complete guide to precious stones and gemstones",
        "potentialAction": {
            "@type": "SearchAction",
            "target": "https://preciousstone.info/search?q={search_term_string}",
            "query-input": "required name=search_term_string"
        }
    }


@app.route('/')
def index():
    """Home page with SEO optimizations."""
    seo = get_seo_data('home')
    structured_data = get_structured_data()
    return render_template('index.html', seo=seo, structured_data=structured_data)


@app.route('/about')
def about():
    """About page with SEO optimizations."""
    seo = get_seo_data('about')
    return render_template('about.html', seo=seo)


@app.route('/sitemap.xml')
def sitemap():
    """Generate sitemap.xml for search engines."""
    pages = []
    
    # Add all routes
    pages.append({
        'loc': url_for('index', _external=True),
        'lastmod': datetime.now().strftime('%Y-%m-%d'),
        'changefreq': 'weekly',
        'priority': '1.0'
    })
    
    pages.append({
        'loc': url_for('about', _external=True),
        'lastmod': datetime.now().strftime('%Y-%m-%d'),
        'changefreq': 'monthly',
        'priority': '0.8'
    })
    
    # Generate XML
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    for page in pages:
        xml.append('  <url>')
        xml.append(f'    <loc>{page["loc"]}</loc>')
        xml.append(f'    <lastmod>{page["lastmod"]}</lastmod>')
        xml.append(f'    <changefreq>{page["changefreq"]}</changefreq>')
        xml.append(f'    <priority>{page["priority"]}</priority>')
        xml.append('  </url>')
    
    xml.append('</urlset>')
    
    response = Response('\n'.join(xml), mimetype='application/xml')
    return response


@app.route('/robots.txt')
def robots_txt():
    """Generate robots.txt for search engine crawlers."""
    content = """User-agent: *
Allow: /
Sitemap: https://preciousstone.info/sitemap.xml

# Disallow admin and private areas
Disallow: /admin/
Disallow: /private/
"""
    response = make_response(content)
    response.headers['Content-Type'] = 'text/plain'
    return response


@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 page with SEO."""
    seo = {
        'title': '404 - Page Not Found | Precious Stones',
        'description': 'The page you are looking for could not be found.',
        'keywords': 'error, not found',
        'og_type': 'website',
        'canonical': url_for('index', _external=True),
    }
    return render_template('404.html', seo=seo), 404


@app.context_processor
def inject_globals():
    """Inject global variables into all templates."""
    return {
        'site_name': 'Precious Stones Info',
        'site_url': 'https://preciousstone.info',
        'current_year': datetime.now().year,
    }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
