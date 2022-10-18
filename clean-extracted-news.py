import numpy as np
import pandas as pd
import json
import datetime
import requests
from bs4 import BeautifulSoup

file_path_news_content = (
    "data/stocks/news_content_UNLYF_2021-01-01_2021-12-31.json"
)
with open(file_path_news_content, "r") as f:
    news_data = json.load(f)
df_news = pd.DataFrame(news_data)


def html_to_text(markup):
    markup = markup.split("Weitere News zum Thema")[0]
    soup = BeautifulSoup(markup, "html.parser")
    clean_content = (
        " ".join([word.strip() for word in soup.text.split()])
        .encode("latin", errors="ignore")
        .decode(errors="ignore")
    )
    return clean_content


file_name = "data/stocks/news_content_UNLYF_2021-01-01_2021-12-31.csv"
df_news["content_clean"] = df_news["content_html"].apply(html_to_text)
df_news.drop("content_html", axis=1).to_csv(file_name)
print("Saved to: ", file_name)
