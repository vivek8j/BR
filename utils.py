import os
import json
import random
import string
import time

from config import USER_AGENTS
from constant import BASE

SCRAPED_LOG_FILE = "scraped_plots.txt"
CHECKPOINT_FILE = "checkpoint.json"


def human_delay():
    time.sleep(random.uniform(1, 1))  # Adjust if needed


def generate_random_cookies():
    return {
        'sessionid': ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)),
        'csrftoken': ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)),
        'accept_language': 'en-US,en;q=0.9',
        'accept_encoding': 'gzip, deflate, br',
        'referer': f"{BASE}/new-homes/"
    }

def get_headers():
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": f"{BASE}/new-homes/"
    }
    cookies = generate_random_cookies()
    headers["Cookie"] = "; ".join(f"{k}={v}" for k, v in cookies.items())
    return headers

def load_scraped_urls() -> set:
    if not os.path.exists(SCRAPED_LOG_FILE):
        return set()
    with open(SCRAPED_LOG_FILE, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f if line.strip())

def save_scraped_url(url: str):
    with open(SCRAPED_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(url.strip() + '\n')

def save_checkpoint(location_url: str, property_url: str, plot_url: str):
    checkpoint = {
        "location_url": location_url,
        "property_url": property_url,
        "plot_url": plot_url
    }
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, indent=2)

def load_checkpoint():
    if not os.path.exists(CHECKPOINT_FILE):
        return None
    with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def clear_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)

