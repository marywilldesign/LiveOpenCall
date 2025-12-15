import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

def makeReceipt(text, img, filepath, spacer_lines_between_text_and_image=1):
    # ======================
    # CONFIG
    # ======================
    PRINTER_WIDTH_PX = 384

    FONT_SIZE = 32
    TIMESTAMP_FONT_SIZE = 16   # lighter / smaller
    LINE_SPACING = int(FONT_SIZE * .8)

    TOP_MARGIN = 10
    SIDE_MARGIN = 8
    BOTTOM_MARGIN = 10
    BG_COLOR = 255  # white
    TEXT_COLOR = 0  # black

    FONT_PATH = "./static/fonts/DeFontePlus-Leger.ttf"

    # ======================
    # FONTS
    # ======================
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        timestamp_font = ImageFont.truetype(FONT_PATH, TIMESTAMP_FONT_SIZE)
    except Exception:
        font = ImageFont.load_default()
        timestamp_font = ImageFont.load_default()
        print("⚠️ Font not found — using default")

    # ======================
    # TIMESTAMP
    # ======================
    timestamp = f"{datetime.now().strftime('%d . %m . %Y · %H:%M')}"


    # ======================
    # TEXT WRAPPING
    # ======================
    dummy_img = Image.new("L", (PRINTER_WIDTH_PX, 10))
    draw_dummy = ImageDraw.Draw(dummy_img)

    max_text_width = PRINTER_WIDTH_PX - (SIDE_MARGIN * 2)
    lines = []

    for paragraph in text.splitlines():
        words = paragraph.split(" ")
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            bbox = draw_dummy.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]

            if text_width <= max_text_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        # blank line between paragraphs
        lines.append("")

    if lines and lines[-1] == "":
        lines.pop()

    text_height = len(lines) * LINE_SPACING
    spacer_height = spacer_lines_between_text_and_image * LINE_SPACING

    # ======================
    # IMAGE RESIZE
    # ======================
    img_ratio = img.height / img.width
    img_width = PRINTER_WIDTH_PX
    img_height = int(img_width * img_ratio)
    img = img.resize((img_width, img_height), Image.Resampling.LANCZOS)
    img = img.convert("L")

    # ======================
    # TIMESTAMP HEIGHT
    # ======================
    ts_bbox = draw_dummy.textbbox((0, 0), timestamp, font=timestamp_font)
    timestamp_height = (ts_bbox[3] - ts_bbox[1]) + 6

    # ======================
    # FINAL IMAGE SIZE
    # ======================
    total_height = (
        TOP_MARGIN +
        timestamp_height +
        text_height +
        spacer_height +
        img_height +
        BOTTOM_MARGIN
    )

    receipt = Image.new("L", (PRINTER_WIDTH_PX, total_height), BG_COLOR)
    draw = ImageDraw.Draw(receipt)

    # ======================
    # DRAW TIMESTAMP
    # ======================
    y = TOP_MARGIN
    draw.text(
        (SIDE_MARGIN, y),
        timestamp,
        fill=TEXT_COLOR,
        font=timestamp_font
    )

    y += timestamp_height

    # ======================
    # DRAW TEXT
    # ======================
    for line in lines:
        if line.strip():
            draw.text((SIDE_MARGIN, y), line, fill=TEXT_COLOR, font=font)
        y += LINE_SPACING

    # spacer
    y += spacer_height

    # ======================
    # DRAW IMAGE
    # ======================
    receipt.paste(img, (0, y))

    # ======================
    # SAVE
    # ======================
    receipt.save(filepath)
    print("✅ Receipt image saved:", filepath)

    return receipt, PRINTER_WIDTH_PX, total_height
