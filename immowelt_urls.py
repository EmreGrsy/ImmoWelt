import pandas as pd
import requests
from bs4 import BeautifulSoup
import math
import logging
from tqdm import tqdm

# Configure logging to file and stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("info.log"), logging.StreamHandler()],
)

class PageURLs:
    """
    This class scraps page URLs from base_url.

    Attributes:
        base_url (str): The base URL that contains all the house listings.

    Methods:
        get_npage: Extract the maximum number of pages in base_url.
        construct_page_url: Construct individual page URLs.
        get_page_url: Get all page_urls in the base_url.
    """

    def __init__(self, base_url):
        self.base_url = base_url
        self.npage = 0
        self.get_npage()

    def get_npage(self):
        try:
            page = requests.get(self.base_url, timeout=10)
            page.raise_for_status()  # Raise an exception for HTTP errors
            elements = BeautifulSoup(page.content, "html.parser")
            logging.info("Base_url is opened")

            for element in elements.find_all("h1"):
                words = element.text.split()
                for word in words:
                    if word.isdigit():
                        nentries = word
                        logging.info(f"There are {nentries} house listings in the base_url.")
            try:
                npage = math.ceil(int(nentries) / 30)  # Assume 30 entries per page
            except:
                npage = math.ceil(int(nentries.replace(".", "")) / 30)  # Remove dots in large numbers
            
            logging.info(f"There are {npage} pages of house listings in the base_url.")

            self.npage = npage
            return 0

        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to open base_url: {e}")
            return 1

    def get_page_urls(self):
        try:
            urls = []
            for page in range(1, self.npage + 1):
                if page == 1:
                    url = (f"https://www.immowelt.de/classified-search?distributionTypes=Rent&estateTypes=Apartment&locations=AD08DE1113&page")
                else:
                    url = (f"https://www.immowelt.de/classified-search?distributionTypes=Rent&estateTypes=Apartment&locations=AD08DE1113&page={page}")
                urls.append(url)
                logging.info(url)
        except Exception as e:
            logging.error(f"An unexpected error occurred while constructing page URLS: {e}")
            return []

        return urls
        

class ExposeLinkExtractor:
    """
    This class scraps housing entries (expose links) from each page URL.
    """

    def __init__(self, url):
        self.url = url

    def extract_expose_links(self):

        try:
            page = requests.get(self.url, timeout=30)
            page.raise_for_status()
            elements = BeautifulSoup(page.content, "html.parser")
            flat_links = elements.find_all("a", href=True)
            expose_links = []

            for link in flat_links:
                link_href = link.get("href")
                if "/expose/" in link_href and "/projekte/expose/" not in link_href:
                    expose_links.append(f"{link_href}")
                    
            return expose_links

        except requests.exceptions.RequestException as e:
            logging.error(f"Error while processing the URL {self.url}: {e}")
            return []  # Return empty list

        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return []


class AllURLs:
    """
    This class scrapes all house listings from the given base_url using ExposeLinkExtractor() and PageURLs().
    """

    def __init__(self, base_url):
        self.base_url = base_url

    def scrape_all_links(self):
        page_scraper = PageURLs(self.base_url)
        urls = page_scraper.get_page_urls()
        all_links = []

        # TODO: remove progress bar when deploying
        with tqdm(total=len(urls), desc="Scraping house listings (expose link) from each page") as pbar:
            for url in urls:
                try:
                    extractor = ExposeLinkExtractor(url)
                    expose_link = extractor.extract_expose_links()
                    logging.info(expose_link)
                    if expose_link is not None:
                        all_links.extend(expose_link)
                except Exception as e:
                    logging.error(f"Failed to scrape links from {url}: {e}")

                pbar.update(1)

        logging.info(f"Total links scraped: {len(all_links)}")
        return all_links
