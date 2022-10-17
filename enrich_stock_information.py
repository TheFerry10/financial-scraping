from threading import get_ident
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import os
from glob import glob
import argparse
import sqlite3
from tqdm import tqdm
from stocks import select_columns_from_table
from isin import WebsiteCheck



def insert_stock_information(stock_information):
    query = f"""INSERT OR IGNORE INTO {table_name}
                VALUES (:ISIN, :STOCK_NAME, :WKN, :SYMBOL, :NEWS_LINK)"""
    with connect:
        c.execute(query, stock_information)
        

def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')

class StockEnricher:
    def __init__(self):
        self.base_url = "https://www.finanzen.net"
    
    def get_url(self, search_string):
        search_api = f"/suchergebnis.asp?strSuchString={search_string}"
        return self.base_url + search_api
        
    def enrich(self):
        for search_string in tqdms(select_columns_from_table(['ISIN', table_name])):
            stock_properties = dict()
            url = self.get_url(search_string)
            websiteCheck = WebsiteCheck(url)
            
            # stock name
            stock_name = websiteCheck.soup.find('h1', {'class': 'snapshot__headline'}).text
            stock_properties["STOCK_NAME"] = stock_name.encode('latin').decode()

            # instrument ids
            for instrument_id in websiteCheck.soup.find('div', {'class': 'badge-bar'}).find_all('h2', {'class': 'badge pointer display-none-md margin-vertical-0.00'}):
                key, value = instrument_id.text.split(' ', 1)
                stock_properties[key.upper()] = value

            # news link
            news_link = websiteCheck.soup.find('a', {'class': 'display-none-md font-whitespace-nowrap-md'}).attrs['href']
            stock_properties["NEWS_LINK"] = self.base_url + news_link.encode('latin').decode()
            insert_stock_information(stock_properties)
            
# Connect to news database
connect = sqlite3.connect("news.db")
c = connect.cursor()
table_name = 'stocks_enriched'

# create table
c.execute(f"""
          CREATE TABLE IF NOT EXISTS {table_name} (
              ISIN text,
              STOCK_NAME text,
              WKN text,
              SYMBOL text,
              NEWS_LINK text,
              UNIQUE(ISIN)
              )
          """)

stockEnricher = StockEnricher()
stockEnricher.enrich()

