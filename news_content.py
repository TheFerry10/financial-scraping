import argparse
import sqlite3
from stock.helper import ArticleContentScraper

parser = argparse.ArgumentParser(
    description="Extract content from article meta data."
)

conn = sqlite3.connect("news.db")

scraper = ArticleContentScraper(conn)
scraper.run()
