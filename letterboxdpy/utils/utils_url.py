import posixpath
import re
from urllib.parse import urlsplit, urlunsplit

from fastfingertips.url_utils import extract_path_segment

from letterboxdpy.constants.project import DOMAIN_SHORT, URL_PROTOCOLS


def extract_boxd_it_id(url: str) -> str | None:
    """
    extract the boxd.it id from a short url.
    example: 'https://boxd.it/7v7X' -> '7v7X'
    """
    return extract_path_segment(url, after=f"{DOMAIN_SHORT}/")


def get_list_slug(url: str) -> str | None:
    """
    extract the slug from a url containing '/list/'.
    example: 'https://letterboxd.com/fastfingertips/list/list_name/' -> 'list_name'
    """
    return extract_path_segment(url, after="/list/")


def is_short_url(url) -> bool:
    """
    this function checks if the URL is a short URL or not,
    and returns a boolean value as the result.
    """
    return any(prot + DOMAIN_SHORT in url for prot in URL_PROTOCOLS)


def resolve_short_url(url: str) -> str:
    """
    Resolves a boxd.it short URL to its canonical Letterboxd URL by following HTTP redirects.
    If the provided URL is not a short URL, it is normalized and returned directly.

    Example:
        >>> resolve_short_url("https://boxd.it/7v7X")
        'https://letterboxd.com/director/todd-haberkorn/'
    """
    if not isinstance(url, str) or not url.strip():
        return url

    if not is_short_url(url):
        return normalize_letterboxd_url(url)

    from letterboxdpy.constants.project import DOMAIN
    from letterboxdpy.core.scraper import Scraper

    session = Scraper.instance()
    response = session.get(
        url.strip(),
        headers=Scraper.headers,
        allow_redirects=False,
        impersonate="chrome120",
    )

    location = response.headers.get("Location")
    if location:
        if location.startswith("/"):
            location = f"{DOMAIN}{location}"
        return normalize_letterboxd_url(location)

    if getattr(response, "final_url", None) and response.final_url != url:
        return normalize_letterboxd_url(response.final_url)

    return normalize_letterboxd_url(url)


def parse_list_url(url: str) -> tuple:
    """Parse list URL to extract username and slug, resolving short URLs if needed."""
    resolved_url = resolve_short_url(url) if is_short_url(url) else url
    # URL format: https://letterboxd.com/username/list/slug/
    pattern = r"letterboxd\.com/([^/]+)/list/([^/]+)"
    match = re.search(pattern, resolved_url)
    if match:
        return match.group(1), match.group(2)
    raise ValueError(f"Invalid list URL format: {url}")


def parse_films_url(url: str) -> tuple[str, str | None]:
    """Parse user films URL to extract username and filter path, resolving short URLs if needed."""
    resolved_url = resolve_short_url(url) if is_short_url(url) else url
    normalized = normalize_letterboxd_url(resolved_url)
    parts = urlsplit(normalized)
    segments = [s for s in parts.path.split("/") if s]
    if len(segments) >= 2 and segments[1] == "films":
        username = segments[0]
        raw_filters = "/".join(segments[2:]) if len(segments) > 2 else None
        filters = None
        if raw_filters:
            cleaned = re.sub(r"(^|/)page/\d+/?", r"\1", raw_filters).strip("/")
            filters = cleaned if cleaned else None
        return username, filters
    raise ValueError(f"Invalid user films URL format: {url}")


def get_page_url(base_url: str, page: int, params: str = "") -> str:
    """
    Generate a paginated URL from a base URL and page number.
    Ensures no double slashes and consistent trailing slashes.

    Note:
        Letterboxd accepts both '/page/1/' and the clean root URL '/',
        but canonical pagination links on Letterboxd point to the root
        path for page 1, while page 2+ follow '/page/{N}/'.
    """
    # Remove any trailing slashes from the base URL
    clean_base = base_url.rstrip("/")
    # Letterboxd canonical pagination: root URL for page 1, /page/N/ for page 2+
    url = f"{clean_base}/" if page == 1 else f"{clean_base}/page/{page}/"
    if params:
        # Append params, ensuring no double '?'
        url += f"?{params.lstrip('?')}"
    return url


def normalize_letterboxd_url(url: str) -> str:
    """
    Normalizes Letterboxd URLs to ensure canonical trailing slashes.
    Prevents Cloudflare WAF challenges and redundant 301/302 redirects.
    Preserves query parameters, fragments, and avoids file extensions.
    """
    if not isinstance(url, str) or not url.strip():
        return url

    parts = urlsplit(url)
    # Only normalize Letterboxd web domains
    if not parts.netloc or "letterboxd.com" not in parts.netloc:
        return url

    path = parts.path
    if not path:
        path = "/"
    elif not path.endswith("/"):
        # Do not append slash if path has a file extension (e.g. .csv, .jpg, .png, .xml)
        _, ext = posixpath.splitext(path)
        if not ext:
            path += "/"

    return urlunsplit((parts.scheme, parts.netloc, path, parts.query, parts.fragment))


def normalize_sort_by(sort_by: str | None) -> str | None:
    """
    Normalizes a sort_by string, stripping leading/trailing slashes and
    removing redundant 'by/' prefixes. Returns None if empty or invalid.

    Example:
        >>> normalize_sort_by("shuffle")
        'shuffle'
        >>> normalize_sort_by("/by/popular/")
        'popular'
        >>> normalize_sort_by("by/release-earliest")
        'release-earliest'
        >>> normalize_sort_by(None)
        None
    """
    if not sort_by or not isinstance(sort_by, str):
        return None

    cleaned = sort_by.strip().strip("/")
    if cleaned.lower().startswith("by/"):
        cleaned = cleaned[3:].strip("/")

    return cleaned if cleaned else None


def apply_sort_by_to_url(url: str, sort_by: str | None) -> str:
    """
    Applies or replaces a /by/{sort_by}/ segment in a Letterboxd URL.
    Preserves trailing slashes, query parameters, and URL fragments.

    Example:
        >>> apply_sort_by_to_url("https://letterboxd.com/user/list/slug/", "shuffle")
        'https://letterboxd.com/user/list/slug/by/shuffle/'
        >>> apply_sort_by_to_url("https://letterboxd.com/user/list/slug/by/name/", "popular")
        'https://letterboxd.com/user/list/slug/by/popular/'
    """
    sort_slug = normalize_sort_by(sort_by)
    if not sort_slug:
        return url

    # If the URL already contains a /by/.../ segment, replace it
    if "/by/" in url:
        return re.sub(r"/by/[^/?#]+/?", f"/by/{sort_slug}/", url)

    # Otherwise append /by/{sort_slug}/ before query and fragment
    parts = urlsplit(url)
    clean_path = parts.path.rstrip("/") + f"/by/{sort_slug}/"
    return urlunsplit(
        (parts.scheme, parts.netloc, clean_path, parts.query, parts.fragment)
    )
