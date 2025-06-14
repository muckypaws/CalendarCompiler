"""Key Calendar Dates to Add, extend here for custom events."""
import os
import json
from modules.helpers import (
    load_json,
    update_year_key,
    resolve_config_path,
    merge_holiday_dicts
)

def load_event_data(filename: str) -> dict:
    """
    Loader for external JSON event files.

    Args:
        filename (str): Name of the JSON file inside the 'config' directory.

    Returns:
        dict: Loaded dictionary of event data.
    """
    config_path = os.path.join('config', filename)
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: '{config_path}' not found. Returning empty dataset.")
        return {}

def custom_events(year: int):
    """
    Return a dictionary of customer user dates.

    Returns:
        dict: Dictionary where keys are date strings (YYYY-MM-DD) and values are dictionaries
              with 'label' (event description) and 'colour' (display colour in calendar).
    """
    return update_year_key(year, load_event_data('custom_events.json'))

def retroevents(year: int):
    """
    Return a dictionary of significant dates in retro computing history.

    These include launch dates of classic home computers (e.g. ZX Spectrum, Commodore 64),
    software milestones, and birthdays of influential figures in computing history 
    (e.g. Clive Sinclair, Steve Wozniak).

    Returns:
        dict: Dictionary where keys are date strings (YYYY-MM-DD) and values are dictionaries
              with 'label' (event description) and 'colour' (display colour in calendar).
    """
    return update_year_key(year, load_event_data('retro_dates.json'))

#def international_dates(year: int):
#    """Set of International Day Of, update here where needed."""
#    return update_year_key(year, load_event_data('international_day_of.json'))


def merge_holiday_dicts(*dicts) -> dict:
    """
    Merge multiple holiday dictionaries into a single dictionary.

    Later dicts overwrite earlier dicts on key conflict.

    Args:
        *dicts: Variable number of dict arguments.

    Returns:
        dict: Merged dictionary.
    """
    merged = {}
    for d in dicts:
        merged.update(d)
    return merged

def international_dates(year :int, include_official=True, include_semi=True, include_fun=True) -> dict:
    """
    Load and combine holiday event data based on user selection.

    Args:
        include_official (bool): Include official UN/WHO days.
        include_semi (bool): Include regional/country semi-official days.
        include_fun (bool): Include fun & pop culture days.

    Returns:
        dict: Combined holiday data.
    """
    event_sources = []

    if include_official:
        event_sources.append(load_json(resolve_config_path('official_days.json')))
    if include_semi:
        event_sources.append(load_json(resolve_config_path('semi_official_days.json')))
    if include_fun:
        event_sources.append(load_json(resolve_config_path('fun_days.json')))

    return update_year_key(year, merge_holiday_dicts(*event_sources))
