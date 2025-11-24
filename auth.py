from flask import request, jsonify
from functools import wraps
import os
from google.cloud import secretmanager

def get_secret(secret_id):
    """Retrieve secret from Google Secret Manager"""
    client = secretmanager.SecretManagerServiceClient()
    project_id = os.environ.get('GCP_PROJECT_ID')
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode('UTF-8')

# Load API keys from Secret Manager
def load_api_keys():
    """Load API keys from Secret Manager"""
    try:
        keys_str = get_secret('gemdb-api-keys')
        # Format: "gems_hub:key1,crypto_hub:key2,desktop_app:key3"
        keys = {}
        for entry in keys_str.split(','):
            app_name, key = entry.strip().split(':')
            keys[key] = app_name
        return keys
    except Exception as e:
        print(f"Error loading API keys: {e}")
        # Fallback to environment variable for local development
        return {
            os.environ.get('GEMS_HUB_API_KEY'): 'gems_hub',
            os.environ.get('DESKTOP_APP_API_KEY'): 'desktop_app',
        }

VALID_API_KEYS = load_api_keys()

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for API key in header
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({
                'error': 'Missing API key',
                'message': 'Please provide X-API-Key header'
            }), 401
        
        if api_key not in VALID_API_KEYS:
            return jsonify({
                'error': 'Invalid API key',
                'message': 'The provided API key is not valid'
            }), 401
        
        # Store app name in request context for logging/analytics
        request.app_name = VALID_API_KEYS[api_key]
        
        return f(*args, **kwargs)
    
    return decorated_function

def optional_api_key(f):
    """Decorator for endpoints that work with or without API key (different permissions)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if api_key and api_key in VALID_API_KEYS:
            request.app_name = VALID_API_KEYS[api_key]
            request.authenticated = True
        else:
            request.app_name = 'anonymous'
            request.authenticated = False
        
        return f(*args, **kwargs)
    
    return decorated_function


