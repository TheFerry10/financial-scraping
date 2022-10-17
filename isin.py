import requests
from bs4 import BeautifulSoup
import sqlite3
from tqdm import tqdm
import pandas as pd
import numpy as np


   

class WebsiteCheck(object):
    def __init__(self, url):
        self.url = url
        self.response = requests.get(url=self.url)
        self.soup = self.get_soup()
        
    def get_soup(self):
        if self.response.status_code == 200:
            return BeautifulSoup(self.response.text, 'html.parser')
        # TODO assert for status code != 200
        
    def check_element_exists(self, element, target_text):
        results = self.soup.find(**element)
        if results:
            return target_text in results.get_text()
        else:
            return False

        


class Stock(object):
    def __init__(self, ISIN, name):
        self.ISIN = ISIN
        self.name = name
        
    def __repr__(self):
        repr = f"Stock({self.ISIN}, {self.name})"
        return repr

    
def insert_stock(stock):
    with conn:
        c.execute("INSERT OR IGNORE INTO stocks VALUES (:ISIN, :name)", {'ISIN': stock.ISIN, 'name': stock.name})





class StockScraping(object):
    def __init__(self):
        self.base_url = "https://www.xetra.com/xetra-de/instrumente/aktien/liste-der-handelbaren-aktien"
        self.search_string = "/xetra/3002!search?state=H4sIAAAAAAAAADWKsQoCMRAFf0W2TmFjkw-wsgh42IfkRQNrgrsb5Dju3z2EdDPMbJSj4Sr9Tb4NZvf3pU8rMcGU_LYfXEXtBjPIzK9qGiAhPkH-cnZUW-KRca8GnVNvvIZcyJfICkefAVnJEzkS6GB7VHznrF3saLpUY5yiJtp_lYqXCqQAAAA&sort=sTitle+asc&hitsPerPage=50&pageNum=PAGENUMBER"
        self.url = self.base_url + self.search_string
        self.get_base_information()
    
    def get_base_information(self):
        self.info = dict()
        url_for_page_0 = self.url.replace('PAGENUMBER', '0')
        websiteCheck = WebsiteCheck(url=url_for_page_0)
        self.info['max_page'] = get_max_page_value(websiteCheck.soup)
        self.info['num_stocks'] = get_number_of_stocks_listed(websiteCheck.soup)
        self.info['page_range'] = range(self.info['max_page'] + 1)
        

    def scrape(self):
        for page_number in tqdm(self.info['page_range']):
            url_for_page = self.url.replace('PAGENUMBER', str(page_number))
            websiteCheck = WebsiteCheck(url_for_page)
            
            for item in websiteCheck.soup.find('div', {'class':'searchList list'}).find_all('li'):
                if (item.find('h4') is not None) & (item.find('p') is not None):
                    stock_name = item.find('h4').get_text().strip()
                    isin_number = item.find('p').get_text().split()[-1]
                    stock = Stock(isin_number, stock_name)
                    insert_stock(stock)


def get_max_page_value(soup):
    page_values_in_nav_panel = []
    for page_button in soup.find('ul', {'class': 'nav-page'}).find_all('li'):
        page_button = page_button.find('button')
        if page_button:
            if page_button.attrs.keys() == {'value', 'type', 'title', 'name'}:
                value = int(page_button['value'])
                page_values_in_nav_panel.append(value)
    return max(page_values_in_nav_panel)

def get_number_of_stocks_listed(soup):
    number_as_string = soup.find('div', {'class': 'results'}).get_text().split()[0]
    return int(number_as_string.replace('.',''))


website_check_xetra = dict(
    url="https://www.xetra.com/xetra-de/instrumente/aktien/liste-der-handelbaren-aktien",
    target_text = "Ergebnisse",
    element_to_check = {'name':'div', 'attrs':{'class': 'results'}}
)


conn = sqlite3.connect("news.db")
c = conn.cursor()

c.execute("""
          CREATE TABLE IF NOT EXISTS stocks (
              ISIN text,
              StockName text,
              UNIQUE(ISIN, StockName)
              )
          """)

stockScraping = StockScraping()
stockScraping.scrape()