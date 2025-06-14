"""
Responsible for loading variable event calculation rules from external rules.json.

This allows country-specific configuration of rule-based holiday generation.

"""
import os
import json
from modules.helpers import load_json

_variable_rules_cache = None

def load_variable_rules() -> dict:
    """
    Load country-specific variable holiday calculation rules from JSON file.

    Uses internal caching to avoid redundant file I/O on multiple calls.
    
    Returns:
        dict: Dictionary mapping country codes to rule sets.
    """
    global _variable_rules_cache
    if _variable_rules_cache is not None:
        return _variable_rules_cache

    base_dir = os.path.dirname(os.path.dirname(__file__))
    full_path = os.path.join(base_dir, 'config', 'rules', 'variable_rules.json')

    try:
        _variable_rules_cache = load_json(full_path)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading rules: {e}")
        _variable_rules_cache = {}

    return _variable_rules_cache
