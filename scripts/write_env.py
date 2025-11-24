"""
Utility to write a simple `.env` file containing GEMDB_API_KEY in the gems/ directory.
Use this to add your local API key without committing secrets into VCS.

Usage:
    python scripts/write_env.py --key "YOUR_KEY_HERE"

This will write (or overwrite) `gems/.env` with GEMDB_API_KEY and default settings.
"""
import argparse
import os
import textwrap


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--key', required=True, help='GEMDB API key or map (e.g. gems_hub:KEY)')
    args = p.parse_args()

    # location of the .env in the gems package
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    env_path = os.path.join(root, '.env')

    content = textwrap.dedent(f"""
    # Local environment variables for Gems Hub (auto-generated)
    GEMDB_API_KEY={args.key}
    FLASK_DEBUG=True
    SECRET_KEY=dev-secret-key-change-in-production
    """)

    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Wrote {env_path} (do not commit this file to VCS)")


if __name__ == '__main__':
    main()
