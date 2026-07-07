import json
import os
import re
from datetime import datetime

SERVICE_NAMES = {
    'tiktok': 'TikTok',
    'tinder': 'Tinder',
    'instagram': 'Instagram',
    'snapchat': 'Snapchat',
    'facebook': 'Facebook',
    'twitter': 'Twitter',
    'reddit': 'Reddit',
    'roblox': 'Roblox',
    'youtube': 'YouTube',
    'vk': 'VK',
    'tumblr': 'Tumblr',
    '9gag': '9GAG',
    'telegram': 'Telegram',
    'twitch': 'Twitch',
    'fortnite': 'Fortnite',
    'leagueoflegends': 'League of Legends',
    'discord': 'Discord',
    'messenger': 'Messenger',
    'dailymotion': 'Dailymotion',
    'bereal': 'BeReal',
    'pinterest': 'Pinterest',
    'minecraft': 'Minecraft',
    'blizzard': 'Blizzard',
    'imgur': 'Imgur',
    'hulu': 'Hulu',
    'xboxlive': 'Xbox Live',
    'vimeo': 'Vimeo',
    'netflix': 'Netflix',
    'steam': 'Steam',
    'mastodon': 'Mastodon',
    'skype': 'Skype',
    'playstation-network': 'PlayStation Network',
    'disneyplus': 'Disney+',
    'primevideo': 'Prime Video',
    'hbomax': 'HBO Max',
    'whatsapp': 'WhatsApp',
    'ebay': 'eBay',
    'signal': 'Signal',
    'google-chat': 'Google Chat',
    'spotify': 'Spotify',
    'chatgpt': 'ChatGPT',
    'amazon': 'Amazon',
    'zoom': 'Zoom'
}

def format_relative_time(ts):
    diff = datetime.now().timestamp() - ts
    if diff < 0:
        return "Updated just now"
    if diff < 60:
        return "Updated just now"
    elif diff < 3600:
        mins = int(diff / 60)
        return f"Updated {mins} minute{'s' if mins > 1 else ''} ago"
    elif diff < 86400:
        hours = int(diff / 3600)
        return f"Updated {hours} hour{'s' if hours > 1 else ''} ago"
    else:
        days = int(diff / 86400)
        return f"Updated {days} day{'s' if days > 1 else ''} ago"

def parse_blocklists():
    json_path = 'data/blocklists.json'
    if not os.path.exists(json_path):
        return []
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # The response is typically {"data": [...]}
    items = data.get('data', []) if isinstance(data, dict) else data
    
    blocks = []
    for item in items:
        id_ = item.get('id')
        name = item.get('name')
        description = item.get('description', '')
        website = item.get('website', '')
        entries = item.get('entries', 0)
        updated_on = item.get('updatedOn')

        # Static overrides for nextdns-recommended
        if id_ == 'nextdns-recommended':
            name = 'NextDNS Ads & Trackers Blocklist'
            description = 'A comprehensive blocklist to block ads & trackers in all countries. This is the recommended starter blocklist.'
            website = 'https://nextdns.io'
        
        if not name:
            name = id_.replace('-', ' ').title()

        if updated_on:
            try:
                # Parse ISO8601 string
                dt = datetime.fromisoformat(updated_on.replace('Z', '+00:00'))
                updated_ts = dt.timestamp()
            except Exception:
                updated_ts = datetime.now().timestamp()
        else:
            updated_ts = datetime.now().timestamp()

        updated_text = format_relative_time(updated_ts)
        entries_text = f"{entries:,} entries"

        blocks.append({
            "id": id_,
            "name": name,
            "description": description or "",
            "website": website or "",
            "entries_text": entries_text,
            "entries": entries,
            "updated_text": updated_text,
            "updated_ts": updated_ts,
            "popularity": 0
        })

    # Sort blocks based on original order to assign popularity
    for idx, b in enumerate(blocks):
        b["popularity"] = len(blocks) - idx
        
    return blocks

def parse_services():
    json_path = 'data/websiteapporgame.json'
    if not os.path.exists(json_path):
        return []
    with open(json_path, 'r') as f:
        data = json.load(f)
        
    items = data.get('data', []) if isinstance(data, dict) else data
    
    services = []
    for item in items:
        id_ = item.get('id')
        name = SERVICE_NAMES.get(id_, id_.replace('-', ' ').title())
        services.append({"id": id_, "name": name})
        
    return services

def parse_tlds():
    json_path = 'data/tlds.json'
    if not os.path.exists(json_path):
        return []
    with open(json_path, 'r') as f:
        data = json.load(f)
        
    # The TLDs list is inside {"data": {"tlds": [{"id": "com"}, ...]}}
    tlds_data = data.get('data', {}).get('tlds', []) if isinstance(data, dict) else []
    raw_tlds = [t.get('id') for t in tlds_data if t.get('id')]
    
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

