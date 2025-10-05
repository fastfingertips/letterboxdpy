# Letterboxd Examples

Example scripts demonstrating `letterboxdpy` library features.

## Installation

```bash
pip install -e .
pip install -r examples/requirements.txt
```

## Examples

**`user_rating_plot.py`**  
Creates a rating distribution histogram with Letterboxd styling.
```bash
python examples/user_rating_plot.py --user <username>
```

**`user_plot_statistics.py`**  
Visualizes movie watching patterns over time with monthly and daily statistics.
```bash
python examples/user_plot_statistics.py --user <username> --start-year 2020 --end-year 2024
```

**`follow_stats.py`**  
Analyzes follow relationships, followback ratios, and mutual follows.
```bash
echo <username> | python examples/follow_stats.py
```

**`export_user_data.py`**  
Exports all user data (films, reviews, lists, followers, etc.) to JSON files.
```bash
echo <username> | python examples/export_user_data.py
```

**`export_user_diary_posters.py`**  
Downloads movie posters from diary entries and organizes them by year.
```bash
echo <username> | python examples/export_user_diary_posters.py
```

**`search_and_export_lists.py`**  
Searches for lists by query and exports them to CSV format.
```bash
echo -e "query\n3" > input.txt
Get-Content input.txt | python examples/search_and_export_lists.py
```

## Requirements

- **Core**: requests, beautifulsoup4, lxml, validators
- **Visualization**: matplotlib, numpy, pillow
- **Data Processing**: pandas

See `requirements.txt` for details.
