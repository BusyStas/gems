import os
from pathlib import Path
import sys

def load_env_file(env_path):
    if not os.path.exists(env_path):
        print('No env file found at', env_path)
        return
    for line in open(env_path, 'r', encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

def main():
    env_path = Path(__file__).resolve().parents[1] / '.env'  # gems/.env
    load_env_file(str(env_path))
    # Ensure the gems package is on sys.path for imports
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from utils.api_client import load_api_key
    print('GEMDB env var:', os.environ.get('GEMDB_API_KEY'))
    print('load_api_key result:', load_api_key())

if __name__ == '__main__':
    main()
