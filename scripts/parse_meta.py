import re
import json
import os
from datetime import datetime

def parse_relative_date(date_str):
    now = datetime.now().timestamp()
    match = re.search(r'(\d+)\s+(day|hour|month|year|minute)', date_str)
    if not match: return now
    val, unit = int(match.group(1)), match.group(2)
    multipliers = {'minute': 60, 'hour': 3600, 'day': 86400, 'month': 2592000, 'year': 31536000}
    return now - (val * multipliers.get(unit, 0))

def parse_blocklists():
    html_path = 'data/blocklists.html'
    if not os.path.exists(html_path): return []
    with open(html_path, 'r') as f: content = f.read()
    
    # Improved regex to handle potential formatting variations in live HTML
    items = re.findall(r'style="font-weight: 500;">(.*?)</div>.*?style="font-size: 0.9em; opacity: 0.5;">(.*?)</div>.*?style="opacity: 0.4;">(.*?) entries</span>.*?style="opacity: 0.4;">Updated (.*?)</span>', content, re.DOTALL)
    
    if not items:
        # Try a more relaxed match for the entry count/updated pattern
        items = re.findall(r'notranslate".*?500;">(.*?)</div>.*?0.5;">(.*?)</div>.*?0.4;">(.*?) entries</span>.*?0.4;">Updated (.*?)</span>', content, re.DOTALL)

    blocks = []
    seen = set()
    for name, desc, entries, updated in items:
        name = name.strip()
        if name in seen: continue
        seen.add(name)
        id_ = name.lower().replace(' & ', '-').replace(' ', '-').replace('.', '').replace("'", '').replace('(', '').replace(')', '')
        if "nextdns-ads" in id_ and "trackers" in id_: id_ = "nextdns-recommended"
        entry_val = entries.replace(',', '').replace(' ', '')
        entry_count = int(entry_val) if entry_val.isdigit() else 0
        blocks.append({
            "id": id_, "name": name, "description": desc.strip(),
            "entries_text": f"{entries.strip()} entries", "entries": entry_count,
            "updated_text": f"Updated {updated.strip()}", "updated_ts": parse_relative_date(updated),
            "popularity": 0 
        })
    for idx, b in enumerate(blocks): b["popularity"] = len(blocks) - idx
    return blocks

def parse_services():
    html_path = 'data/websiteapporgame.html'
    if not os.path.exists(html_path): return []
    with open(html_path, 'r') as f: content = f.read()
    items = re.findall(r'notranslate".*?500;">(.*?)</span>', content)
    seen = set()
    services = []
    for name in items:
        name = name.strip()
        if name in seen: continue
        seen.add(name)
        id_ = name.lower().replace(' ', '-')
        norm = {"Disney+": "disneyplus", "HBO Max": "hbomax", "Prime Video": "primevideo", "Xbox Live": "xboxlive", "PlayStation Network": "playstation-network", "YouTube": "youtube"}
        id_ = norm.get(name, id_)
        services.append({"id": id_, "name": name})
    return services

def main():
    meta = {
        "blocklists": parse_blocklists(),
        "parental_services": parse_services(),
        "tlds": [], # TLDs often require a different parse strategy if in a long list
        "categories": [
            {"id": "porn", "name": "Porn", "description": "Blocks adult and pornographic content."},
            {"id": "gambling", "name": "Gambling", "description": "Blocks gambling content."},
            {"id": "dating", "name": "Dating", "description": "Blocks all dating websites & apps."},
            {"id": "piracy", "name": "Piracy", "description": "Blocks P2P websites, protocols, etc."},
            {"id": "social-networks", "name": "Social Networks", "description": "Blocks all social networks sites and apps."},
            {"id": "gaming", "name": "Online Gaming", "description": "Blocks online gaming websites and networks."},
            {"id": "video-streaming", "name": "Video Streaming", "description": "Blocks video streaming services."}
        ],
        "last_updated": datetime.now().isoformat()
    }
    
    # Load existing meta to preserve data if new parse finds nothing
    if os.path.exists('data/blocks_meta.json'):
        with open('data/blocks_meta.json', 'r') as f:
            old = json.load(f)
            if not meta["blocklists"]: meta["blocklists"] = old.get("blocklists", [])
            if not meta["parental_services"]: meta["parental_services"] = old.get("parental_services", [])
            meta["tlds"] = old.get("tlds", [])
            meta["categories"] = old.get("categories", [])

    with open('data/blocks_meta.json', 'w') as f:
        json.dump(meta, f, indent=2)
    print(f"Meta updated: {len(meta['blocklists'])} blocklists, {len(meta['parental_services'])} services.")

if __name__ == "__main__":
    main()
