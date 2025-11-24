import os
import json
from utils.api_client import load_api_key


def test_load_api_key_from_gems_config(tmp_path, monkeypatch):
    # Create a temp gems config file
    cfg = {
        "gemdb_api_url": "http://localhost:8000",
        "gemdb_api_token": "gems_hub:GEMS_CFG_KEY,desktop_app:OTHER"
    }
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text(json.dumps(cfg))

    # Override the environment variable so loader uses cfg path
    monkeypatch.setenv('GEMS_CONFIG_PATH', str(cfg_path))
    # Ensure no other sources override
    monkeypatch.delenv('GEMDB_API_KEY', raising=False)
    monkeypatch.delenv('GEMHUNTER_API_KEY', raising=False)

    key = load_api_key()
    assert key == 'GEMS_CFG_KEY'
