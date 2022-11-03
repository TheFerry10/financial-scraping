import unittest
from stock.helper import get_pagination_links

class TestPagination(unittest.TestCase):
    def test_pagination(self):
        url = "https://www.finanzen.net/news/apple-news"
        sample_link = "https://www.finanzen.net/news/apple-news@intpagenr_1"
        links = get_pagination_links(url)
        self.assertIn(sample_link,
                      links,
                      f"Sample link {sample_link} should be in extracted links")
    
if __name__ == "__main__":
    unittest.main()