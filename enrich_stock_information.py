import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import os
from glob import glob
import argparse

parser = argparse.ArgumentParser(description='Enrich stock information from finanzen.net')
parser.add_argument('--input-dir', type=str, dest='input_dir', default="data/stocks/processed", help='Input data dir')
parser.add_argument('--num-stocks', type=int, dest='num_stocks', default=None, help='Number of stocks to be processed')
args = parser.parse_args()

processed_data_path = args.input_dir
num_stocks = args.num_stocks
if num_stocks is None:
    print("Gather information for all stocks")

def load_file_path_to_latest_stock_collection(processed_data_path):
    stocks_file_paths = glob(processed_data_path + "/*_xetra.csv")
    datetime_strings = [os.path.basename(path).split('_')[0] for path in stocks_file_paths]
    for path in stocks_file_paths:
        if max(datetime_strings) in path:
            stocks_file_path = path
            print(f"Newest file: {stocks_file_path}")
            break
    return stocks_file_path


def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')


file_path_stock_collection = load_file_path_to_latest_stock_collection(
    processed_data_path)

if num_stocks is None:
    df_stocks = pd.read_csv(file_path_stock_collection)
else:
    df_stocks = pd.read_csv(file_path_stock_collection).sample(num_stocks)

path, ext = os.path.splitext(file_path_stock_collection)
new_path_and_ext = path + "_finanzen" + ext

base_url = "https://www.finanzen.net"

stock_properties_for_all_stocks = []
for search_string in df_stocks['ISIN'].values:
    stock_properties = dict()
    print(search_string)
    search_api = f"/suchergebnis.asp?strSuchString={search_string}"
    url = base_url + search_api
    soup = get_soup(url)
    
    # stock name
    stock_name = soup.find('h1', {'class': 'snapshot__headline'}).text
    stock_properties["stock_name"] = stock_name.encode('latin').decode()

    # instrument ids
    for instrument_id in soup.find('div', {'class': 'badge-bar'}).find_all('h2', {'class': 'badge background-color-de-black-haze pointer display-none-md margin-vertical-0.00'}):
        key, value = instrument_id.text.split(' ', 1)
        stock_properties[key] = value

    # news link
    news_link = soup.find('a', {'class': 'display-none-md font-whitespace-nowrap-md'}).attrs['href']
    stock_properties["news_link"] = base_url + news_link.encode('latin').decode()
    stock_properties_for_all_stocks.append(stock_properties)


df_stocks_enriched = pd.merge(df_stocks, pd.DataFrame(stock_properties_for_all_stocks), how='left', on='ISIN')
df_stocks_enriched.to_csv(new_path_and_ext, index=False)
print(f"Done! Enriched stock data saved to: {new_path_and_ext}")
