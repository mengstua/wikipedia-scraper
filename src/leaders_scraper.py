# src/leaders_scraper.py
import requests
from bs4 import BeautifulSoup
import json
import re

# Define a custom exception for expired cookies
class CookieExpiredException(Exception):
    pass

class WikipediaScraper:
    """" This code defines the """
    def __init__(self):
        """Initialize the scraper with base URLs and a fresh cookie."""
        self.base_url = "https://country-leaders.onrender.com"
        self.country_endpoint = "/countries"
        self.leaders_endpoint = "/leaders"
        self.cookies_endpoint = "/cookie"
        self.leaders_data = {}
        self.cookie = self.refresh_cookie()

    def refresh_cookie(self):
        """Get a new cookie from the API."""
        res = requests.get(self.base_url + self.cookies_endpoint)
        if res.status_code != 200:
            raise CookieExpiredException("Failed to refresh cookie")
        return res.cookies

    def get_countries(self):
        """Fetch the list of countries from the API."""
        res = requests.get(self.base_url + self.country_endpoint, cookies=self.cookie)
        if res.status_code != 200:
            raise CookieExpiredException("Cookie expired or invalid while getting countries")
        return res.json()

    def get_leaders(self, country):
        """Fetch leaders for a given country and scrape their Wikipedia paragraph."""
        res = requests.get(self.base_url + self.leaders_endpoint, cookies=self.cookie, params={"country": country})
        if res.status_code != 200:
            raise CookieExpiredException("Cookie expired to get leaders")
        leaders = res.json()
        session =  requests.Session()
        for leader in leaders:
            wiki_url = leader.get("wikipedia_url")
            if wiki_url:
                paragraph = self.get_first_paragraph(wiki_url, session)
                leader["first_paragraph"] = paragraph
            else:
                leader["first_paragraph"] = "No Wikipedia URL available"
        self.leaders_data[country] = leaders

    def get_first_paragraph(self, wikipedia_url, session):
        """Extract the first meaningful paragraph from a Wikipedia URL using a session."""
        print(f"Scraping: {wikipedia_url}")
        res = session.get(wikipedia_url)
        if res.status_code != 200:
            raise Exception("Failed to load Wikipedia page")

        parag = BeautifulSoup(res.text, "html.parser")
        paragraphs = parag.find_all("p")

        for p in paragraphs:
            text = p.get_text().strip()

            if len(text) > 50:
                # Remove citations like [1], [a], etc.
                text = re.sub(r"\[\w+?\]", "", text)
                # Remove phonetic pronunciations within slashes or parentheses
                text = re.sub(r"\((?:IPA:)?[^)]*\)", "", text)
                # Remove curly braces or other brackets
                text = re.sub(r"\{[^}]*\}", "", text)
                # Remove HTML character entities (&nbsp;, &amp; etc.)
                text = re.sub(r"&\w+?;", "", text)
                # Remove multiple spaces/newlines
                text = re.sub(r"\s+", " ", text)
                return text

        return "No valid paragraph found."

    def to_json_file(self, filepath):
        """Save the leaders data to a JSON file."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.leaders_data, f, indent=4, ensure_ascii=False)