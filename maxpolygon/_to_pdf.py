"""
Filename: maxpolygon._to_pdf.py
---
Author: TravisGK
Date: 9 August 2025

Description: This file defines a function to save a PIL image as a PDF.
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from PIL import Image


def save_img_as_pdf(img_path: str, output_path: str, pagesize=letter, cover=False):
    # Read image and DPI.
    img = Image.open(img_path)
    w_px, h_px = img.size

    page_w, page_h = pagesize

    if cover:
        scale = max(page_w / w_px, page_h / h_px)
    else:
        scale = min(page_w / w_px, page_h / h_px)

    scaled_w = w_px * scale
    scaled_h = h_px * scale

    x = 0
    y = page_h - scaled_h  # align top of image to top of page

    c = canvas.Canvas(output_path, pagesize=pagesize)
    # drawImage will place and scale the image. mask='auto' lets it keep transparency if present.

    c.drawImage(img_path, x, y, width=scaled_w, height=scaled_h, mask="auto")
    c.showPage()
    c.save()
