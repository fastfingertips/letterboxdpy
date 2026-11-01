"""Tests for the List class."""

import unittest

import pytest

from letterboxdpy.list import List, ListSort


@pytest.mark.smoke()
class TestList(unittest.TestCase):
    """Integration tests for List scraping methods."""

    @classmethod
    def setUpClass(cls):
        cls.list_instance = List("official", "letterboxds-top-500-films")

    def test_list_url_format(self):
        """Test list URL ends with a trailing slash to prevent 403 Forbidden errors."""
        self.assertTrue(self.list_instance.url.endswith("/"))
        self.assertEqual(
            self.list_instance.url,
            "https://letterboxd.com/official/list/letterboxds-top-500-films/",
        )

    def test_list_metadata(self):
        """Test basic metadata extraction of a list."""
        self.assertTrue(bool(self.list_instance.title))
        self.assertEqual(self.list_instance.username, "official")
        self.assertTrue(bool(self.list_instance.author))
        self.assertGreater(self.list_instance.count, 0)
        self.assertEqual(self.list_instance.last_page, 5)
        self.assertEqual(self.list_instance.total_pages, 5)

    def test_list_movies(self):
        """Test movie extraction from a list."""
        movies = self.list_instance.movies
        self.assertIsInstance(movies, dict)
        self.assertGreater(len(movies), 0)

    def test_list_pagination_constants(self):
        """Test pagination constant for UserList."""
        from letterboxdpy.pages.user_list import UserList

        self.assertEqual(UserList.FILMS_PER_PAGE, 100)

    def test_list_sort_by(self):
        """Test list with sort_by parameter."""
        sorted_list = List(
            "official", "letterboxds-top-500-films", sort_by=ListSort.POPULAR
        )
        self.assertEqual(sorted_list.sort_by, "popular")
        self.assertEqual(
            sorted_list.url,
            "https://letterboxd.com/official/list/letterboxds-top-500-films/by/popular/",
        )

    def test_list_get_page(self):
        """Test fetching a single page from a list."""
        p1 = self.list_instance.get_page(1)
        self.assertIsInstance(p1, dict)
        self.assertEqual(len(p1), 100)

    def test_list_max_pages(self):
        """Test limiting page extraction with max_pages."""
        two_pages = self.list_instance.get_movies(max_pages=1)
        self.assertIsInstance(two_pages, dict)
        self.assertEqual(len(two_pages), 100)

    def test_list_invalid_pagination_arguments(self):
        """Test invalid page numbers raise ValueError."""
        with self.assertRaises(ValueError):
            self.list_instance.get_page(0)
        with self.assertRaises(ValueError):
            self.list_instance.get_movies(max_pages=0)


if __name__ == "__main__":
    unittest.main()
