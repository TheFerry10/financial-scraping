from bs4 import BeautifulSoup


def html_to_text(markup):
    soup = BeautifulSoup(markup, "html.parser")
    clean_content = (
        " ".join([word.strip() for word in soup.text.split()])
        .encode("latin", errors="ignore")
        .decode(errors="ignore")
    )
    return clean_content


def cut_text_at_phrase(text, phrase):
    return text.split(phrase)[0]


# file_path_html = "data/stocks/tests/content.html"
# with open(file_path_html, 'r') as f:
#     html = f.read()
# text_from_html = cut_text_at_phrase(text=html_to_text(html), phrase='Weitere News zum Thema')
# file_path_text = "data/stocks/tests/content.txt"
# with open(file_path_text, 'w') as f:
#     f.write(text_from_html)
