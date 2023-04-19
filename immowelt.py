import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime

class ImmoWeltScraper:
    """
    This class implements a web scraper for the immowelt.de website, which extracts information from real estate listings.

    Attributes:
        url (str): The URL of the web page to be scraped.
        page (Response): The HTTP response object returned by sending a GET request to the URL.
        elements (BeautifulSoup): The BeautifulSoup object representing the parsed HTML content of the page.

    Methods:
        get_title: Extracts the title of the listing.
        get_address: Extracts the address of the listing.
        get_cost: Extracts the monthly cost of the listing.
        get_deposit: Extracts the required deposit for the listing.
        get_living_space: Extracts the living space of the listing.
        get_room_number: Extracts the number of rooms of the listing.
        get_timestamp: Returns the current timestamp.
        scrape: Executes all the above methods and returns the extracted information as a Pandas DataFrame.
    """

    def __init__(self, url):
        self.url = url
        self.page = requests.get(url)
        self.elements = BeautifulSoup(self.page.content, "html.parser")
        
    def get_title(self):
        title = self.elements.find('h1').text.strip()
        return title
    
    def get_address(self):
        addresses = self.elements.find_all('span', {'data-cy': re.compile(r'.*address.*')})
        address_details = []
        for address in addresses:
            address_text = address.text.strip().replace('\n', '')
            address_text = re.sub(r'\s+', ' ', address_text)
            address_details.append(address_text)
        address = ', '.join(address_details)
        return address
    
    def get_cold_rent(self):
        cold_rent_entries = self.elements.find_all('div', {'class': re.compile(r'.*hardfacts.*')})
        cold_price = []
        for cold_rent in cold_rent_entries:
            if cold_rent.find('div', string=re.compile(r'.*Kaltmiete.*')):
                cold_rent = cold_rent.find_parent('div').find('strong').text.strip()
                cold_rent = re.sub(r'[^\d,]+', '', cold_rent).replace(',', '.')
                cold_rent = float(cold_rent)
                cold_price.append(cold_rent)
            if cold_price:
                cost = cold_price[0]
            else:
                cost = None
            return cost

    def get_warm_rent(self):
        warm_rent_entries = self.elements.find_all('sd-cell-col', {'class': re.compile(r'.*color.*')})
        warm_price = []
        for warm_rent in warm_rent_entries:
            if warm_rent.text.strip() == "Warmmiete":
                warm_cost = warm_rent.find_next_sibling("sd-cell-col").text.strip()
                warm_cost = re.sub(r'[^\d,]+', '', warm_cost).replace(',', '.')
                warm_cost = float(warm_cost)
                warm_price.append(warm_cost)
        if warm_price:
            cost = warm_price[0]
        else:
            cost = None
        return cost
    
    def get_deposit(self):
        deposit = self.elements.find_all('div', {'data-cy': re.compile(r'.*depos.*')})
        deposits = []
        if deposit:
            deposit_amount = deposit[0].find('p', {'class': 'card-content'}).text.strip()
            deposit_amount = re.sub(r'[^\d,]+', '', deposit_amount).replace(',', '.')
            deposits.append(float(deposit_amount))
        # Having a deposit lower the 500 is not possible, probably they have written something like "3times the cold rent bla bla"
        # but I don't care adding that information.
        if deposits and deposits[0] > 500:
            deposit = deposits[0]
        else:
            deposit = None
        return deposit
    
    def get_living_space(self):
        areas = self.elements.find_all('div', {'class': re.compile(r'.*hardfacts.*')})
        living_space = None
        for area in areas:
            size_text = area.find('div', string=re.compile(r'.*Wohnfläche.*'))
            if size_text:
                living_space = float(size_text.find_parent('div').find('span').text.strip().split()[0].replace(',', '.'))
                break
        return living_space

    def get_room_number(self):
        areas = self.elements.find_all('div', {'class': re.compile(r'.*hardfacts.*')})
        room_number = None
        for area in areas:
            room_text = area.find('div', string=re.compile(r'.*Zimmer.*'))
            if room_text:
                room_number = room_text.find_parent('div').find('span').text.strip()
                break
        return room_number
    
    def get_detail_object(self):
        details = self.elements.find_all('h3')
        object = None
        for detail in details:
            if detail.text.strip() == 'Objektbeschreibung':
                object = detail.next_sibling.find('p').text
                object = object.split('...')[0]
                object = object.split('Außerdem')[0]
                object = object.strip()
                if not object:
                    object = None
                break
        return object
    
    def get_detail_furnishing(self):
        details = self.elements.find_all('h3')
        furnishing = None
        for detail in details:
            if detail.text.strip() == 'Ausstattung':
                furnishing = detail.next_sibling.find('p').text
                furnishing = furnishing.split('...')[0]
                furnishing = furnishing.split('Außerdem')[0]
                furnishing = furnishing.strip()
                if not furnishing:
                    furnishing = None      
                break
        return furnishing

    def get_timestamp(self):
        now = datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        return timestamp

    def scrape(self):
        title = self.get_title()
        address = self.get_address()
        cold_rent = self.get_cold_rent()
        warm_rent = self.get_warm_rent()
        deposit = self.get_deposit()
        living_space = self.get_living_space()
        room_number = self.get_room_number()
        object_detail = self.get_detail_object()
        furnishing = self.get_detail_furnishing()
        timestamp = self.get_timestamp()

        data = {
            'title': [title],
            'address': [address],
            'cold_rent': [cold_rent],
            'warm_rent': [warm_rent],
            'deposit': [deposit],
            'living_space': [living_space] if living_space else [None],
            'room_number': [room_number] if room_number else [None],
            'timestamp': [timestamp],
            'object_detail': [object_detail],
            'furnishing': [furnishing],
            'url': [self.url]
        }

        df = pd.DataFrame(data)
        return df
