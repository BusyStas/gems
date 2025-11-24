import os
import importlib
import sys
from pathlib import Path


def test_app_loads_env_from_package(tmp_path, monkeypatch):
    # Create a temporary .env in gems/ (package dir)
    pkg_dir = Path(__file__).resolve().parents[1]
    env_path = pkg_dir / '.env'
    # Write env with a unique key
    env_path.write_text('GEMDB_API_KEY=gems_hub:TEST_KEY_FROM_ENV_FILE\n')

    # Ensure OS env doesn't override
    monkeypatch.delenv('GEMDB_API_KEY', raising=False)
    # Some CI or environment may set test values; explicitly clear it to avoid pollution
    monkeypatch.setenv('GEMDB_API_KEY', '')

    # Remove app modules to force reload
    for mod in list(sys.modules.keys()):
        if mod.startswith('gems.app') or mod == 'app' or mod.startswith('gems.config') or mod == 'config':
            del sys.modules[mod]

    # Now import app and check the config
    sys.path.insert(0, str(pkg_dir))
    import app as loaded_app
    assert loaded_app.app.config.get('GEMDB_API_KEY') == 'gems_hub:TEST_KEY_FROM_ENV_FILE'

    # Cleanup
    env_path.unlink()
