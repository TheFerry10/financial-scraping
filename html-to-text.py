
from bs4 import BeautifulSoup

file_path_html = "data/stocks/tests/content.html"
with open(file_path_html, 'r') as f:
    html = f.read()


def html_to_text(markup):
    markup = markup.split('Weitere News zum Thema')[0]
    soup = BeautifulSoup(markup, 'html.parser')
    clean_content = ' '\
        .join([word.strip() for word in soup.text.split()])\
        .encode('latin', errors='ignore')\
        .decode(errors='ignore')
    return clean_content

text_from_html = html_to_text(html)
file_path_text = "data/stocks/tests/content.txt"
with open(file_path_text, 'w') as f:
    f.write(text_from_html)
print("Done!")
