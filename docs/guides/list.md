# List Guide

The `List` class allows extracting metadata, film entries, creation dates, tags, and notes from any user-curated Letterboxd list.

---

## Quick Example

```python
from letterboxdpy.list import List

# Initialize using list author username and list slug
film_list = List("bugracoskun", "cold-palettes-dark-cities")

print(f"Title: {film_list.title}")
print(f"Author: {film_list.author}")
print(f"Total Films: {film_list.count}")
print(f"Created: {film_list.date_created}")
print(f"Updated: {film_list.date_updated}")
print(f"Tags: {film_list.tags}")
print(f"Description: {film_list.description}")
```

??? example "Sample `List` Payload Structure (Mock Demonstration)"

    ```json
    {
      "username": "bugracoskun",
      "slug": "cold-palettes-dark-cities",
      "list_id": "10000001",
      "title": "cold palettes, dark cities",
      "author": "bugra",
      "url": "https://letterboxd.com/bugracoskun/list/cold-palettes-dark-cities/",
      "count": 25,
      "date_created": "2025-01-01T00:00:00.000000Z",
      "date_updated": "2025-06-01T00:00:00.000000Z",
      "description": "Sample curated list demonstrating movie collection responses.",
      "tags": [
        "atmosphere",
        "neo-noir",
        "sample-list"
      ],
      "_movies": {
        "51345": {
          "slug": "se7en",
          "name": "Se7en",
          "year": 1995,
          "url": "https://letterboxd.com/film/se7en/"
        },
        "47104": {
          "slug": "the-crow",
          "name": "The Crow",
          "year": 1994,
          "url": "https://letterboxd.com/film/the-crow/"
        },
        "...": "..."
      }
    }
    ```

---

## Accessing and Iterating Films

The `.movies` property uses **lazy loading**; film entries are fetched and parsed from Letterboxd only upon first access, and cached for subsequent calls:

```python
# len() returns total films count
print(f"List size: {len(film_list)}")

# Iterate over movies dictionary
for movie_id, film in film_list.movies.items():
    print(f"- [{movie_id}] {film['name']} ({film['year']})")
    print(f"  URL: {film['url']}")
```

---

### Fetching Specific Pages & Limiting Extraction

By default, `.movies` or `.get_movies()` paginates through all pages until the end of the list. When working with large lists (e.g. lists containing thousands of entries) or building UI pagination, you can extract a single page or limit the number of pages fetched:

```python
# Fetch only page 1 (fast, single HTTP request)
page_one_films = film_list.get_movies(page=1)

# Fetch a specific page with sorting (e.g. shuffled page 1)
shuffled_sample = film_list.get_movies(page=1, sort_by="shuffle")

# Limit extraction to the first 2 pages (up to 200 films)
first_two_pages = film_list.get_movies(max_pages=2)
```

---

## Sorting List Entries

You can customize the ordering of films in a list using the `sort_by` parameter, either during initialization or directly via `.get_movies(sort_by=...)`. Letterboxd sort slugs such as `"popular"`, `"shuffle"`, `"release"`, `"rating"`, and `"name"` are supported natively or via the `ListSort` constants:

```python
from letterboxdpy.list import List, ListSort

# Initialize list with shuffled ordering
shuffled_list = List("official", "letterboxds-top-500-films", sort_by=ListSort.SHUFFLE)
print(shuffled_list.url)
# Output: https://letterboxd.com/official/list/letterboxds-top-500-films/by/shuffle/

# Fetch movies in specific sort order on demand
popular_films = shuffled_list.get_movies(sort_by=ListSort.POPULAR)
earliest_films = shuffled_list.get_movies(sort_by=ListSort.RELEASE_EARLIEST)
```

Common sort options provided in `ListSort`:

| Constant | Slug Value | Description |
| :--- | :--- | :--- |
| `ListSort.SHUFFLE` | `"shuffle"` | Randomize film order |
| `ListSort.POPULAR` | `"popular"` | Most popular films first |
| `ListSort.NAME` | `"name"` | Alphabetical by film title |
| `ListSort.RELEASE` | `"release"` | Newest release date first |
| `ListSort.RELEASE_EARLIEST` | `"release-earliest"` | Earliest release date first |
| `ListSort.RATING` | `"rating"` | Highest average rating first |
| `ListSort.RATING_LOWEST` | `"rating-lowest"` | Lowest average rating first |
| `ListSort.ADDED` | `"added"` | Most recently added to list |
| `ListSort.ADDED_EARLIEST` | `"added-earliest"` | Earliest added to list |
| `ListSort.SHORTEST` | `"shortest"` | Shortest runtime first |
| `ListSort.LONGEST` | `"longest"` | Longest runtime first |
| `ListSort.REVERSE` | `"reverse"` | Reverse curator's order |

## List Metadata Reference

| Property | Type | Description |
| :--- | :--- | :--- |
| `list_id` | `str` | Unique numeric identifier for the list on Letterboxd |
| `title` | `str` | Human-readable title of the list |
| `author` | `str` | Letterboxd username of the creator |
| `url` | `str` | Canonical web URL of the list |
| `sort_by` | `str \| None` | Active sort key applied to the list URL |
| `count` | `int` | Total number of film entries |
| `last_page` | `int` | Total number of pagination pages |
| `date_created`| `str` | ISO 8601 creation timestamp |
| `date_updated`| `str` | ISO 8601 last modified timestamp |
| `description` | `str` | Optional markdown/text notes attached to the list |
| `tags` | `list[str]` | Custom user tags assigned to the list |
| `movies` | `dict` | Dictionary mapping `movie_id` to movie dictionaries |

---

## API Reference

For detailed function definitions, see the [List API Reference](../api/list.md).
