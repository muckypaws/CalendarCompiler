"""
Module for calculating rule-based dynamic holidays using country-driven rules.

Supports civil holiday rules (e.g. Mother's Day, Father's Day, Yorkshire Pudding Day)
and Christian moveable feasts (e.g. Easter, Pentecost, Advent).

Author: Jason Brooks
"""

from datetime import date, timedelta
from modules.rules_loader import load_variable_rules
from modules.event_loader import update_year_key

# --- Orthodox Easter Calculation ---

def calculate_orthodox_easter(year: int) -> date:
    """
    Calculate Orthodox Easter Sunday for a given year.

    Uses the Meeus Julian algorithm with Gregorian correction to compute the 
    Orthodox Easter date observed in Eastern Orthodox churches.

    Args:
        year (int): The year to calculate for.

    Returns:
        date: The date of Orthodox Easter Sunday.
    """
    a = year % 4
    b = year % 7
    c = year % 19
    d = (19 * c + 15) % 30
    e = (2 * a + 4 * b - d + 34) % 7
    month = (d + e + 114) // 31
    day = ((d + e + 114) % 31) + 1
    julian_easter = date(year, month, day)
    gregorian_easter = julian_easter + timedelta(days=13)
    return gregorian_easter

def calculate_florii(year: int) -> dict:
    """
    Calculate Florii (Romanian Flowers Day) for the given year.

    Florii occurs on Orthodox Palm Sunday, exactly one week before Orthodox Easter.

    Args:
        year (int): The year to calculate Florii for.

    Returns:
        dict: Dictionary containing Florii keyed by MM-DD.
    """
    orthodox_easter = calculate_orthodox_easter(year)
    florii_date = orthodox_easter - timedelta(days=7)
    return { florii_date.strftime("%m-%d"): {
        "label": "Florii (Flowers Day) (RO)", "colour": "mediumvioletred"
    }}

# --- Moveable Cultural Holidays ---

def calculate_volkstrauertag(year: int) -> dict:
    """
    Calculate German Volkstrauertag (National Day of Mourning).

    Occurs two Sundays before Advent (Advent = 4 Sundays before Christmas).

    Args:
        year (int): The year to calculate Volkstrauertag for.

    Returns:
        dict: Dictionary containing Volkstrauertag keyed by MM-DD.
    """
    christmas = date(year, 12, 25)
    advent_start = christmas - timedelta(days=christmas.weekday() + 22)
    volkstrauertag = advent_start - timedelta(weeks=2)
    event_date = volkstrauertag.strftime("%m-%d")
    return { event_date: {"label": "Volkstrauertag (Germany)", "colour": "black"} }

def calculate_remembrance_sunday(year: int) -> dict:
    """
    Calculate Remembrance Sunday (second Sunday of November).

    Args:
        year (int): The year to calculate Remembrance Sunday for.

    Returns:
        dict: Dictionary containing Remembrance Sunday keyed by MM-DD.
    """
    d = date(year, 11, 1)
    while d.weekday() != 6:
        d += timedelta(days=1)
    d += timedelta(weeks=1)
    event_date = d.strftime("%m-%d")
    return { event_date: {"label": "Remembrance Sunday", "colour": "red"} }

# --- Civil Holiday Rules ---

def calculate_mothers_day(year: int, rule: str) -> dict:
    """
    Calculate Mother's Day according to country-specific rule.

    Args:
        year (int): The year to calculate for.
        rule (str): Rule identifier (e.g. 'mothering_sunday', 'second_sunday_may').

    Returns:
        dict: Dictionary containing Mother's Day keyed by MM-DD.
    """
    if rule == "mothering_sunday":
        d = date(year, 3, 1)
        while d.weekday() != 6:
            d += timedelta(days=1)
        d += timedelta(weeks=3)
        event_date = d.strftime("%m-%d")
        label = "Mother's Day (UK)"
    elif rule == "second_sunday_may":
        d = date(year, 5, 1)
        while d.weekday() != 6:
            d += timedelta(days=1)
        d += timedelta(weeks=1)
        event_date = d.strftime("%m-%d")
        label = "Mother's Day"
    else:
        return {}

    return { event_date: {"label": label, "colour": "pink"} }

def calculate_fathers_day(year: int, rule: str) -> dict:
    """
    Calculate Father's Day according to country-specific rule.

    Args:
        year (int): The year to calculate for.
        rule (str): Rule identifier (e.g. 'third_sunday_june', 'first_sunday_september').

    Returns:
        dict: Dictionary containing Father's Day keyed by MM-DD.
    """
    if rule == "third_sunday_june":
        d = date(year, 6, 1)
        while d.weekday() != 6:
            d += timedelta(days=1)
        d += timedelta(weeks=2)
        event_date = d.strftime("%m-%d")
        label = "Father's Day"
    elif rule == "first_sunday_september":
        d = date(year, 9, 1)
        while d.weekday() != 6:
            d += timedelta(days=1)
        event_date = d.strftime("%m-%d")
        label = "Father's Day (AU)"
    elif rule == "ascension_day":
        return {}
    else:
        return {}

    return { event_date: {"label": label, "colour": "blue"} }

def calculate_yorkshire_pudding_day(year: int, rule: str) -> dict:
    """
    Calculate Yorkshire Pudding Day.

    Args:
        year (int): The year to calculate for.
        rule (str): Rule identifier (e.g. 'first_sunday_february').

    Returns:
        dict: Dictionary containing Yorkshire Pudding Day keyed by MM-DD.
    """
    if rule == "first_sunday_february":
        d = date(year, 2, 1)
        while d.weekday() != 6:
            d += timedelta(days=1)
        event_date = d.strftime("%m-%d")
        return { event_date: {"label": "Yorkshire Pudding Day", "colour": "goldenrod"} }
    else:
        return {}

# --- Christian Moveable Feast Calculations ---

def calculate_easter_date(year: int) -> date:
    """
    Calculate Western Easter Sunday (Gregorian) for a given year.

    Uses Meeus/Jones/Butcher Gregorian algorithm.

    Args:
        year (int): The year to calculate for.

    Returns:
        date: Western Easter date.
    """
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)

def build_christian_events(year: int) -> dict:
    """
    Generate rule-based Christian feasts for the given year.

    Includes Ash Wednesday, Good Friday, Easter Sunday, Ascension Day,
    Pentecost Sunday, and Advent Sundays.

    Args:
        year (int): The year to calculate feasts for.

    Returns:
        dict: Dictionary of Christian events keyed by MM-DD.
    """
    data = {}
    easter = calculate_easter_date(year)

    data[easter.strftime("%m-%d")] = {"label": "Easter Sunday", "colour": "pink"}
    data[(easter - timedelta(days=2)).strftime("%m-%d")] = {"label": "Good Friday", "colour": "red"}
    data[(easter - timedelta(days=46)).strftime("%m-%d")] = {"label": "Ash Wednesday", "colour": "grey"}
    data[(easter + timedelta(days=39)).strftime("%m-%d")] = {"label": "Ascension Day", "colour": "blue"}
    data[(easter + timedelta(days=49)).strftime("%m-%d")] = {"label": "Pentecost Sunday", "colour": "purple"}

    christmas = date(year, 12, 25)
    advent_start = christmas - timedelta(days=christmas.weekday() + 22)
    for i in range(4):
        sunday = advent_start - timedelta(weeks=i)
        event_date = sunday.strftime("%m-%d")
        data[event_date] = {"label": f"Advent {4 - i}", "colour": "purple"}

    return update_year_key(year, data)


# --- Master Rule Engine ---

def build_variable_event_dataset(year: int, country_code: str = "GB") -> dict:
    """
    Build full variable event dataset combining civil, Christian, and cultural holidays.

    Args:
        year (int): The year to calculate events for.
        country_code (str): ISO 2-letter country code.

    Returns:
        dict: Dictionary of calculated holidays keyed by YYYY-MM-DD.
    """
    data = {}
    rules = load_variable_rules()
    country_rules = rules.get(country_code.upper(), {})

    if "mothers_day" in country_rules:
        data.update(calculate_mothers_day(year, country_rules["mothers_day"]))

    if "fathers_day" in country_rules:
        data.update(calculate_fathers_day(year, country_rules["fathers_day"]))

    if "yorkshire_pudding_day" in country_rules:
        data.update(calculate_yorkshire_pudding_day(year, country_rules["yorkshire_pudding_day"]))

    if country_rules.get("christian", False):
        data.update(build_christian_events(year))

    moveable = country_rules.get("moveable_cultural", {})

    if moveable.get("remembrance_sunday", False):
        data.update(calculate_remembrance_sunday(year))

    if moveable.get("volkstrauertag", False):
        data.update(calculate_volkstrauertag(year))

    if moveable.get("florii", False):
        data.update(calculate_florii(year))

    return update_year_key(year, data)
