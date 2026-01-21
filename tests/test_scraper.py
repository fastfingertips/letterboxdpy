from letterboxdpy.core.scraper import Scraper, url_encode, scrape
from bs4 import BeautifulSoup
import unittest


class TestScraper(unittest.TestCase):

    def setUp(self):
        self.scraper = Scraper("letterboxd.com")

        self.valid_film_url = "https://letterboxd.com/film/dune-part-two/"
        self.invalid_film_url = "https://letterboxd.com/film/duneparttwo/"

    def test_valid_film_url(self):
        # Test direct scrape (stateless)
        self.assertIsInstance(
            scrape(self.valid_film_url), BeautifulSoup
        )
    
    def test_active_scraper_context(self):
        # Test with context manager
        with Scraper() as scraper:
            self.assertIsInstance(
                scrape(self.valid_film_url), BeautifulSoup
            )
            # The active session is used internally by scrape
            self.assertTrue(True) # Reached here means no exception
    
    def test_invalid_film_url(self):
        with self.assertRaises(Exception):
            scrape(self.invalid_film_url)

    def test_url_encode(self):
        query = "Dune: Part Two"
        encoded_query = url_encode(query)
        self.assertEqual(encoded_query, "Dune%3A%20Part%20Two")

if __name__ == '__main__':
    unittest.main()
