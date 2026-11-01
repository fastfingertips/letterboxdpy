"""
Page parser for user watchlist.
Extracts watchlist data by scraping Letterboxd HTML pages.
"""

from letterboxdpy.constants.project import DOMAIN
from letterboxdpy.core.scraper import parse_url
from letterboxdpy.pages.user_list import extract_movies
from letterboxdpy.utils.movies_extractor import (
    extract_movies_from_vertical_list,
)
from letterboxdpy.utils.utils_parser import get_list_last_page
from letterboxdpy.utils.utils_url import (
    apply_sort_by_to_url,
    get_page_url,
    normalize_sort_by,
)


class UserWatchlist:
    FILMS_PER_PAGE = 7 * 4

    def __init__(self, username: str, sort_by: str | None = None) -> None:
        self.username = username
        self.sort_by = normalize_sort_by(sort_by)
        self.url = f"{DOMAIN}/{self.username}/watchlist/"
        if self.sort_by:
            self.url = apply_sort_by_to_url(self.url, self.sort_by)

    def __str__(self) -> str:
        return f"Not printable object of type: {self.__class__.__name__}"

    def get_owner(self) -> str:
        return self.username

    def get_count(self) -> int:
        return extract_count(self.url)

    def get_last_page(self) -> int:
        count = self.get_count()
        if count == 0:
            return 0
        return get_list_last_page(parse_url(self.url), count=count)

    @property
    def total_pages(self) -> int:
        return self.get_last_page()

    def get_movies(
        self,
        sort_by: str | None = None,
        page: int | None = None,
        max_pages: int | None = None,
    ) -> dict:
        target_sort = sort_by or self.sort_by
        return extract_movies(
            self.url,
            self.FILMS_PER_PAGE,
            sort_by=target_sort,
            page=page,
            max_pages=max_pages,
        )

    def get_page(self, page: int = 1, sort_by: str | None = None) -> dict:
        return self.get_movies(sort_by=sort_by, page=page)

    def get_watchlist(
        self,
        filters: dict | None = None,
        sort_by: str | None = None,
        page: int | None = None,
        max_pages: int | None = None,
    ) -> dict:
        target_sort = sort_by or self.sort_by
        return extract_watchlist(
            self.username,
            filters,
            sort_by=target_sort,
            page=page,
            max_pages=max_pages,
        )


def extract_count(url: str) -> int:
    """Extracts the number of films from the watchlist page's DOM."""
    dom = parse_url(url)

    watchlist_div = dom.find("div", class_="s-watchlist-content")
    if watchlist_div and "data-num-entries" in watchlist_div.attrs:
        return int(watchlist_div["data-num-entries"])

    count_span = dom.find("span", class_="js-watchlist-count")

    if count_span:
        count = count_span.text.split()[0]
        return int(count.replace(",", ""))

    raise ValueError("Watchlist count could not be extracted from DOM")


def _build_watchlist_url(
    username: str,
    filters: dict | None = None,
    sort_by: str | None = None,
) -> tuple[str, str | None]:
    """Constructs the base watchlist URL with filters and sorting applied."""
    active_sort = normalize_sort_by(sort_by)
    base_url = f"{DOMAIN}/{username}/watchlist/"

    if filters and isinstance(filters, dict):
        f = ""
        for key, values in filters.items():
            if key == "by":
                if not active_sort:
                    val = values[0] if isinstance(values, list) else values
                    active_sort = normalize_sort_by(val)
                continue
            if not isinstance(values, list):
                values = [values]
            f += f"{key}/"
            f += "+".join([str(v) for v in values]) + "/"
        base_url += f

    if active_sort:
        base_url = apply_sort_by_to_url(base_url, active_sort)

    return base_url, active_sort


def extract_watchlist(
    username: str,
    filters: dict | None = None,
    sort_by: str | None = None,
    page: int | None = None,
    max_pages: int | None = None,
) -> dict:
    """
    Extracts a user's watchlist from the platform.

    filter examples:
        - keys: decade, year, genre

        # positive genre & negative genre (start with '-')
        - {genre: ['mystery']}  <- same -> {genre: 'mystery'}
        - {genre: ['-mystery']} <- same -> {genre: '-mystery'}

        # multiple genres
        - {genre: ['mystery', 'comedy'], decade: '1990s'}
        - {genre: ['mystery', '-comedy'], year: '2019'}
        - /decade/1990s/genre/action+-drama/
          ^^---> {'decade':'1990s','genre':['action','-drama']}
    """
    if page is not None and page < 1:
        raise ValueError("Page number must be >= 1")
    if max_pages is not None and max_pages < 1:
        raise ValueError("max_pages must be >= 1")

    base_url, active_sort = _build_watchlist_url(username, filters, sort_by)

    data = {
        "available": False,
        "count": 0,
        "last_page": None,
        "filters": filters,
        "sort_by": active_sort,
        "data": {},
    }

    FILMS_PER_PAGE = 28  # Total films per page (7 rows * 4 columns)

    # Single-page extraction
    if page is not None:
        dom = parse_url(get_page_url(base_url, page))
        movies_on_page = extract_movies_from_vertical_list(dom)

        for no, (movie_id, movie_data) in enumerate(movies_on_page.items(), start=1):
            movie_data.update({"page": page, "no": no})
            data["data"][movie_id] = movie_data

        data["count"] = len(data["data"])
        data["available"] = data["count"] > 0
        data["last_page"] = page
        return data

    # Multi-page extraction
    current_page = 1
    no = 1
    while True:
        dom = parse_url(get_page_url(base_url, current_page))
        movies_on_page = extract_movies_from_vertical_list(dom)

        for movie_id, movie_data in movies_on_page.items():
            movie_data.update({"page": current_page, "no": no})
            data["data"][movie_id] = movie_data
            no += 1

        if len(movies_on_page) < FILMS_PER_PAGE or (
            max_pages and current_page >= max_pages
        ):
            break
        current_page += 1

    # Set the count of films and availability
    data["count"] = len(data["data"])
    data["available"] = data["count"] > 0
    data["last_page"] = current_page

    # Reverse numbering for default watchlist where Letterboxd lists newest added first
    if not active_sort and not max_pages:
        for fv in data["data"].values():
            fv.update({"no": data["count"] - fv["no"] + 1})

    return data
