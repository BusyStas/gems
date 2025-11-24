"""
Tiny API client helper for the Gems Hub app.
Provides a minimal wrapper to fetch gem metadata from the shared gemdb API.
"""
import requests
import logging
import os
from flask import current_app

logger = logging.getLogger(__name__)


def _get_secret_from_gcp(secret_id: str = 'gemdb-api-keys') -> str:
    """Return secret from GCP Secret Manager, or None if not available."""
    try:
        from google.cloud import secretmanager
    except Exception:
        return None
    project_id = os.environ.get('GCP_PROJECT_ID')
    if not project_id:
        return None
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode('UTF-8')
    except Exception:
        return None


def load_api_key(preferred_app_name: str = 'gems_hub') -> str | None:
    """Load API key by checking: app config -> Secret Manager -> environment variable.

    If Secret Manager secret contains comma-separated pairs of app:key, the function tries to
    pick a pair with app == preferred_app_name. Otherwise, if secret contains a single value,
    it is interpreted as a raw key.
    """
    # 1) current_app config takes precedence when available
    try:
        cfg_key = current_app.config.get('GEMDB_API_KEY')
        if cfg_key:
            return cfg_key
    except Exception:
        pass

    # 2) Try Secret Manager
    secret_raw = _get_secret_from_gcp()
    if secret_raw:
        # If it's a map like 'app:key,app2:key2', look for our application
        try:
            # Try parse as pairs
            entries = [e.strip() for e in secret_raw.split(',') if e.strip()]
            for entry in entries:
                if ':' in entry:
                    appname, key = entry.split(':', 1)
                    if appname.strip() == preferred_app_name:
                        return key.strip()
            # not found, if the secret looks like 'app:key', return first key
            if entries and ':' in entries[0]:
                return entries[0].split(':', 1)[1].strip()
            # Raw single key
            return secret_raw.strip()
        except Exception:
            # fallback to treat as single key
            return secret_raw.strip()

    # 3) fallback to ENV var
    return os.environ.get('GEMDB_API_KEY') or os.environ.get('GEMHUNTER_API_KEY')


def get_gems_from_api(limit: int = 1000):
    """Return list of gem objects from the API, or None on error.

    The function uses current_app.config for GEMDB_API_URL and GEMDB_API_KEY (optional).
    If the API isn't available, returns None. Caller should fallback to local file parsing.
    """
    try:
        if not current_app:
            return None
        base = current_app.config.get('GEMDB_API_URL', 'https://api.preciousstone.info')
        token = load_api_key() or ''
        url = f"{base.rstrip('/')}/api/v1/gems/"
        params = {'limit': limit}
        headers = {}
        if token:
            headers['X-API-Key'] = token
        r = requests.get(url, params=params, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json()
        else:
            logger.warning(f"Gems API returned {r.status_code}: {r.text}")
            return None
    except Exception as e:
        logger.warning(f"Error calling Gems API: {e}")
        return None


def build_types_structure_from_api(gems_list):
    """Build a types dict compatible with existing YAML structure.

    Returns a dict: { 'Gemstones by Mineral Group': [ { group: [gems...] }, ... ] }
    """
    if not isinstance(gems_list, list):
        return {}
    groups = {}
    for gem in gems_list:
        try:
            name = gem.get('gem_type_name') or gem.get('gem_type_name')
            group = gem.get('Mineral_Group') or 'Miscellaneous'
            groups.setdefault(group, []).append(name)
        except Exception:
            continue

    # Build list as expected (list of dicts or strings)
    section = []
    for grp, gems in sorted(groups.items()):
        section.append({grp: gems})

    return {'Gemstones by Mineral Group': section}
