import math
import re

from fastfingertips.string_utils import extract_number_from_text

from letterboxdpy.constants.project import DOMAIN, GENRES
from letterboxdpy.core.exceptions import ResourceNotFoundError
from letterboxdpy.core.scraper import parse_url
from letterboxdpy.utils.movies_extractor import extract_movie_info
from letterboxdpy.utils.utils_url import (
    apply_sort_by_to_url,
    get_page_url,
    normalize_sort_by,
    parse_films_url,
)


class UserFilms:
    FILMS_PER_PAGE = 12 * 6

    def __init__(
        self,
        username: str,
        filters: dict | str | None = None,
        sort_by: str | None = None,
    ) -> None:
        self.username = username
        self.filters = filters
        self.url, self.sort_by = _build_films_url(self.username, self.filters, sort_by)
        self._dom = None

    def __str__(self) -> str:
        return f"Not printable object of type: {self.__class__.__name__}"

    @classmethod
    def from_url(cls, url: str, sort_by: str | None = None) -> "UserFilms":
        username, filters = parse_films_url(url)
        return cls(username=username, filters=filters, sort_by=sort_by)

    @property
    def dom(self):
        if self._dom is None:
            self._dom = parse_url(self.url)
        return self._dom

    def get_count(self) -> int:
        return extract_count(self.dom)

    def get_last_page(self, count: int | None = None) -> int:
        total = self.get_count() if count is None else count
        if total <= 0:
            return 0
        return math.ceil(total / self.FILMS_PER_PAGE)

    def get_films(
        self,
        sort_by: str | None = None,
        page: int | None = None,
        max_pages: int | None = None,
    ) -> dict:
        target_sort = sort_by or self.sort_by
        initial_dom = (
            self._dom
            if (target_sort == self.sort_by and self._dom is not None)
            else None
        )
        return extract_user_films(
            self.url,
            sort_by=target_sort,
            page=page,
            max_pages=max_pages,
            initial_dom=initial_dom,
        )

    def get_films_rated(
        self,
        rating: float | int,
        page: int | None = None,
        max_pages: int | None = None,
    ) -> dict:
        assert rating in [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5], "Invalid rating"
        clean_base = self.url.rstrip("/")
        url = f"{clean_base}/rated/{rating}/by/date/"
        return extract_user_films(url, page=page, max_pages=max_pages)

    def get_films_not_rated(
        self,
        page: int | None = None,
        max_pages: int | None = None,
    ) -> dict:
        clean_base = self.url.rstrip("/")
        url = f"{clean_base}/rated/none/by/date/"
        return extract_user_films(url, page=page, max_pages=max_pages)

    def get_genre_info(self) -> dict:
        return extract_user_genre_info(self.username)


def _build_films_url(
    username: str,
    filters: dict | str | None = None,
    sort_by: str | None = None,
) -> tuple[str, str | None]:
    """Constructs the base user films URL with filters and sorting applied."""
    active_sort = normalize_sort_by(sort_by)
    base_url = f"{DOMAIN}/{username}/films/"

    if isinstance(filters, str):
        clean_filter = filters.strip("/")
        if clean_filter:
            base_url = f"{base_url}{clean_filter}/"
    elif isinstance(filters, dict):
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

    if active_sort and "/by/" not in base_url:
        base_url = apply_sort_by_to_url(base_url, active_sort)

    return base_url, active_sort


def extract_count(dom_or_url) -> int:
    """Extracts total watched film count from page DOM or URL."""
    dom = parse_url(dom_or_url) if isinstance(dom_or_url, str) else dom_or_url
    if not dom:
        return 0

    heading = dom.find("p", class_="ui-block-heading")
    if heading:
        text = heading.get_text()
        digits = re.search(r"watched\s+([\d,]+)", text)
        if digits:
            return int(digits.group(1).replace(",", ""))
        if any(
            neg in text for neg in ("hasn\u2019t", "hasn't", "haven\u2019t", "haven't")
        ):
            return 0

    h1 = dom.find("h1", class_="section-heading")
    tooltip = h1.find("span", class_="tooltip") if h1 else None
    if tooltip and tooltip.get("title"):
        digits = re.search(r"[\d,]+", tooltip.get("title"))
        if digits:
            return int(digits.group(0).replace(",", ""))

    js_count = dom.find("span", class_="js-film-count")
    if js_count:
        digits = re.search(r"[\d,]+", js_count.get_text())
        if digits:
            return int(digits.group(0).replace(",", ""))

    replace = dom.find("span", class_="replace-if-you")
    if replace and replace.next_sibling:
        digits = re.search(r"[\d,]+", str(replace.next_sibling))
        if digits:
            return int(digits.group(0).replace(",", ""))

    return 0


def extract_user_films(
    url: str,
    sort_by: str | None = None,
    page: int | None = None,
    max_pages: int | None = None,
    initial_dom=None,
) -> dict:
    """Extracts user films and their details from the given URL."""
    if page is not None and page < 1:
        raise ValueError("page must be >= 1")
    if max_pages is not None and max_pages < 1:
        raise ValueError("max_pages must be >= 1")

    FILMS_PER_PAGE = 12 * 6
    target_sort = normalize_sort_by(sort_by)
    if target_sort and "/by/" not in url:
        url = apply_sort_by_to_url(url, target_sort)

    def calculate_statistics(movies: dict) -> dict:
        """Calculates film statistics including liked and rating percentages."""
        liked_count = sum(movie["liked"] for movie in movies.values())
        rating_count = len(
            [
                movie["rating"]
                for movie in movies.values()
                if movie["rating"] is not None
            ]
        )

        count = len(movies)
        liked_percentage = round(liked_count / count * 100, 2) if liked_count else 0.0
        rating_percentage = 0.0
        rating_average = 0.0

        if rating_count:
            ratings = [movie["rating"] for movie in movies.values() if movie["rating"]]
            rating_percentage = round(rating_count / count * 100, 2)
            rating_average = round(sum(ratings) / rating_count, 2)

        return {
            "count": count,
            "liked_count": liked_count,
            "rating_count": rating_count,
            "liked_percentage": liked_percentage,
            "rating_percentage": rating_percentage,
            "rating_average": rating_average,
        }

    movie_list = {"movies": {}}
    current_page = page or 1

    while True:
        if current_page == 1 and initial_dom is not None and not target_sort:
            dom = initial_dom
        else:
            page_url = get_page_url(url, current_page)
            dom = parse_url(page_url)

        movies = extract_movies_from_user_watched(dom)
        movie_list["movies"] |= movies

        if (
            page is not None
            or len(movies) < FILMS_PER_PAGE
            or (max_pages and current_page >= max_pages)
        ):
            break
        current_page += 1

    stats = calculate_statistics(movie_list["movies"])
    movie_list.update(stats)
    return movie_list


def extract_movies_from_user_watched(dom, max=12 * 6) -> dict:
    """
    supports user watched films section
    """

    def _extract_rating_and_like_status(container):
        """Parse rating and like status from viewing data spans."""

        def _extract_rating_from_span(span):
            """Extract rating from span using pattern matching."""
            classes = span.get("class", [])

            # Skip if no rating-related classes found
            if not any("rating" in cls or "rated-" in cls for cls in classes):
                return None

            # Define extraction patterns (modern first, legacy as fallback)
            patterns = [
                lambda cls: cls.startswith("rated-") and cls.split("-")[-1],  # rated-X
                lambda cls: (
                    "rating" in cls
                    and "-" in cls
                    and cls != "rating"
                    and cls.split("-")[-1]
                ),  # rating-color-X
            ]

            for pattern in patterns:
                for cls in classes:
                    try:
                        rating_str = pattern(cls)
                        if rating_str and rating_str.isdigit():
                            return int(rating_str) / 2.0
                    except (ValueError, IndexError, AttributeError):
                        continue

            return None

        def _extract_like_status(span):
            """Extract like status from span class."""
            return any("like" in cls for cls in span.get("class", []))

        poster_viewingdata = (
            container.find("p", {"class": "poster-viewingdata"}) or container.p
        )
        rating = None
        liked = False

        if poster_viewingdata and poster_viewingdata.span:
            for span in poster_viewingdata.find_all("span"):
                if rating is None:
                    rating = _extract_rating_from_span(span)
                if not liked:
                    liked = _extract_like_status(span)

        return rating, liked

    def _get_movie_details(container):
        """Extract complete movie information including rating and like status."""
        movie_data = extract_movie_info(container)
        if not movie_data:
            return None

        movie_id, data = movie_data
        rating, liked = _extract_rating_and_like_status(container)

        data.update({"id": movie_id, "rating": rating, "liked": liked})

        return data["slug"], data

    def _find_movie_containers(dom):
        """Find movie containers using modern structure with legacy fallback."""
        container_selectors = [
            ("li", {"class": "griditem"}),  # Modern React structure
            ("li", {"class": "poster-container"}),  # Legacy structure
            ("li", {"class": "posteritem"}),  # Liked films structure
        ]

        for tag, attrs in container_selectors:
            containers = dom.find_all(tag, attrs)
            if containers:
                return containers
        return []

    containers = _find_movie_containers(dom)

    movies = {}
    for container in containers:
        if len(movies) >= max:
            break

        movie_details = _get_movie_details(container)
        if movie_details:
            slug, data = movie_details
            movies[slug] = data

    return movies


def extract_user_genre_info(username: str) -> dict:
    ret = {}
    for genre in GENRES:
        try:
            dom = parse_url(f"{DOMAIN}/{username}/films/genre/{genre}/")
            data = dom.find(
                "span",
                {
                    "class": ["replace-if-you"],
                },
            )
            count = (
                extract_number_from_text(data.next_sibling)
                if data and data.next_sibling
                else 0
            )
            ret[genre] = count or 0
        except ResourceNotFoundError:
            ret[genre] = 0

    return ret
