import requests
from bs4 import BeautifulSoup

class GetLinks:
    """
    This class implements a web scraper for the immowelt.de website, which extracts expose links from real estate listings.

    Attributes:
        url (str): The URL of the web page to be scraped.
        page (Response): The HTTP response object returned by sending a GET request to the URL.
        elements (BeautifulSoup): The BeautifulSoup object representing the parsed HTML content of the page.

    Methods:
        get_expose_links: Extracts the expose links of the listings on the page and returns them as a list.
    """
    def __init__(self, url):
        self.url = url
    
    def get_expose_links(self):
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
