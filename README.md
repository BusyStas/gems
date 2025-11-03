# Gems Hub - A Comprehensive Gemstone Information Hub

**Live Site:** https://preciousstone.info

A Flask-based web application providing comprehensive information about gems, gemstones, investments, and jewelry. Designed for deployment on Google Cloud Run.

## Features

- **Responsive Design**: Mobile-first design with collapsible sidebar menu
- **Green Color Scheme**: Elegant shades of green throughout the site
- **Comprehensive Content**: Information about gem types, investment strategies, and jewelry
- **SEO Optimized**: Meta tags, sitemap, robots.txt for search engine visibility
- **Cloud Ready**: Configured for Google Cloud Run deployment

## Structure

```
gems/
├── app.py                  # Main Flask application
├── config.py               # Configuration settings
├── routes/                 # Route handlers
│   ├── main.py            # Home page routes
│   ├── gems.py            # Gem information routes
│   ├── investments.py     # Investment information routes
│   └── jewelry.py         # Jewelry routes
├── templates/             # Jinja2 templates
│   ├── base.html         # Base template
│   ├── home.html         # Home page
│   ├── includes/         # Reusable template components
│   ├── gems/             # Gem pages
│   ├── investments/      # Investment pages
│   └── jewelry/          # Jewelry pages
├── static/               # Static assets
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript files
│   ├── robots.txt       # SEO robots file
│   └── sitemap.xml      # SEO sitemap
├── Dockerfile           # Docker configuration
├── app.yaml            # Google App Engine config
├── cloudbuild.yaml     # Google Cloud Build config
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Navigation

The site includes:
- **Home**: Welcome page with overview
- **Type of Gems**: Information about precious, semi-precious, and organic gems
- **Investments**: Market trends and value assessment guides
- **Jewelry**: Rings, necklaces, and earrings information

## Local Development

### Prerequisites

- Python 3.11+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/BusyStas/gems.git
cd gems
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the development server:
```bash
python app.py
```

5. Open your browser to `http://localhost:8080`

## Google Cloud Deployment

### Deploy to Cloud Run

1. Install Google Cloud SDK and authenticate:
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

2. Build and deploy:
```bash
gcloud builds submit --config cloudbuild.yaml
```

Or deploy directly with Docker:
```bash
gcloud run deploy gems-hub --source . --region us-central1 --allow-unauthenticated
```

### Deploy to App Engine

```bash
gcloud app deploy
```

## Environment Variables

Set these in your deployment environment:

- `SECRET_KEY`: Flask secret key for sessions
- `SITE_URL`: Your site's URL (e.g., https://preciousstone.info)
- `GOOGLE_ANALYTICS_ID`: Google Analytics tracking ID (optional)
- `GOOGLE_SEARCH_CONSOLE_VERIFICATION`: Google Search Console verification code (optional)

## Configuration

Edit `config.py` to customize:
- Site name and description
- SEO keywords
- Social media handles
- Google Analytics settings

## Design

The site uses a green color palette with:
- Primary green: #2d5016
- Medium green: #4a7c2e
- Light green: #6fa84a
- Pale green: #a8d48e
- Soft green: #d4edc7
- Mint green: #e8f5e0

## Features

### Navigation
- Collapsible sidebar menu with sandwich button
- Top navigation bar with pipe-separated links
- Submenu support for hierarchical navigation
- Responsive mobile-friendly design

### SEO
- Meta tags for social media sharing
- Sitemap.xml for search engines
- Robots.txt for crawler control
- Semantic HTML structure

### Accessibility
- ARIA labels for navigation
- Semantic HTML elements
- Keyboard navigation support
- Screen reader friendly

## License

Copyright © 2025 Gems Hub. All rights reserved.

## Author

BusyStas
- GitHub: https://github.com/BusyStas
- Other projects: 
  - https://github.com/BusyStas/stasclub
  - https://github.com/BusyStas/stasboston

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
