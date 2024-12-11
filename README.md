# ImmoWelt Web Scraper

A tool to extract rental apartments data in Hamburg from ImmoWelt, hopefully (when I have time) will turn this into  Hamburg real estate chatbot.

## Features

### Completed
- Fixed text description parsing.
- Simplified and optimized parsing logic.
- Saved parsed data to JSON.
- Set up necessary libraries.

### TODO
- Configure logging for error tracking.
- Enable email notifications for errors.
- Use LLMs for data translation.
- Develop a local Retrieval-Augmented Generation (RAG) chatbot.

## Usage
1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/ImmoWelt-web-scraper.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the scraper:
   ```bash
   python scraper.py
   ```
4. Find the parsed data in `data.json`.
