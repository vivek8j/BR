from typing import List, Tuple, Optional, Dict
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
import json
import re
import requests
import logging

from constant import NOT_AVAILABLE, BASE, GROUND_FLOOR_ID, FIRST_FLOOR_ID, VALID_ROOM_KEYWORDS
from fetcher import fetch_soup

postcode_cache = {}
def lookup_postcode_data(postcode: str) -> dict:
    postcode = postcode.strip().upper()
    if not postcode or postcode == "NOT_AVAILABLE":
        return {

            "city": "NOT_AVAILABLE",
            "latitude": "NOT_AVAILABLE",
            "longitude": "NOT_AVAILABLE",
            "area":"NOT_AVAILABLE",
            "subarea":"NOT_AVAILABLE"
        }

    if postcode in postcode_cache:
        return postcode_cache[postcode]

    try:
        encoded = quote(postcode)
        url = f"https://api.postcodes.io/postcodes/{encoded}"
        logging.info(f"Looking up postcode data for: {postcode}")
        r = requests.get(url, timeout=5, verify=False)
        if r.status_code == 200:
            data = r.json().get("result", {})
            city = data.get("admin_district") or data.get("nuts") or "NOT_AVAILABLE"
            latitude = data.get("latitude") or "NOT_AVAILABLE"
            longitude = data.get("longitude") or "NOT_AVAILABLE"
            area = data.get("admin_ward") or "NOT_AVAILABLE"
            subarea = data.get("parish") or "NOT_AVAILABLE"
        else:
            logging.warning(f"Postcode API returned {r.status_code} for {postcode}")
            city = latitude = longitude = area = subarea = "NOT_AVAILABLE"
    except Exception as e:
        logging.warning(f"Postcode API error for {postcode}: {e}")
        city = latitude = longitude = area = subarea = "NOT_AVAILABLE"

    result = {
     
        "city": city,
        "latitude": latitude,
        "longitude": longitude,
        "area":area,
        "subarea":subarea
    }
    postcode_cache[postcode] = result
    return result


def extract_plots(property_url: str, region: str) -> List[Tuple[str, str, str, str]]:
    soup = fetch_soup(property_url)
    if not soup:
        return []

    available_section = soup.find('div', attrs={'data-jump': 'available-homes'})
    if not available_section:
        return []

    plots = []
    plot_cards = available_section.select('.plot-list__plot')

    for card in plot_cards:
        a = card.select_one('a.plot')
        if not a or not a.has_attr('href'):
            continue

        plot_url = urljoin(BASE, a['href'])

        scheme_messages = []
        for cls in ['plot__status-message--custom', 'plot__status-message--highlight', 'plot__details-product-tag']:
            scheme_el = card.select_one(f'.{cls}')
            if scheme_el:
                text = scheme_el.get_text(strip=True)
                if text:
                    title_cased = ' '.join(word.capitalize() for word in text.split())
                    scheme_messages.append(title_cased)

        scheme_offer = " / ".join(scheme_messages) if scheme_messages else NOT_AVAILABLE
        plots.append((plot_url, region, scheme_offer))

    return plots


def parse_plot_data(plot_url: str, region: str, outlet: str, scheme_offer: str, proximity: str) -> Optional[Dict]:
    soup = fetch_soup(plot_url)
    if not soup:
        return None

    info = _get_base_info(region, outlet, scheme_offer, proximity, plot_url)

    header = soup.select_one('.marketing-header')
    if not header:
        return None

    plot_name = header.select_one('.marketing-heading--primary')
    info['PLOT'] = plot_name.get_text(strip=True) if plot_name else NOT_AVAILABLE

    brand_el = header.select_one('.marketing-header__secondary-heading h2.marketing-heading--secondary')
    if brand_el:
        type = brand_el.get_text(strip=True)
        info['TYPE'] = type if type else NOT_AVAILABLE

    addr_el = header.select_one('.marketing-header__address .address')
    address = addr_el.get_text(strip=True) if addr_el else ""
    postcode = (address.split(',')[-1] or "").strip() if address else NOT_AVAILABLE

    info['ADDRESS'] = address
    info['POSTCODE'] = postcode

    address_parts = [part.strip() for part in address.split(',') if part.strip()]

    if len(address_parts) >= 3:
        info['LOCATION'] = address_parts[-3]
        info['COUNTY'] = address_parts[-2]
    else:
        info['LOCATION'] = NOT_AVAILABLE
        info['COUNTY'] = NOT_AVAILABLE

    postcode_data = lookup_postcode_data(postcode)
    info['CITY'] = postcode_data['city']
    info['LATITUDE'] = postcode_data['latitude']
    info['LONGITUDE'] = postcode_data['longitude']


    bedrooms = NOT_AVAILABLE
    price = NOT_AVAILABLE
    availability = "For Sale"

    for li in header.select('.marketing-header__details .icon-list__item'):
        icon = li.find('use')
        if not icon:
            continue
        href = icon.get('xlink:href', "")
        text = li.get_text(strip=True)
        if 'bedroom-bar' in href:
            bedrooms = text
        elif 'price-bar' in href:
            cleaned_text = re.sub(r'(?i)^from\s*', '', text)
            price = cleaned_text
            if "coming soon" in text.lower():
                availability = "Coming Soon"

    info['BEDROOM'] = bedrooms
    info['PRICE_LATEST'] = price
    info['AVAILABILITY'] = availability
    info['PRICE_RANGE']=price

    info['GROUND_FLOOR_DIMENSIONS'] = _extract_dimensions(soup, GROUND_FLOOR_ID)
    info['FIRST_FLOOR_DIMENSIONS'] = _extract_dimensions(soup, FIRST_FLOOR_ID)
    info['PARKING_CONFIGURATION'] = _extract_parking_feature(soup)

    couch_count = _count_keyword_occurrences(
        [info['GROUND_FLOOR_DIMENSIONS'], info['FIRST_FLOOR_DIMENSIONS']],
        VALID_ROOM_KEYWORDS['couch']
    )
    bathroom_count = _count_keyword_occurrences(
        [info['GROUND_FLOOR_DIMENSIONS'], info['FIRST_FLOOR_DIMENSIONS']],
        VALID_ROOM_KEYWORDS['bathroom']
    )

    info['LIVING_ROOM'] = f"{couch_count} Couch" if couch_count else NOT_AVAILABLE
    info['BATHROOM'] = f"{bathroom_count} Bathroom" if bathroom_count else NOT_AVAILABLE
    info['FEATURES'] = _extract_features(soup)

    return info


def _get_base_info(region, outlet, scheme_offer, proximity, url) -> Dict:
    from config import get_base_info
    info = get_base_info()
    info.update({
        "REGION": region,
        # "LOCATION": location,
        "OUTLET": outlet,
        "SCHEMES_OFFERS": scheme_offer,
        "PROXIMITY": proximity,
        "URL": url,
    })
    return info


def _extract_dimensions(soup: BeautifulSoup, floor_id: str) -> str:
    selector = f'button[data-floor-plan-v2-accordion-item-id="{floor_id}"] .floor-plan-v2__accordion-item-content'
    div = soup.select_one(selector)
    if not div:
        return NOT_AVAILABLE
    data = div.get('data-floor-plan-v2-dimensions')
    if not data:
        return NOT_AVAILABLE
    try:
        rooms = json.loads(data.replace('&quot;', '"'))
        lines = []
        for idx, room in enumerate(rooms, 1):
            room_name = room.get('room', '')
            metric = room.get('metric', '')
            imperial = room.get('imperial', '').replace('"', '')
            lines.append(f"{idx}. {room_name} {metric}({imperial})")
        return "\n".join(lines)
    except Exception:
        return NOT_AVAILABLE


def _extract_parking_feature(soup: BeautifulSoup) -> str:
    keywords = ["parking", "garage", "carport", "driveway"]
    features = soup.select('ul.feature-list li.feature-list__item')
    matches = []
    for li in features:
        text = li.get_text(strip=True).lower()
        for keyword in keywords:
            if keyword in text:
                final_value = ' '.join(word.capitalize() for word in text.split())
                if final_value not in matches:
                    matches.append(final_value)
                break
    return "/".join(matches) if matches else NOT_AVAILABLE


def _count_keyword_occurrences(dimensions: List[str], keywords: set) -> int:
    count = 0
    for text in dimensions:
        lines = text.splitlines()
        for line in lines:
            parts = line.split()
            if len(parts) > 1:
                room = parts[1].lower()
                if any(kw in room for kw in keywords):
                    count += 1
    return count


def _extract_features(soup: BeautifulSoup) -> str:
    features = [el.get_text(strip=True) for el in soup.select('.l-icons__icon-title')]
    return " / ".join(features) if features else NOT_AVAILABLE

