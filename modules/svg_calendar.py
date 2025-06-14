"""SVG Generation Module to create the basic calendar outline."""
import os
import calendar
import math
import xml.sax.saxutils as saxutils
from datetime import datetime
from modules.helpers import wrap_text, load_settings, trim_calendar_grid, build_full_calendar_grid
from modules.calendar_events import ISO_COUNTRY_NAMES

def escape_xml(text):
    """Escape &, <, >, ', and " for XML."""
    return saxutils.escape(text)

def generate_svg_calendar(year: int, month: int, output_dir="calendars", holidays: dict = None):
    """
    Generate an A4 landscape SVG calendar for a given month and year.

    This function creates a visual calendar in SVG format with weekday headers, 
    numbered day boxes, and optional holiday/event annotations. It supports 
    highlighting specific days using a `holidays` dictionary keyed by ISO date strings.

    The output file is saved to the specified output directory using the filename 
    pattern 'CalYYYYMM.svg'.

    Parameters:
        year (int): The calendar year (e.g., 2026).
        month (int): The calendar month (1–12).
        output_dir (str, optional): Directory to save the SVG file. Defaults to 'calendars'.
        holidays (dict, optional): A dictionary of holiday events keyed by ISO date strings 
            (e.g., '2026-03-17'), where each value is a dict with:
            - 'label': str – Displayed label for the event (can include newlines).
            - 'colour': str – Optional text colour (e.g., 'blue', 'red'). Defaults to black.

    Returns:
        None. Outputs an SVG file to disk and prints the file path upon success.
    """
    settings = load_settings()

    # A4 landscape size (SVG points)
    page_width = 842
    page_height = 595

    # Layout constants
    cell_padding = 5
    title_height = 50
    header_height = 30
    grid_top = title_height + header_height
    days_in_week = 7
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(year, month)
    rows = len(month_days)
    cell_width = page_width / days_in_week
    cell_height = (page_height - grid_top) / rows
    # Estimate max characters per line based on cell width and font size
    # Approx 7.5 pixels per character for font size 10
    approx_char_width = 4.5
    max_chars_per_line = int(cell_width // approx_char_width)
    font_family = "Arial"

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    filename = f"Cal{year}{month:02d}.svg"
    filepath = os.path.join(output_dir, filename)

    # Month title
    month_name = datetime(year, month, 1).strftime("%B %Y")

    scale_factor = settings.get("scale_factor", 1.0)  # 95% scaling; change as needed or load from settings.json
    offset_x = (page_width * (1 - scale_factor)) / 2
    offset_y = (page_height * (1 - scale_factor)) / 2

    # Start SVG
    svg = [f'<svg width="{page_width}" height="{page_height}" xmlns="http://www.w3.org/2000/svg">']
    svg.append(f'<g transform="translate({offset_x},{offset_y}) scale({scale_factor})">')

    mh = settings["month_header"]
    svg.append(
        f'<text x="{page_width/2}" y="{title_height/1.5}" text-anchor="middle" '
        f'font-size="{mh["fontsize"]}" font-family="{mh["font"]}" font-weight="{mh["weight"]}" fill="{mh["colour"]}">{month_name}</text>'
    )

    # Weekday headers
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_box_colour = settings.get("weekday_box_colour", "#393939")
    for i, dayinfo in enumerate(settings["days_of_week"]):
        x = i * cell_width
        label = dayinfo["label"]
        font = dayinfo.get("font", "Arial")
        fontsize = dayinfo.get("fontsize", 12)
        weight = dayinfo.get("weight", "bold")
        colour = dayinfo.get("colour", "#ffffff")
        
        svg.append(
            f'<rect x="{x}" y="{title_height}" width="{cell_width}" height="{header_height}" fill="{weekday_box_colour}" stroke="{weekday_box_colour}" stroke-width="1" />'
        )

        svg.append(
            f'<text x="{x + cell_width / 2}" y="{title_height + header_height * 0.7}" '
            f'text-anchor="middle" font-size="{fontsize}" font-family="{font}" font-weight="{weight}" fill="{colour}">{label}</text>'
        )


    # Day boxes and dates
    # New: use the build_full_calendar_grid function
    month_grid = build_full_calendar_grid(year, month, week_start=0)  # 0 for Monday
    month_grid = trim_calendar_grid(month_grid, month)

    for row_idx, week in enumerate(month_grid):
        for col_idx, (cell_year, cell_month, cell_day, in_current_month) in enumerate(week):

            x = col_idx * cell_width
            y_pos = grid_top + row_idx * cell_height

            # Dim or colour differently if not in current month
            if not in_current_month:
                fill_colour = settings.get("invalid_cell_colour", "#dddddd")
                day_num_colour = "#888888"
            elif col_idx == 5:
                fill_colour = settings.get("weekend_colours", {}).get("saturday", "#d3f5ff")
                day_num_colour = settings["day_number"]["colour"]
            elif col_idx == 6:
                fill_colour = settings.get("weekend_colours", {}).get("sunday", "#d3f5ff")
                day_num_colour = settings["day_number"]["colour"]
            else:
                fill_colour = "white"
                day_num_colour = settings["day_number"]["colour"]

            svg.append(f'<rect x="{x}" y="{y_pos}" width="{cell_width}" height="{cell_height}" fill="{fill_colour}" stroke="black" />')

            # Draw the day number for all boxes (including spillover days)
            dn = settings["day_number"]
            svg.append(
                f'<text x="{x + cell_padding}" y="{y_pos + 16}" font-size="{dn["fontsize"]}" '
                f'font-family="{dn["font"]}" font-weight="{dn["weight"]}" fill="{day_num_colour}">{cell_day}</text>'
            )

            # Only add holidays if this is the current month
            date_key = f"{cell_year}-{cell_month:02d}-{cell_day:02d}"
            if holidays and date_key in holidays and in_current_month:
                entry_data = holidays[date_key]
                line_offset = 0

                if "entries" in entry_data:
                    # New multi-entry format
                    for entry in entry_data["entries"]:
                        raw_lines = entry.get("label", "").split("\n")
                        colour = entry.get("colour", "black")
                        for raw in raw_lines:
                            wrapped = wrap_text(raw, max_chars=max_chars_per_line)
                            for line in wrapped:
                                line_y = y_pos + 30 + (line_offset * 14)
                                et = settings["event_text"]
                                svg.append(
                                    f'<text x="{x + cell_padding}" y="{line_y}" font-size="{et["fontsize"]}" '
                                    f'font-family="{et["font"]}" font-weight="{et["weight"]}" fill="{colour}">{escape_xml(line)}</text>'
                                )
                                line_offset += 1
                else:
                    # Legacy single-entry fallback
                    raw_lines = entry_data.get("label", "").split("\n")
                    colour = entry_data.get("colour", "black")
                    for raw in raw_lines:
                        wrapped = wrap_text(raw, max_chars=max_chars_per_line)
                        for line in wrapped:
                            line_y = y_pos + 30 + (line_offset * 14)
                            et = settings["event_text"]
                            svg.append(
                                f'<text x="{x + cell_padding}" y="{line_y}" font-size="{et["fontsize"]}" '
                                f'font-family="{et["font"]}" font-weight="{et["weight"]}" fill="{colour}">{escape_xml(line)}</text>'
                            )
                            line_offset += 1

    svg.append('</g>')
    svg.append('</svg>')

    with open(filepath, "w") as f:
        f.write("\n".join(svg))

    print(f"Created: {filepath}")

def generate_legend_svg(country_colours, event_types, output_path, num_cols=5, branding_text="Generated by Calendar Compiler | https://github.com/muckypaws/CalendarCompiler"):
    """Generate a multi-column SVG legend/key showing country colours, event types, border, and branding."""
    width, height = 1400, 720  # Increased height for branding/footer
    margin_x = 60
    margin_y = 80
    col_width = 260
    row_height = 30

    svg = [
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
        # Background
        f'<rect width="100%" height="100%" fill="white" />',
        # Border
        f'<rect x="2" y="2" width="{width-4}" height="{height-4}" fill="none" stroke="black" stroke-width="3" />',
        # Title
        f'<text x="{width//2}" y="40" text-anchor="middle" font-size="28" font-family="Arial" font-weight="bold">Legend / Key</text>',
        # Section header
        f'<text x="{margin_x-10}" y="70" font-size="18" font-family="Arial" font-weight="bold">Countries:</text>'
    ]
    countries = sorted(country_colours.items())
    rows_per_col = math.ceil(len(countries) / num_cols)

    for idx, (cc, colour) in enumerate(countries):
        col = idx // rows_per_col
        row = idx % rows_per_col
        x = margin_x + col * col_width
        y = margin_y + row * row_height
        full_name = ISO_COUNTRY_NAMES.get(cc, cc)
        svg.append(f'<rect x="{x}" y="{y}" width="20" height="20" fill="{colour}" stroke="black"/>')
        svg.append(f'<text x="{x + 30}" y="{y + 16}" font-size="16" font-family="Arial">{cc} – {full_name}</text>')

    # Optionally add Event Types section (if provided)
    if event_types:
        y_events = margin_y + (rows_per_col * row_height) + 40
        svg.append(f'<text x="{margin_x-10}" y="{y_events}" font-size="18" font-family="Arial" font-weight="bold">Event Types:</text>')
        for idx, (label, colour) in enumerate(event_types.items()):
            y_evt = y_events + 10 + idx * row_height
            svg.append(f'<rect x="{margin_x}" y="{y_evt}" width="20" height="20" fill="{colour}" stroke="black"/>')
            svg.append(f'<text x="{margin_x + 30}" y="{y_evt + 16}" font-size="16" font-family="Arial">{label}</text>')

    # Branding bar (footer)
    svg.append(
        f'<rect x="0" y="{height-38}" width="{width}" height="38" fill="#222" />'
        f'<text x="{width//2}" y="{height-14}" text-anchor="middle" font-size="16" font-family="Arial" fill="#fafafa">{branding_text}</text>'
    )

    svg.append('</svg>')
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
