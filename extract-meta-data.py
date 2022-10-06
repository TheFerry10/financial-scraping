import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import os
from glob import glob
from datetime import date
from datetime import datetime
import hashlib
import argparse
import sqlite3
from article import ArticleMetaData



# Argument parsing
parser = argparse.ArgumentParser(
    description='Extract article meta data for all articles related to a stock in a specified time range.')
parser.add_argument('ticker', type=str, help='stock ticker')
parser.add_argument('start', type=str, help='start date YYYY-MM-DD')
parser.add_argument('end', type=str, help='end date YYYY-MM-DD')
args = parser.parse_args()

# Input data
start_date = date.fromisoformat(args.start)
end_date = date.fromisoformat(args.end)
stock_ticker = [t.strip() for t in args.ticker.upper().split(',')]

# Constants
df_stocks = pd.read_csv(
    "data/stocks/processed/20220824T074737_xetra_finanzen.csv")

print("Ticker: ", stock_ticker)
print("Start date: ", str(start_date))
print("End date: ", str(end_date))


def get_hash_from_string(string):
    result = hashlib.sha1(string.encode())
    return result.hexdigest()


def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')


def get_links_for_all_pages(soup):
    pagination_list_object = soup.find('ul', {'class': "pagination__list"})
    if pagination_list_object:
        pagination_objects = pagination_list_object.find_all(
            'a', {'class': 'pagination__text'})
        links = [pagination.attrs['href']
                 for pagination in pagination_objects][:-1]
        return links
    else:
        return []


def get_news_links(df_stocks, start_date, end_date):
    base_url = "https://www.finanzen.net"
    extracted_news_properties = []
    failed_links = []
    for ISIN, url_news in df_stocks[['ISIN', 'news_link']].values:
        links_all_pages = get_links_for_all_pages(get_soup(url_news))
        if links_all_pages:
            for link in links_all_pages:
                url = base_url + link
                print(url)
                soup = get_soup(url)
                for news in soup.find_all('div', {'class': 'news news--item-with-media'}):
                    news_entry = dict()
                    date = news.find('time', {'class': 'news__date'})
                    article_date = datetime.strptime(
                        date.text, '%d.%m.%y').date()
                    if (start_date <= article_date <= end_date):
                        source = news.find('span', {'class': 'news__source'})
                        kicker = news.find('span', {'class': 'news__kicker'})
                        title = news.find('span', {'class': 'news__title'})
                        link = news.find(
                            'a', {'class': 'news__card'}).attrs['href']
                        id = get_hash_from_string(link)
                        keys = ['id', 'ISIN', 'date', 'title',
                                'source', 'kicker', 'link_article']
                        values = [id, ISIN, date, title, source, kicker, link]
                        for key, value in zip(keys, values):
                            if hasattr(value, 'text'):
                                news_entry[key] = value.text.encode(
                                    'latin').decode()
                            else:
                                news_entry[key] = value
                        if news_entry['link_article']:
                            news_entry['link_article'] = base_url + \
                                news_entry['link_article']
                                
                        insert_article_meta_data(news_entry)
                        extracted_news_properties.append(news_entry)
        else:
            print(url_news)
            failed_links.append(url_news)
    return extracted_news_properties

# sql helper functions
def insert_article_meta_data(news_entry):
    with conn:
        c.execute("INSERT OR IGNORE INTO article_meta VALUES (:id, :ISIN, :date, :title, :source, :kicker, :link_article)",
                  news_entry
                  )

def get_article_meta_data_by_id(id):
    c.execute("SELECT * FROM article_meta WHERE id=:id", {'id', id})
    return c.fetchall()

def get_all_article_meta_data():
    c.execute("SELECT * FROM article_meta")
    return c.fetchall()

conn = sqlite3.connect('news.db')
c = conn.cursor()

# create table
c.execute("""
          CREATE TABLE IF NOT EXISTS article_meta (
              id text UNIQUE,
              ISIN text,
              date text,
              title text,
              source text,
              kicker text,
              link_article text
              )
          """)


df_stocks_selected = df_stocks.query("Symbol in @stock_ticker").copy()
extracted_news_properties = get_news_links(
    df_stocks_selected, start_date, end_date)

# stock_tickers = '-'.join(stock_ticker)
# file_name = '_'.join(['news', stock_tickers, str(start_date), str(end_date)])
# file_name += '.csv'
# file_path = f"data/stocks/{file_name}"
# df_stock_news = pd.DataFrame(extracted_news_properties)
# df_stock_news.to_csv(file_path, index=False)
# print(f"Save to {file_path}")
