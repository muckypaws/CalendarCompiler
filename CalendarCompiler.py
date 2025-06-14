#!/usr/bin/env python
"""
Main entry point for the SVG Calendar Generator project.

Handles command-line arguments, settings, and orchestration of calendar output.
"""
import json
import argparse
import os
import sys
from datetime import datetime
from modules import svg_calendar
from modules.helpers import load_json, save_json, merge_holiday_data
from modules.helpers import load_settings, get_api_key, is_enabled
from modules.helpers import export_holiday_validation_file
from modules import calendar_events
from modules import api_connectors
from modules import export_calander
from modules.variable_events import build_variable_event_dataset
from modules.event_loader import (
    load_international_events,
    load_retro_events,
    load_uk_events,
    load_custom_events,
    load_cultural_events
)

# One of my fave hacks for force lowercase on CLI Switches
# But not always recommended
class CaseInsensitiveArgumentParser(argparse.ArgumentParser):
    """ArgumentParser that supports case-insensitive command-line flags."""

    def _parse_optional(self, arg_string):
        if arg_string.startswith('--'):
            # Try to match argument names in lower-case
            arg_string = arg_string.lower()
            # If you want, map specific aliases here...
        return super()._parse_optional(arg_string)

def parse_cli_args():
    """
    Parse CLI for SVG Calendar Generator.

    Only set a value if the user provides the flag.
    """
    parser = argparse.ArgumentParser(description="SVG Calendar Generator")

    # Set the year to create the calendar
    parser.add_argument('--year', type=int, help='Year to generate calendar for')

    # Main event group toggles
    parser.add_argument('--international', action='store_true',
                        help='Include international days (full)')
    parser.add_argument('--official', action='store_true',
                        help='Include official international days only')
    parser.add_argument('--semi_official', action='store_true',
                        help='Include semi-official national days')
    parser.add_argument('--fun', action='store_true',
                        help='Include fun days (informal, novelty, pop culture)')
    parser.add_argument('--retro', action='store_true',
                        help='Include retro computing anniversaries')
    parser.add_argument('--religious', action='store_true',
                        help='Include religious dates')
    parser.add_argument('--uk_holidays', action='store_true',
                        help='Include UK holidays')
    parser.add_argument('--custom_events', action='store_true',
                        help='Include your custom events (birthdays, etc.)')
    parser.add_argument('--country_list', action='store_true',
                        help='Include additional countries on ISO Code.')

    # Export Options, PDF, PNG or JPG
    parser.add_argument('--exportpdf', action='store_true',
                        help='Export calendar as a compiled PDF')
    parser.add_argument('--exportpng', action='store_true',
                        help='Export calendar pages as PNG files')
    parser.add_argument('--exportjpg', action='store_true',
                        help='Export calendar pages as JPEG files')

    # Folder Locations
    parser.add_argument('--artwork', type=str,
                        help='Override folder containing all artwork files')
    parser.add_argument('--exportto', type=str,
                        help='Override output folder for final calendar export')

    # Cleanup Temp Files
    parser.add_argument('--cleanup', action='store_true',
                        help='Cleanup the Temporary Files Folder')

    # Request opening of PDF or Folder with default application.
    parser.add_argument('--open', action='store_true',
                        help='Try to open PDF or Folder after compilation')
    
    # Request generation of SVG Files only (Final No Compilation)
    parser.add_argument('--svgonly', action='store_true',
                        help='Generate The SVG Files Only')
    
    # Compile the calendar only
    parser.add_argument('--compileonly', action='store_true',
                        help='Compile the Calendar without generating the SVG Files (Use existing/edited)')

    return parser.parse_args()


def update_settings_with_cli(settings, args):
    """
    Update include_days flags in settings from CLI if present.

    Supports nested international options for official/semi_official/fun flags.

    Args:
        settings (dict): Config dict with 'include_days'.
        args (argparse.Namespace): Parsed CLI args.

    Returns:
        dict: Updated settings dict.
    """
    # Ensure include_days exists
    if "include_days" not in settings:
        settings["include_days"] = {}

    # Handle nested international flags
    if getattr(args, "international", False):
        settings["include_days"]["international"] = {
            "official": True,
            "semi_official": True,
            "fun": True
        }
    else:
        if "international" not in settings["include_days"]:
            settings["include_days"]["international"] = {}

        # Apply fine-grained overrides if set
        for subkey in ["official", "semi_official", "fun"]:
            if getattr(args, subkey, False):
                settings["include_days"]["international"][subkey] = True

    # Handle other flags
    for key in ["retro", "religious", "uk_holidays", "custom_events", "country_list"]:
        if getattr(args, key, False):
            settings["include_days"][key] = True

    # Year override
    if getattr(args, "year", None):
        settings["year"] = args.year

    # Open on completion override
    if getattr(args, "open", None):
        settings["OpenOnCompletion"] = True

    for export_flag, setting_key in [
        ("exportpdf", "export_pdf"),
        ("exportpng", "export_png"),
        ("exportjpg", "export_jpg"),
    ]:
        if getattr(args, export_flag, False):
            if "output" not in settings:
                settings["output"] = {}
            settings["output"][setting_key] = True

    # Artwork folder override
    if getattr(args, "artwork", None):
        if "art_files" not in settings:
            settings["art_files"] = {}
        settings["art_files"]["artwork_folder"] = args.artwork

    # Export folder override
    if getattr(args, "exportto", None):
        if "output" not in settings:
            settings["output"] = {}
        settings["output"]["pdf_dir"] = args.exportto

    # Cleanup override
    if getattr(args, "cleanup", None):
        if "art_files" not in settings:
            settings["art_files"] = {}
        settings["art_files"]["cleanup"] = True

    return settings


def generate_all_svgs(settings, holiday_data):
    """
    Generate SVG calendar files for all twelve months using project settings.

    This function iterates over all months in the configured calendar year,
    generating an SVG calendar for each month using the specified output directory.
    The output directory is determined from settings['output']['svg_dir'].
    Holidays are passed to each month for annotation.

    Args:
        settings (dict): Project settings, including 'output' with 'svg_dir'.
        holiday_data (dict): Holiday/event data to annotate in each month.

    Returns:
        None
    """
    svg_dir = settings.get('output', {}).get('svg_dir', './calendars')
    year = int(settings['year'])
    for month in range(1, 13):
        print(f"Generating SVG for {year}-{month:02d} in {svg_dir}")
        svg_calendar.generate_svg_calendar(year, month, output_dir=svg_dir, holidays=holiday_data)

    legend_svg_path = os.path.join(settings['output']['svg_dir'], 'legend.svg')

    branding_config = settings.get("branding", {})
    branding_text = branding_config.get("branding_text", "Generated with Calendar Compiler")
    branding_url = branding_config.get("branding_url", "")

    # Combine branding text and url for the footer
    full_branding = branding_text
    if branding_url:
        full_branding += " | " + branding_url

    svg_calendar.generate_legend_svg(
        calendar_events.COUNTRY_COLOURS,
        calendar_events.EVENT_TYPES,
        legend_svg_path,
        num_cols=5,
        branding_text=full_branding
    )

    print("\n\nSVG Calender File Created")
    print("="*25)
    print()

def load_event_data_from_options(settings, year):
    """
    Load and merge all holiday event data according to the provided settings.

    This function dynamically loads multiple holiday data layers based on the user's 
    configuration, including international days, religious holidays (from cache/API), 
    retro events, UK holidays, country lists, custom events, and variable rule-based dates.

    Args:
        settings (dict): The loaded settings configuration.
        year (int): The target year for the calendar build.

    Returns:
        dict: Combined holiday data dictionary with merged events.
    """
    holiday_data = {}

    #if is_enabled(settings, "uk_holidays"):
        # Load Country Holiday List (using existing calendar_events code)
    raw = calendar_events.get_combined_holidays(settings)
    merge_holiday_data(raw, load_uk_events(year))
    holiday_data = raw

    # Load Religious holidays (Calendarific API)
    if is_enabled(settings, "religious"):
        cache_path = f"./config/calendarific_multifaith_{year}.json"
        try:
            all_faiths = load_json(cache_path)
            print(f"Loaded multi-faith holidays from cache: {cache_path}")
        except (FileNotFoundError, json.JSONDecodeError):
            print("Fetching fresh multi-faith holiday data from Calendarific...")
            api_key = get_api_key(settings, "API_KEY", "./.env")
            raw_data = api_connectors.fetch_calendarific_json(api_key, year)
            all_faiths = api_connectors.extract_multi_faith_holidays(raw_data)
            save_json(all_faiths, cache_path)
            print(f"Saved fresh multi-faith data to cache: {cache_path}")
        merge_holiday_data(holiday_data, all_faiths)

    # Load User Custom Events as defined in the file
    if is_enabled(settings, "custom_events"):
        merge_holiday_data(holiday_data, load_custom_events(year))

    # Load File-Based Event Sources
    if is_enabled(settings, "retro"):
        merge_holiday_data(holiday_data, load_retro_events(year))

    if is_enabled(settings, "international"):
        intl_cfg = settings.get("include_days", {}).get("international", {})
        merge_holiday_data(holiday_data, load_international_events(year, intl_cfg))

    # Load rule engine for local country (always)
    local_country = settings.get("local_country", "GB")
    merge_holiday_data(holiday_data, build_variable_event_dataset(year, local_country))

    # If country_list is enabled — also run for each additional country
    if settings.get("include_days", {}).get("country_list", False):
        for code in settings.get("include_country_list", {}).get("countries", []):
            # Skip if we're already handled local_country above
            if code != local_country:
                merge_holiday_data(holiday_data, build_variable_event_dataset(year, code))
                merge_holiday_data(holiday_data, load_cultural_events(year))


    holiday_data = calendar_events.canonicalise_holiday_data(holiday_data)

    # Final Merge of Data if enabled in settings.
    holiday_data = calendar_events.merge_identical_holidays(
            holiday_data,
            merge_enabled=settings.get("merge_identical_holidays", False)
        )
    #merge_holiday_data(holiday_data, merged)
    
    return holiday_data



def compile_calendar(settings):
    """Compile the Calendar based on user options."""
    # Handle export formats based on config
    output_settings = settings.get("output", {})

    if output_settings.get("export_pdf", False):
        export_calander.export_calendar_pdf(settings)

    if output_settings.get("export_png", False):
        export_calander.export_calendar_pngs(settings)

    if output_settings.get("export_jpg", False):
        export_calander.export_calendar_jpgs(settings)

def main():
    """
    Entry point for generating the calendar output.

    This function processes command-line arguments, loads configuration settings,
    resolves and merges all holiday event data layers, and generates calendar outputs 
    in various formats (PDF, PNG, JPG) based on user-defined options.

    Raises:
        Exception: If Calendarific API data retrieval or parsing fails.
    """
    args = parse_cli_args()
    settings = load_settings()
    settings = update_settings_with_cli(settings, args)
    year = settings.get("year", datetime.now().year)


    if args.compileonly and args.svgonly:
        print("Both SVGOnly and CompileOnly Flags Set, nothing to do")
        sys.exit(0)
    
    # Load all holiday event data based on user config
    holiday_data = load_event_data_from_options(settings, year)

    # Generate SVG Calendar
    if not args.compileonly:
        generate_all_svgs(settings, holiday_data)
    else:
        print("Not generating the Calendar SVG Files at user request")

    # If generating SVGs only (for user review/manual editing) don't compile the calendar
    if not args.svgonly:
        compile_calendar(settings)
    else:
        print("Calendar NOT Compiled as user requested SVG Generation ONLY")

    # Debug for the time being
    export_holiday_validation_file(settings, holiday_data)

if __name__ == "__main__":
    main()
