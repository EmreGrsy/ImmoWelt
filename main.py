from immowelt import ImmoWebScraper
from getlinks import GetLinks
import pandas as pd
import time
from tqdm import tqdm
import concurrent.futures

start = time.time()

url = "https://www.immowelt.de/liste/hamburg/wohnungen/mieten?sort=relevanz"

get_links = GetLinks(url)
expose_links = get_links.get_expose_links()

data = []

def scrape_data(link):
    scraper = ImmoWebScraper(link)
    row = {
        "title": scraper.get_title(),
        "address": scraper.get_address(),
        "cold_rent": scraper.get_cold_rent(),
        "warm_rent": scraper.get_warm_rent(),
        "deposit": scraper.get_deposit(),
        "living_space": scraper.get_living_space(),
        "room_number": scraper.get_room_number(),
        "flat_info": scraper.get_flat_info(),
        "object_detail": scraper.get_detail_object(),
        "furnishing": scraper.get_detail_furnishing(),
        "extra": scraper.get_detail_extra(),
        "timestamp": scraper.get_query_time(),
        "url": link
    }
    return row

with concurrent.futures.ThreadPoolExecutor() as executor:
    results = list(tqdm(executor.map(scrape_data, expose_links), total=4))

df = pd.DataFrame(results)

end = time.time()
print('Time taken to run: ', end - start)