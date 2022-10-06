class ArticleMetaData:
    """Article meta data"""

    def __init__(self, id, ISIN, date, title, source, kicker, link_article):
        self.id = id
        self.ISIN = ISIN
        self.date = date
        self.title = title
        self.source = source
        self.kicker = kicker
        self.link_article = link_article
        

    def __repr__(self):
        repr = f"ArticleMetaData({self.id}, {self.ISIN}, {self.date}, {self.title}, {self.source}, {self.kicker}, {self.link_article})"
        return repr

