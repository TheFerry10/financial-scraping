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