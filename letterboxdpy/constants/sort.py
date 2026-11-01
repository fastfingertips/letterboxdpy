"""
Sort constants for Letterboxd lists and watchlists.
"""


class ListSort:
    """Supported sort orders for Letterboxd curated lists."""

    SHUFFLE = "shuffle"
    NAME = "name"
    POPULAR = "popular"
    RELEASE = "release"
    RELEASE_EARLIEST = "release-earliest"
    RATING = "rating"
    RATING_LOWEST = "rating-lowest"
    ADDED = "added"
    ADDED_EARLIEST = "added-earliest"
    SHORTEST = "shortest"
    LONGEST = "longest"
    REVERSE = "reverse"
    YOUR_RATING = "your-rating"
    YOUR_RATING_LOWEST = "your-rating-lowest"
    YOUR_DIARY = "your-diary"
    YOUR_DIARY_EARLIEST = "your-diary-earliest"
    OWNER_RATING = "owner-rating"
    OWNER_RATING_LOWEST = "owner-rating-lowest"
    OWNER_DIARY = "owner-diary"
    OWNER_DIARY_EARLIEST = "owner-diary-earliest"


class WatchlistSort:
    """Supported sort orders for Letterboxd user watchlists."""

    DATE_LATEST = ""  # Default ordering (recently added)
    DATE_EARLIEST = "date-earliest"
    POPULAR = "popular"
    NAME = "name"
    RELEASE = "release"
    RELEASE_EARLIEST = "release-earliest"
    RATING = "rating"
    RATING_LOWEST = "rating-lowest"
    SHUFFLE = "shuffle"
    SHORTEST = "shortest"
    LONGEST = "longest"
    YOUR_RATING = "your-rating"
    YOUR_RATING_LOWEST = "your-rating-lowest"
