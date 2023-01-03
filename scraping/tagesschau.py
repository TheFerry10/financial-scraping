import sqlite3
from scraping.retrieve import get_soup, get_hash_from_string
import requests
import datetime
from datetime import date
from typing import List
from scraping.helper import normalize_datetime



class TagesschauScraper:
    
    def __init__(self):
        self.ressorts = ["wirtschaft", "inland", "ausland"]
        self.date_pattern = "%Y-%m-%d"
    
    def get_url(self, date_: date, ressort: str = None):
        date_str = date_.strftime(self.date_pattern)
        if ressort in self.ressorts:
            return f"https://www.tagesschau.de/archiv/?datum={date_str}&ressort={ressort}"
        elif ressort is None:
            return f"https://www.tagesschau.de/archiv/?datum={date_str}"
        else:
            raise ValueError
        
    
    def get_archive_headline(self, soup):
        archive_headline = soup.find(class_="archive__headline").get_text()
        return archive_headline
    
    def get_all_news_teaser(self, soup):
        all_news_teaser = soup.find_all(class_="columns teaser-xs twelve teaser-xs__wide")
        teasers = []
        for teaser in all_news_teaser:
            teaser_struct = dict()
            teaser_struct = {key: teaser.find(class_=f"teaser-xs__{key}").get_text(strip=True) for key in ['date', 'topline', 'headline', 'shorttext']}
            teaser_struct['link'] = teaser.find(class_="teaser-xs__link").get('href')
            teaser_struct['id'] = get_hash_from_string(teaser_struct['link'])
            teaser_struct['date'] = normalize_datetime(teaser_struct['date'])
            
            try:
                soup_link = get_soup(requests.get(teaser_struct['link']))
                teaser_struct['tags'] = ','.join(self.get_tags_from_article(soup_link))
                teasers.append(teaser_struct)
                 
            except requests.exceptions.TooManyRedirects:
                print(f"Article not found for link: {teaser_struct['link']}. Ignore extracted data.")
                
        return teasers
    
    def get_tags_from_article(self, soup):
        tags_group = soup.find(class_="taglist")
        if tags_group:
            return [tag.get_text(strip=True) for tag in tags_group.find_all(class_="tag-btn tag-btn--light-grey") if hasattr(tag, "get_text")]
        else:
            return []
        
        

class TagesschauDB:
    _DB_NAME = "news.db"
    _TABLE_NAME = "Tagesschau"
    
    def __init__(self):
        self.connect()
        
    def connect(self):
        self.conn = sqlite3.connect(TagesschauDB._DB_NAME)
        self.c = self.conn.cursor()
        print(f"Connected to {TagesschauDB._DB_NAME}")
        
    def create_table(self) -> None:
        query = f"""
            CREATE TABLE IF NOT EXISTS  {TagesschauDB._TABLE_NAME} (
            id text UNIQUE,
            timestamp datetime,
            topline text,
            headline text,
            shorttext text,
            link text,
            tags text)
            """
        self.c.execute(query)
        
    def drop_table(self) -> None:
        query = f"""
            DROP TABLE IF EXISTS {TagesschauDB._TABLE_NAME}
            """
        self.c.execute(query)
        
    def insert(self, content: dict) -> None:
        query = f"""
            INSERT OR IGNORE INTO {TagesschauDB._TABLE_NAME}
            VALUES (:id, :date, :topline, :headline, :shorttext, :link, :tags)
            """
        with self.conn:
            self.c.execute(query, content)
        



def get_dates_in_interval(start: date, end: date) -> List[date]:
    """
    Get all calendar dates between start end end date.
    """
    return [start + datetime.timedelta(days=x) for x in range((end - start).days + 1)]