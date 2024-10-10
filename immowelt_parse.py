import requests
from bs4 import BeautifulSoup
import logging
import json


# Configure logging to file and stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("info.log"), logging.StreamHandler()],
)

class ParsePageJson:
    """
    Extracts housing related data from the JSON object obtained from the webpage.

    Attributes:
        page_url (str): The URL of the webpage containing the JSON object.
        page_json (dict): The JSON object to parse.
        num_total_features (int): The total number of features to extract.
        num_extracted_features (int): The number of features successfully extracted.
        data (dict): The extracted data.

    Methods:
        __init__(page_url): Initializes the object with the page URL and loads the JSON object.
        get_json_object(): Loads the JSON object from the webpage.
        extract_features(): Extracts the housing related data from the JSON object.
    """

    def __init__(self, page_url):
        self.page_url = page_url
        self.num_total_features = 12
        self.num_extracted_features = 0
        self.data = {}
        self.valid_json = True
        self.get_json_object()


    def get_json_object(self):
        page = requests.get(self.page_url, timeout=30)
        elements = BeautifulSoup(page.content, "html.parser")
        data = elements.find('script', id='__NEXT_DATA__').text
        logging.info(f"{self.page_url}")
        
        if data is None:
            logging.error(f"Error parsing URL: {self.page_url} - no JSON data found")
            self.valid_json = False
            return {}
        self.page_json = json.loads(data)

        if "statusCode" in self.page_json["props"]["pageProps"]["classified"] and isinstance(self.page_json["props"]["pageProps"]["classified"]["statusCode"], int):
            logging.error(f"Skipping URL: {self.page_url} - page has a status code of {self.page_json['props']['pageProps']['classified']['statusCode']}")
            return {}
		
        
    def extract_features(self):
        if not self.valid_json:
            logging.error(f"Skipping URL: {self.page_url} - invalid JSON data")
            return {}

        try:
            self.data["id"] = self.page_json["props"]["pageProps"]["classified"]["id"]
            self.num_extracted_features += 1
        except Exception as e:
            self.data["id"] = None

        try:
            self.data["url"] = self.page_url
        except Exception as e:
            self.data["url"] = None

        try:
            self.data["title"] = self.page_json["props"]["pageProps"]["classified"]["title"]
            self.num_extracted_features += 1
        except Exception as e:
            self.data["title"] = None

        try:
            self.data["creationDate"] = self.page_json["props"]["pageProps"]["classified"]["metadata"]["creationDate"]
            self.num_extracted_features += 1
        except Exception as e:
            self.data["creationDate"] = None

        try:
            self.data["updateDate"] = self.page_json["props"]["pageProps"]["classified"]["metadata"]["updateDate"]
            self.num_extracted_features += 1
        except Exception as e:
            self.data["updateDate"] = None

        try:
            self.data["city"] = self.page_json["props"]["pageProps"]["classified"]["sections"]["location"]["address"]["city"]
            self.num_extracted_features += 1
        except Exception as e:
            self.data["city"] = None

        try:
            self.data["zipCode"] = self.page_json["props"]["pageProps"]["classified"]["sections"]["location"]["address"]["zipCode"]
            self.num_extracted_features += 1
        except Exception as e:
            self.data["zipCode"] = None

        try:
            self.data["street"] = self.page_json["props"]["pageProps"]["classified"]["sections"]["location"]["address"]["street"]
            self.num_extracted_features += 1
        except Exception as e:
            self.data["street"] = None

        try:
            self.data["district"] = self.page_json["props"]["pageProps"]["classified"]["sections"]["location"]["address"]["district"]
            self.num_extracted_features += 1
        except Exception as e:
            self.data["district"] = None

        try:
            addressPublished = self.page_json["props"]["pageProps"]["classified"]["sections"]["location"]["isAddressPublished"]
            if addressPublished == "true":
                self.data["coordinates"] = self.page_json["props"]["pageProps"]["classified"]["sections"]["location"]["geometry"]["coordinates"]
                self.num_extracted_features += 1
            else:
                self.data["coordinates"] = None
        except Exception as e:
            self.data["coordinates"] = None

        try:
            self.data["locationDescription"] = self.page_json["props"]["pageProps"]["classified"]["sections"]["hardFacts"]["locationDescription"]
            self.num_extracted_features += 1
        except Exception as e:
            self.data["locationDescription"] = None            

        try:
            facts_dict = {}
            facts = self.page_json["props"]["pageProps"]["classified"]["sections"]["hardFacts"]["facts"]
            for fact in facts:
                facts_dict[fact["type"]] = fact["value"]
                self.num_extracted_features += 1
            self.data.update(facts_dict)
        except Exception as e:
            pass

        try:
            textDetails_dict = {}
            textDetails = self.page_json["props"]["pageProps"]["classified"]["sections"]["description"]["texts"]
            for textDetail in textDetails:
                if "headline" in textDetail:
                    headline = textDetail["headline"]
                else:
                    headline = "Description"
                text = textDetail["text"]
                textDetails_dict[headline] = text
                self.num_extracted_features += 1
            self.data.update(textDetails_dict)
        except Exception as e:
            pass

        try:
            features_dict = {}
            features = self.page_json["props"]["pageProps"]["classified"]["sections"]["energy"]["features"]
            for feature in features:
                features_dict[feature["type"]] = feature["value"]
                self.num_extracted_features += 1
            self.data.update(features_dict)   
        except Exception as e:
            pass

        try:
            certificates_dict = {}
            certificates = self.page_json["props"]["pageProps"]["classified"]["sections"]["energy"]["certificates"][0]["features"]
            for feature in certificates:
                certificates_dict[feature["type"]] = feature["value"]
                self.num_extracted_features += 1
            self.data.update(certificates_dict)
        except Exception as e:
            pass

        try:
            energyRating_dict = {}
            energyRating = self.page_json["props"]["pageProps"]["classified"]["sections"]["energy"]["certificates"][0]["scales"][0]["efficiencyClass"]["rating"]
            energyRequirement = self.page_json["props"]["pageProps"]["classified"]["sections"]["energy"]["certificates"][0]["scales"][0]["values"][0]["value"]
            energyRating_dict = {"energyRating": energyRating, "energyRequirement": energyRequirement}
            self.data.update(energyRating_dict)
            self.num_extracted_features += 2
        except Exception as e:
            pass

        try:
            housePrices_dict = {}
            housePrices = self.page_json["props"]["pageProps"]["classified"]["sections"]["price"]["base"]["details"]
            for housePrice in housePrices:
                housePrices_dict[housePrice["label"]["main"]] = housePrice["value"]["main"]["value"]
                self.num_extracted_features += 1
            self.data.update(housePrices_dict) 
        except Exception as e:
            pass

        try:
            details_dict = {}
            details = self.page_json["props"]["pageProps"]["classified"]["sections"]["features"]["details"]["categories"]
            for detail in details:
                for element in detail["elements"]:
                    details_dict[element["icon"]] = element["value"]
                    self.num_extracted_features += 1
            self.data.update(details_dict)
        except Exception as e:
            pass
		
        logging.info(f"From page {self.page_url} {self.num_extracted_features} features extracted")

        return self.data
