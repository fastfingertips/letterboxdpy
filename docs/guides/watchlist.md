# Watchlist Guide

`letterboxdpy` provides two complementary approaches to access a user's watchlist: the dedicated lightweight `Watchlist` class, and the filtered `UserWatchlist` page handler.

---

## Standalone `Watchlist` Class

The simplest way to inspect a member's saved watchlist:

```python
from letterboxdpy.watchlist import Watchlist, WatchlistSort

# Default watchlist (ordered by date added)
watchlist = Watchlist("bugracoskun")

# Watchlist sorted by popularity or shuffled
shuffled_watchlist = Watchlist("bugracoskun", sort_by=WatchlistSort.SHUFFLE)
popular_watchlist = Watchlist("bugracoskun", sort_by=WatchlistSort.POPULAR)

print(f"Username: {watchlist.username}")
print(f"Total Films: {watchlist.count}")

# .movies is lazily evaluated on first access
for movie_id, film in list(watchlist.movies.items())[:5]:
    print(f"- {film['name']} ({film['year']}) -> {film['url']}")
```

??? example "Sample `Watchlist` Payload Structure (Mock Demonstration)"

    ```json
    {
      "username": "bugracoskun",
      "url": "https://letterboxd.com/bugracoskun/watchlist/",
      "count": 150,
      "movies": {
        "51557": {
          "slug": "constantine",
          "name": "Constantine",
          "year": 2005,
          "url": "https://letterboxd.com/film/constantine/"
        },
        "35903": {
          "slug": "time",
          "name": "Time",
          "year": 2006,
          "url": "https://letterboxd.com/film/time/"
        },
        "...": "..."
      }
    }
    ```

---

## Advanced Filtered Watchlists

When you need to filter a user's watchlist by genre, decade, release year, or streaming provider, use the `pages.watchlist` handler on a `User` instance:

```python
from letterboxdpy.user import User

user = User("bugracoskun")
```

=== "Filter by Genre"
    ```python
    # Positive genre filter
    mystery_watchlist = user.pages.watchlist.get_watchlist(
        filters={"genre": ["mystery"]}
    )

    # Exclude specific genres (e.g. no horror)
    no_horror = user.pages.watchlist.get_watchlist(
        filters={"genre": ["-horror"]}
    )
    ```

=== "Filter by Decade / Year"
    ```python
    # 1990s films in watchlist
    nineties = user.pages.watchlist.get_watchlist(
        filters={"decade": "1990s"}
    )

    # Released in 2024
    films_2024 = user.pages.watchlist.get_watchlist(
        filters={"year": "2024"}
    )
    ```

=== "Sort Watchlist"
    ```python
    # Watchlist sorted by highest rating
    highest_rated = user.pages.watchlist.get_watchlist(
        sort_by="rating"
    )

    # Shuffled watchlist combined with genre filter
    shuffled_scifi = user.pages.watchlist.get_watchlist(
        filters={"genre": "science-fiction"},
        sort_by="shuffle"
    )
    ```

=== "Filter by Streaming Service"
    ```python
    # Available on Criterion Channel or Netflix
    streaming = user.pages.watchlist.get_watchlist(
        filters={"service": ["criterion-channel", "netflix"]}
    )
    ```

??? example "Example Filtered Watchlist Output"

    ```json
    {
      "count": 14,
      "data": {
        "51557": {
          "name": "Constantine",
          "year": 2005,
          "slug": "constantine",
          "url": "https://letterboxd.com/film/constantine/"
        }
      }
    }
    ```

---

## API Reference

For detailed class definitions, see:
- [Watchlist API Reference](../api/watchlist.md)
- [User API Reference](../api/user.md)
