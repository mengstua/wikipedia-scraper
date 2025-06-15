# main.py
from src.leaders_scraper import WikipediaScraper, CookieExpiredException
import time

"""These pythion program evaluate calls WikipediaScraper, CookieExpiredException methods from the Leaders_scrapper class"""

def main():
    scraper = WikipediaScraper()
    try:
        countries = scraper.get_countries()
    except CookieExpiredException:
        scraper.cookie = scraper.refresh_cookie()
        countries = scraper.get_countries()

    for country in countries:
        try:
            scraper.get_leaders(country)
        except CookieExpiredException:
            scraper.cookie = scraper.refresh_cookie()
            scraper.get_leaders(country)

    scraper.to_json_file("leaders_data.json")
    print("Saved leaders data to leaders_data.json")

if __name__ == "__main__":
    main()