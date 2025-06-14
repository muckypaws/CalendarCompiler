"""
Module for loading various event datasets into the CalendarCompiler system.

This module centralises the loading, merging, and management of multiple categories 
of holidays, observances, and events, including:

- International days (official, semi-official, fun)
- Religious holidays
- Retro computing anniversaries
- UK public holidays
- User-defined custom events

Event data is expected to be stored in JSON format within the config/events directory.

All loaders return a dictionary where keys are date strings (formatted MM-DD)
and values are dictionaries containing holiday/event metadata such as labels and colours.

Functions:
    - resolve_config_path(): Build full file paths for event files.
    - merge_holiday_dicts(): Merge multiple event dictionaries.
    - load_international_events(): Load international events by category.
    - load_religious_events(): Load religious holidays.
    - load_retro_events(): Load retro computing anniversaries.
    - load_uk_holidays(): Load UK public holidays.
    - load_custom_events(): Load user-defined custom events.

Author: Jason Brooks
"""
from modules.helpers import (
    load_json, 
    update_year_key, 
    resolve_config_path,
    merge_holiday_dicts,
    load_json_cached
    )

def load_international_events(year :int, intl_settings: dict) -> dict:
    """
    Load international events based on fine-grained config.

    Args:
        intl_settings (dict): dict containing sub-keys official/semi_official/fun.

    Returns:
        dict: Combined international holidays.
    """
    event_sources = []

    if intl_settings.get("official", True):
        event_sources.append(load_json(resolve_config_path('official_days.json')))
    if intl_settings.get("semi_official", True):
        event_sources.append(load_json(resolve_config_path('semi_official_days.json')))
    if intl_settings.get("fun", True):
        event_sources.append(load_json(resolve_config_path('fun_days.json')))

    return update_year_key(year,merge_holiday_dicts(*event_sources))

def load_religious_events(year: int) -> dict:
    """
    Load religious holidays from the religious_days.json configuration file.

    Returns:
        dict: A dictionary containing religious holiday data, where keys are date strings
              in MM-DD format and values are dictionaries with holiday labels and colours.
    """
    return update_year_key(year,load_json_cached(resolve_config_path('religious_days.json')))


def load_retro_events(year: int) -> dict:
    """
    Load retro computing anniversaries and events from the retro_days.json configuration file.

    Returns:
        dict: A dictionary containing retro event data, where keys are date strings
              in MM-DD format and values are dictionaries with event labels and colours.
    """
    return update_year_key(year,load_json_cached(resolve_config_path('retro_days.json')))


def load_uk_events(year: int) -> dict:
    """
    Load UK-specific public holidays from the uk_holidays.json configuration file.

    Returns:
        dict: A dictionary containing UK holiday data, where keys are date strings
              in MM-DD format and values are dictionaries with holiday labels and colours.
    """
    return update_year_key(year,load_json_cached(resolve_config_path('uk_events.json')))


def load_custom_events(year: int) -> dict:
    """
    Load user-defined custom events from the custom_events.json configuration file.

    Returns:
        dict: A dictionary containing custom event data, where keys are date strings
              in MM-DD format and values are dictionaries with event labels and colours.
    """
    return update_year_key(year,load_json_cached(resolve_config_path('custom_events.json')))

def load_cultural_events(year: int) -> dict:
    """
    Load cultural observance events for the given year from JSON file.

    This includes non-legal, folklore, seasonal, or minor observance events 
    that supplement official holidays. Cultural events may vary by country 
    and are fully optional.

    The data source is located in `config/events/cultural_days.json` and 
    uses the following format:

    {
        "RO": {
            "02-24": {"label": "Dragobete (RO)", "colour": "mediumvioletred"},
            ...
        },
        "ALL": {
            "12-31": {"label": "New Year's Eve", "colour": "blue"}
        }
    }

    Args:
        year (int): The calendar year being processed.

    Returns:
        dict: Dictionary of cultural holiday data in MultiColourHolidayDict format.
    """
    # Load raw JSON file
    data = load_json_cached(resolve_config_path('cultural_days.json'))

    result = {}

    # Process both country-specific and global 'ALL' entries
    for region_key, entries in data.items():
        for mmdd, event in entries.items():
            full_date = f"{year}-{mmdd}"
            result.setdefault(full_date, {"entries": []})
            result[full_date]["entries"].append({
                "label": event["label"],
                "colour": event["colour"]
            })

    return result
