import logging
import time
import requests
# from bs4 import BeautifulSoup
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
from utils import get_headers

# Disable SSL verification warnings (can remove this if using valid certs)
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

class FetchFailed(Exception):
    pass


def fetch_soup(url: str, retries: int = 3, backoff: int = 2):
    for attempt in range(retries):
        try:
            logging.info(f"�� Fetching: {url}")
            headers = get_headers()

            response = requests.get(
                url,
                headers=headers,
                timeout=10,
                verify=False  # Only if your production SSL fails; otherwise, use verify=True
            )

            if response.status_code == 200:
                return BeautifulSoup(response.text, "html.parser")
            logging.warning(f"Non-200 status {response.status_code} on {url}")

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching {url} (attempt {attempt + 1}): {e}")

        time.sleep(backoff ** attempt)

    raise FetchFailed(f"Failed to fetch {url} after {retries} attempts.")
