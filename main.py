from immowelt_data import ImmoWeltData
import pandas as pd
import time


# Define the base URL
base_url = "https://www.immowelt.de/liste/hamburg/wohnungen/mieten"

start = time.time()
scraper = ImmoWeltData(base_url)
data = scraper.scrape_data_from_page_urls()
data = pd.DataFrame(data)
end = time.time()

print('Time taken to run: ', end - start)