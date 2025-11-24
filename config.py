"""
Configuration settings for Gems Hub Flask application
"""

import os
import json

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
    # GEMDB API settings (external PreciousStone API)
    GEMDB_API_URL = os.environ.get('GEMDB_API_URL', 'https://api.preciousstone.info')
    # GEMDB API key: prefer environment variable. If not set, look for a local config.json
    GEMDB_API_KEY = os.environ.get('GEMDB_API_KEY', '')

    # If no API key in env var, attempt to load from a `config.json` file in the gems package
    # (matching how gemhunter stores keys in gemhunter/config.json as `gemdb_api_token`).
    if not GEMDB_API_KEY:
        try:
            config_path = os.environ.get('GEMS_CONFIG_PATH') or os.path.join(os.path.dirname(__file__), 'config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as cf:
                    cfg = json.load(cf)
                token = cfg.get('gemdb_api_token') or cfg.get('GEMDB_API_KEY') or cfg.get('gemdb_api_key')
                if token:
                    # token could be a map like 'gems_hub:KEY,desktop_app:KEY2'
                    entries = [e.strip() for e in str(token).split(',') if e.strip()]
                    chosen = None
                    for entry in entries:
                        if ':' in entry:
                            appname, key = entry.split(':', 1)
                            if appname.strip() == 'gems_hub':
                                chosen = key.strip()
                                break
                    if not chosen and entries and ':' in entries[0]:
                        chosen = entries[0].split(':', 1)[1].strip()
                    GEMDB_API_KEY = chosen or str(token).strip()
        except Exception:
            # keep default empty string on error
            pass
