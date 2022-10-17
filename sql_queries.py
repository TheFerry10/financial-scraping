import sqlite3

connect = sqlite3.connect("news.db")
c = connect.cursor()


# Join the ID column from article meta and article content and select only 
# the ids which does't exist in article content. What kind of join operation is that?

def article_records_not_in_table(columns):
    columns_string = ','.join(['id'] + columns)
    query = f"""SELECT {columns_string}
                FROM article_meta
                WHERE id NOT IN (SELECT ID FROM article_content)
            """
    c.execute(query)
    return c.fetchall()

def get_columns_from_id(id, columns):
    columns_string = ','.join(columns)
    query = f"""SELECT {columns_string}
                FROM article_meta
                WHERE id = '{id}';
            """
    print(query)
    c.execute(query)
    return c.fetchall()