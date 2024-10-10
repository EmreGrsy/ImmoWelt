from immowelt_urls import AllURLs
from immowelt_parse import ParsePageJson
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import logging
import json


# Configure logging to file and stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("info.log"), logging.StreamHandler()],
)


base_url = "https://www.immowelt.de/liste/hamburg/wohnungen/mieten"

all_urls_scraper = AllURLs(base_url)
expose_links = all_urls_scraper.scrape_all_links()

data = []
num = 0

for link in expose_links:
    page = ParsePageJson(link)
    page_data = page.extract_features()
    data.append(page_data)
    num += 1
    logging.info(f"{num}/{len(expose_links)}")

with open('data.json', 'w') as f:
    json.dump(data, f)