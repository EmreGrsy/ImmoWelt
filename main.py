from immowelt import ImmoWebScraper
from getlinks import GetLinks
import pandas as pd
import time
from tqdm import tqdm

start = time.time()

url = "https://www.immowelt.de/liste/hamburg/wohnungen/mieten?sort=relevanz"

get_links = GetLinks(url)
expose_links = get_links.get_expose_links()

data = []
for link in tqdm(expose_links):
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
        "timestamp": scraper.get_timestamp(),
        "url": link
    }
    data.append(row)

df = pd.DataFrame(data)

end = time.time()
print('Time taken to run: ', end - start)