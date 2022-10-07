import sqlite3

connect = sqlite3.connect("news.db")
c = connect.cursor()
table_name = "stocks"

def get_ISIN(limit=None):
    if limit is not None:
        query = f"SELECT ISIN FROM {table_name} LIMIT {limit};"
    else:
        query = f"SELECT ISIN FROM {table_name};"
    c.execute(query)
    ISIN_numbers = [ISIN_number[0] for ISIN_number in c.fetchall()]
    return ISIN_numbers

def get_ISIN_and_news_link(tickers):
    keys = [f'ticker_{i}' for i in range(len(tickers))]
    keys_in_query = [f':ticker_{i}' for i in range(len(tickers))]
    ticker_dict = {key: value for key, value in zip(keys, tickers)}
    placeholder = ','.join(keys_in_query)
    query = f"""SELECT ISIN, NEWS_LINK FROM stocks_enriched
               WHERE SYMBOL IN ({placeholder});"""
    c.execute(query, ticker_dict)
    return c.fetchall()

print(get_ISIN_and_news_link(['GOOG', 'AMZN', 'ABT', 'AA']))