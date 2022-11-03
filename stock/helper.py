import requests
from bs4 import BeautifulSoup
import sqlite3
from tqdm import tqdm
from dataclasses import dataclass
from scraping.retrieve import get_soup
from scraping.retrieve import get_soup, get_hash_from_string
from datetime import datetime
from datetime import date
from typing import List
import re
from typing import List


StockTicker = str    


StockTickers = List[str]

@dataclass
class Stock:
    ISIN: str
    name: str



class NewsQueries:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self.c = conn.cursor()
    
    def insert_article_meta_data(self, news_entry):
        with self.c:
            self.c.execute(
                "INSERT OR IGNORE INTO article_meta VALUES (:id, :isin, :news_datetime, :title, :source, :kicker, :link)",
                news_entry,
            )


    def get_article_meta_data_by_id(self, id):
        self.c.execute("SELECT * FROM article_meta WHERE id=:id", {"id", id})
        return self.c.fetchall()


    def get_all_article_meta_data(self):
        self.c.execute("SELECT * FROM article_meta")
        return self.c.fetchall()

    def create_article_table_meta(self):
        table_name = "article_meta"
        query = f"""CREATE TABLE IF NOT EXISTS {table_name} (
                        id text UNIQUE,
                        isin text,
                        news_datetime text,
                        title text,
                        source text,
                        kicker text,
                        link text)
                        """
        self.c.execute(query)


class StockQueries:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self.c = conn.cursor()


    def create_stock_table_base(self):
        table_name = "stocks"
        query = f"""CREATE TABLE IF NOT EXISTS {table_name} (
                        ISIN text,
                        Stock text,
                        UNIQUE(ISIN, StockName))
                """
        self.c.execute(query)

    def create_stock_table_enriched(self):
        table_name = "stocks_enriched"
        query = f"""CREATE TABLE IF NOT EXISTS {table_name} (
                        ISIN text,
                        Stock text,
                        WKN text,
                        SYMBOL text,
                        NewsLink text,
                        UNIQUE(ISIN))
                """
        self.c.execute(query)

    def insert_stock(self, stock: Stock) -> None:
        with self.conn:
            self.c.execute(
                "INSERT OR IGNORE INTO stocks VALUES (:ISIN, :name)",
                {"ISIN": stock.ISIN, "name": stock.name},
            )

    def insert_stock_information(self, stock_information):
        table_name = "stocks_enriched"
        query = f"""INSERT OR IGNORE INTO {table_name}
                    VALUES (:ISIN, :STOCK_NAME, :WKN, :SYMBOL, :NEWS_LINK)"""
        with self.conn:
            self.c.execute(query, stock_information)


    def select_columns_from_table(self, columns, table, condition=None, parameter=None):
        columns_string = ",".join(columns)
        query = f"SELECT {columns_string} FROM {table}"
        if condition is not None:
            query += f" WHERE {condition}"
        self.c.execute(query, parameter)
        return self.c.fetchall()



class StockScraping(object):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self.stockQueries = StockQueries(conn)
        self.base_url = "https://www.xetra.com/xetra-de/instrumente/aktien/liste-der-handelbaren-aktien"
        self.search_string = "/xetra/3002!search?state=H4sIAAAAAAAAADWKsQoCMRAFf0W2TmFjkw-wsgh42IfkRQNrgrsb5Dju3z2EdDPMbJSj4Sr9Tb4NZvf3pU8rMcGU_LYfXEXtBjPIzK9qGiAhPkH-cnZUW-KRca8GnVNvvIZcyJfICkefAVnJEzkS6GB7VHznrF3saLpUY5yiJtp_lYqXCqQAAAA&sort=sTitle+asc&hitsPerPage=50&pageNum=PAGENUMBER"
        self.url = self.base_url + self.search_string
        self.stockQueries.create_stock_table_base()
        self.get_base_information()

    def get_base_information(self):
        self.info = dict()
        url_for_page_0 = self.url.replace("PAGENUMBER", "0")
        response = requests.get(url_for_page_0)
        soup = get_soup(response)
        self.info["max_page"] = self.get_max_page_value(soup)
        self.info["num_stocks"] = self.get_number_of_stocks_listed(soup)
        self.info["page_range"] = range(self.info["max_page"] + 1)

    def scrape(self):
        for page_number in tqdm(self.info["page_range"]):
            url_for_page = self.url.replace("PAGENUMBER", str(page_number))
            response = requests.get(url_for_page)
            soup = get_soup(response)

            for item in soup.find("div", {"class": "searchList list"}).find_all("li"):
                if (item.find("h4") is not None) & (item.find("p") is not None):
                    stock_name = item.find("h4").get_text().strip()
                    isin_number = item.find("p").get_text().split()[-1]
                    stock = Stock(isin_number, stock_name)
                    self.stockQueries.insert_stock(stock)

    def get_max_page_value(self, soup):
        page_values_in_nav_panel = []
        for page_button in soup.find("ul", {"class": "nav-page"}).find_all("li"):
            page_button = page_button.find("button")
            if page_button:
                if page_button.attrs.keys() == {"value", "type", "title", "name"}:
                    value = int(page_button["value"])
                    page_values_in_nav_panel.append(value)
        return max(page_values_in_nav_panel)

    def get_number_of_stocks_listed(self, soup):
        number_as_string = soup.find("div", {"class": "results"}).get_text().split()[0]
        return int(number_as_string.replace(".", ""))


class StockEnricher:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self.stockQueries = StockQueries(conn=conn)
        self.base_url = "https://www.finanzen.net"
        self.stockQueries.create_stock_table_enriched()

    def get_url(self, search_string):
        search_api = f"/suchergebnis.asp?strSuchString={search_string}"
        return self.base_url + search_api

    def enrich(self):
        table_name = "stocks_enriched"
        for search_string in tqdm(
            self.stockQueries.select_columns_from_table(["ISIN"], table_name)
        ):
            search_string = search_string[0]
            stock_properties = dict()
            url = self.get_url(search_string)
            response = requests.get(url)
            soup = get_soup(response)
            print(url)

            # stock name
            stock_name = soup.find("h1", {"class": "snapshot__headline"}).text
            stock_properties["STOCK_NAME"] = stock_name.encode("latin").decode()

            # instrument ids
            for instrument_id in soup.find("div", {"class": "badge-bar"}).find_all(
                "h2",
                {"class": "badge pointer display-none-md margin-vertical-0.00"},
            ):
                key, value = instrument_id.text.split(" ", 1)
                stock_properties[key.upper()] = value

            # news link
            news_link = soup.find(
                "a", {"class": "display-none-md font-whitespace-nowrap-md"}
            ).attrs["href"]
            stock_properties["NEWS_LINK"] = (
                self.base_url + news_link.encode("latin").decode()
            )
            self.stockQueries.insert_stock_information(stock_properties)




class NewsMetaData:
    def __init__(self, news, isin):
      self.news = news
      self.date_pattern = "%Y-%m-%dT%H:%M:%S"
      self.isin = isin
      self.executed = False

    
    def get_news_datetime(self):
        return datetime.strptime(get_encoded_text(self.news.find("time", {"class": "news__date"}).attrs["datetime"]), self.date_pattern)
    
    def get_source(self):
        return get_encoded_text(self.news.find("span", {"class": "news__source"}))
        
    def get_kicker(self):
        return get_encoded_text(self.news.find("span", {"class": "news__kicker"}))
        
    def get_title(self):        
        return get_encoded_text(self.news.find("span", {"class": "news__title"}))
    
    def get_link(self):
        return get_encoded_text(self.news.find("a", {"class": "news__card"}).attrs["href"])
        
    def get_id(self, link):
        return get_hash_from_string(link)
    
    def is_article_date_in_interval(self, start_date, end_date):
        if start_date <= self.get_news_datetime().date() <= end_date:
            return True
        else:
            return False
    
    def extract(self):
        keys = ["id",
                "isin",
                "news_datetime",
                "title",
                "source",
                "kicker",
                "link"
                ]
        values = [self.get_id(self.get_link()), 
                  self.isin,
                  str(self.get_news_datetime()),
                  self.get_title(),
                  self.get_source(),
                  self.get_kicker(),
                  self.get_link()
                  ]
        self.meta_data = {key: value for key, value in zip(keys, values)}
        self.executed = True
        




def get_encoded_text(obj):
    if hasattr(obj, "text"):
        return obj.text.encode('latin').decode()
    else:
        return obj
            


    

      
class ArticleMetaScraper:
    def __init__(self, conn: sqlite3.Connection, start_date: datetime.date, end_date: datetime.date, isin: str):
        self.base_url = "https://www.finanzen.net"
        self.stockQueries = StockQueries(conn)
        self.newsQueries = NewsQueries(conn)
        self.start_date = start_date
        self.end_date = end_date
        self.isin = isin
    
    
    def extract_news_metadata(self, isin, news):
        newsMetaData = NewsMetaData(news, isin)
        if newsMetaData.is_article_date_in_interval(self.start_date, self.end_date):
            newsMetaData.extract()
        return newsMetaData


    def save_extracted_meta_data(self, isin, soup):
        all_news = soup.find_all("div", {"class": "news news--item-with-media"}) 
        for news in all_news:
            newsMetaData = self.extract_news_metadata(isin, news)
            if newsMetaData.executed:
                print(newsMetaData.meta_data)
                self.newsQueries.insert_article_meta_data(newsMetaData.meta_data)


    def get_news_link(self, ISIN: str):
        return self.stockQueries.select_columns_from_table(
            columns=["NEWS_LINK"],
            table="stocks_enriched",
            condition="ISIN = :ISIN",
            parameter={"ISIN": ISIN})[0][0]
    
    def run(self):
        news_link = self.get_news_link(self.isin)
        pagination_links = get_pagination_links(news_link)
        for link in pagination_links:
            response = requests.get(link)
            soup = get_soup(response)
            self.save_extracted_meta_data(self.isin, soup)



website_check_xetra = dict(
    url="https://www.xetra.com/xetra-de/instrumente/aktien/liste-der-handelbaren-aktien",
    target_text="Ergebnisse",
    element_to_check={"name": "div", "attrs": {"class": "results"}},
)

def validate_links(links):
    print("Validate links...")
    for link in tqdm(links):
        response = requests.get(link)
        if response.status_code != 200:
            raise ValueError
    print("Validation successful")


def get_pagination_links(url: str):
    base_url = "https://www.finanzen.net"
    response = requests.get(url)
    soup = get_soup(response)
    
    pagination_list = soup.find("ul", {"class": "pagination__list"})
    pagination_objects = pagination_list.find_all("a", {"class": "pagination__text"})
    links = [pagination.attrs["href"] for pagination in pagination_objects]
    base_links = [link.split('_')[0] for link in links if len(link.split('_')) == 2]
    page_numbers = [int(link.split('_')[1]) for link in links if len(link.split('_')) == 2]
    max_page = max(page_numbers)
    base_link = max(base_links, key=base_links.count)
    links = [base_url + "_".join([base_link, str(i)]) for i in range(1, max_page+1)]
    validate_links(links)
    return links
    