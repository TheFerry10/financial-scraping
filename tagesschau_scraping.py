from scraping.tagesschau import TagesschauDB
from scraping.tagesschau import TagesschauScraper
from scraping.tagesschau import get_dates_in_interval
from scraping.retrieve import get_soup
import requests
from datetime import date
from tqdm import tqdm

def main():
    db = TagesschauDB()
    db.drop_table()
    db.create_table()
    
    tagesschauScraper = TagesschauScraper()
    dates = get_dates_in_interval(date(2022,1,1), date(2022,1,31))
    
    for date_ in tqdm(dates):
        url = tagesschauScraper.get_url(date_, "wirtschaft")
        response = requests.get(url)
        soup = get_soup(response)
        teasers = tagesschauScraper.get_all_news_teaser(soup)
        for teaser in teasers:
            if teaser:
                db.insert(teaser)
    
    

if __name__ == '__main__':
    main()