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
    
    items_html = re.split(r'<div[^>]*class="list-group-item"', content)[1:]
    
    blocks = []
    seen = set()
    
    for html in items_html:
        name_match = re.search(r'style="font-weight: 500;">(.*?)</div>', html)
        if not name_match: continue
        name = name_match.group(1).strip()
        if name in seen: continue
        seen.add(name)

        desc_match = re.search(r'style="font-size: 0.9em; opacity: 0.5;">(.*?)</div>', html)
        description = desc_match.group(1).strip() if desc_match else ""

        link_match = re.search(r'<a target="_blank"[^>]*href="(.*?)"', html)
        website = link_match.group(1).strip() if link_match else ""

        entries_match = re.search(r'style="opacity: 0.4;">(.*?) entries</span>', html)
        entries_text = f"{entries_match.group(1).strip()} entries" if entries_match else "0 entries"
        entry_val = entries_match.group(1).replace(',', '').replace(' ', '') if entries_match else "0"
        entries_count = int(entry_val) if entry_val.isdigit() else 0

        updated_match = re.search(r'style="opacity: 0.4;">Updated (.*?)</span>', html)
        updated_text = f"Updated {updated_match.group(1).strip()}" if updated_match else "Updated unknown"
        updated_ts = parse_relative_date(updated_match.group(1)) if updated_match else datetime.now().timestamp()

        id_ = name.lower().replace(' & ', '-').replace(' ', '-').replace('.', '').replace("'", '').replace('(', '').replace(')', '')
        if "nextdns-ads" in id_ and "trackers" in id_: id_ = "nextdns-recommended"

        blocks.append({
            "id": id_, "name": name, "description": description, "website": website,
            "entries_text": entries_text, "entries": entries_count, "updated_text": updated_text,
            "updated_ts": updated_ts, "popularity": 0 
        })

    for idx, b in enumerate(blocks):
        b["popularity"] = len(blocks) - idx
        
    return blocks

def parse_services():
    html_path = 'data/websiteapporgame.html'
    if not os.path.exists(html_path): return []
    with open(html_path, 'r') as f: content = f.read()
    
    items = re.findall(r'notranslate"[^>]*style="font-weight: 500;">(.*?)</span>', content)
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

def parse_tlds():
    html_path = 'data/tlds.html'
    if not os.path.exists(html_path): return []
    with open(html_path, 'r') as f: content = f.read()
    raw_tlds = re.findall(r'notranslate"[^>]*>\.(.*?)</span>', content)
    filtered = [tld for tld in set(raw_tlds) if re.match(r'^[a-zA-Z0-9.-]+$', tld)]
    return sorted(filtered)

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

    # Revert to single JSON payload
    meta = {
        "last_updated": datetime.now().isoformat(),
        "blocklists": blocklists,
        "parental_services": services,
        "tlds": tlds,
        "categories": categories
    }

    os.makedirs('data', exist_ok=True)
    with open('data/blocks_meta.json', 'w') as f:
        json.dump(meta, f, indent=2)
        
    print(f"Meta updated in blocks_meta.json: {len(blocklists)} blocklists, {len(services)} services, {len(tlds)} ASCII TLDs.")

if __name__ == "__main__":
    main()
