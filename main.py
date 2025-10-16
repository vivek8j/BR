import logging
import sys
import io
from typing import Optional, Dict
from utils import human_delay, load_scraped_urls, save_scraped_url, save_checkpoint, load_checkpoint, clear_checkpoint
from config import columns_order
from writer import append_to_csv,ensure_columns
from fetcher import FetchFailed
from parsers.location_parser import extract_locations
from parsers.property_parser import extract_properties, extract_outlet_and_proximity
from parsers.plot_parser import extract_plots, parse_plot_data
from constant import START_URL, NOT_AVAILABLE, RUN_DATE

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("scraper.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

####Good
def scrape_plot(
    plot_url: str,
    region: str,
    # location: str,
    outlet: str,
    scheme_offer: str,
    proximity: str,
    location_url: str,
    property_url: str
) -> Optional[Dict]:
    try:
        data = parse_plot_data(plot_url,region, outlet, scheme_offer, proximity)
        # data = parse_plot_data(plot_url, region, location, outlet, scheme_offer, proximity)
        if data:
            append_to_csv(data, columns_order)
            save_scraped_url(plot_url)
            save_checkpoint(location_url, property_url, plot_url)
        return data
    except FetchFailed as e:
        logging.error(f"Fetch failed for plot URL {plot_url}: {e}")
        raise e
    except Exception as e:
        logging.error(f"Unexpected error parsing plot {plot_url}: {e}", exc_info=True)
        raise e

# def scrape_plot(
#     plot_url: str,
#     region: str,
#     location: str,
#     outlet: str,
#     scheme_offer: str,
#     proximity: str,
#     location_url: str,
#     property_url: str
# ) -> Optional[Dict]:
#     try:
#         data = parse_plot_data(plot_url, region, location, outlet, scheme_offer, proximity)
#         if data:
#             sanitized_data = ensure_columns(data, columns_order)  # Sanitize the data before saving
#             append_to_csv(sanitized_data, columns_order)
#             save_scraped_url(plot_url)
#             save_checkpoint(location_url, property_url, plot_url)
#         return data
#     except FetchFailed as e:
#         logging.error(f"Fetch failed for plot URL {plot_url}: {e}")
#         raise e
#     except Exception as e:
#         logging.error(f"Unexpected error parsing plot {plot_url}: {e}", exc_info=True)
#         raise e


def scrape_property(property_url: str, region: str, location_url: str,
                    scraped_urls: set, resume_plot: Optional[str]) -> None:
# def scrape_property(property_url: str, region: str, location: str, location_url: str,
                    # scraped_urls: set, resume_plot: Optional[str]) -> None:
    human_delay()
    outlet, proximity = extract_outlet_and_proximity(property_url)
    outlet = outlet or NOT_AVAILABLE
    proximity = proximity or NOT_AVAILABLE

    plots = extract_plots(property_url,region)
    # plots = extract_plots(property_url, region, location)
    logging.info(f"Found {len(plots)} plots for {property_url}")

    resume_found = resume_plot is None

    for plot_url, _, scheme_offer in plots:
    # for plot_url, _, _, scheme_offer in plots:
        if not resume_found:
            if plot_url == resume_plot:
                resume_found = True
            else:
                continue  # skip until match
        if plot_url in scraped_urls:
            logging.info(f"✅ Already scraped: {plot_url}")
            continue
        human_delay()
        scrape_plot(plot_url,region,outlet, scheme_offer, proximity, location_url, property_url)
        # scrape_plot(plot_url, region, location, outlet, scheme_offer, proximity, location_url, property_url)

def scrape_location(location_url: str, region: str,
                    scraped_urls: set, resume_property_url: Optional[str],
                    resume_plot_url: Optional[str]) -> None:
# def scrape_location(location_url: str, region: str, location: str,
#                     scraped_urls: set, resume_property_url: Optional[str],
#                     resume_plot_url: Optional[str]) -> None:
    properties = list(extract_properties(location_url, region))
    # properties = list(extract_properties(location_url, region, location))

    resume_found = resume_property_url is None

    for property_url, _ in properties:
    # for property_url, _, _ in properties:
        if not resume_found:
            if property_url == resume_property_url:
                resume_found = True
            else:
                continue  # skip until match

        scrape_property(property_url, region, location_url, scraped_urls,
                        resume_plot_url if property_url == resume_property_url else None)
        # scrape_property(property_url, region, location, location_url, scraped_urls,
        #                 resume_plot_url if property_url == resume_property_url else None)

def main() -> None:
    logging.info("Starting scrape from: %s on %s", START_URL, RUN_DATE)

    scraped_urls = load_scraped_urls()
    checkpoint = load_checkpoint()

    resume_location_url = checkpoint.get("location_url") if checkpoint else None
    resume_property_url = checkpoint.get("property_url") if checkpoint else None
    resume_plot_url = checkpoint.get("plot_url") if checkpoint else None

    try:
        resume_found = resume_location_url is None

        for location_url, region in extract_locations(START_URL):
        # for location_url, region, location in extract_locations(START_URL):    
            if not resume_found:
                if location_url == resume_location_url:
                    resume_found = True
                else:
                    continue  # skip

            scrape_location(location_url, region, scraped_urls,
                            resume_property_url if location_url == resume_location_url else None,
                            resume_plot_url if location_url == resume_location_url else None)
            # scrape_location(location_url, region, location, scraped_urls,
            #                 resume_property_url if location_url == resume_location_url else None,
            #                 resume_plot_url if location_url == resume_location_url else None)

        # ✅ Finished successfully
        logging.info("Scraping completed successfully. Clearing checkpoint.")
        clear_checkpoint()

    except KeyboardInterrupt:
        logging.warning("Interrupted by user. Partial data saved.")
    except Exception as e:
        logging.error("Critical error in main loop: %s", str(e), exc_info=True)

if __name__ == "__main__":
    main()
