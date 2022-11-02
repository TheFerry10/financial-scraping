from stock.helper import get_pagination_links

url = "https://www.finanzen.net/news/apple-news"
links = get_pagination_links(url)

print(links)