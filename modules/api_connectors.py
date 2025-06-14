"""
API connector utilities for retrieving holiday and calendar event data.

Handles requests to external holiday APIs and formats results for calendar integration.
"""
import requests

def fetch_calendarific_json(api_key, year=2026, country="GB"):
    """
    Fetch religious holiday data from the Calendarific API for a given year and country.

    Args:
        api_key (str): Your Calendarific API key.
        year (int, optional): The target year for which holidays should be retrieved. Defaults to 2026.
        country (str, optional): The 2-letter ISO country code (e.g., 'GB' for the United Kingdom). Defaults to 'GB'.

    Returns:
        dict: Parsed JSON response from the Calendarific API containing holiday data.

    Raises:
        requests.RequestException: If the HTTP request fails or times out.
    """
    url = "https://calendarific.com/api/v2/holidays"
    params = {
        "api_key": api_key,
        "country": country,
        "year": year,
        "type": "religious"
    }
    response = requests.get(url, params=params)
    return response.json()

def extract_multi_faith_holidays(raw_json) -> dict:
    """
    Extract and categorise religious holidays from Calendarific's JSON response by faith group.

    This function filters the raw Calendarific response to identify holidays with religious significance,
    using keywords to infer the religion and assign each holiday a colour for calendar display purposes.

    Supported religions include:
        - Jewish
        - Christian (including Orthodox)
        - Muslim/Islamic
        - Hindu
        - Buddhist

    Args:
        raw_json (dict): The raw JSON dictionary returned by the Calendarific API.

    Returns:
        dict: A dictionary where keys are ISO-formatted date strings (YYYY-MM-DD),
              and values are dictionaries with "label" (event name) and "colour" (string colour code).
    """
    colour_map = {
        "jewish": "#D28800",
        "hebrew": "#D28800",
        "muslim": "green",
        "islamic": "green",
        "christian": "purple",
        "orthodox": "purple",
        "hindu": "#AD9200",
        "buddh": "saddlebrown",  
    }

    multi_holidays = {}

    for holiday in raw_json.get("response", {}).get("holidays", []):
        types = [t.lower() for t in holiday.get("type", [])]
        primary = holiday.get("primary_type", "").lower()
        name = holiday.get("name", "").lower()
        desc = holiday.get("description", "").lower()

        # Match based on any keyword
        matched_religion = next((
            religion for religion in colour_map
            if religion in primary or
               any(religion in t for t in types) or
               religion in name or
               religion in desc
        ), None)

        if matched_religion:
            date_key = holiday["date"]["iso"]
            label = holiday["name"]
            colour = colour_map[matched_religion]

            if date_key in multi_holidays:
                if label not in multi_holidays[date_key]["label"]:
                    multi_holidays[date_key]["label"] += f"\n{label}"
            else:
                multi_holidays[date_key] = {"label": label, "colour": colour}

    return multi_holidays

def extract_jewish_holidays_from_calendarific(raw_json) -> dict:
    """
    Extract Jewish holidays from raw Calendarific JSON data.

    This function searches the Calendarific response for holidays
    that are identified as Jewish based on their primary type,
    type list, name, or description fields.

    Holidays are returned in a dictionary keyed by ISO date (YYYY-MM-DD),
    each containing a label and a fixed colour ("#D28800") for Jewish events.

    Args:
        raw_json (dict): The raw JSON object returned from Calendarific API.

    Returns:
        dict: A dictionary mapping date strings to holiday metadata.
              Example:
              {
                  "2026-04-23": {"label": "Passover", "colour": "#D28800"},
                  ...
              }
    """
    jewish_holidays = {}

    for holiday in raw_json.get("response", {}).get("holidays", []):
        # Check primary type or type list or name for indicators
        primary = holiday.get("primary_type", "").lower()
        types = [t.lower() for t in holiday.get("type", [])]
        name = holiday.get("name", "").lower()
        desc = holiday.get("description", "").lower()

        is_jewish = (
            "jewish" in primary or
            "hebrew" in primary or
            any("jewish" in t or "hebrew" in t for t in types) or
            "jewish" in desc or
            "jewish" in name
        )

        if is_jewish:
            date_key = holiday["date"]["iso"]
            label = holiday["name"]
            jewish_holidays[date_key] = {"label": label, "colour": "#D28800"}

    return jewish_holidays  