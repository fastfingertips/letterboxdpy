"""Tests for the UserFilms class and film page extraction."""

import unittest

import pytest
from bs4 import BeautifulSoup

from letterboxdpy.pages.user_films import (
    UserFilms,
    _build_films_url,
    extract_count,
)
from letterboxdpy.utils.utils_url import parse_films_url


class TestUserFilmsUnit(unittest.TestCase):
    """Unit tests for UserFilms URL construction and count extraction."""

    def test_build_films_url_default(self):
        url, sort = _build_films_url("nmcassa")
        self.assertEqual(url, "https://letterboxd.com/nmcassa/films/")
        self.assertIsNone(sort)

    def test_build_films_url_string_filter(self):
        url, sort = _build_films_url("nmcassa", "genre/comedy")
        self.assertEqual(url, "https://letterboxd.com/nmcassa/films/genre/comedy/")
        self.assertIsNone(sort)

    def test_build_films_url_with_sort(self):
        url, sort = _build_films_url("nmcassa", sort_by="rating")
        self.assertEqual(url, "https://letterboxd.com/nmcassa/films/by/rating/")
        self.assertEqual(sort, "rating")

    def test_build_films_url_dict_filter_and_sort(self):
        url, sort = _build_films_url(
            "nmcassa",
            {"genre": "action", "decade": "1990s"},
            sort_by="popular",
        )
        self.assertEqual(
            url,
            "https://letterboxd.com/nmcassa/films/genre/action/decade/1990s/by/popular/",
        )
        self.assertEqual(sort, "popular")

    def test_parse_films_url(self):
        username, filters = parse_films_url("https://letterboxd.com/nmcassa/films/")
        self.assertEqual(username, "nmcassa")
        self.assertIsNone(filters)

        username, filters = parse_films_url(
            "https://letterboxd.com/nmcassa/films/genre/comedy/"
        )
        self.assertEqual(username, "nmcassa")
        self.assertEqual(filters, "genre/comedy")

        username, filters = parse_films_url(
            "https://letterboxd.com/nmcassa/films/genre/action/page/3/"
        )
        self.assertEqual(username, "nmcassa")
        self.assertEqual(filters, "genre/action")

    def test_extract_count_from_dom_variations(self):
        # 1. Heading with count
        html1 = "<p class='ui-block-heading'>nmcassa has watched 369 comedy films.</p>"
        dom1 = BeautifulSoup(html1, "html.parser")
        self.assertEqual(extract_count(dom1), 369)

        # 2. Heading with zero watched
        html2 = "<p class='ui-block-heading'>nmcassa hasn't watched any films released in 1870.</p>"
        dom2 = BeautifulSoup(html2, "html.parser")
        self.assertEqual(extract_count(dom2), 0)

        # 3. Section heading tooltip
        html3 = "<h1 class='section-heading'><span class='tooltip' title='770&nbsp;films'>Watched</span></h1>"
        dom3 = BeautifulSoup(html3, "html.parser")
        self.assertEqual(extract_count(dom3), 770)

        # 4. Empty DOM
        self.assertEqual(extract_count(None), 0)


@pytest.mark.smoke()
class TestUserFilmsIntegration(unittest.TestCase):
    """Integration tests for UserFilms scraping."""

    @classmethod
    def setUpClass(cls):
        cls.films = UserFilms("nmcassa")

    def test_user_films_metadata(self):
        self.assertEqual(self.films.username, "nmcassa")
        self.assertEqual(self.films.url, "https://letterboxd.com/nmcassa/films/")
        count = self.films.get_count()
        self.assertGreater(count, 0)
        last_page = self.films.get_last_page(count)
        self.assertGreater(last_page, 0)

    def test_user_films_from_url(self):
        films = UserFilms.from_url("https://letterboxd.com/nmcassa/films/genre/comedy/")
        self.assertEqual(films.username, "nmcassa")
        self.assertEqual(films.filters, "genre/comedy")
        self.assertEqual(
            films.url, "https://letterboxd.com/nmcassa/films/genre/comedy/"
        )
        self.assertGreater(films.get_count(), 0)

    def test_user_films_get_single_page(self):
        page1 = self.films.get_films(page=1)
        self.assertIn("movies", page1)
        self.assertEqual(len(page1["movies"]), UserFilms.FILMS_PER_PAGE)
        self.assertIn("rating_average", page1)

    def test_user_films_invalid_pagination(self):
        with self.assertRaises(ValueError):
            self.films.get_films(page=0)
        with self.assertRaises(ValueError):
            self.films.get_films(max_pages=0)


if __name__ == "__main__":
    unittest.main()
