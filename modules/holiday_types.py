"""
Typing for data used in the project.

Update here for new types as needed.
"""
from typing import TypedDict, Dict, List

class HolidayLine(TypedDict):
    """Simple data type for label and colour."""

    label: str
    colour: str

# Each date (YYYY-MM-DD) maps to a list of individually coloured lines
MultiColourHolidayDict = Dict[str, List[HolidayLine]]
