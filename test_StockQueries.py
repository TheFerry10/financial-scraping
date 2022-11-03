from stock.helper import StockQueries
import unittest
import sqlite3


class TestStockQueries(unittest.TestCase):
    def select_columns_from_table(self):
        # ABNB
        ISIN = "US0090661010"
        table_name = "stocks_enriched"
        query_condition = "ISIN = :ISIN"
        parameter = {"ISIN": ISIN}
        
        conn = sqlite3.connect("news.db")
        self.stockQueries = StockQueries(conn)
        news_links = self.stockQueries.select_columns_from_table(
            columns=["NEWS_LINK"],
            table=table_name,
            condition=query_condition,
            parameter=parameter)
        self.assertEqual(news_links, [("https://www.finanzen.net/news/airbnb-news",)])
        self.assertEqual(news_links[0], "https://www.finanzen.net/news/airbnb-news")

    
if __name__ == "__main__":
    unittest.main()