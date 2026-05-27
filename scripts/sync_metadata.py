import subprocess
import json
import os
import sys
from datetime import datetime

# Constants
# When running as a script, we assume current working directory is the repo root
RAW_PRIVACY_JSON = "data/privacy_raw.json"
BLOCKLISTS_HTML = "data/blocklists.html"
SERVICES_HTML = "data/websiteapporgame.html"
TLDS_HTML = "data/tlds.html"

# Use environment variable for cookie
DEFAULT_COOKIE = 'pst=s%3AYRHOVOLQYXO6dn8Nm7c1Ni8917vM%2FsXzTDjBMZQsdfc%3D.W%2BWZVNJKOsMcdgq8DhgBo8xk2zGEEGP06Rvb%2B0%2Br31M; sid=s%3Aln6mzmzltsAJPOODcnXm3tBAUb29Tcfe.c226pTP7IjE2%2FN%2FJChfR6V%2F2%2FSa9sKnJUaPg41vFF3U'
COOKIE = os.environ.get('NEXTDNS_COOKIE', DEFAULT_COOKIE)

BASE_HEADERS = [
    '-H', 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:151.0) Gecko/20100101 Firefox/151.0',
    '-H', 'Accept: */*',
    '-H', 'Accept-Language: en-US,en;q=0.9',
    '-H', 'Origin: https://my.nextdns.io',
    '-H', 'Referer: https://my.nextdns.io/',
    '-H', f'Cookie: {COOKIE}',
    '--compressed'
]

def fetch_url(url, output_file):
    print(f"Fetching {url}...")
    cmd = ['curl', '-L', url] + BASE_HEADERS
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(result.stdout)
        return True
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return False

def sync():
    # Identify repo root (handle being run from scripts/ dir or repo root)
    if os.path.exists('scripts/sync_metadata.py'):
        root = '.'
    else:
        root = '..'
        os.chdir(root)

    # 1. Fetch JSON (The actual API state)
    fetch_url('https://api.nextdns.io/profiles/889455/privacy', RAW_PRIVACY_JSON)
    
    # 2. Fetch HTMLs from the Dashboard
    fetch_url('https://my.nextdns.io/889455/privacy', BLOCKLISTS_HTML)
    fetch_url('https://my.nextdns.io/889455/parentalcontrol', SERVICES_HTML)
    fetch_url('https://my.nextdns.io/889455/security', TLDS_HTML)

    print("Running metadata parser...")
    subprocess.run(['python3', 'scripts/parse_meta.py'], check=True)
    print("Metadata sync complete.")

if __name__ == "__main__":
    sync()
