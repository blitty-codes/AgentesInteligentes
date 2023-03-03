import unittest
import logging
from datetime import datetime

from article import Article


class TestExtractor(unittest.TestCase):
    def test_n_10_since_2000(self):
        """
        Test can fetch information from 10 articles since 2000
        """
        # print("\n[+] Starting test_n_10_since_2000")
        art = Article(save_to_file=False)
        articles = art.extract(
                n=10,
                since=datetime.strptime('2000-1-23', '%Y-%m-%d'))
        
        self.assertEqual(len(articles), 10)
    
    def test_n_50_since_2000(self):
        """
        Test can fetch information from 50 articles since 2000
        """
        # print("\n[+] Starting test_n_50_since_2000")
        art = Article(save_to_file=False)
        articles = art.extract(
                n=50,
                since=datetime.strptime('2000-1-23', '%Y-%m-%d'))
        
        self.assertEqual(len(articles), 17)
    
    
    def test_n_100(self):
        """
        Test can fetch information from 50 articles since "today"
        """
        # print("\n[+] Starting test_n_100")

        art = Article(save_to_file=False)
        articles = art.extract(n=50)

        self.assertEqual(len(articles), 50)

if __name__ == '__main__':
    logging.basicConfig(level='DEBUG', format='%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
    unittest.main() 
