import re
from typing import Iterator, Tuple
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from fetcher import fetch_soup
from constant import BASE, NOT_AVAILABLE, PROXIMITY_KEYWORDS_PATTERN
import logging



def extract_properties(location_url: str, region: str) -> Iterator[Tuple[str, str, str]]:
    soup = fetch_soup(location_url)
    if not soup:
        return
    for card in soup.select('.location-list-card'):
        a = card.select_one('a.location-list-card__heading')
        if a and a.has_attr('href'):
            yield urljoin(BASE, a['href']), region
            # yield urljoin(BASE, a['href']), region, location

def extract_outlet_and_proximity(prop_url: str) -> Tuple[str, str]:
    soup = fetch_soup(prop_url)
    if not soup:
        return NOT_AVAILABLE, NOT_AVAILABLE

    outlet = soup.select_one('.breadcrumb__item-link--current')
    outlet = outlet.get_text(strip=True) if outlet else NOT_AVAILABLE

    proximities = [
        item.get_text(strip=True)
        for item in soup.select('.feature-list__item-text')
        if re.search(PROXIMITY_KEYWORDS_PATTERN, item.get_text(strip=True), re.I)
    ]

    return outlet, " / ".join(proximities) if proximities else NOT_AVAILABLE

