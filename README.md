[![Build Status](https://img.shields.io/github/workflow/status/muckypaws/CalendarCompiler/CI)](https://github.com/muckypaws/CalendarCompiler/actions)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Repo](https://img.shields.io/badge/github-muckypaws%2FCalendarCompiler-blue?logo=github)](https://github.com/muckypaws/CalendarCompiler)
# SVG Calendar Generator

**A Python-powered, configurable, and print-ready calendar generator.**

Create beautiful, multi-format (PDF, PNG, JPG) calendars with full artwork integration, public holiday/event support, and extensive customisation. Designed for makers, families, retro computing fans, and educators alike.

---

## Features

- **A4 Landscape calendars with monthly/cover artwork and public holidays**
- **Auto-compilation into PDF, PNG, and JPG formats**
- **Custom events and multi-country holiday support**
- **Configurable branding, page numbers, and metadata**
- **CLI and `settings.json`-driven workflow**
- **Open source, cross-platform, easy to extend**
- **Supports multiple countries for public holidays via `include_country_list` in settings.**
- **Auto-generates a legend/key page with colour codes for all countries and event types.**
- **Branding is now fully configurable via the `"branding"` section in `settings.json`.**

---

## New In Kernel v0.2 (June 2025)

- ✅ New modular Variable Rule Engine
- ✅ Per-country rule logic (Mother's Day, Father's Day, Volkstrauertag, Florii, etc)
- ✅ Canonicalised label merge & conflict resolution
- ✅ Full country ISO list support (`include_country_list`)
- ✅ Christian + Orthodox feast calculations (Ash Wednesday, Easter, Florii, Advent, etc)
- ✅ Automatic holiday export validation for auditing (`holiday_export_YEAR.csv`)
- ✅ Fully PEP257-compliant engineering design
- ✅ Extensible JSON rule configuration (`rules/variable_rules.json`)

---

## Example Output

- Compiled PDF suitable for printing (front cover, 12 art spreads, calendar pages, back cover)
- Individual PNG/JPG files per page (for upload to print services)
- Holidays/important dates highlighted and colour-coded

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/muckypaws/CalendarCompiler.git
cd CalendarCompiler
```

### 2. Install Dependencies

Ensure you have **Python 3.8+**.  
Install the required Python packages (preferably in a virtual environment):

```bash
pip install -r requirements.txt
```

**System library note:**  
For SVG→PNG conversion, you must install the [Cairo graphics library](https://cairosvg.org/documentation/#installation):

- **macOS:** `brew install cairo`
- **Ubuntu:** `sudo apt-get install libcairo2`
- **Windows:** [See CairoSVG docs for help](https://cairosvg.org/documentation/#installation)

### 3. Prepare Your Artwork

Place your cover, monthly, and back images in the folder specified in `settings.json` (default: `./artwork`).  
Acceptable formats: PNG or JPG.

### 4. Configure Settings

Edit `config/settings.json` to match your desired year, artwork, holiday regions, and output options. See below for parameter reference.

### 5. Generate Your Calendar

Run the tool from the project root:

```bash
python CalendarCompiler.py
```

Or with custom CLI options, e.g.:

```bash
python CalendarCompiler.py --exportpdf --artwork ./artwork/Amstrad --exportto ./output_pdfs/Amstrad --cleanup
python CalendarCompiler.py --exportpdf --artwork ./artwork/BobThePolarBear --exportto ./output_pdfs/BobThePolarBear --cleanup
```

---

## Configuration Reference (`settings.json`)

```json
{
  "year": 2026,
  "scale_factor": 0.95,
  "include_days": {
    "international": false,
    "retro": true,
    "religious": true,
    "uk_holidays": true,
    "country_list": true,
    "custom_events": true
  },
    "include_country_list": {
    "countries": ["FR", "ES", "DE", "PL", "TR", "RO", "NL", "AT", "AU"]
  },
  "art_files": {
    "cleanup": true,
    "artwork_folder": "./artwork",
    "front_cover": "cover_front.png",
    "back_cover": "cover_back.png",
    "monthly_spreads": [
      "art_01.png", "art_02.png", "...", "art_12.png"
    ]
  },
  "output": {
    "pdf_dir": "output_pdfs",
    "png_dir": "output_pngs",
    "jpg_dir": "output_jpgs",
    "svg_dir": "calendars",
    "export_pdf": true,
    "export_png": false,
    "export_jpg": false
  }
}
```


## New Configuration Reference: Rule Engine

In addition to `settings.json`, Kernel v0.2 introduces:

### `rules/variable_rules.json`

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

**Parameter Highlights:**
- **year:** Calendar year to generate
- **include_days:** Toggle which types of holidays/events are shown
- **art_files:** Paths and filenames for covers and monthly artwork; `"cleanup"` removes temp PNGs after export
- **output:** Output folders for each format, and which exports to enable
- **pdf_metadata:** Metadata fields for the PDF
- **branding:** Show/hide branding and set custom text

---

## Usage Tips

- You can override many settings via CLI flags (see `--help`).
- All output is written to folders specified in `settings.json` (`output_pdfs`, `output_pngs`, etc.).
- Temporary PNGs are cleaned up if `"cleanup": true` in `art_files`.
- Branding is enabled by default—switch off in config if desired, but attribution is appreciated!

---

## Extending and Customising

- Add new event types or regional holiday support by updating the holiday logic or event data files.
- Brand or style each month uniquely with different artwork.
- Submit feature requests or pull requests via GitHub!

---

## Attribution

Created by **Jason Brooks**  
Blog: [muckypaws.com](https://muckypaws.com)  
GitHub: [github.com/muckypaws](https://github.com/muckypaws)

If you enjoy or adapt this project, a GitHub star, attribution, or contribution is always welcome!

---

## Licence

This project is licensed under the [GPLv3 License](LICENSE).  
You are free to use, modify, and redistribute this project with attribution.

---

## Support & Contributions

- Issues, ideas, or improvements? Please open an [issue](https://github.com/muckypaws/CalendarCompiler/issues) or submit a pull request!
- For installation help, see the **INSTALL.md** or contact via GitHub.

---
