import unittest
import requests
from scraping.retrieve import get_soup
from scraping.tagesschau import TagesschauScraper
from scraping.tagesschau import get_dates_in_interval
from scraping.tagesschau import format_date
from datetime import date
import json

class TestTagesschauScraper(unittest.TestCase):
    def setUp(self):
        self.tageschauScraper = TagesschauScraper()
        self.url = "https://www.tagesschau.de/archiv/?datum=2022-03-01&ressort=wirtschaft"
        with open("data/news/tagesschau/sample.html", "r") as f:
            self.html = f.read()
        with open("data/news/tagesschau/test_teasers.json", "r") as f:
            self.test_teasers = json.load(f)
    
    def test_archive_headline(self):
        archive_headline = self.tageschauScraper.get_archive_headline(self.url)
        self.assertEqual(archive_headline, "1. März 2022")
        
    def test_get_all_news_teaser(self):
        response = requests.get(self.url)
        soup = get_soup(response)
        all_news_teaser = self.tageschauScraper.get_all_news_teaser(soup)
        self.assertEqual(all_news_teaser, self.test_teasers)
        
    def test_get_dates_in_interval(self):
        start = date(2022, 1, 1)
        end = date(2022, 1, 3)
        solution = [date(2022, 1, x) for x in range(1,4)]
        self.assertEqual(get_dates_in_interval(start, end), solution)
        
    def test_format_date(self):
        self.assertEqual(format_date(date(2022,3,1)), "2022-03-01")

        
if __name__ == '__main__':
    unittest.main()