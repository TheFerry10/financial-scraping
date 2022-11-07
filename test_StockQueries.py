from stock.helper import StockQueries
import unittest
import sqlite3


class TestStockQueries(unittest.TestCase):
    def test_symbol_to_isin(self):
        conn = sqlite3.connect("news.db")
        stockQueries = StockQueries(conn)
        self.assertEqual(stockQueries.symbol_to_isin('AAPL'), 'US0378331005')
        self.assertNotEqual(stockQueries.symbol_to_isin('GOOG'), 'US0378331005')
        
    def test_symbol_to_isin_for_unknown_symbol(self):
        conn = sqlite3.connect("news.db")
        stockQueries = StockQueries(conn)
        with self.assertRaises(ValueError):
            stockQueries.symbol_to_isin('XXXX')
    
if __name__ == "__main__":
    unittest.main()