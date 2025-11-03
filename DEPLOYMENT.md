# Precious Stones Website - Deployment Guide

This Flask application is optimized for Google Cloud App Engine deployment with built-in SEO features.

## Features

- ✅ Flask web framework
- ✅ SEO-optimized meta tags (title, description, keywords)
- ✅ Open Graph and Twitter Card support
- ✅ Structured data (JSON-LD)
- ✅ Automatic sitemap.xml generation
- ✅ robots.txt for search engines
- ✅ Mobile-responsive design
- ✅ Google Cloud App Engine ready
- ✅ Custom 404 error page

## Local Development

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application in development mode:
```bash
FLASK_ENV=development python app.py
```

Or on Windows:
```bash
set FLASK_ENV=development
python app.py
```

The application will be available at `http://localhost:8080`

**Note:** Debug mode is only enabled when `FLASK_ENV=development`. In production, the application runs without debug mode for security.

## Google Cloud Deployment

### Prerequisites

- Google Cloud account
- Google Cloud SDK installed (`gcloud` command)
- Project created in Google Cloud Console

### Deployment Steps

1. Initialize gcloud (if not already done):
```bash
gcloud init
```

2. Set your project:
```bash
gcloud config set project YOUR_PROJECT_ID
```

3. Deploy to App Engine:
```bash
gcloud app deploy
```

4. View your application:
```bash
gcloud app browse
```

### Custom Domain

To use the custom domain `preciousstone.info`:

1. Verify domain ownership in Google Cloud Console
2. Add custom domain in App Engine settings
3. Update DNS records as instructed by Google Cloud
4. Update the `site_url` in `app.py` to match your domain

## SEO Features

### Meta Tags
- Title, description, and keywords on every page
- Open Graph tags for social media sharing
- Twitter Card support
- Canonical URLs

### Sitemap
- Automatically generated at `/sitemap.xml`
- Includes all routes registered with `@ext.register_generator`

### Robots.txt
- Available at `/robots.txt`
- Configured to allow all search engines
- References sitemap location

### Structured Data
- JSON-LD schema markup
- WebSite schema for enhanced search results
- SearchAction for Google Search integration

### Performance
- Gunicorn WSGI server
- Automatic scaling on App Engine
- Static file caching

## Project Structure

```
gems/
├── app.py              # Main Flask application
├── app.yaml            # Google Cloud App Engine configuration
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   ├── base.html       # Base template with SEO
│   ├── index.html      # Home page
│   ├── about.html      # About page
│   └── 404.html        # Error page
└── static/             # Static files
    └── css/
        └── style.css   # Stylesheet
```

## Environment Variables

You can set environment variables in `app.yaml`:

```yaml
env_variables:
  FLASK_ENV: 'production'
```

## Monitoring

Monitor your application in Google Cloud Console:
- App Engine Dashboard
- Logs Explorer
- Error Reporting
- Performance monitoring

## Cost Optimization

The `app.yaml` is configured with:
- Automatic scaling
- Minimum 0 instances (scales to zero when idle)
- Maximum 10 instances
- 65% CPU utilization target

This ensures cost-effective hosting on Google Cloud.

## Support

For issues or questions, visit: https://preciousstone.info
