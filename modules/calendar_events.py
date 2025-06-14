"""calendar_events.py - Module for retrieving and combining UK public holidays.

This module uses the `holidays` package to fetch national and regional UK holidays
for a given year. It combines these into a single dictionary, noting overlaps
and assigning different colours for each region.
"""
import os
import re
import calendar
import datetime
from collections import defaultdict
import holidays as myholidays
from modules.helpers import (
    remap_null_keys,
    canonicalise_label,
    load_json_cached
    )
from .holiday_types import MultiColourHolidayDict, HolidayLine

# Globals - for now.
CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'config')

EVENT_TYPES = load_json_cached(os.path.join(CONFIG_DIR, 'event_types.json'))
COUNTRY_COLOURS = load_json_cached(os.path.join(CONFIG_DIR, 'iso_country_colours.json'))
ISO_COUNTRY_NAMES = load_json_cached(os.path.join(CONFIG_DIR, 'iso_country_names.json'))

# Special case, can't have key of None in JSON, so work around...
aus_region_colours_raw = load_json_cached(os.path.join(CONFIG_DIR, 'australian_region_colours.json'))

# Convert NATIONAL key to None
AUS_REGION_COLOURS = remap_null_keys(aus_region_colours_raw, null_key='NATIONAL')

def normalise_label(label: str) -> str:
    """Clean redundant suffixes in label strings for stable deduplication."""
    # Simplify redundant 'observed' stacking
    pattern = re.compile(r"(observed(?:,\s*observed)+)")
    label = pattern.sub("observed", label)

    # If somehow multiple parentheses appear, strip down
    while "(observed, observed" in label:
        label = label.replace("(observed, observed", "(observed")

    # Remove trailing junk commas
    label = re.sub(r"\(observed(?:,\s*)*\)", "(observed)", label)

    return label

def canonicalise_holiday_data(holiday_data: dict) -> dict:
    """
    Deduplicate identical label+colour entries for each date before merge phase.

    Args:
        holiday_data (dict): Raw holiday data dictionary with potential redundant entries.

    Returns:
        dict: Cleaned dictionary with duplicate entries removed.
    """
    cleaned_data = {}

    for date_key, data in holiday_data.items():
        seen = set()
        deduped_entries = []

        for entry in data.get("entries", []):
            # Build tuple key (label, colour)
            entry_key = (normalise_label(entry["label"]), entry["colour"])
            if entry_key not in seen:
                seen.add(entry_key)
                deduped_entries.append(entry)

        cleaned_data[date_key] = {"entries": deduped_entries}

    return cleaned_data


def smart_merge_au_holidays(holiday_data):
    """
    For each date, merge holidays with identical names, appending all region codes into the label.

    Args:
        holiday_data (MultiColourHolidayDict): {date: {"entries": [{"label", "colour"}, ...]}}

    Returns:
        MultiColourHolidayDict: With merged entries.
    """
    import re
    merged = {}

    for date, data in holiday_data.items():
        name_to_regions = {}
        name_to_colour = {}

        for entry in data["entries"]:
            # Parse out name and region from label, e.g. "Christmas Day (NSW)"
            m = re.match(r"^(.*) \(([^)]+)\)$", entry["label"])
            if m:
                name, region = m.group(1).strip(), m.group(2).strip()
            else:
                name, region = entry["label"], "National"
            if name not in name_to_regions:
                name_to_regions[name] = []
            if region not in name_to_regions[name]:
                name_to_regions[name].append(region)
            # Use the first colour (can be improved if you want to blend)
            name_to_colour.setdefault(name, entry["colour"])

        merged_entries = []
        for name, regions in name_to_regions.items():
            merged_label = f"{name} ({', '.join(regions)})"
            merged_entries.append({"label": merged_label, "colour": name_to_colour[name]})
        merged[date] = {"entries": merged_entries}

    return merged

from collections import defaultdict

def merge_identical_holidays(holiday_data, merge_enabled=True, default_colour="black"):
    """
    Merge holiday entries for each date when multiple countries share an identical holiday name.

    Fully harmonised: stable canonicalisation for merge keys, safe preservation of display labels,
    and correct handling of observed suffixes.

    Args:
        holiday_data (dict): Dictionary in MultiColourHolidayDict format,
                             {date: {"entries": [{"label": "Name (CC)", "colour": ...}, ...]}}
        merge_enabled (bool): If False, does not alter input; if True, merges identical holidays.
        default_colour (str): Colour to use for merged entries if not set per-country.

    Returns:
        dict: Holiday data with merged entries where applicable.
    """
    if not merge_enabled:
        return holiday_data

    merged_data = {}

    for date, data in holiday_data.items():
        name_to_countries = defaultdict(list)
        name_to_colours = defaultdict(list)
        canonical_to_display = {}

        for entry in data.get("entries", []):
            label = entry["label"]

            # Default extraction: assume full label unless we parse country suffix
            name = label.strip()
            cc = None

            # Extract (CC) suffix if present
            if '(' in label and label.endswith(')'):
                name_part, cc_part = label.rsplit('(', 1)
                name = name_part.strip()
                cc = cc_part[:-1].strip()

                # Patch: observed suffix is NOT a country code
                if cc.lower() == "observed":
                    cc = None
                    name = f"{name} (observed)"

            # Build canonical key for internal merge
            display_name = name  # preserve original name for output
            canonical_name = canonicalise_label(display_name)

            name_to_countries[canonical_name].append(cc)
            name_to_colours[canonical_name].append(entry.get("colour", default_colour))

            if canonical_name not in canonical_to_display:
                canonical_to_display[canonical_name] = display_name

        merged_entries = []

        for canonical_name, countries in name_to_countries.items():
            display_name = canonical_to_display[canonical_name]
            unique_countries = [c for c in countries if c]

            # Colour selection logic (stable, deterministic)
            colour_counts = defaultdict(int)
            for colour in name_to_colours[canonical_name]:
                colour_counts[colour] += 1

            max_count = max(colour_counts.values())
            most_common = [colour for colour, count in colour_counts.items() if count == max_count]

            # Handle fully identical no-country situations
            if all(cc is None for cc in name_to_countries[canonical_name]):
                if len(set(name_to_colours[canonical_name])) > 1:
                    entry_colour = "black"
                else:
                    entry_colour = name_to_colours[canonical_name][0]
            else:
                for colour in name_to_colours[canonical_name]:
                    if colour in most_common:
                        entry_colour = colour
                        break
                else:
                    entry_colour = default_colour

            # Build final merged label using display name
            if len(unique_countries) > 1:
                merged_label = f"{display_name} ({', '.join(sorted(unique_countries))})"
            elif unique_countries:
                merged_label = f"{display_name} ({unique_countries[0]})"
            else:
                merged_label = display_name

            merged_entries.append({"label": merged_label, "colour": entry_colour})

        merged_data[date] = {"entries": merged_entries}

    return merged_data


def get_multi_country_holidays(settings) -> MultiColourHolidayDict:
    """
    Retrieve and combine holidays for multiple countries in a multi-entry format.

    Args:
        settings (dict): Settings with 'holidays'/'countries' and 'year'.

    Returns:
        MultiColourHolidayDict: {ISO date: {"entries": [ {"label", "colour"}, ... ]}}
    """
    countries = settings.get('include_country_list', {}).get('countries', [])
    year = int(settings['year'])
    holiday_data: MultiColourHolidayDict = {}

    for cc in countries:
        colour = COUNTRY_COLOURS.get(cc, 'grey')
        hdays = myholidays.country_holidays(cc, years=year)
        for date, name in hdays.items():
            date_key = date.strftime("%Y-%m-%d") if hasattr(date, "strftime") else str(date)
            entry = {"label": f"{name} ({cc})", "colour": colour}
            if date_key in holiday_data:
                if entry not in holiday_data[date_key]["entries"]:
                    holiday_data[date_key]["entries"].append(entry)
            else:
                holiday_data[date_key] = {"entries": [entry]}

    return holiday_data

def get_combined_holidays(settings) -> MultiColourHolidayDict:
    """
    Return a unified holiday dictionary for the calendar engine.

    Combining UK region-colour-coded holidays, Australian state/territory holidays,
    and/or multi-country holidays as per config.

    Args:
        settings (dict): Project settings.

    Returns:
        MultiColourHolidayDict: Holidays ready for calendar rendering.
    """
    all_holidays = {}

    # Add UK holidays if enabled
    if settings.get('include_days', {}).get('uk_holidays', False):
        uk_holidays = get_uk_combined_holidays(int(settings['year']))
        all_holidays.update(uk_holidays)

    # Only process Country List if Country List Flag is Set.
    if settings.get("include_days", {}).get("country_list", False):
        # Parse countries list robustly
        icl = settings.get('include_country_list', {})
        if isinstance(icl, dict):
            country_list = icl.get('countries', []).copy()
        else:
            country_list = list(icl)  # fallback if flat list

        # Special-case: Australia (call dedicated AU function and remove from country list)
        if "AU" in country_list:
            au_holidays = get_au_combined_holidays(int(settings['year']))
            au_holidays = smart_merge_au_holidays(au_holidays)
            for date, data in au_holidays.items():
                if date in all_holidays:
                    for entry in data["entries"]:
                        if entry not in all_holidays[date]["entries"]:
                            all_holidays[date]["entries"].append(entry)
                else:
                    all_holidays[date] = data
            country_list.remove("AU")

        # Add other multi-country holidays if any left
        if country_list:
            patched_settings = settings.copy()
            # update the countries list in the correct structure
            if isinstance(icl, dict):
                patched_settings["include_country_list"]["countries"] = country_list
            else:
                patched_settings["include_country_list"] = country_list
            mc_holidays = get_multi_country_holidays(patched_settings)
            for date, data in mc_holidays.items():
                if date in all_holidays:
                    for entry in data["entries"]:
                        if entry not in all_holidays[date]["entries"]:
                            all_holidays[date]["entries"].append(entry)
                else:
                    all_holidays[date] = data

    return all_holidays


def get_au_combined_holidays(year: int) -> MultiColourHolidayDict:
    """
    Retrieve and combine Australian national and state/territory holidays for a given year.

    Holidays are grouped by date in ISO format (YYYY-MM-DD), with each date containing
    one or more entries. Overlapping holidays from different Australian regions are merged
    into the same day but retain their individual labels and colours.

    Region colours:
        - "#AD9200"      = Australia (default/national)
        - "darkblue"  = New South Wales (NSW)
        - "crimson"   = Victoria (VIC)
        - "teal"      = Queensland (QLD)
        - "saddlebrown" = South Australia (SA)
        - "green"     = Western Australia (WA)
        - "purple"    = Tasmania (TAS)
        - "deepskyblue" = Northern Territory (NT)
        - "#D28800"    = Australian Capital Territory (ACT)

    Args:
        year (int): The year to generate holidays for.

    Returns:
        MultiColourHolidayDict: A dictionary of ISO date strings to lists of holiday entries.
    """
    # All state/territory codes (as used in `holidays`)
    subdivisions = [None, "NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT"]

    holiday_data: MultiColourHolidayDict = {}

    def add_holiday(source, region_code):
        """
        Add holidays from a specific region/territory into the combined dictionary.

        Args:
            source (dict): Holidays dict from holidays.country_holidays().
            region_code (str or None): Subdivision/state code.
        """
        colour = AUS_REGION_COLOURS.get(region_code, "grey")
        for date, name in source.items():
            date_key = date.strftime("%Y-%m-%d") if hasattr(date, "strftime") else str(date)
            label = f"{name} ({region_code if region_code else 'National'})"
            entry: HolidayLine = {"label": label, "colour": colour}
            if date_key in holiday_data:
                if entry not in holiday_data[date_key]["entries"]:
                    holiday_data[date_key]["entries"].append(entry)
            else:
                holiday_data[date_key] = {"entries": [entry]}

    # Loop through national (None) and all subdivisions
    for subdiv in subdivisions:
        region_holidays = myholidays.country_holidays("AU", years=year, subdiv=subdiv) if subdiv else myholidays.country_holidays("AU", years=year)
        add_holiday(region_holidays, subdiv)

    return holiday_data


def get_uk_combined_holidays(year: int) -> MultiColourHolidayDict:
    """
    Retrieve and combine UK national and regional holidays for a given year.

    in a unified multi-entry format compatible with the calendar rendering engine.

    Holidays are grouped by date in ISO format (YYYY-MM-DD), with each date containing
    one or more entries. Overlapping holidays from different UK regions are merged
    into the same day but retain their individual labels and colours.

    Region colours:
        - "red"   = UK-wide (default)
        - "blue"  = Scotland
        - "green" = Northern Ireland
        - "#D28800" = Wales

    Args:
        year (int): The year to generate holidays for.

    Returns:
        MultiColourHolidayDict: A dictionary of ISO date strings to lists of holiday entries.
    """
    # Load region-specific holidays
    uk = myholidays.UnitedKingdom(years=year)
    scotland = myholidays.UnitedKingdom(years=year, subdiv="Scotland")
    northern_ireland = myholidays.UnitedKingdom(years=year, subdiv="Northern Ireland")
    wales = myholidays.UnitedKingdom(years=year, subdiv="Wales")

    holiday_data: MultiColourHolidayDict = {}

    def add_holiday(source, colour: str):
        for date, name in source.items():
            date_key = date.strftime("%Y-%m-%d")
            entry: HolidayLine = {"label": name, "colour": colour}
            if date_key in holiday_data:
                if entry not in holiday_data[date_key]["entries"]:
                    holiday_data[date_key]["entries"].append(entry)
            else:
                holiday_data[date_key] = {"entries": [entry]}

    # Apply each region
    add_holiday(uk, "red")
    add_holiday(scotland, "blue")
    add_holiday(northern_ireland, "green")
    add_holiday(wales, "#D28800")

    return holiday_data


def nth_weekday_of_month(year, month, weekday, n):
    """
    Get the date of the nth weekday (0=Monday) of a given month/year.

    E.g., second Sunday in May = nth_weekday_of_month(2026, 5, 6, 2)
    """
    count = 0
    for day in range(1, 32):
        try:
            dt = datetime.date(year, month, day)
        except ValueError:
            break
        if dt.weekday() == weekday:
            count += 1
            if count == n:
                return dt
    return None

def last_weekday_of_month(year, month, weekday):
    """Get the date of the last weekday (0=Monday) of a given month/year."""
    last_day = calendar.monthrange(year, month)[1]
    for day in range(last_day, 0, -1):
        dt = datetime.date(year, month, day)
        if dt.weekday() == weekday:
            return dt
    return None

def add_variable_days(year, day_dict):
    """
    Add variable/floating international and humorous days to the day_dict.

    Args:
        year (int): The year for calculation.
        day_dict (dict): The international_days dict to update.
    Returns:
        dict: Updated day_dict.
    """
    # Example: Mother's Day UK (Fourth Sunday of Lent = 4th Sunday in March in 2026)
    mothers_day_uk = nth_weekday_of_month(year, 3, 6, 4)
    if mothers_day_uk:
        day_dict[mothers_day_uk.strftime('%Y-%m-%d')] = {
            "label": "Mother's Day (UK)", "colour": "pink"
        }

    # Father's Day UK/US (Third Sunday in June)
    fathers_day = nth_weekday_of_month(year, 6, 6, 3)
    if fathers_day:
        day_dict[fathers_day.strftime('%Y-%m-%d')] = {
            "label": "Father's Day (UK/US)", "colour": "blue"
        }

    # "Blue Monday" (third Monday in January)
    blue_monday = nth_weekday_of_month(year, 1, 0, 3)
    if blue_monday:
        day_dict[blue_monday.strftime('%Y-%m-%d')] = {
            "label": "Blue Monday", "colour": "blue"
        }

    # Yorkshire Pudding Day (UK, 1st Sunday in February)
    yorkshire_pud_day = nth_weekday_of_month(year, 2, 6, 1)
    if yorkshire_pud_day:
        day_dict[yorkshire_pud_day.strftime('%Y-%m-%d')] = {
            "label": "National Yorkshire Pudding Day (UK)", "colour": "brown"
        }

    # Thanksgiving US (Fourth Thursday of November)
    thanksgiving = nth_weekday_of_month(year, 11, 3, 4)
    if thanksgiving:
        day_dict[thanksgiving.strftime('%Y-%m-%d')] = {
            "label": "Thanksgiving (US)", "colour": "#D28800"
        }

    # Black Friday (day after US Thanksgiving)
    if thanksgiving:
        black_friday = thanksgiving + datetime.timedelta(days=1)
        day_dict[black_friday.strftime('%Y-%m-%d')] = {
            "label": "Black Friday", "colour": "black"
        }

    # Other examples: Towel Day (always May 25), etc. are static, not needed here.

    return day_dict

