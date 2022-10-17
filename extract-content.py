import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import os
import json
from glob import glob
import argparse
import sqlite3
from tqdm import tqdm
import html_to_text
import sql_queries

# Argument parsing
parser = argparse.ArgumentParser(description='Extract content from article meta data.')


def get_soup(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    else:
        print(f"Access denied for url: {url}. Output is None.")
        return None


def append_to_json(file_path_json, dict_to_save):
    news_object = []
    try:
        with open(file_path_json, 'r') as f:
            news_object = json.load(f)
    except FileNotFoundError:
        print(f"File {file_path_json} not found and will be created")

    news_object.append(dict_to_save)
    with open(file_path_json, 'w') as json_file:
        json.dump(news_object, json_file)


def is_url_ingested(id, file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        ids = [data_point['id'] for data_point in data]
    except FileNotFoundError:
        ids = []
    return id in ids


def is_div_element_in_soup(soup, element_prop):
    if soup.find('div', element_prop):
        return True
    else:
        return False


# sql helper functions
def get_id_and_news_links():
    query = """SELECT id, link_article FROM article_meta
               LIMIT 5;"""
    c.execute(query)
    return c.fetchall()

def insert_news_content(news_content):
    query = """INSERT OR IGNORE INTO article_content
               VALUES (:ID, :TIMESTAMP, :HEADLINE, :TEASER, :CONTENT)"""
    with connect:
        c.execute(query, news_content)
    

# connect to news.db
connect = sqlite3.connect("news.db")
c = connect.cursor()

# create table
c.execute("""
          CREATE TABLE IF NOT EXISTS article_content (
              ID text UNIQUE,
              TIMESTAMP text,
              HEADLINE text,
              TEASER text,
              CONTENT text
              )
          """)




base_url = "https://www.finanzen.net"


for id, url in tqdm(sql_queries.article_records_not_in_table(columns=['link_article'])):
    
    headline_text = None
    teaser_text = None
    news_extracted = None
    print(url)


    soup = get_soup(url)
    if soup:
        # headline
        if is_div_element_in_soup(soup, {'class': 'row news-snapshot'}):
            headline_html = soup.find(
                'div', {'class': 'row news-snapshot'})
        else:
            if is_div_element_in_soup(soup, {'class': 'single-article'}):
                headline_html = soup.find(
                    'div', {'class': 'single-article'})
            else:
                headline_html = None

        try:
            headline_text = headline_html.find(
                'h1').text.encode('latin').decode()
        except AttributeError:
            print('Headline has not been identified from the implemented rules.')
            print(headline_html)
            continue

        # teaser
        if is_div_element_in_soup(soup, {'class': 'teaser teaser-snapshot'}):
            teaser_html = soup.find(
                'div', {'class': 'teaser teaser-snapshot'})
        else:
            teaser_html = None

        try:
            teaser_text = teaser_html.find_all(
                'div')[-1].text.encode('latin').decode()
        except AttributeError:
            print('Teaser has not been identified from the implemented rules.')
            print(teaser_html)
            continue

        if is_div_element_in_soup(soup, {'class': 'pull-left mright-20'}):
            datetime_html = soup.find(
                'div', {'class': 'pull-left mright-20'})
        else:
            datetime_html = None

        try:
            datetime_text = datetime_html.text
        except AttributeError:
            print('No date found in article')
            datetime_text = None

        # news content
        news_container = soup.find('div', {'id': 'news-container'})

        div_properties_to_delete = [
            {'class': 'dropdown-container-triangle seperate-triangle'},
            {'class': 'dropdown-container-chartflow relative'},
            {'class': 'visible-xs-block'},
            {'class': 'pull-right'},
            {'class': 'lvgSearchOuter'},
            {'class': 'native-content-ad-container'},
            {'class': 'medium-font light-grey'},
            {'class': '', },
        ]

        for div_properties in div_properties_to_delete:
            if news_container.find('div', div_properties):
                news_container.find('div', div_properties).decompose()

        content_html = news_container.prettify()
        content_text = html_to_text.cut_text_at_phrase(text=html_to_text.html_to_text(content_html), phrase='Weitere News zum Thema')

        # put the content together in a structured format
        news_extracted = {key: value for key, value in zip(
            ['ID', 'TIMESTAMP', 'HEADLINE', 'TEASER', 'CONTENT'],
            [id, datetime_text, headline_text, teaser_text, content_text])
                          }
        insert_news_content(news_extracted)

