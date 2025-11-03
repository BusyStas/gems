# Precious Stones Info

A Flask-based website for precious stones and gemstones information, optimized for SEO and ready for Google Cloud deployment.

🌐 **Website:** https://preciousstone.info

## Features

✨ **SEO Optimized**
- Meta tags (title, description, keywords)
- Open Graph and Twitter Card support
- JSON-LD structured data
- Automatic sitemap.xml generation
- robots.txt for search engines
- Canonical URLs

🎨 **Modern Design**
- Responsive, mobile-first layout
- Clean, professional styling
- Accessible navigation
- Custom 404 error page

☁️ **Google Cloud Ready**
- App Engine configuration included
- Gunicorn WSGI server
- Automatic scaling support
- Production-ready security settings

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run in development mode
FLASK_ENV=development python app.py
```

Visit `http://localhost:8080`

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions for Google Cloud App Engine.

## Project Structure

```
gems/
├── app.py              # Main Flask application
├── app.yaml            # Google Cloud App Engine config
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates with SEO
├── static/            # CSS and static assets
└── DEPLOYMENT.md      # Deployment guide
```

## Security

- Debug mode disabled in production
- Updated dependencies with no known vulnerabilities
- Secure headers and configurations
- HTTPS enforced in App Engine

## License

All rights reserved © 2025
