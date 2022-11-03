from stock.helper import ArticleMetaScraper
from datetime import date
import sqlite3
import unittest

class TestArticleMetaScraper(unittest.TestCase):
    def test_ArticleMetaScraper(self):
        conn = sqlite3.connect("news.db")
        start_date = date(2020,1,1)
        end_date = date(2020,3,1)
        tickers = ["AAPL"]

        articleMetaScraper = ArticleMetaScraper(conn, start_date, end_date, tickers)
        articleMetaScraper.extract_article_meta_data()