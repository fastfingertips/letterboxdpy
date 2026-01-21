from __future__ import annotations
from contextlib import contextmanager
from contextvars import ContextVar
from urllib.parse import quote

from bs4 import BeautifulSoup, Tag
from curl_cffi import requests

from letterboxdpy.constants.project import DOMAIN_FULL, SITE
from letterboxdpy.core.exceptions import (
    InvalidResponseError,
    PageFetchError,
    PageLoadError
)
from letterboxdpy.utils.utils_file import JsonFile

_active_scraper: ContextVar[Scraper | None] = ContextVar('_active_scraper', default=None)

class Scraper:
    """
    Handles network requests to Letterboxd using curl_cffi for performance 
    and Cloudflare bypass. Supports persistent sessions via instance or context manager.
    """
    domain: str = DOMAIN_FULL
    timeout: int | tuple[int, int] = (5, 15)
    builder: str = "lxml"

    _default_headers: dict = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Referer": SITE,
        "X-Requested-With": "XMLHttpRequest"
    }

    def __init__(self, domain: str | None = None, user_agent: str | None = None):
        """Initialize a scraper instance with a persistent session."""
        self.session = requests.Session()
        self.headers = Scraper._default_headers.copy()
        
        if domain:
            self.domain = domain
        if user_agent:
            self.headers["User-Agent"] = user_agent
        
        self.session.headers.update(self.headers)
        self._token = None

    def __enter__(self):
        self._token = _active_scraper.set(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._token:
            _active_scraper.reset(self._token)
            self._token = None
        self.session.close()

    @contextmanager
    def active(self):
        """
        Non-closing context manager: Temporarily sets this scraper as active 
        without closing the session on exit. Useful for internal library calls.
        """
        token = _active_scraper.set(self)
        try:
            yield self
        finally:
            _active_scraper.reset(token)

    def close(self):
        self.session.close()

    def get_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse HTML from URL."""
        response = self.fetch(url)
        self._check_for_errors(url, response)
        return self._parse_html(response)

    def fetch(self, url: str) -> requests.Response:
        """Fetch raw response from URL using the instance session."""
        try:
            return self.session.get(
                url,
                timeout=self.timeout[1] if isinstance(self.timeout, tuple) else self.timeout,
                impersonate="chrome131"
            )
        except Exception as e:
            raise PageLoadError(url, str(e))



    # Shared Utility

    @staticmethod
    def _check_for_errors(url: str, response: requests.Response) -> None:
        if response.status_code != 200:
            message = Scraper._get_error_message(response)
            error_details = Scraper._format_error(url, response, message)

            if response.status_code == 404:
                raise PageFetchError(error_details)
            else:
                raise PageLoadError(url, error_details)

    @staticmethod
    def _get_error_message(response: requests.Response) -> str:
        dom = BeautifulSoup(response.text, Scraper.builder)
        message_section = dom.find("section", {"class": "message"})
        
        if isinstance(message_section, Tag):
            strong = message_section.find("strong")
            if strong:
                return strong.get_text()
                
        return "Unknown error occurred"

    @staticmethod
    def _format_error(url: str, response: requests.Response, message: str) -> str:
        return JsonFile.stringify({
            'code': response.status_code,
            'reason': str(response.reason),
            'url': url,
            'message': message
        }, indent=2)

    @staticmethod
    def _parse_html(response: requests.Response) -> BeautifulSoup:
        try:
            return BeautifulSoup(response.text, Scraper.builder)
        except Exception as e:
            raise InvalidResponseError(f"Error parsing response: {e}")

def scrape(url: str, parse: bool = True) -> requests.Response | BeautifulSoup:
    """
    Unified context-aware scraper:
    - If parse=True (default): Returns BeautifulSoup (DOM).
    - If parse=False: Returns raw requests.Response.
    
    Uses active session if inside a 'with Scraper():' block, otherwise uses a temporary instance.
    """
    active = _active_scraper.get()
    scraper = active if active else Scraper()
    response = scraper.fetch(url)

    if not parse:
        return response

    Scraper._check_for_errors(url, response)
    return Scraper._parse_html(response)

def url_encode(query: str, safe: str = '') -> str:
    return quote(query, safe=safe)

if __name__ == "__main__":
    import sys
    from pykit.terminal_utils import get_input # type: ignore
   
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8') # type: ignore

    input_domain = ''
    while not len(input_domain.strip()):
        input_domain = get_input('Enter url: ', index=0)

    print(f"Parsing {input_domain}...")

    parsed_dom = scrape(input_domain)
    
    if isinstance(parsed_dom, BeautifulSoup):
        title_text = "No Title"
        if parsed_dom.title and parsed_dom.title.string:
            title_text = parsed_dom.title.string
            
        print(f"Title: {title_text}")

        input("Click Enter to see the DOM...")
        print(f"HTML: {parsed_dom.prettify()}")
    else:
        print("Error: Could not parse DOM.")
        
    print("*" * 20 + "\nDone!")