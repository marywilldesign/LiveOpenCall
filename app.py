import os
import subprocess
from flask import Flask, request, render_template
from PIL import Image, ImageDraw, ImageFont
import receiptGenerator as rg

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




UPLOAD_FOLDER = "uploads"
PRINTER_NAME = "Star_TSP143__STR_T_001_"

app = Flask(__name__)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def print_file(filepath, w_px, h_px):
    #px_per_mm = 203/25.4
    #w_mm = 72.0
    #h_buffer = 50 # tune me for the margin, units mm
    # just empirically tested and this width worked . . . 
    # why? 
    #-o PageSize=Custom.204x500
    #h_mm = w_mm*h_px/w_px + h_buffer
    #print(h_mm,'mm')
    h_arb = int(203*h_px/w_px) + 100
    subprocess.run([
        "lp",
        "-d", PRINTER_NAME,
# you cannot have both orientation fixed with fit-to-page.
        #"-o", "fit-to-page",
        "-o", "PageCutType=0NoCutPage", # turn off cutting / turn on -- 1PartialCutPage
        "-o", "DocCutType=0NoCutDoc", # turn off cutting / turn on -- 1PartialCutDoc
        #"-o", "orientation-requested=0",
        #"-o", "PageSize=Custom.72.0x{h_mm:.1f}",
        "-o", "PageSize=Custom.203x%f"%h_arb,
        filepath
    ])

    # -o PageCutType=0NoCutPage -o DocCutType=0NoCutDoc

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/print", methods=["POST"])
def print_endpoint():
    #name = request.form.get("name","").strip()
    #title = request.form.get("title","").strip()
    text = request.form.get("text","").strip()
    image_file = request.files.get("image")

    #font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    #if os.path.exists(font_path):
    #    font = ImageFont.truetype(font_path, 12)
    #else:
    #    font = ImageFont.load_default()

    #padding = 2
    #top_margin = 12
    #max_width = 384

    # ---------------- CREATE TEXT IMAGE ----------------
    #text_lines = []
    #if name: text_lines.append(f"ARTIST: {name}")
    #if title: text_lines.append(f"TITLE: {title}")
    #if text: text_lines += text.splitlines()

    #dummy = Image.new("1",(1,1))
    #draw_dummy = ImageDraw.Draw(dummy)
    #line_heights = []
    #total_height = 0
    #for line in text_lines:
    #    bbox = draw_dummy.textbbox((0,0), line, font=font)
    #    h = bbox[3]-bbox[1]
    #    line_heights.append(h)
    #    total_height += h+padding

    # ---------------- LOAD IMAGE ----------------
    has_image = request.form.get("has_image") == "true"
    if has_image:
        img = Image.open(image_file).convert("L")#.point(lambda x:0 if x<128 else 255, "1")
    else:
        img = Image.new("1", (433, 5), color=1)  # color=1 => white, color=0 => black    #    scale = max_width/img.width
    #    new_height = int(img.height*scale)
    #    img = img.resize((max_width,new_height))
    #else:
    #    img = None

    # ---------------- FINAL COMBINED IMAGE ----------------
    #final_height = top_margin + total_height + (img.height if img else 0) + padding
    #final_img = Image.new("1", (max_width, final_height), 1)
    #draw = ImageDraw.Draw(final_img)

    # top dashed line
    #draw.text((2,0), "-"*40, font=font, fill=0)

    #y = top_margin
    #for i,line in enumerate(text_lines):
    #    draw.text((2,y), line, font=font, fill=0)
    #    y += line_heights[i]+padding

    #if img:
    #    final_img.paste(img, (0,y))

    filepath = os.path.join(UPLOAD_FOLDER, "receipt.png")
    im, w_px, h_px = rg.makeReceipt(text, img, filepath) # this produces a file called receipt.png

    #im.save('test.png')
    print_file(filepath, w_px, h_px)
    return "Receipt sent to printer!"

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
