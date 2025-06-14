# Calendar Compiler Configuration Guide (Kernel v0.2)

This document explains every configuration option available for the Calendar Compiler.
All settings are controlled via `settings.json` and supplemental rule files under `config/rules/`.

---

## Table of Contents

* [General Settings](#general-settings)
* [Holiday/Event Inclusion](#holidayevent-inclusion)
* [Country Selection](#country-selection)
* [Holiday Merge Options](#holiday-merge-options)
* [Artwork and Files](#artwork-and-files)
* [Output Settings](#output-settings)
* [Calendar Visual Customisation](#calendar-visual-customisation)
* [PDF Metadata](#pdf-metadata)
* [Branding Options](#branding-options)
* [Rule Engine (Kernel v0.2)](#rule-engine-kernel-v02)
* [API Keys & Advanced](#api-keys--advanced)
* [Example Settings File](#example-settings-file)

---

## General Settings

| Setting        | Type  | Description                                                  | Example |
| -------------- | ----- | ------------------------------------------------------------ | ------- |
| `year`         | int   | Calendar year to generate.                                   | `2026`  |
| `scale_factor` | float | Scale for SVG/PDF output (0.95 is default, 1.0 = full size). | `0.95`  |

---

## Holiday/Event Inclusion

The `include_days` object controls which types of special days appear on your calendar.

| Setting         | Type | Description                                                                                     |
| --------------- | ---- | ----------------------------------------------------------------------------------------------- |
| `international` | bool | Show international days (e.g. UN days, global events).                                          |
| `retro`         | bool | Include retro computing events (launch dates, anniversaries, etc.).                             |
| `religious`     | bool | Include religious holidays from Calendarific API (Christian, Jewish, Muslim, Hindu, etc.).      |
| `uk_holidays`   | bool | Show UK national and regional bank holidays (via python-holidays).                              |
| `country_list`  | bool | Include additional countries for public holidays (see [Country Selection](#country-selection)). |
| `custom_events` | bool | Show user-defined custom events from JSON files.                                                |

---

## Country Selection

To show public holidays for additional countries, use the `include_country_list` block.

```json
"include_country_list": {
  "countries": ["FR", "ES", "DE", "PL", "TR", "RO", "NL", "AT", "AU"]
}
```

* **`countries`**: List of [ISO 3166-1 alpha-2 country codes](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes).

  * Example: `"FR"` = France, `"DE"` = Germany, `"AU"` = Australia.
  * `"AU"` triggers state/territory level breakdown for Australian regions.

---

## Holiday Merge Options

| Setting                    | Type | Description                                                                                                   | Default |
| -------------------------- | ---- | ------------------------------------------------------------------------------------------------------------- | ------- |
| `merge_identical_holidays` | bool | Merge same-named holidays from different regions into a single entry, showing combined region codes in label. | `true`  |

---

## Artwork and Files

Configure artwork files for cover, monthly spreads, and file cleanup.

```json
"art_files": {
  "cleanup": true,
  "artwork_folder": "./artwork",
  "front_cover": "cover_front.png",
  "back_cover": "cover_back.png",
  "monthly_spreads": [
    "art_01.png", "art_02.png", ..., "art_12.png"
  ]
}
```

---

## Output Settings

Control where generated files are saved and which formats to export.

```json
"output": {
  "pdf_dir": "output_pdfs",
  "png_dir": "output_pngs",
  "jpg_dir": "output_jpgs",
  "svg_dir": "./calendars",
  "export_pdf": true,
  "export_png": false,
  "export_jpg": false
}
```

---

## Calendar Visual Customisation

| Setting               | Purpose                                |
| --------------------- | -------------------------------------- |
| `days_of_week`        | Weekday headers (font, colour, labels) |
| `weekday_box_colour`  | Background colour for weekday boxes    |
| `invalid_cell_colour` | Background for inactive cells          |
| `weekend_colours`     | Colour overrides for Sat/Sun           |
| `day_number`          | Font and colour for day numbers        |
| `event_text`          | Font and colour for holiday/event text |
| `month_header`        | Font and colour for month title        |

---

## PDF Metadata

```json
"pdf_metadata": {
  "title": "Calendar",
  "author": "Jason Brooks - www.muckypaws.com",
  "subject": "Calendar Generator by Jason Brooks",
  "keywords": "calendar, svg, holidays, printable"
}
```

---

## Branding Options

```json
"branding": {
  "show_branding": true,
  "show_page_numbers": true,
  "branding_text": "Generated with Calendar Compiler",
  "branding_url": "https://github.com/muckypaws/CalendarCompiler"
}
```

---

## Rule Engine (Kernel v0.2)

Kernel v0.2 introduces country-driven rule files located at:

```bash
config/rules/variable_rules.json
```

These control civil holidays (Mother's Day, Father's Day), Christian moveable feasts, and cultural rules.

### Example Rule File Structure:

```json
{
  "GB": {
    "mothers_day": "mothering_sunday",
    "fathers_day": "third_sunday_june",
    "yorkshire_pudding_day": "first_sunday_february",
    "christian": true,
    "moveable_cultural": {
      "remembrance_sunday": true
    }
  },
  "DE": {
    "fathers_day": "ascension_day",
    "christian": true,
    "moveable_cultural": {
      "volkstrauertag": true
    }
  },
  "RO": {
    "mothers_day": "second_sunday_may",
    "fathers_day": "third_sunday_june",
    "christian": true,
    "moveable_cultural": {
      "florii": true
    }
  }
}
```

> You may freely extend this structure for future countries.

---

## API Keys & Advanced

* `api_key` (currently reserved for Calendarific integration). If set to `USE_ENVIRONMENT`, will load from `.env` file.

---

## Export Audit File

After each calendar build, a full merged export file is created for audit purposes:

```bash
holiday_export_YEAR.csv
```

This file includes:

* Final calculated dates
* Region codes
* Event labels
* Assigned colours

Use this file for debugging, verification, or cross-checking data integrity.

---

## Notes and Tips

* Any missing files will trigger warnings but will not stop calendar generation.
* All file paths are relative to project root unless absolute paths are given.
* Almost all config values can be overridden via CLI.
* Merge logic handles conflict resolution automatically.
* Rules engine allows extreme flexibility for international expansion.

---

For more help visit:

[https://github.com/muckypaws/CalendarCompiler](https://github.com/muckypaws/CalendarCompiler)
