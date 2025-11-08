"""
Configuration settings for Gems Hub Flask application
"""

import os

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # SEO settings
    SITE_NAME = "Gems Hub"
    SITE_DESCRIPTION = "Your comprehensive resource for gems, gemstones, investments, and jewelry information"
    SITE_URL = os.environ.get('SITE_URL', 'https://preciousstone.info')
    SITE_KEYWORDS = "gems, gemstones, precious stones, jewelry, gem investment, diamond, ruby, sapphire, emerald"
    
    # Meta settings
    # Default Open Graph image (SVG placeholder included in repository)
    DEFAULT_OG_IMAGE = "/static/images/og-image.svg"
    TWITTER_HANDLE = "@gemshub"
    
    # Google Cloud settings
    GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID', '')
    GOOGLE_SEARCH_CONSOLE_VERIFICATION = os.environ.get('GOOGLE_SEARCH_CONSOLE_VERIFICATION', '')
    
    # Application settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'False') == 'True'
    TESTING = False
