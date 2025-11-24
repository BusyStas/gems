"""
Copy gemhunter/config.json to gems/config.json for local development convenience.
Usage:
    python scripts/sync_gemhunter_config.py
Optionally set GEMHUNTER_CONFIG_PATH or GEMS_CONFIG_PATH environment variables to override paths.
"""
import os
import json
from pathlib import Path


def main():
    repo_root = Path(__file__).resolve().parents[1]
    gemhunter_path = Path(os.environ.get('GEMHUNTER_CONFIG_PATH') or repo_root.parent / 'gemhunter' / 'config.json')
    dest = Path(os.environ.get('GEMS_CONFIG_PATH') or repo_root / 'config.json')

    if not gemhunter_path.exists():
        print(f"gemhunter config not found at: {gemhunter_path}")
        return 1

    # Read and write (preserve as-is)
    try:
        data = json.loads(gemhunter_path.read_text(encoding='utf-8'))
        dest.write_text(json.dumps(data, indent=4), encoding='utf-8')
        print(f"Copied {gemhunter_path} -> {dest}")
        return 0
    except Exception as e:
        print('Failed to copy config:', e)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
