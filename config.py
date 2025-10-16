from datetime import datetime
from constant import NOT_AVAILABLE, RUN_DATE, COMPETITOR_WEB

OUTPUT_CSV = f"mpi_barratthomes_{RUN_DATE}.csv"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/91.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/82.0.4136.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0",
    "Mozilla/5.0 (Windows NT 6.1; rv:54.0) Gecko/20100101 Firefox/54.0"
]

def get_base_info():
        return {
            "COMPANY_NAME": COMPETITOR_WEB,
            "BRAND_NAME": COMPETITOR_WEB,
            "SOURCE_SITE":COMPETITOR_WEB,
            "OUTLET": NOT_AVAILABLE,
            "REGION": NOT_AVAILABLE,
            "ADDRESS": NOT_AVAILABLE,
            "AREA": NOT_AVAILABLE,
            "SUB_AREA": NOT_AVAILABLE,
            "COUNTY":NOT_AVAILABLE,
            "CITY":NOT_AVAILABLE,
            "LOCATION": NOT_AVAILABLE,
            "POSTCODE": NOT_AVAILABLE,
            "PLOT": NOT_AVAILABLE,
            "TYPE": NOT_AVAILABLE,
            "PROPERTY_TYPE":NOT_AVAILABLE,
            "PRICE_RANGE": NOT_AVAILABLE,
            "PRICE_LATEST": NOT_AVAILABLE,
            "AVAILABILITY": NOT_AVAILABLE,
            "BEDROOM": NOT_AVAILABLE,
            "BATHROOM": NOT_AVAILABLE,
            "LIVING_ROOM": NOT_AVAILABLE,
            "GROUND_FLOOR_DIMENSIONS": NOT_AVAILABLE,
            "FIRST_FLOOR_DIMENSIONS": NOT_AVAILABLE,
            "SECOND_FLOOR_DIMENSIONS":NOT_AVAILABLE,
            "LONGITUDE": NOT_AVAILABLE,
            "LATITUDE": NOT_AVAILABLE,
            "SCHEMES_OFFERS": NOT_AVAILABLE,
            "SCHEMES_OFFERS_DATE":RUN_DATE,	
            "EVENT":NOT_AVAILABLE,
            "EVENT_DATE":NOT_AVAILABLE,
            "FEATURES": NOT_AVAILABLE,
            "TENURE": NOT_AVAILABLE,
            "NHBC_WARRANTY": NOT_AVAILABLE,
            "HBF_STAR_RATING": NOT_AVAILABLE,
            "PARKING_CONFIGURATION": NOT_AVAILABLE,
            "EXPECTED_COMPLETION_DATE": NOT_AVAILABLE,
            "PROXIMITY": NOT_AVAILABLE,
            "RUN_DATE": RUN_DATE,
            "URL": NOT_AVAILABLE
        }

columns_order = list(get_base_info().keys())

