import sqlite3
from stock.helper import StockEnricher

conn = sqlite3.connect("news.db")


stockEnricher = StockEnricher(conn=conn)
stockEnricher.enrich()
