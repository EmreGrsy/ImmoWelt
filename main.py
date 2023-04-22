from immowelt import ImmoWebScraper
from getlinks import GetLinks
import pandas as pd
import time
from tqdm import tqdm
import concurrent.futures

start = time.time()

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


# Define the base URL and query parameters
base_url = "https://www.immowelt.de/liste/hamburg/wohnungen/mieten"
params = {
    "d": "true",
    "sd": "DESC",
    "sf": "RELEVANCE",
    "cp": 1  # Start with the first page of results
}

data = []

# Loop through all the pages of results
while True:
    # Construct the URL for the current page of results
    url = f"{base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"

    # Scrape the links to individual listings on the page
    get_links = GetLinks(url)
    expose_links = get_links.get_expose_links()

    # Check if there are no more pages to scrape
    if not expose_links:
        break

    # Scrape the data from each individual listing on the page
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(tqdm(executor.map(scrape_data, expose_links), total=len(expose_links)))

    # Add the results to the master list
    data.extend(results)

    # Update the query parameters to get the next page of results
    params["cp"] += 1

# Convert the list of results to a Pandas DataFrame
df = pd.DataFrame(data)

end = time.time()
print('Time taken to run: ', end - start)