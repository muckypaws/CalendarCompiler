"""
Calendar export routines for SVG Calendar Generator.

Handles assembly and output of compiled PDF (A4 landscape) 
from supplied artwork and SVG calendar pages.
"""
import os
import shutil
import cairosvg
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
from modules.helpers import open_file_or_folder

def ensure_dir_exists(path):
    """
    Ensure that the specified directory exists, creating it if necessary.

    Args:
        path (str): Path to the directory to check/create.

    Returns:
        None
    """
    os.makedirs(path, exist_ok=True)

def cleanup_temp_files(temp_files, temp_dir, enable_cleanup=True):
    """
    Delete all files in `temp_files` and then attempt to remove `temp_dir`.

    Args:
        temp_files (list): List of file paths to remove.
        temp_dir (str): Path to directory to remove after files are deleted.
        enable_cleanup (bool): Whether to actually perform cleanup.

    Returns:
        None
    """
    if not enable_cleanup:
        print("Cleanup skipped (set 'cleanup': true in settings.json to enable).\n")
        return

    print("Cleaning up temporary PNG files...\n\n")
    for path in temp_files:
        try:
            os.remove(path)
        except Exception as e:
            print(f"Warning: Could not remove temp file {path}: {e}\n")

    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"Warning: Could not remove temp directory {temp_dir}: {e}\n")

def add_page_number(pdf_canvas, page_width, page_height, number):
    """Add a page number at the bottom centre of the PDF page."""
    pdf_canvas.setFont("Helvetica", 10)
    pdf_canvas.setFillColorRGB(0.4, 0.4, 0.4)
    pdf_canvas.drawCentredString(page_width / 2, 4, f"Page {number}")


def add_branding(pdf_canvas, page_width, page_height, branding_text, branding_url):
    """
    Draw branding text at the bottom right corner of a PDF page.

    Args:
        pdf_canvas (canvas.Canvas): ReportLab canvas object.
        page_width (float): Width of the page in points.
        page_height (float): Height of the page in points.
        branding_text (str): The text to display for branding.

    Returns:
        None
    """
    pdf_canvas.setFont("Helvetica", 8)
    pdf_canvas.setFillColorRGB(0.5, 0.5, 0.5)  # Subtle grey
    margin = 4
    #pdf_canvas.drawCentredString(page_width//2, margin, branding_text["branding_text"])
    pdf_canvas.drawString(margin*2, margin, branding_text)
    pdf_canvas.drawRightString(page_width - margin, margin, branding_url)


def add_extras(pdf_canvas, page_width, page_height, branding_parms, page_number):
    """Add additional information to the PDF."""
    if branding_parms.get("show_page_numbers", False):
        add_page_number(pdf_canvas, page_width, page_height, page_number)

    if branding_parms.get("show_branding", False):
        add_branding(pdf_canvas, page_width, page_height,
                     branding_parms["branding_text"], branding_parms["branding_url"])

    pdf_canvas.showPage()


def svg_to_png(svg_path, png_path, output_width=842, output_height=595):
    """
    Convert an SVG file to PNG format for embedding in PDF.

    Args:
        svg_path (str): Path to the SVG file.
        png_path (str): Output path for the PNG file.
        output_width (int): Target width in pixels.
        output_height (int): Target height in pixels.

    Returns:
        None
    """
    cairosvg.svg2png(url=svg_path, write_to=png_path,
                     output_width=3508, output_height=2480,
                     background_color='white')

def add_image_to_canvas(pdf_canvas, image_path, page_width, page_height):
    """
    Draw a scaled image (PNG/JPG) centred on the PDF page.

    Args:
        pdf_canvas (canvas.Canvas): ReportLab canvas object.
        image_path (str): Path to the image file.
        page_width (float): Width of the PDF page.
        page_height (float): Height of the PDF page.

    Returns:
        None
    """
    image = ImageReader(image_path)
    iw, ih = image.getSize()
    scale = min(page_width / iw, page_height / ih)
    new_w, new_h = iw * scale, ih * scale
    x = (page_width - new_w) / 2
    y = (page_height - new_h) / 2
    pdf_canvas.setFillColorRGB(1, 1, 1)  # White
    pdf_canvas.rect(0, 0, page_width, page_height, fill=1, stroke=0)
    pdf_canvas.drawImage(image, x, y, width=new_w, height=new_h)




def export_calendar_pdf(settings):
    """
    Export a full calendar as a compiled PDF (A4 landscape) with art and calendar pages.

    Args:
        settings (dict): Project settings, including 'art_files' and 'output'.

    Returns:
        None
    """
    page_width, page_height = landscape(A4)

    # Get all relevant paths from settings
    art = settings.get('art_files', {})
    artwork_folder = art.get('artwork_folder', './artwork')
    front_cover = art.get('front_cover')
    back_cover = art.get('back_cover')
    monthly_art = art.get('monthly_spreads', [])

    output_settings = settings.get("output", {})
    svg_dir = output_settings.get("svg_dir", "./calendars")
    output_dir = output_settings.get("pdf_dir", "./output")
    output_pdf_path = os.path.join(output_dir, f"Calendar_{settings['year']}.pdf")

    year = int(settings.get("year"))
    months = list(range(1, 13))

    # Prepare temp PNG directory for converted SVGs
    tmp_png_dir = os.path.join(output_dir, "tmp_pngs")
    ensure_dir_exists(tmp_png_dir)
    ensure_dir_exists(output_dir)
    temp_pngs = []
    branding = settings.get("branding", {})

    print(f"Compiling Calender PDF for {year}")
    print("="*31)
    print()

    c = canvas.Canvas(output_pdf_path, pagesize=landscape(A4))

    page_number = 1
    missing_files = []

    # --- Front Cover ---
    if front_cover:
        front_cover_path = os.path.join(artwork_folder, front_cover)
        if os.path.exists(front_cover_path):
            print(f"Adding the Front Cover: {front_cover_path}\n")
            add_image_to_canvas(c, front_cover_path, page_width, page_height)
            #add_branding(c,page_width, page_height,branding)
            c.showPage()
        else:
            missing_files.append(front_cover_path)
            print(f"*** WARNING: Unable to find Front Cover Image: {front_cover_path}")

    # --- Month Pages ---
    for i, month in enumerate(months):
        # Monthly art
        if i < len(monthly_art):
            month_art_path = os.path.join(artwork_folder, monthly_art[i])
            if os.path.exists(month_art_path):
                print(f"  Adding Month Artwork: {month_art_path}")
                add_image_to_canvas(c, month_art_path, page_width, page_height)
                #add_branding(c,page_width, page_height,branding)
                c.showPage()
                page_number += 1
            else:
                missing_files.append(month_art_path)
                print(f"*** WARNING: Unable to find artwork: {month_art_path}")
        # Calendar SVG (convert to PNG)
        svg_filename = f"Cal{year}{month:02d}.svg"
        svg_path = os.path.join(svg_dir, svg_filename)
        png_filename = f"Cal{year}{month:02d}.png"
        png_path = os.path.join(tmp_png_dir, png_filename)
        if os.path.exists(svg_path):
            print(f" Adding Month Calendar: {svg_path}\n")
            svg_to_png(svg_path, png_path,
                       output_width=int(page_width),
                       output_height=int(page_height))
            temp_pngs.append(png_path)
            add_image_to_canvas(c, png_path, page_width, page_height)
            page_number += 1
            add_extras(c,page_width, page_height,branding, page_number)
            #add_branding(c,page_width, page_height,branding)
            #c.showPage()
        else:
            missing_files.append(svg_path)
            print(f"*** WARNING: Unable to find Calendar: {svg_path}")


    # --- Back Cover ---
    if back_cover:
        back_cover_path = os.path.join(artwork_folder, back_cover)
        if os.path.exists(back_cover_path):
            print(f" Adding the Back Cover: {back_cover_path}\n")
            add_image_to_canvas(c, back_cover_path, page_width, page_height)
            #add_branding(c,page_width, page_height,branding)
            page_number += 1
            add_extras(c,page_width, page_height,branding, page_number)
            #c.showPage()
        else:
            missing_files.append(back_cover_path)
            print(f"*** WARNING: Unable to find Back Cover Image: {back_cover_path}")

    # --- Set Meta Data Baby Yeah! ----
    meta = settings.get("pdf_metadata", {})

    title = meta.get("title", f"{year} Calendar")

    c.setTitle(title)
    c.setAuthor(meta.get("author", "Calendar Generator - By Jason Brooks - www.muckypaws.com"))
    c.setSubject(meta.get("subject", "A4 Calendar"))
    c.setKeywords(meta.get("keywords", "calendar, svg, python"))
    c.setCreator("Calendar Generator by Jason Brooks, https://github.com/muckypaws/CalendarCompiler")
    c.save()
    print(f" Compiled PDF saved to: {output_pdf_path}")

    if missing_files:
        print(f"\n**** Warning: {len(missing_files)} missing files/artwork, file incomplete ****")
        if missing_files:
            print("\nSummary of missing files:")
            for fname in missing_files:
                print(f" - {fname}")
            print()

    # --- Cleanup section, if enabled in settings ---
    cleanup_temp_files(temp_pngs, tmp_png_dir, enable_cleanup=art.get("cleanup", False))

    if settings["OpenOnCompletion"]:
        open_file_or_folder(output_pdf_path)


# --- Stubs for PNG/JPEG export to implement next ---
def export_calendar_pngs(settings):
    """
    Export each calendar page and artwork as individual PNG files.

    Args:
        settings (dict): Project settings, including 'art_files' and 'output'.

    Returns:
        None
    """
    art = settings.get('art_files', {})
    artwork_folder = art.get('artwork_folder', './artwork')
    front_cover = art.get('front_cover')
    back_cover = art.get('back_cover')
    monthly_art = art.get('monthly_spreads', [])

    output_settings = settings.get("output", {})
    svg_dir = output_settings.get("svg_dir", "./calendars")
    output_dir = output_settings.get("png_dir", "./output_pngs")
    year = int(settings.get("year"))
    months = list(range(1, 13))

    ensure_dir_exists(output_dir)
    tmp_png_dir = os.path.join(output_dir, "tmp_pngs")
    ensure_dir_exists(tmp_png_dir)
    temp_pngs = []

    print(f"Creating Calender PNGs for {year}")
    print("="*31)
    print()

    # --- Front Cover ---
    if front_cover:
        src_path = os.path.join(artwork_folder, front_cover)
        out_path = os.path.join(output_dir, "cover_front.png")
        if os.path.exists(src_path):
            print(f"Exporting Front Cover PNG: {out_path}")
            shutil.copy(src_path, out_path)
        else:
            print(f"*** WARNING: Unable to find Front Cover Image: {src_path}")

    # --- Month Pages ---
    for i, month in enumerate(months):
        # Month artwork
        if i < len(monthly_art):
            src_path = os.path.join(artwork_folder, monthly_art[i])
            out_path = os.path.join(output_dir, f"art_{month:02d}.png")
            if os.path.exists(src_path):
                print(f"  Exporting Month Artwork: {out_path}")
                shutil.copy(src_path, out_path)
            else:
                print(f"*** WARNING: Unable to find artwork: {src_path}")

        # Calendar SVG (convert to PNG)
        svg_filename = f"Cal{year}{month:02d}.svg"
        svg_path = os.path.join(svg_dir, svg_filename)
        out_png = os.path.join(output_dir, f"calendar_{month:02d}.png")
        tmp_png = os.path.join(tmp_png_dir, f"calendar_{month:02d}.png")
        if os.path.exists(svg_path):
            print(f"  Exporting Month Calendar PNG: {out_png}")
            svg_to_png(svg_path, tmp_png)
            shutil.copy(tmp_png, out_png)
            temp_pngs.append(tmp_png)
        else:
            print(f"*** WARNING: Unable to find Calendar: {svg_path}")

    # --- Back Cover ---
    if back_cover:
        src_path = os.path.join(artwork_folder, back_cover)
        out_path = os.path.join(output_dir, "cover_back.png")
        if os.path.exists(src_path):
            print(f"Exporting Back Cover PNG: {out_path}")
            shutil.copy(src_path, out_path)
        else:
            print(f"*** WARNING: Unable to find Back Cover Image: {src_path}")

    # --- Cleanup temporary PNGs, if enabled ---
    cleanup_temp_files(temp_pngs, tmp_png_dir, enable_cleanup=art.get("cleanup", False))

    if settings["OpenOnCompletion"]:
        open_file_or_folder(output_dir)

def export_calendar_jpgs(settings):
    """
    Export each calendar page and artwork as individual JPG files.

    Args:
        settings (dict): Project settings, including 'art_files' and 'output'.

    Returns:
        None
    """
    art = settings.get('art_files', {})
    artwork_folder = art.get('artwork_folder', './artwork')
    front_cover = art.get('front_cover')
    back_cover = art.get('back_cover')
    monthly_art = art.get('monthly_spreads', [])

    output_settings = settings.get("output", {})
    svg_dir = output_settings.get("svg_dir", "./calendars")
    output_dir = output_settings.get("jpg_dir", "./output_jpgs")
    year = int(settings.get("year"))
    months = list(range(1, 13))

    ensure_dir_exists(output_dir)
    tmp_png_dir = os.path.join(output_dir, "tmp_pngs")
    ensure_dir_exists(tmp_png_dir)
    temp_pngs = []

    print(f"Compiling Calender JPGs for {year}")
    print("="*32)
    print()

    # --- Helper to convert and save JPG ---
    def png_to_jpg(png_path, jpg_path):
        with Image.open(png_path) as im:
            rgb_im = im.convert('RGB')
            rgb_im.save(jpg_path, quality=95)

    # --- Front Cover ---
    if front_cover:
        src_path = os.path.join(artwork_folder, front_cover)
        out_path = os.path.join(output_dir, "cover_front.jpg")
        if os.path.exists(src_path):
            print(f"Exporting Front Cover JPG: {out_path}")
            png_to_jpg(src_path, out_path)
        else:
            print(f"*** WARNING: Unable to find Front Cover Image: {src_path}")

    # --- Month Pages ---
    for i, month in enumerate(months):
        # Month artwork
        if i < len(monthly_art):
            src_path = os.path.join(artwork_folder, monthly_art[i])
            out_path = os.path.join(output_dir, f"art_{month:02d}.jpg")
            if os.path.exists(src_path):
                print(f"  Exporting Month Artwork JPG: {out_path}")
                png_to_jpg(src_path, out_path)
            else:
                print(f"*** WARNING: Unable to find artwork: {src_path}")

        # Calendar SVG (convert to PNG, then to JPG)
        svg_filename = f"Cal{year}{month:02d}.svg"
        svg_path = os.path.join(svg_dir, svg_filename)
        tmp_png = os.path.join(tmp_png_dir, f"calendar_{month:02d}.png")
        out_jpg = os.path.join(output_dir, f"calendar_{month:02d}.jpg")
        if os.path.exists(svg_path):
            print(f"  Exporting Month Calendar JPG: {out_jpg}")
            svg_to_png(svg_path, tmp_png)
            png_to_jpg(tmp_png, out_jpg)
            temp_pngs.append(tmp_png)
        else:
            print(f"*** WARNING: Unable to find Calendar: {svg_path}")

    # --- Back Cover ---
    if back_cover:
        src_path = os.path.join(artwork_folder, back_cover)
        out_path = os.path.join(output_dir, "cover_back.jpg")
        if os.path.exists(src_path):
            print(f"Exporting Back Cover JPG: {out_path}")
            png_to_jpg(src_path, out_path)
        else:
            print(f"*** WARNING: Unable to find Back Cover Image: {src_path}")

    # --- Cleanup temporary PNGs, if enabled ---
    cleanup_temp_files(temp_pngs, tmp_png_dir, enable_cleanup=art.get("cleanup", False))

    if settings["OpenOnCompletion"]:
        open_file_or_folder(output_dir)
