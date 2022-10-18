import requests
from bs4 import BeautifulSoup
import sqlite3
from tqdm import tqdm
from dataclasses import dataclass
from scraping.retrieve import get_soup


@dataclass
class Stock:
    ISIN: str
    name: str


class StockQueries:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self.c = c = conn.cursor()

    def insert_stock(self, stock: Stock) -> None:
        with self.conn:
            self.c.execute(
                "INSERT OR IGNORE INTO stocks VALUES (:ISIN, :name)",
                {"ISIN": stock.ISIN, "name": stock.name},
            )

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

    def insert_stock_information(self, stock_information):
        table_name = "stocks_enriched"
        query = f"""INSERT OR IGNORE INTO {table_name}
                    VALUES (:ISIN, :STOCK_NAME, :WKN, :SYMBOL, :NEWS_LINK)"""
        with self.conn:
            self.c.execute(query, stock_information)

    def select_columns_from_table(self, columns, table):
        columns_string = ",".join(columns)
        query = f"""SELECT {columns_string} FROM {table};"""
        self.c.execute(query)
        return self.c.fetchall()

    def get_ISIN_and_news_link(self, tickers):
        keys = [f"ticker_{i}" for i in range(len(tickers))]
        keys_in_query = [f":ticker_{i}" for i in range(len(tickers))]
        ticker_dict = {key: value for key, value in zip(keys, tickers)}
        placeholder = ",".join(keys_in_query)
        query = f"""SELECT ISIN, NEWS_LINK FROM stocks_enriched
                WHERE SYMBOL IN ({placeholder});"""
        self.c.execute(query, ticker_dict)
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


website_check_xetra = dict(
    url="https://www.xetra.com/xetra-de/instrumente/aktien/liste-der-handelbaren-aktien",
    target_text="Ergebnisse",
    element_to_check={"name": "div", "attrs": {"class": "results"}},
)
