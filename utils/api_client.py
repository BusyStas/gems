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


def _get_key_from_gemhunter_config(preferred_app_name: str = 'gems_hub') -> str | None:
    """Deprecated: gemhunter config fallback removed. This function intentionally returns None.
    Gems app now reads keys from gems/config.json as a local config fallback instead.
    """
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
            # If configuration contains a comma-separated mapping (app:key,app2:key2), pick the preferred app
            try:
                entries = [e.strip() for e in str(cfg_key).split(',') if e.strip()]
                for entry in entries:
                    if ':' in entry:
                        appname, key = entry.split(':', 1)
                        if appname.strip() == preferred_app_name:
                            return key.strip()
                # Not found or single value mapping
                if entries and ':' in entries[0]:
                    return entries[0].split(':', 1)[1].strip()
                # Raw single key
                return str(cfg_key).strip()
            except Exception:
                return str(cfg_key).strip()
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
    # If env var contains mapping 'gems_hub:KEY,desktop_app:KEY2', parse and pick preferred_app_name
    env_val = os.environ.get('GEMDB_API_KEY') or os.environ.get('GEMHUNTER_API_KEY')
    if env_val:
        try:
            entries = [e.strip() for e in env_val.split(',') if e.strip()]
            for entry in entries:
                if ':' in entry:
                    appname, key = entry.split(':', 1)
                    if appname.strip() == preferred_app_name:
                        return key.strip()
            # not found, if the env looks like 'app:key', return first key
            if entries and ':' in entries[0]:
                return entries[0].split(':', 1)[1].strip()
            # raw single key
            return env_val.strip()
        except Exception:
            return env_val.strip()
    # 4) Developer convenience: if running locally, attempt to read a gems/config.json file if present.
    # This lets load_api_key work even outside a Flask app context (for tests or small scripts).
    try:
        gems_cfg_path = os.environ.get('GEMS_CONFIG_PATH') or os.path.join(os.path.dirname(__file__), '..', 'config.json')
        if os.path.exists(gems_cfg_path):
            import json
            with open(gems_cfg_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            token = cfg.get('gemdb_api_token') or cfg.get('GEMDB_API_KEY') or cfg.get('gemdb_api_key')
            if token:
                entries = [e.strip() for e in str(token).split(',') if e.strip()]
                for entry in entries:
                    if ':' in entry:
                        appname, key = entry.split(':', 1)
                        if appname.strip() == preferred_app_name:
                            return key.strip()
                if entries and ':' in entries[0]:
                    return entries[0].split(':', 1)[1].strip()
                return str(token).strip()
    except Exception:
        pass
    return None


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


def get_api_health():
    """Return API health endpoint result as a dict: {status, body} or None on error."""
    try:
        base = current_app.config.get('GEMDB_API_URL', 'https://api.preciousstone.info')
        token = load_api_key() or ''
        url = f"{base.rstrip('/')}/health"
        headers = {}
        if token:
            headers['X-API-Key'] = token
        r = requests.get(url, headers=headers, timeout=5)
        try:
            body = r.json()
        except Exception:
            body = r.text
        return {'status_code': r.status_code, 'body': body}
    except Exception as e:
        logger.warning(f"Error calling API health endpoint: {e}")
        return None


def get_api_key_info(preferred_app_name: str = 'gems_hub'):
    """Return a tuple (key, source) where source is 'config', 'secret_manager', 'env', or None
    The key is the parsed single key value (not mapping). If no key is found, returns (None, None).
    """
    try:
        # Check config first
        try:
            cfg_key = current_app.config.get('GEMDB_API_KEY')
            if cfg_key:
                # parse mapping if necessary
                entries = [e.strip() for e in str(cfg_key).split(',') if e.strip()]
                for entry in entries:
                    if ':' in entry:
                        appname, key = entry.split(':', 1)
                        if appname.strip() == preferred_app_name:
                            return key.strip(), 'config'
                if entries and ':' in entries[0]:
                    return entries[0].split(':', 1)[1].strip(), 'config'
                return str(cfg_key).strip(), 'config'
        except Exception:
            pass

        # Check Secret Manager
        sec = _get_secret_from_gcp()
        if sec:
            try:
                entries = [e.strip() for e in str(sec).split(',') if e.strip()]
                for entry in entries:
                    if ':' in entry:
                        appname, key = entry.split(':', 1)
                        if appname.strip() == preferred_app_name:
                            return key.strip(), 'secret_manager'
                if entries and ':' in entries[0]:
                    return entries[0].split(':', 1)[1].strip(), 'secret_manager'
                return str(sec).strip(), 'secret_manager'
            except Exception:
                return str(sec).strip(), 'secret_manager'

        # Fallback to ENV var
        env_val = os.environ.get('GEMDB_API_KEY') or os.environ.get('GEMHUNTER_API_KEY')
        if env_val:
            try:
                entries = [e.strip() for e in env_val.split(',') if e.strip()]
                for entry in entries:
                    if ':' in entry:
                        appname, key = entry.split(':', 1)
                        if appname.strip() == preferred_app_name:
                            return key.strip(), 'env'
                if entries and ':' in entries[0]:
                    return entries[0].split(':', 1)[1].strip(), 'env'
                return env_val.strip(), 'env'
            except Exception:
                return env_val.strip(), 'env'

    except Exception as e:
        logger.warning(f"Error introspecting API key: {e}")
        return None, None



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
