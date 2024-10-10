import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

class ImmoWeltScrapper:
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
        get_category: Extracts the type of the listing, e.g. apartment, mansion etc.
        get_availability: Extracts the date when the listing is available for renting.
        get_amenities: Extracts amenities.
        get_built_year:Extracts the year the house was built.
        get_energy_consumption: Extracts energy consumption (kWh/(m²·a)) 
        get_detail_object: Returns flat details.
        get_detail_furnishing: Returns furnishing details of the flat.
        get_query_time: Returns the query times.
        scrape: Executes all the above methods and returns the extracted information as a Pandas DataFrame.
    """

    def __init__(self, url):
        self.url = url
        self.page = requests.get(url)
        self.elements = BeautifulSoup(self.page.content, "html.parser")
        
    def get_title(self):
        try:
            title = self.elements.find('h1').text.strip()
        except AttributeError:
            title = None
        return title
    
    def get_address(self):
        addresses = self.elements.find_all('span', {'data-cy': re.compile(r'.*address.*')})
        address_details = []
        for address in addresses:
            try:
                address_text = address.text.strip().replace('\n', '')
                address_text = re.sub(r'\s+', ' ', address_text)
                address_details.append(address_text)
            except AttributeError:
                pass
        address = ', '.join(address_details)
        return address
    
    def get_cold_rent(self):
        cold_rent = None
        try: 
            cold_rent = self.elements.find('div', string=re.compile(r'.*Kaltmiete.*'))
            cold_rent = cold_rent.find_parent('div').find('strong').text.strip()
            cold_rent = re.sub(r'[^\d,]+', '', cold_rent).replace(',', '.')
            if cold_rent and not isinstance(cold_rent, str):
                cold_rent = float(cold_rent)
        except AttributeError:
            pass
        return cold_rent

    def get_warm_rent(self):
        warm_rent_entries = self.elements.find_all('sd-cell-col', re.compile(r'.*color.*'))
        warm_rent = None
        try:
            warm_rent = next(warm_rent for warm_rent in warm_rent_entries if warm_rent.text.strip() == "Warmmiete")
            warm_cost = warm_rent.find_next_sibling("sd-cell-col").text.strip()
            warm_cost = re.sub(r'[^\d,]+', '', warm_cost).replace(',', '.')
            warm_cost = float(warm_cost)
            return warm_cost
        except (StopIteration, AttributeError):
            pass
        try: 
            warm_rent = self.elements.find('div', string=re.compile(r'.*Warmmiete.*'))
            warm_rent = warm_rent.find_parent('div').find('strong').text.strip()
            warm_rent = re.sub(r'[^\d,]+', '', warm_rent).replace(',', '.')
            warm_rent = float(warm_rent)
        except (StopIteration, AttributeError):
            return None
        return warm_rent

    def get_deposit(self):
        deposit = None
        try:
            deposit_entries = self.elements.find_all('div', {'data-cy': re.compile(r'.*depos.*')})
            if deposit_entries:
                deposit_amount = deposit_entries[0].find('p', {'class': 'card-content'}).text.strip()
                deposit_amount = re.sub(r'[^\d,]+', '', deposit_amount).replace(',', '.')
                deposit = deposit_amount
        except AttributeError:
            pass
        return deposit

    def get_living_space(self):
        living_space = None
        try:
            living_space = self.elements.find('div',string=re.compile(r'.*Wohnfläche.*'))
            living_space = living_space.find_parent('div').find('span').text.strip().split()[0].replace(',', '.')
            # Check if the living_space can be converted to float
            if re.match(r'^\d+(\.\d+)?$', living_space):
                living_space = float(living_space)
            else:
                living_space = None  # If it can't be converted, set it to None
        except AttributeError:
             pass
        return living_space

    def get_room_number(self):
        room_number = None
        try:
            room_number = self.elements.find('div', string=re.compile(r'.*Zimmer.*'))
            room_number = room_number.find_parent('div').find('span').text.strip().replace(',', '.')
            if room_number and not isinstance(room_number, str):
                room_number = float(room_number)
        except AttributeError:
            pass
        return room_number
    
    def get_category(self):
        category = None
        for element in self.elements.find_all('h2'):
            if element.text.strip() == 'Die Wohnung':
                try:
                    equipment = element.find_next_sibling('div', class_='equipment')
                    category = equipment.find('p', string='Kategorie').find_next_sibling('p').text.strip()
                except AttributeError:
                    pass
        return category

    def get_floor(self):
        floor = None
        for element in self.elements.find_all('h2'):
            if element.text.strip() == 'Die Wohnung':
                try:
                    equipment = element.find_next_sibling('div', class_='equipment')
                    floor = equipment.find('p', string='Wohnungslage').find_next_sibling('p').text.strip()[0]
                except AttributeError:
                    pass
        return floor

    def get_availability(self):
        availability = None
        for element in self.elements.find_all('h2'):
            if element.text.strip() == 'Die Wohnung':
                try:
                    equipment = element.find_next_sibling('div', class_='equipment')
                    availability = equipment.find('p', string='Bezug').find_next_sibling('p').text.strip()
                    if availability == 'sofort':
                        availability = datetime.today().strftime('%d.%m.%Y')
                except AttributeError:
                    pass
        return availability

    def get_amenities(self):
        amenities = None
        for element in self.elements.find_all('h2'):
            if element.text.strip() == 'Die Wohnung':
                try:
                    amenities_block = element.find_next_sibling('div', class_='textlist--icon')
                    amenities_list = [amenity.text.strip() for amenity in amenities_block.find_all('li')]
                    amenities = ', '.join(amenities_list)
                except AttributeError:
                    pass
        return amenities

    def get_built_year(self):
        built_year = None
        for element in self.elements.find_all('h3'):
            if element.text.strip() == 'Wohnanlage':
                try:
                    baujahr = element.find_next_sibling('div').find('li').text.split()[1]
                    built_year = baujahr
                except (AttributeError, IndexError):
                    pass
        return built_year
    
    def get_detail_object(self):
        details = self.elements.find_all('h3')
        object = None
        for detail in details:
            if detail.text.strip() == 'Objektbeschreibung':
                object = detail.next_sibling.find('p').text
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
                if not furnishing:
                    furnishing = None      
                break
        return furnishing

    def get_detail_extra(self):
        details = self.elements.find_all('h3')
        extra = None
        for detail in details:
            if detail.text.strip() == 'Weitere Informationen':
                extra= detail.next_sibling.find('p').text
                if not extra:
                    extra = None      
                break
        return extra    
    
    # Energy consumption unit kWh/(m²·a)
    def get_energy_consumption(self):
        consumption = None
        try:
            entries = self.elements.find('sd-cell-col',  {'data-cy':"energy-consumption"})
            if entries:
                consumption = entries.text.split()[1]
        except AttributeError:
            pass
        return consumption

    def get_query_time(self):
        now = datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        return timestamp
'''
    def scrape(self):
        title = self.get_title()
        address = self.get_address()
        cold_rent = self.get_cold_rent()
        warm_rent = self.get_warm_rent()
        deposit = self.get_deposit()
        living_space = self.get_living_space()
        room_number = self.get_room_number()
        category = self.get_category()
        floor = self.get_floor()
        availability = self.get_availability()
        amenities = self.get_amenities()
        built_year = self.get_built_year()
        object_detail = self.get_detail_object()
        furnishing = self.get_detail_furnishing()
        extra_detail = self.get_detail_extra()
        timestamp = self.get_query_time()

        data = {
            'title': [title],
            'address': [address],
            'cold_rent': [cold_rent],
            'warm_rent': [warm_rent],
            'deposit': [deposit],
            'living_space': [living_space] if living_space else [None],
            'room_number': [room_number] if room_number else [None],
            'category' : [category],
            'floor' : [floor],
            'availability_date' : [availability],
            'amenities' : [amenities],
            'built_year' : [built_year],
            'timestamp': [timestamp],
            'object_detail': [object_detail],
            'extra_detail': [extra_detail],
            'furnishing': [furnishing],
            'url': [self.url]
        }

        return data
'''
