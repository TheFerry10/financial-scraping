import sqlite3
from stock.helper import StockScraping

conn = sqlite3.connect("news.db")


stockScraping = StockScraping(conn=conn)
stockScraping.scrape()
