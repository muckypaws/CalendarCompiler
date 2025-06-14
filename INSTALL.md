
# Installation Guide – CalendarCompiler

This guide helps you set up and run the CalendarCompiler project on macOS, Linux, or Windows.

---

## 1. Prerequisites

- **Python 3.8 or higher**  
  Download from [python.org](https://www.python.org/downloads/).

- **Git** (optional, for cloning the repo)  
  Download from [git-scm.com](https://git-scm.com/).

---

## 2. Clone the Repository

```bash
git clone https://github.com/muckypaws/CalendarCompiler.git
cd CalendarCompiler
```
*Or [download a ZIP](https://github.com/muckypaws/CalendarCompiler/archive/refs/heads/main.zip) and extract it.*

---

## 3. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate         # macOS/Linux
venv\ScriptsActivate            # Windows
```

---

## 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Install Cairo Graphics Library

This is required for SVG to PNG conversion (via CairoSVG):

- **macOS:**  
  ```bash
  brew install cairo
  ```
- **Ubuntu/Debian:**  
  ```bash
  sudo apt-get install libcairo2
  ```
- **Fedora:**  
  ```bash
  sudo dnf install cairo
  ```
- **Windows:**  
  - Follow the [CairoSVG Windows instructions](https://cairosvg.org/documentation/#installation).
  - You may need [MSYS2](https://www.msys2.org/) or precompiled binaries.

---

## 6. Prepare Your Artwork

- Place your front cover, back cover, and monthly artwork images in the folder specified in `config/settings.json` (default: `./artwork`).
- Recommended format: PNG (or JPG).

---

## 7. Configure Your Calendar

- Edit `config/settings.json` to adjust:
  - Calendar year (`year`)
  - Holiday/event inclusion
  - Artwork file names and folder
  - Output directories for PDF, PNG, and JPG
  - Metadata and branding

---

## 8. Run the Calendar Compiler

```bash
python CalendarCompiler.py
```
*Or add CLI flags for advanced control:*
```bash
python CalendarCompiler.py --exportpdf --exportpng --cleanup
```

---

## 9. Output

- PDFs are written to `output_pdfs/` (by default)
- PNGs to `output_pngs/`
- JPGs to `output_jpgs/`
- SVGs to `calendars/`
- Adjust output folders in `settings.json` as needed

---

## 10. Troubleshooting

- **Missing cairo:**  
  If you see errors about missing `cairo`, ensure the library is installed (see step 5 above).
- **Artwork not found:**  
  Check that all art files listed in `settings.json` exist in your artwork folder.
- **Permission errors:**  
  Run your terminal/command prompt as administrator (Windows) or check directory permissions (macOS/Linux).

---

## Licence

This project is licensed under the **GNU General Public License v3.0 only (GPL-3.0-only)**.  
See the [LICENSE](LICENSE) file for details.

---

## Need Help?

- Open an [issue on GitHub](https://github.com/muckypaws/CalendarCompiler/issues)
- Visit [muckypaws.com](https://muckypaws.com)
- Contact Jason Brooks via GitHub

---
