import sqlite3
from stock.helper import StockQueries
import argparse

parser = argparse.ArgumentParser(description='Return ISIN from a stock symbol.')
parser.add_argument('symbol', type=str, help='Stock ticker')
args = parser.parse_args()
symbol = args.symbol

conn = sqlite3.connect("news.db")
stockQueries = StockQueries(conn)
isin = stockQueries.symbol_to_isin(symbol)
print(isin)
