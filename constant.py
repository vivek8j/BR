from datetime import datetime

BASE = "https://www.barratthomes.co.uk"

START_URL = f"{BASE}/new-homes/"

NOT_AVAILABLE = "NOT_AVAILABLE"
GROUND_FLOOR_ID = "1"
FIRST_FLOOR_ID = "2"

RUN_DATE = datetime.now().strftime('%m_%d_%Y_%H_%M_%S')

VALID_ROOM_KEYWORDS = {
    "couch": {"living", "lounge", "family", "sitting", "drawing", "front", "common", "den"},
    "bathroom": {"bathroom", "ensuite", "en‑suite", "wc", "shower"}
}

PROXIMITY_KEYWORDS_PATTERN = r'\b(mile|minutes|walk|centre|city|near|close|adjacent|proximity|distance|within|walkable|surrounding)'
