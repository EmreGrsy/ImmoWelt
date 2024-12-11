# ImmoWelt Web Scraper

A tool to extract rental apartment data in Hamburg from ImmoWelt, with plans to expand into a Hamburg real estate chatbot.

### Features
- Extracts key housing data, including:
  - **id**: Unique listing identifier
  - **url**: Property listing URL
  - **title**: Listing title
  - **creationDate**: Listing creation date
  - **updateDate**: Last update date
  - **city, zipCode, street, district**: Address details
  - **coordinates**: Geographic coordinates (if published)
  - **locationDescription**: Description of the location
  - **hardFacts**: Property details (e.g., rooms, area)
  - **textDetails**: Additional descriptive text
  - **energyFeatures**: Energy-related features and certificates
  - **energyRating**: Energy efficiency class and requirements
  - **housePrices**: Price details
  - **details**: Other property features (e.g., amenities)
    
### TODO
- Configure logging for error tracking.
- Enable email notifications for errors.
- Use LLMs for translation.
- Develop a local Retrieval-Augmented Generation (RAG) chatbot.

## Usage
1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/ImmoWelt-web-scraper.git
