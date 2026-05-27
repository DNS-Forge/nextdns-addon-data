import re
import json
import os
from datetime import datetime

def parse_relative_date(date_str):
    now = datetime.now().timestamp()
    match = re.search(r'(\d+)\s+(day|hour|month|year|minute|second)', date_str)
    if not match: return now
    val, unit = int(match.group(1)), match.group(2)
    multipliers = {'second': 1, 'minute': 60, 'hour': 3600, 'day': 86400, 'month': 2592000, 'year': 31536000}
    return now - (val * multipliers.get(unit, 0))

def parse_blocklists():
    html_path = 'data/blocklists.html'
    if not os.path.exists(html_path): return []
    with open(html_path, 'r') as f: content = f.read()
    
    # Split content into individual list-group-item divs
    items_html = re.split(r'<div[^>]*class="list-group-item"', content)[1:]
    
    blocks = []
    seen = set()
    
    for html in items_html:
        # Extract Name
        name_match = re.search(r'style="font-weight: 500;">(.*?)</div>', html)
        if not name_match: continue
        name = name_match.group(1).strip()
        if name in seen: continue
        seen.add(name)

        # Extract Description
        desc_match = re.search(r'style="font-size: 0.9em; opacity: 0.5;">(.*?)</div>', html)
        description = desc_match.group(1).strip() if desc_match else ""

        # Extract Website/GitHub link
        link_match = re.search(r'<a target="_blank"[^>]*href="(.*?)"', html)
        website = link_match.group(1).strip() if link_match else ""

        # Extract Entries
        entries_match = re.search(r'style="opacity: 0.4;">(.*?) entries</span>', html)
        entries_text = f"{entries_match.group(1).strip()} entries" if entries_match else "0 entries"
        entry_val = entries_match.group(1).replace(',', '').replace(' ', '') if entries_match else "0"
        entries_count = int(entry_val) if entry_val.isdigit() else 0

        # Extract Updated
        updated_match = re.search(r'style="opacity: 0.4;">Updated (.*?)</span>', html)
        updated_text = f"Updated {updated_match.group(1).strip()}" if updated_match else "Updated unknown"
        updated_ts = parse_relative_date(updated_match.group(1)) if updated_match else datetime.now().timestamp()

        # ID Generation
        id_ = name.lower().replace(' & ', '-').replace(' ', '-').replace('.', '').replace("'", '').replace('(', '').replace(')', '')
        if "nextdns-ads" in id_ and "trackers" in id_: id_ = "nextdns-recommended"

        blocks.append({
            "id": id_,
            "name": name,
            "description": description,
            "website": website,
            "entries_text": entries_text,
            "entries": entries_count,
            "updated_text": updated_text,
            "updated_ts": updated_ts,
            "popularity": 0 
        })

    # Preserve original order for popularity scoring
    for idx, b in enumerate(blocks):
        b["popularity"] = len(blocks) - idx
        
    return blocks

def parse_services():
    html_path = 'data/websiteapporgame.html'
    if not os.path.exists(html_path): return []
    with open(html_path, 'r') as f: content = f.read()
    
    # Improved regex for services to catch all span names
    items = re.findall(r'notranslate"[^>]*style="font-weight: 500;">(.*?)</span>', content)
    seen = set()
    services = []
    for name in items:
        name = name.strip()
        if name in seen: continue
        seen.add(name)
        id_ = name.lower().replace(' ', '-')
        # Normalization mapping
        norm = {"Disney+": "disneyplus", "HBO Max": "hbomax", "Prime Video": "primevideo", "Xbox Live": "xboxlive", "PlayStation Network": "playstation-network", "YouTube": "youtube"}
        id_ = norm.get(name, id_)
        services.append({"id": id_, "name": name})
    return services

def parse_tlds():
    html_path = 'data/tlds.html'
    if not os.path.exists(html_path): return []
    with open(html_path, 'r') as f: content = f.read()
    raw_tlds = re.findall(r'notranslate"[^>]*>\.(.*?)</span>', content)
    filtered = [tld for tld in set(raw_tlds) if re.match(r'^[a-zA-Z0-9.-]+$', tld)]
    return sorted(filtered)

def save_json(data, filename):
    os.makedirs('data', exist_ok=True)
    with open(f'data/{filename}', 'w') as f:
        json.dump(data, f, indent=2)

def main():
    print("Starting comprehensive metadata parse...")
    blocklists = parse_blocklists()
    services = parse_services()
    tlds = parse_tlds()
    
    categories = [
        {"id": "porn", "name": "Porn", "description": "Blocks adult and pornographic content."},
        {"id": "gambling", "name": "Gambling", "description": "Blocks gambling content."},
        {"id": "dating", "name": "Dating", "description": "Blocks all dating websites & apps."},
        {"id": "piracy", "name": "Piracy", "description": "Blocks P2P websites, protocols, etc."},
        {"id": "social-networks", "name": "Social Networks", "description": "Blocks all social networks sites and apps."},
        {"id": "gaming", "name": "Online Gaming", "description": "Blocks online gaming websites and networks."},
        {"id": "video-streaming", "name": "Video Streaming", "description": "Blocks video streaming services."}
    ]

    save_json(blocklists, 'blocklists.json')
    save_json(services, 'parental_services.json')
    save_json(tlds, 'tlds.json')
    save_json(categories, 'categories.json')
    
    index = {
        "last_updated": datetime.now().isoformat(),
        "files": ["blocklists.json", "parental_services.json", "tlds.json", "categories.json"]
    }
    save_json(index, 'blocks_meta.json')
    print(f"Meta updated: {len(blocklists)} blocklists (with websites), {len(services)} services, {len(tlds)} ASCII TLDs.")

if __name__ == "__main__":
    main()
