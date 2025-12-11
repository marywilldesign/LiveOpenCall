# python
import os
from io import BytesIO
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from pdf2image import convert_from_path

def makeReceipt(text, img, filepath, spacer_lines_between_text_and_image=1):
    # CONFIG (points)
    PAGE_WIDTH_MM = 72  # target paper width (mm)
    PAGE_WIDTH_PT = PAGE_WIDTH_MM * mm  # points
    DPI = 300
    font_path = './static/fonts/Jacquard24-Regular.ttf'
    font_size = 18  # pt
    top_margin_mm = 5
    top_margin_pt = top_margin_mm * mm
    line_height_pt = font_size * 1.2  # line spacing in points
    line_padding_pt = 0  # extra space between lines in points
    bottom_margin_pt = 5 * mm  # ensure some breathing room at bottom

    # Register font
    try:
        pdfmetrics.registerFont(TTFont('Jacquard', font_path))
        font_name = 'Jacquard'
    except Exception:
        font_name = 'Helvetica'
        print("Font not found; using Helvetica")

    # Measure and wrap text to page width (in points)
    def string_width_pts(s: str) -> float:
        c = canvas.Canvas(BytesIO(), pagesize=(1, 1))
        c.setFont(font_name, font_size)
        w = c.stringWidth(s, font_name, font_size)
        c._filename = ''
        return w

    max_text_width_pts = PAGE_WIDTH_PT - 4 * mm

    text_lines = []
    for para in text.splitlines():
        words = para.split()
        if not words:
            text_lines.append('')
            continue
        current = []
        for word in words:
            test = (' '.join(current + [word]) if current else word)
            if string_width_pts(test) <= max_text_width_pts:
                current.append(word)
            else:
                if current:
                    text_lines.append(' '.join(current))
                    current = [word]
                else:
                    # truncate a single long word
                    w = word
                    while string_width_pts(w) > max_text_width_pts and len(w) > 1:
                        w = w[:-1]
                    text_lines.append(w + '...')
                    current = []
        if current:
            text_lines.append(' '.join(current))

    # Compute text block height (points)
    visible_lines = [l for l in text_lines if l.strip() != '']
    num_lines = len(visible_lines)
    text_height_pt = 0 if num_lines == 0 else num_lines * line_height_pt + (num_lines - 1) * line_padding_pt

    # Add spacer between text and image, expressed in "line units"
    spacer_height_pt = spacer_lines_between_text_and_image * line_height_pt

    # Compute image height in points to fit page width
    pil_img = img  # PIL.Image
    img_width_pt = PAGE_WIDTH_PT
    img_height_pt = pil_img.height * (img_width_pt / pil_img.width)

    # Compute total page height in points (include spacer)
    content_height_pt = top_margin_pt + text_height_pt + spacer_height_pt + img_height_pt
    page_height_pt = content_height_pt + bottom_margin_pt

    print(f"Auto-height: {content_height_pt/mm:.1f}mm ({page_height_pt/mm:.1f}mm page) | Text lines: {num_lines} | Spacer lines: {spacer_lines_between_text_and_image}")

    # Create PDF
    c = canvas.Canvas("receipt.pdf", pagesize=(PAGE_WIDTH_PT, page_height_pt))
    c.setFont(font_name, font_size)

    # Optional dashed line at top
    c.drawString(2 * mm, page_height_pt - top_margin_pt, '-' * 50)

    # Draw text from top down
    y = page_height_pt - top_margin_pt - line_height_pt
    for line in text_lines:
        if line.strip() == '':
            y -= (line_height_pt + line_padding_pt)
            continue
        c.drawString(2 * mm, y, line)
        y -= (line_height_pt + line_padding_pt)

    # Apply spacer before the image
    y -= spacer_height_pt

    # Place image with bottom-margin protection
    img_lower_left_y = y - img_height_pt
    if img_lower_left_y < bottom_margin_pt:
        img_lower_left_y = bottom_margin_pt

    c.drawImage(
        ImageReader(pil_img),
        0,
        img_lower_left_y,
        width=img_width_pt,
        height=img_height_pt,
        preserveAspectRatio=True,
        anchor='sw'
    )

    c.showPage()
    c.save()

    # Render PDF to PIL
    img_pdf = convert_from_path("receipt.pdf", dpi=DPI, first_page=1, last_page=1)[0]
    os.remove("receipt.pdf")

    # Conservative crop (leave a tiny bottom slack to avoid shaving content)
    bbox = img_pdf.getbbox()
    if bbox:
        left, top, right, bottom = bbox
        bottom = min(bottom + 2, img_pdf.height)
        img_pdf = img_pdf.crop((left, top, right, bottom))

    # Convert to grayscale and resize to target printer width
    img_png = img_pdf.convert("L")
    final_width = 384
    scale = final_width / img_png.width
    final_height = int(round(img_png.height * scale))
    img_png = img_png.resize((final_width, final_height), Image.Resampling.LANCZOS)

    img_png.save(filepath)
    print('temporary image saved at ', filepath)
    return img_png, final_width, final_height
