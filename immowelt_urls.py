from tqdm import tqdm
import concurrent.futures
import requests
from bs4 import BeautifulSoup
import math

class PageURLs:
    """
    This class scraps page URLs of the given base_url.

    Attributes:
        base_url (str): The base URL that contains all the house listings.

    Methods:
        get_max_page: Extract the maximum number of pages in base_url.
        construct_page_url: Construct the each individual page URL.
        page_url: Define all page urls given in the base_url.
    """
    def __init__(self, base_url):
        self.base_url = base_url
        self.params = {
            "d": "true",
            "sd": "DESC",
            "sf": "RELEVANCE",
        }

    def get_max_page(self):
        page = requests.get(self.base_url)
        elements = BeautifulSoup(page.content, "html.parser")  
        for element in elements.find_all('h1'):
            nentries = element.text.split()[0]
            npages = math.ceil(int(nentries) / 20)
        return npages
    
    def construct_page_url(self, page):
        self.params["sp"] = page
        url = f"{self.base_url}?{'&'.join([f'{k}={v}' for k, v in self.params.items()])}"
        return url

    def page_urls(self):
        max_pages = self.get_max_page()
        urls = []
        with tqdm(total=max_pages, desc="Constructing page URLs") as pbar:
            for page in range(1, max_pages + 1):
                url = self.construct_page_url(page)
                urls.append(url)
                pbar.update(1)
        return urls

class ExposeLinkExtractor:
    """
    This class scraps rental entries from page URL.
    """
    def __init__(self, url):
        self.url = url
    
    def extract_expose_links(self):
        try:
            page = requests.get(self.url)
            elements = BeautifulSoup(page.content, "html.parser")
            flat_links = elements.find_all("a", href=True)

            expose_links = []
            for link in flat_links:
                link_href = link.get("href")
                if "/expose/" in link_href and "/projekte/expose/" not in link_href:
                    expose_links.append(link_href)

            return expose_links
        except:
            print("An error occurred while processing the URL.")
            return []
        
class AllURLs:
    """
    This class scraps each listing from the given base_URL using ExposeLinkExtractor() and PageURLs() function.
    """
    def __init__(self, base_url):
        self.base_url = base_url

    def scrape_links(self, url):
        try:
            extractor = ExposeLinkExtractor(url)
            expose_links = extractor.extract_expose_links()
            return expose_links
        except:
            return None
    
    def scrape_all_links(self):
        page_scraper = PageURLs(self.base_url)
        urls = page_scraper.page_urls()
        
        all_urls = []
        with tqdm(total=len(urls), desc="Scraping individual URLs from each page") as pbar:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for links in executor.map(self.scrape_links, urls):
                    if links is not None:
                        all_urls.extend(links)
                    pbar.update(1)
        
        return all_urls