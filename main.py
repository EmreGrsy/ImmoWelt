from immowelt import ImmoWebScraper
from getlinks import GetLinks
import pandas as pd
import time
from tqdm import tqdm
import concurrent.futures

class Schedule:
    """
    A class for scheduling and executing web scraping of ImmoWelt listings.

    This class includes methods for constructing the URLs of the pages to scrape, scraping the links to individual listings
    on each page, and scraping the data from each individual listing.

    Attributes:
        base_url (str): The base URL of the ImmoWelt search results page.
        max_num_pages (int): The maximum number of pages of results to scrape.

    Methods:
        construct_page_urls: Constructs the URLs of the pages to scrape.
        scrape_links: Scrapes the links to individual listings on a given page.
        scrape_data: Scrapes the data from a single ImmoWeb listing.
        scrape_data_from_page_urls: Scrapes the data from all listings on all pages of the search results.
    """
    def __init__(self, base_url, max_num_pages):
        self.base_url = base_url
        self.max_num_pages = max_num_pages
        self.params = {
            "d": "true",
            "sd": "DESC",
            "sf": "RELEVANCE",
        }

    def construct_page_urls(self):
        urls = []
        for page in range(1, self.max_num_pages+1):
            self.params["sp"] = page
            url = f"{self.base_url}?{'&'.join([f'{k}={v}' for k, v in self.params.items()])}"
            urls.append(url)
        return urls

    def scrape_links(self, url):
        try:
            get_links = GetLinks(url)
            expose_links = get_links.get_expose_links()
            return expose_links
        except:
            return None

    def scrape_data(self, link):
        scraper = ImmoWebScraper(link)
        row = {
            "title": scraper.get_title(),
            "address": scraper.get_address(),
            "cold_rent": scraper.get_cold_rent(),
            "warm_rent": scraper.get_warm_rent(),
            "deposit": scraper.get_deposit(),
            "living_space": scraper.get_living_space(),
            "room_number": scraper.get_room_number(),
            "floor" : scraper.get_floor(),
            "availability" : scraper.get_availability(),
            "amenities" : scraper.get_amenities(),
            "built_year" : scraper.get_built_year(),
            "object_detail": scraper.get_detail_object(),
            "furnishing": scraper.get_detail_furnishing(),
            "extra": scraper.get_detail_extra(),
            "timestamp": scraper.get_query_time(),
            "url": link
        }
        return row

    def scrape_data_from_page_urls(self):
        # Get the URLs for each page of results
        page_urls = self.construct_page_urls()

        # Scrape the links to individual listings on each page
        with concurrent.futures.ThreadPoolExecutor() as executor:
            expose_links = list(executor.map(self.scrape_links, page_urls))

        # Flatten the list of links
        expose_links = [link for sublist in expose_links for link in sublist]

        # Scrape the data from each individual listing
        with concurrent.futures.ThreadPoolExecutor() as executor:
            data = list(tqdm(executor.map(self.scrape_data, expose_links)))

        # Return the list of scraped data
        return data


# Define the base URL and number of pages to scrape
base_url = "https://www.immowelt.de/liste/hamburg/wohnungen/mieten"

# I don't know how to limit the max page num.
# If there are 41 pages and I give 50 max page num,
# it turns back after 41 page and gets the first page again.
max_num_pages = 50

start = time.time()
scheduler = Schedule(base_url, max_num_pages)
data = scheduler.scrape_data_from_page_urls()
kk = scheduler.construct_page_urls()
data = pd.DataFrame(data)
end = time.time()

print('Time taken to run: ', end - start)