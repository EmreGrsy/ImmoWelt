from immowelt_scrapper import ImmoWeltScrapper
from immowelt_urls import AllURLs
import pandas as pd
from tqdm import tqdm
import concurrent.futures


class ImmoWeltData:
    """
    This class gets individual real estate urls and scrapes their data.
    This is where the magic happens :)
    """
    def __init__(self, base_url):
        self.base_url = base_url

    def scrape_data(self, link):
        scraper = ImmoWeltScrapper(link)
        row = {
            "title": scraper.get_title(),
            "address": scraper.get_address(),
            "cold_rent": scraper.get_cold_rent(),
            "warm_rent": scraper.get_warm_rent(),
            "deposit": scraper.get_deposit(),
            "living_space": scraper.get_living_space(),
            "room_number": scraper.get_room_number(),
            "floor": scraper.get_floor(),
            "availability": scraper.get_availability(),
            "amenities": scraper.get_amenities(),
            "built_year": scraper.get_built_year(),
            "energy_consumption": scraper.get_energy_consumption(),
            "object_detail": scraper.get_detail_object(),
            "furnishing": scraper.get_detail_furnishing(),
            "extra": scraper.get_detail_extra(),
            "timestamp": scraper.get_query_time(),
            "url": link
        }
        return row
    
    def scrape_data_from_page_urls(self):
        all_urls_scraper = AllURLs(self.base_url)
        expose_links = all_urls_scraper.scrape_all_links()

        all_data = []
        with tqdm(total=len(expose_links), desc="Gathering real estate information") as pbar:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for result in executor.map(self.scrape_data, expose_links):
                    all_data.append(result)
                    pbar.update(1)
        
        return all_data