import os
import json
import importlib
import sys
from pathlib import Path

def test_gems_config_json_key_loading(tmp_path, monkeypatch):
    # Create a temporary gems/config.json
    config_json = tmp_path / 'config.json'
    token = 'gems_hub:CONFIG_KEY_GEMS'
    config_json.write_text(json.dumps({'gemdb_api_token': token}))

    # Ensure environment vars are not present
    monkeypatch.delenv('GEMDB_API_KEY', raising=False)
    monkeypatch.delenv('GEMHUNTER_API_KEY', raising=False)
    monkeypatch.setenv('GEMS_CONFIG_PATH', str(config_json))

    # Reload config module so it re-reads the config file
    if 'config' in sys.modules:
        del sys.modules['config']
    import config
    importlib.reload(config)

    assert config.Config.GEMDB_API_KEY == 'CONFIG_KEY_GEMS'
