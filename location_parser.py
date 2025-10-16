
from urllib.parse import urljoin, urlparse
from typing import Iterator, Tuple
from fetcher import fetch_soup
from constant import BASE, NOT_AVAILABLE


def extract_locations(start_url: str) -> Iterator[Tuple[str, str, str]]:
    soup = fetch_soup(start_url)
    if not soup:
        return
    for a in soup.select('.location-group__list .location-group__link'):
        href = a.get('href')
        if not href:
            continue
        full_url = urljoin(BASE, href)
        region,_ = _parse_location_parts(full_url)

        yield full_url, region



def _parse_location_parts(url: str) -> Tuple[str, str]:
    parts = urlparse(url).path.strip('/').split('/')
    if len(parts) >= 3:
        return parts[1].replace('-', ' ').title(), parts[2].replace('-', ' ').title()
    return NOT_AVAILABLE, NOT_AVAILABLE

