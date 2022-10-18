import scraping.queries.sql_queries as sql_queries

print("article_records_not_in_table")
print(sql_queries.article_records_not_in_table(["link_article"]))

print("get_columns_from_id")
get_columns_from_id_parameter = dict(
    id="f3c042162beb22e79ec8a4491126d53e1281b360", columns=["link_article"]
)

print(
    sql_queries.get_columns_from_id(
        get_columns_from_id_parameter["id"],
        get_columns_from_id_parameter["columns"],
    )
)
