from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import sqlite3
from tqdm import tqdm
import pandas as pd
import numpy as np
from dataclasses import dataclass


def get_soup(response: dict):
    if response.status_code != 200:
        raise ValueError
    return BeautifulSoup(response.text, 'html.parser')

   
class WebsiteCheck(object):
    def __init__(self, url):
        self.url = url
        response = requests.get(url=self.url)
        self.soup = self.get_soup(response)
        
        
    def check_element_exists(self, element, target_text):
        results = self.soup.find(**element)
        if results:
            return target_text in results.get_text()
        else:
            return False