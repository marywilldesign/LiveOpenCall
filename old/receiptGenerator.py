import os
from PIL import Image, ImageDraw, ImageFont
# ReportLab + pdf2image (install: pip install reportlab pdf2image; conda install poppler)
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from pdf2image import convert_from_path  # Renders PDF → PIL
from io import BytesIO

#text = 'this is some test text for printing that is short and has a lot of different info in it lol. It wraps automatically and supports multiple lines naturally!'
#image_file = './marcelatope.png'


def makeReceipt(text,img,filepath):
    # Config
    PAGE_WIDTH_MM = 72  # Thermal (~384px @203DPI)
    DPI = 300  # PNG sharpness
    #font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
    font_path = './static/fonts/Jacquard24-Regular.ttf'
    font_size = 18  # pt
    top_margin_mm = 5
    line_height_mm = font_size * 1.2 / 72 * 25.4  # pt → mm (precise)
    padding_mm = 0

    # Register font (fallback)
    try:
        pdfmetrics.registerFont(TTFont('Jacquard', font_path))
        font_name = 'Jacquard'
    except:
        font_name = 'Helvetica'
        print("Font not found; using Helvetica")

    # ---------------- COMPUTE EXACT CONTENT HEIGHT (AUTO-ADJUST) ----------------
    def string_width(text):
        c = canvas.Canvas(BytesIO(), pagesize=(1,1))
        c.setFont(font_name, font_size)
        w = c.stringWidth(text, font_name, font_size)
        c._filename = ''  # Avoid temp file
        return w

    max_text_width = PAGE_WIDTH_MM * mm - 4 * mm

    # Wrap text (same logic)
    text_lines = []
    for para in text.splitlines():
        words = para.split()
        if not words: 
            text_lines.append(''); continue
        current_line = []
        for word in words:
            test_line = (' '.join(current_line + [word]) if current_line else word)
            if string_width(test_line) <= max_text_width:
                current_line.append(word)
            else:
                if current_line:
                    text_lines.append(' '.join(current_line))
                    current_line = [word]
                else:  # Truncate long word
                    w = word
                    while string_width(w) > max_text_width and len(w) > 1:
                        w = w[:-1]
                    text_lines.append(w + '...')
                    current_line = []
        if current_line:
            text_lines.append(' '.join(current_line))

    # Calc heights
    num_text_lines = len([l for l in text_lines if l.strip()])  # Skip empty
    text_height_mm = num_text_lines * line_height_mm + padding_mm * (num_text_lines - 1)

    img_height_mm = 0
    # if os.path.exists(image_file):
    #print('about to load', image_file)
    pil_img = img #Image.open(image_file).convert("L").point(lambda x:0 if x<128 else 255, "1")#Image.open(image_file)
    #print('loaded !')
    img_width_mm = PAGE_WIDTH_MM * mm
    img_height_mm = (pil_img.height * img_width_mm / pil_img.width) / 72 * 25.4  # px → mm

    content_height_mm = top_margin_mm + text_height_mm + img_height_mm + padding_mm
    PAGE_HEIGHT_MM = content_height_mm + 5

    print(f"Auto-height: {content_height_mm:.1f}mm ({PAGE_HEIGHT_MM:.1f}mm page) | Text lines: {num_text_lines}")

    # ---------------- CREATE PDF WITH EXACT HEIGHT ----------------
    c = canvas.Canvas("receipt.pdf", pagesize=(PAGE_WIDTH_MM * mm, PAGE_HEIGHT_MM * mm))
    width, height = PAGE_WIDTH_MM * mm, PAGE_HEIGHT_MM * mm
    c.setFont(font_name, font_size)

    # Dashed line (top)
    c.drawString(2 * mm, height - top_margin_mm * mm, '-' * 50)

    # Text (from top down)
    y_pos = height - (top_margin_mm + line_height_mm) * mm
    for line in text_lines:
        c.drawString(2 * mm, y_pos, line)
        y_pos -= (line_height_mm + padding_mm) * mm

    # Image (below text)
    #if os.path.exists(image_file):
    c.drawImage(ImageReader(img), 0, y_pos - img_height_mm * mm, 
        width=PAGE_WIDTH_MM * mm, height=img_height_mm * mm)

    c.showPage()
    c.save()

    # ---------------- PNG: Render + Monochrome + Resize (NO WHITESPACE) ----------------
    img_pdf = convert_from_path("receipt.pdf", dpi=DPI, first_page=1, last_page=1)[0]
    os.remove("receipt.pdf")

    # Auto-crop whitespace (extra tight)
    bbox = img_pdf.getbbox()  # Content bounding box
    img_pdf = img_pdf.crop(bbox)

    img_png = img_pdf.convert("L")#.point(lambda x: 0 if x < 128 else 255, "1")
    final_width = 384
    scale = final_width / img_pdf.width
    final_height = int(img_png.height * scale)
    img_png = img_png.resize((final_width, final_height), Image.Resampling.LANCZOS)

    
    print('about to save at ', filepath)
    img_png.save(filepath)
    print('temporary image saved at ', filepath)
    return img_png, final_width, final_height