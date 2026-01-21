"""
Scraper Context Manager Tests

Validates the new scraper system:
- Context manager sets active scraper correctly
- Session is reused within the same context
- curl_cffi library is used for requests
- parse_url respects the active scraper context
"""
import unittest
import sys
sys.path.insert(0, sys.path[0] + '/..')

from letterboxdpy.core.scraper import Scraper, _active_scraper, scrape
import curl_cffi


class TestScraperContext(unittest.TestCase):
    """Test suite for scraper context management."""

    def test_no_active_scraper_outside_context(self):
        """Active scraper should be None outside context."""
        self.assertIsNone(_active_scraper.get())

    def test_context_manager_sets_active_scraper(self):
        """Context manager should set the active scraper."""
        with Scraper() as s:
            active = _active_scraper.get()
            self.assertIsNotNone(active)
            self.assertIs(active, s)

    def test_context_manager_clears_active_scraper(self):
        """Active scraper should be None after exiting context."""
        with Scraper():
            self.assertIsNotNone(_active_scraper.get())
        self.assertIsNone(_active_scraper.get())

    def test_session_identity_preserved(self):
        """Same session object should be used for multiple requests."""
        with Scraper() as s:
            session_id_before = id(s.session)
            scrape("https://letterboxd.com/film/v-for-vendetta/")
            session_id_after = id(s.session)
            self.assertEqual(session_id_before, session_id_after)

    def test_curl_cffi_requests_module(self):
        """requests module should be from curl_cffi."""
        from letterboxdpy.core import scraper
        self.assertEqual(scraper.requests.__name__, 'curl_cffi.requests')

    def test_curl_cffi_session_type(self):
        """Session should be curl_cffi.requests.Session instance."""
        s = Scraper()
        self.assertIsInstance(s.session, curl_cffi.requests.Session)

    def test_parse_url_uses_active_context(self):
        """parse_url should use active scraper when inside context."""
        with Scraper() as s:
            self.assertIs(_active_scraper.get(), s)
            dom = scrape("https://letterboxd.com/film/inception/")
            self.assertIsNotNone(dom)
            self.assertIs(_active_scraper.get(), s)

    def test_parse_url_works_without_context(self):
        """parse_url should work without active context (stateless)."""
        self.assertIsNone(_active_scraper.get())
        dom = scrape("https://letterboxd.com/film/the-matrix/")
        self.assertIsNotNone(dom)

    def test_nested_context_restores_outer(self):
        """Inner context exit should restore outer context."""
        with Scraper() as outer:
            with Scraper() as inner:
                self.assertIs(_active_scraper.get(), inner)
            # After inner exits, outer should be restored
            self.assertIs(_active_scraper.get(), outer)


if __name__ == "__main__":
    unittest.main(verbosity=2)
