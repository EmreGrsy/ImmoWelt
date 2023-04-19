url = "https://www.immowelt.de/liste/hamburg/wohnungen/mieten?sort=relevanz"

get_links = GetLinks(url)
expose_links = get_links.get_expose_links()

data = []
for link in expose_links:
    scraper = ImmoWebScraper(link)
    row = {
        "title": scraper.get_title(),
        "address": scraper.get_address(),
        "cold_rent": scraper.get_cold_rent(),
        "warm_rent": scraper.get_warm_rent(),
        "deposit": scraper.get_deposit(),
        "living_space": scraper.get_living_space(),
        "room_number": scraper.get_room_number(),
        "object_detail": scraper.get_detail_object(),
        "furnishing": scraper.get_detail_furnishing(),
        "timestamp": scraper.get_timestamp(),
        "url": link
    }
    data.append(row)

df = pd.DataFrame(data)
