import json
import os
import sys
import requests

# Constants
RAW_PRIVACY_JSON = "data/privacy_raw.json"
BLOCKLISTS_JSON = "data/blocklists.json"
SERVICES_JSON = "data/websiteapporgame.json"
TLDS_JSON = "data/tlds.json"

# 1. Retrieve the API Key from the environment
API_KEY = os.environ.get('NEXTDNS_API_KEY')

if not API_KEY:
    print("Error: NEXTDNS_API_KEY environment variable is not set.", file=sys.stderr)
    print("Please set it using: export NEXTDNS_API_KEY='your_api_key_here'", file=sys.stderr)
    sys.exit(1)

HEADERS = {
    'Accept': 'application/json',
    'X-Api-Key': API_KEY,
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:151.0) Gecko/20100101 Firefox/151.0'
}

def fetch_json(url, output_file):
    print(f"Fetching {url}...")
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Error fetching {url}: HTTP {response.status_code} - {response.text}", file=sys.stderr)
            return False
        
        data = response.json()
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return False

def resolve_profile_id():
    url = 'https://api.nextdns.io/profiles'
    print(f"Resolving profile ID dynamically from {url}...")
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Error fetching profiles: HTTP {response.status_code} - {response.text}", file=sys.stderr)
            return None
        
        data = response.json()
        profiles = data.get('data', [])
        if not profiles:
            print("Error: No profiles found for this NextDNS account.", file=sys.stderr)
            return None
        
        # Try to find a profile named "Default" (case-insensitive)
        for p in profiles:
            if p.get('name', '').strip().lower() == 'default':
                pid = p.get('id')
                print(f"Found 'Default' profile with ID: {pid}")
                return pid
        
        # Fall back to the first profile in the list
        pid = profiles[0].get('id')
        print(f"No 'Default' profile found. Falling back to the first profile: {profiles[0].get('name')} (ID: {pid})")
        return pid
    except Exception as e:
        print(f"Error resolving profile ID: {e}", file=sys.stderr)
        return None

def sync():
    if os.path.exists('scripts/sync_metadata.py'):
        root = '.'
    else:
        root = '..'
        os.chdir(root)

    profile_id = resolve_profile_id()
    if not profile_id:
        print("Error: Could not resolve dynamic profile ID. Aborting sync.", file=sys.stderr)
        sys.exit(1)

    success = True
    success &= fetch_json(f'https://api.nextdns.io/profiles/{profile_id}/privacy', RAW_PRIVACY_JSON)
    success &= fetch_json('https://api.nextdns.io/privacy/blocklists', BLOCKLISTS_JSON)
    success &= fetch_json('https://api.nextdns.io/parentalcontrol/services', SERVICES_JSON)
    success &= fetch_json(f'https://api.nextdns.io/profiles/{profile_id}/security', TLDS_JSON)

    if not success:
        print("Error: One or more fetches failed. Aborting metadata parsing.", file=sys.stderr)
        sys.exit(1)

    print("Running metadata parser...")
    import subprocess
    subprocess.run(['python3', 'scripts/parse_meta.py'], check=True)
    print("Metadata sync complete.")

if __name__ == "__main__":
    sync()