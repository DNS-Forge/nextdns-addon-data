import subprocess
import json
import os
import sys
from datetime import datetime

# Constants
RAW_PRIVACY_JSON = "data/privacy_raw.json"
# We will transition these HTML files to JSON soon
BLOCKLISTS_HTML = "data/blocklists.html" 
SERVICES_HTML = "data/websiteapporgame.html"
TLDS_HTML = "data/tlds.html"

# 1. Retrieve the API Key from the environment
API_KEY = os.environ.get('NEXTDNS_API_KEY')

# Prevent the script from running if the API Key is missing
if not API_KEY:
    print("Error: NEXTDNS_API_KEY environment variable is not set.", file=sys.stderr)
    print("Please set it using: export NEXTDNS_API_KEY='your_api_key_here'", file=sys.stderr)
    sys.exit(1)

# 2. Update Headers to use X-Api-Key instead of Cookie
BASE_HEADERS = [
    '-H', 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:151.0) Gecko/20100101 Firefox/151.0',
    '-H', 'Accept: application/json', # Explicitly request JSON from the API
    '-H', f'X-Api-Key: {API_KEY}',    # Official NextDNS API Authentication
    '--compressed'
]

def fetch_url(url, output_file):
    print(f"Fetching {url}...")
    cmd = ['curl', '-L', '-s', url] + BASE_HEADERS
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        content = result.stdout
        
        # Check for authentication error from the API
        if '{"errors":' in content and 'unauthorized' in content.lower():
             print(f"Error: API Key is invalid or unauthorized for {url}.")
             return False
            
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return False

def sync():
    if os.path.exists('scripts/sync_metadata.py'): root = '.'
    else: root = '..'; os.chdir(root)

    # Note: We are still hitting the HTML dashboard for these three until we map 
    # out the exact API JSON endpoints for them in the next step.
    fetch_url('https://api.nextdns.io/profiles/889455/privacy', RAW_PRIVACY_JSON)
    fetch_url('https://my.nextdns.io/889455/privacy', BLOCKLISTS_HTML)
    fetch_url('https://my.nextdns.io/889455/parentalcontrol', SERVICES_HTML)
    fetch_url('https://my.nextdns.io/889455/security', TLDS_HTML)

    print("Running metadata parser...")
    subprocess.run(['python3', 'scripts/parse_meta.py'], check=True)
    print("Metadata sync complete.")

if __name__ == "__main__":
    sync()