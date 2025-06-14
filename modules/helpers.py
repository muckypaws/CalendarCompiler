"""
Various helper functions covering basic I/O, Settings Retrieval, Merge Calendar Data Etc.

and much more...
"""
import os
import sys
import subprocess
import json
import re
import calendar
import textwrap
from datetime import datetime
from datetime import date, timedelta
from dotenv import load_dotenv
from modules.holiday_types import MultiColourHolidayDict

#try:
#    from modules.holiday_types import MultiColourHolidayDict
#except ModuleNotFoundError:
#    # fallback for running helpers.py directly or in debugging
#    import sys
#    import os
#    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#    from modules.holiday_types import MultiColourHolidayDict

# Module-level variable to cache settings after first load
_CACHED_SETTINGS = None
_json_cache = {}

def get_api_key(settings=None, keyname="MY_API_KEY", env_path=".env"):
    """
    Retrieve API key, trying (in order):.

    1. settings dict (lowercase key)
    2. .env file (ENV key, uppercase)
    3. OS environment variables (uppercase)

    Args:
        settings (dict, optional): Settings dict, may contain the key.
        keyname (str): Name of the key to look up (case-insensitive).
        env_path (str): Path to .env file.

    Returns:
        str: The API key value.

    Raises:
        RuntimeError: If no API key is found by any method.
    """
    settings_key = keyname.lower()
    env_keyname = keyname.upper()

    # 1. Try settings dict (lowercase)
    if settings and settings_key in settings:
        if settings[settings_key] != "USE_ENVIRONMENT":
            return settings[settings_key]

    # 2. Try .env file (uppercase key)
    load_dotenv(env_path)
    env_val = os.getenv(env_keyname)
    if env_val:
        return env_val

    # 3. Try OS env directly (uppercase key)
    env_val = os.environ.get(env_keyname)
    if env_val:
        return env_val

    # Not found
    raise RuntimeError(
        f"API key '{env_keyname}' not found in settings.json, .env file, or environment variables!"
    )

def is_enabled(settings, key):
    """
    Check if a feature flag (e.g. 'uk_holidays') is enabled in settings['include_days'].

    Defaults to False if the section or key is missing.

    Args:
        settings (dict): Settings dictionary.
        key (str): Feature key to check.

    Returns:
        bool: True if enabled, False otherwise.
    """
    return settings.get("include_days", {}).get(key, False)

def open_file_or_folder(path):
    """
    Open a file (PDF) or folder (image directory) with the system's default app/platform.

    Supports Windows, macOS, and Linux.
    
    Args:
        path (str): The path to the file or directory.
    """
    if sys.platform.startswith('darwin'):  # macOS
        subprocess.run(['open', path])
    elif sys.platform.startswith('win'):
        os.startfile(os.path.normpath(path))
    elif sys.platform.startswith('linux'):
        subprocess.run(['xdg-open', path])
    else:
        print(f"Cannot open files on this OS: {sys.platform}")

def load_settings(settings_path="./config/settings.json", force_reload=False):
    """
    Load (and cache) configuration parameters from a JSON file.

    Args:
        settings_path (str): Path to the JSON config file.
        force_reload (bool): If True, re-read from disk even if cached.

    Returns:
        dict: Parsed configuration dictionary.

    Raises:
        FileNotFoundError: If the config file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    global _CACHED_SETTINGS
    if _CACHED_SETTINGS is not None and not force_reload:
        return _CACHED_SETTINGS

    if not os.path.exists(settings_path):
        raise FileNotFoundError(f"Settings file '{settings_path}' not found.")

    with open(settings_path, "r", encoding="utf-8") as f:
        settings = json.load(f)

    _CACHED_SETTINGS = settings
    return _CACHED_SETTINGS

def remap_null_keys(data: dict, null_key: str = 'NATIONAL') -> dict:
    """
    Convert specified string key in a dictionary to Python None key.

    Args:
        data (dict): The dictionary to process.
        null_key (str): The placeholder string representing None in JSON.

    Returns:
        dict: Dictionary with specified key replaced by None.
    """
    return {None if k == null_key else k: v for k, v in data.items()}


def save_json(data, file_path, pretty=True):
    """
    Save Python data as a JSON file.

    Parameters:
        data (dict or list): The data to serialize and write to file.
        file_path (str): The full path (including filename) to save the JSON output.
        pretty (bool): Whether to use indented formatting for readability. Defaults to True.

    Raises:
        OSError: If the file cannot be written.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        if pretty:
            json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            json.dump(data, f, separators=(',', ':'), ensure_ascii=False)

def load_json_cached(file_path):
    """Load data from a JSON file with internal caching to prevent redundant I/O."""
    if file_path in _json_cache:
        return _json_cache[file_path]

    data = load_json(file_path)
    _json_cache[file_path] = data
    return data

def load_json(file_path):
    """
    Load data from a JSON file.

    Parameters:
        file_path (str): The full path to the JSON file to be loaded.

    Returns:
        dict or list: The deserialized data from the JSON file.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No such file: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        #print(f"Loading File: {file_path}")
        return json.load(f)

def merge_holiday_data(base: MultiColourHolidayDict, additional: MultiColourHolidayDict) -> None:
    """
    Merge additional holiday data into the base dictionary.

    Deduplicates entries and ensures consistency across formats.
    
    Args:
        base (MultiColourHolidayDict): Main holiday dataset (in-place modified).
        additional (MultiColourHolidayDict): Additional data to merge in.
    """
    for date_key, data in additional.items():
        # --- Normalise additional input ---
        if "entries" not in data and "label" in data and "colour" in data:
            data = {"entries": [{"label": data["label"], "colour": data["colour"]}]}

        # --- Normalise base input ---
        if date_key not in base:
            base[date_key] = data  # Safe to add directly now that additional is normalised
            #continue
        elif "entries" not in base[date_key] and "label" in base[date_key]:
            legacy = base[date_key]
            base[date_key] = {"entries": [{"label": legacy["label"], "colour": legacy["colour"]}]}

        # Merge entries, deduplicate by label and unify colours if mismatched
        all_entries = base[date_key]["entries"] + data["entries"]
        grouped = {}
        for entry in all_entries:
            label = entry["label"]
            grouped.setdefault(label, set()).add(entry["colour"])

        base[date_key]["entries"] = [
            {"label": label, "colour": "black" if len(colours) > 1 else list(colours)[0]}
            for label, colours in grouped.items()
        ]

def wrap_text(text, max_chars=22):
    """
    Wrap a string into a list of lines, each with a maximum character count.

    Args:
        text (str): The input string.
        max_chars (int): Approximate number of characters per line.

    Returns:
        List[str]: Wrapped lines.
    """
    return textwrap.wrap(text, width=max_chars)


def canonicalise_label(label: str) -> str:
    """
    Convert a holiday or event label to a canonical (normalised) form for deduplication.

    Handles common abbreviation and variant cases, e.g. 'Saint' vs 'St', punctuation,
    and British/American English differences.

    Args:
        label (str): The event or holiday label to normalise.

    Returns:
        str: Canonicalised label string.
    """
    # Lowercase for case-insensitive matching
    canon = label.lower()

    # Replace common English holiday terms
    canon = canon.replace('&', 'and')
    canon = re.sub(r"\bsaint\b", "St", canon)
    canon = re.sub(r"\bst\.?\b", "St", canon)
    canon = canon.replace('shrove tuesday', 'Pancake Day')
    #canon = canon.replace('all hallows', 'All Saints')

    # Remove possessives and other punctuation
    canon = re.sub(r"[’']", '', canon)        # Remove apostrophes/quotes
    canon = re.sub(r"[^\w\s]", '', canon)     # Remove other punctuation

    # Remove redundant words
    canon = re.sub(r"\bday\b", '', canon)
    canon = re.sub(r"\bthe\b", '', canon)
    canon = re.sub(r"\bholiday\b", '', canon)
    canon = re.sub(r"\bhol\b", '', canon)

    # Normalise whitespace
    canon = re.sub(r"\s+", " ", canon)
    canon = canon.strip()

    return canon

def trim_calendar_grid(grid, target_month):
    """
    Trim trailing rows from a full 6x7 calendar grid if they contain only days outside the target month.

    Args:
        grid (list): List of week rows, each a list of (year, month, day, is_current_month) tuples.
        target_month (int): The integer month being displayed.

    Returns:
        list: The trimmed grid with extraneous bottom rows removed.
    """
    while grid and all(cell[1] != target_month for cell in grid[-1]):
        grid.pop()
    return grid


def build_full_calendar_grid(year, month, week_start=0):
    """
    Generate a complete 6x7 calendar grid for a specified month.
    
    Including spillover days from the previous and next months, suitable for display 
    in calendar layouts.

    This function constructs a two-dimensional list representing the calendar for the given
    month and year. Each cell contains a tuple with the year, month, day, and a boolean
    indicating whether the day belongs to the requested month. The grid always contains 6 rows
    (weeks) and 7 columns (days), ensuring a uniform structure for calendar rendering.
    Days that belong to the previous or next month are included to fill the grid and
    may be styled differently in display logic.

    Args:
        year (int): The calendar year (e.g., 2026).
        month (int): The calendar month (1–12).
        week_start (int, optional): The starting weekday for the calendar (0=Monday, 6=Sunday).
            Defaults to 0 (Monday), which matches UK and ISO-8601 conventions.

    Returns:
        list[list[tuple]]: A 6x7 list-of-lists structure.
            Each inner list represents a week and contains 7 tuples of the form:
                (cell_year, cell_month, cell_day, is_current_month)
            - cell_year (int): The year of the date in the cell.
            - cell_month (int): The month of the date in the cell.
            - cell_day (int): The day of the month for the cell.
            - is_current_month (bool): True if the cell belongs to the target month, 
            - False otherwise.

    Example:
        >>> build_full_calendar_grid(2026, 1, week_start=0)[0]
        [(2025, 12, 29, False), (2025, 12, 30, False), (2025, 12, 31, False),
         (2026, 1, 1, True), (2026, 1, 2, True), (2026, 1, 3, True), (2026, 1, 4, True)]
    """
    cal = calendar.Calendar(firstweekday=week_start)
    first_day_of_month = date(year, month, 1)
    first_weekday = (first_day_of_month.weekday() - week_start) % 7
    # Find first cell date (might be in prev month)
    grid_start = first_day_of_month - timedelta(days=first_weekday)
    grid = []
    for i in range(6 * 7):
        cell_date = grid_start + timedelta(days=i)
        grid.append((
            cell_date.year,
            cell_date.month,
            cell_date.day,
            cell_date.month == month  # True if this cell is the actual month
        ))
    # Make it a list-of-lists (rows of 7)
    return [grid[i*7:(i+1)*7] for i in range(6)]

def export_holiday_validation_file(settings: dict, holiday_data: dict):
    """Export the fully merged holiday data to a validation file."""
    year = settings.get("year", "unknown")
    output_file = f"holiday_export_{year}.csv"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("Date,Label,Colour\n")
        for date_key in sorted(holiday_data.keys()):
            entries = holiday_data[date_key].get("entries", [])
            for entry in entries:
                f.write(f"{date_key},{entry['label']},{entry['colour']}\n")

    print(f"Holiday export file written: {output_file}")

def update_year_key(year, base):
    """
    Update MM-DD event dictionary to YYYY-MM-DD for a given year, skipping invalid dates.

    Args:
        year (int): Target year for the events (e.g., 2027).
        base (dict): Dictionary with 'MM-DD' keys and event info as values.

    Returns:
        dict: New dictionary with valid 'YYYY-MM-DD' keys and event info as values.
              Invalid dates (e.g., Feb 29 in non-leap years) are skipped.
    """
    events = {}
    for mmdd, info in base.items():
        date_str = f"{year}-{mmdd}"
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            events[date_str] = info
        except ValueError:
            continue
    return events

def resolve_config_path(filename: str) -> str:
    """
    Resolve full path to a file inside config/events directory.

    Args:
        filename (str): Name of JSON file inside config/events.

    Returns:
        str: Full absolute path.
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))  # modules/ -> project root
    return os.path.join(base_dir, 'config', 'events', filename)

def merge_holiday_dicts(*dicts) -> dict:
    """
    Merge multiple holiday dictionaries into a single dictionary.

    Args:
        *dicts: Variable number of dict arguments.

    Returns:
        dict: Merged dictionary.
    """
    merged = {}
    for d in dicts:
        merged.update(d)
    return merged