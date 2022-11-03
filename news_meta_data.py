import argparse
from stock.helper import StockQueries
from stock.helper import ArticleMetaScraper
from datetime import date
import sqlite3

conn = sqlite3.connect("news.db")

# Argument parsing
parser = argparse.ArgumentParser(
    description="Extract article meta data for all articles related to a stock in a specified time range."
)
parser.add_argument("isin", type=str, help="ISIN")
parser.add_argument("start", type=str, help="start date YYYY-MM-DD")
parser.add_argument("end", type=str, help="end date YYYY-MM-DD")
args = parser.parse_args()

# Input data
start_date = date.fromisoformat(args.start)
end_date = date.fromisoformat(args.end)
isin = args.isin
# tickers = [t.strip() for t in args.ticker.upper().split(",")]


print("Ticker: ", isin)
print("Start date: ", str(start_date))
print("End date: ", str(end_date))


articleMetaScraper = ArticleMetaScraper(conn, start_date, end_date, isin)
articleMetaScraper.run()