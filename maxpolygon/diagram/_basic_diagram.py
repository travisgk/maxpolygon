"""
Filename: maxpolygon.diagram._basic_diagram.py
---
Author: TravisGK
Date: 20 July 2025

Description: This file defines a function which uses PIL
             to draw and return a basic diagram of a specified
             polygon contained within a square.
"""


from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Image output settings.
IMG_SIZE = 1200  # Output image size (pixels)
SQUARE_PADDING = 250  # Padding around the square (pixels)

# Vertex render settings.
CENTER_VERT_RADIUS = 2
HINT_VERT_RADIUS = 3

# Label settings.
LABEL_POLY_VERTS = True
LABEL_HINT_POINTS = True
LABEL_OFFSET_X = 3
LABEL_OFFSET_Y = -10
LETTERS = "ac" # a = anticlockwise, c = clockwise
CLOCKWISE_COLOR = (0, 200, 100)  # label color for clockwise.
ANTICLOCKWISE_COLOR = (0, 100, 200)  # label color for anticlockwise.
LINE_COLOR = (137, 137, 137)  
SQUARE_BORDER_COLOR = (187, 187, 187)

def to_px(val, paper_size, invert: bool=False):
    if val == -1:
        return -999999  # renders point out-of-bounds.
    percent = (val / paper_size)
    if invert:
        percent = 1 - percent

    return percent * (IMG_SIZE - 2 * SQUARE_PADDING) + SQUARE_PADDING


def create_basic_diagram(
    coords: list,
    center: tuple,
    indexed_hint_points: list,
    paper_size,
    invert_y: bool=True,
) -> "Image":

    # 1) Load the fonts.
    current_file = Path(__file__).resolve()
    font_path = current_file.parent.parent / "res" / "font.otf"
    big_font = ImageFont.truetype(font_path, size=41)

    # 2) Convert the units into pixels.
    def as_px(val, invert: bool=False):
        # A helper func that inserts <paper_size> for readability.
        return to_px(val, paper_size, invert)

    px_coords = [(as_px(x), as_px(y, invert=invert_y)) for x, y in coords]
    px_center = (as_px(center[0]), as_px(center[1], invert=invert_y))
    px_indexed_hints = [
        [
            (as_px(x), as_px(y, invert=invert_y)) 
            for x, y in hints
        ] for hints in indexed_hint_points
    ]

    # 3) Create the image and draws the shape.
    # 3a) Create the image and drawing object.
    img = Image.new("RGB", (IMG_SIZE, IMG_SIZE), "white")
    draw = ImageDraw.Draw(img)

    # 3b) Draw the square border.
    draw.rectangle(
        [
            SQUARE_PADDING,
            SQUARE_PADDING,
            IMG_SIZE - SQUARE_PADDING,
            IMG_SIZE - SQUARE_PADDING,
        ],
        outline=SQUARE_BORDER_COLOR,
        width=4
    )

    # 3c) Draw the polygon lines.
    draw.polygon(px_coords, outline=LINE_COLOR, width=4)
    for i, (x, y) in enumerate(coords):
        p_x, p_y = px_coords[i]

    # 3d) Draw the center.
    cx, cy = px_center
    r = CENTER_VERT_RADIUS
    draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=LINE_COLOR)

    # 4) Draw the numbering labels for the polygon and its hint points.
    # 4a) Label each point of the polygon.
    if LABEL_POLY_VERTS:
        for index, (p_x, p_y) in enumerate(px_coords):
            text_pos = (p_x + LABEL_OFFSET_X, p_y + LABEL_OFFSET_Y)
            draw.text(text_pos, str(index + 1), fill="black", font=big_font)

    # 4b) Draw the hint point vertices and labels.
    r = HINT_VERT_RADIUS
    for index, points in enumerate(px_indexed_hints):
        for point_index, (p_x, p_y) in enumerate(points):
            if x == -1:
                continue

            # Choose the fill color depending on direction.
            if point_index == 0:
                fill_color = ANTICLOCKWISE_COLOR
            else:
                fill_color = CLOCKWISE_COLOR
            draw.ellipse((p_x-r, p_y-r, p_x+r, p_y+r), fill=fill_color)

            if LABEL_HINT_POINTS:
                # Label the hint point with a number
                # followed by "a" or "c".
                off = -1 if point_index == 0 else 1
                base_num = (index + off) % len(coords) + 1
                letter_str = f"{base_num}{LETTERS[point_index]}"
                text_pos = (p_x + LABEL_OFFSET_X, p_y + LABEL_OFFSET_Y)
                draw.text(
                    text_pos, letter_str, fill=fill_color, font=big_font
                )

    # 5) Return the finished PIL image.
    return img