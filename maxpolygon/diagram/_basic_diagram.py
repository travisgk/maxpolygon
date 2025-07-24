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

from maxpolygon._config import *


def to_px(val, paper_size, invert: bool = False):
    if val == -1:
        return -999999  # renders point out-of-bounds.
    percent = val / paper_size
    if invert:
        percent = 1 - percent

    return percent * (IMG_SIZE - 2 * SQUARE_PADDING) + SQUARE_PADDING


def create_basic_diagram(
    coords: list,
    center: tuple,
    indexed_hint_points: list,
    paper_size,
    invert_y: bool = True,
) -> "Image":

    # 1) Load the fonts.
    current_file = Path(__file__).resolve()
    font_path = current_file.parent.parent / "res" / "font.otf"
    big_font = ImageFont.truetype(font_path, size=BIG_FONT_SIZE)

    # 2) Convert the units into pixels.
    def as_px(val, invert: bool = False):
        # A helper func that inserts <paper_size> for readability.
        return to_px(val, paper_size, invert)

    px_coords = [(as_px(x), as_px(y, invert=invert_y)) for x, y in coords]
    px_center = (as_px(center[0]), as_px(center[1], invert=invert_y))
    px_indexed_hints = [
        [(as_px(x), as_px(y, invert=invert_y)) for x, y in hints]
        for hints in indexed_hint_points
    ]

    # 3) Create the image and drawing object.
    img = Image.new("RGB", (IMG_SIZE, IMG_SIZE), "white")
    draw = ImageDraw.Draw(img)

    # 4) Draw the square border.
    draw.rectangle(
        [
            SQUARE_PADDING,
            SQUARE_PADDING,
            IMG_SIZE - SQUARE_PADDING,
            IMG_SIZE - SQUARE_PADDING,
        ],
        outline=SQUARE_BORDER_COLOR,
        width=4 * ANTIALIAS,
    )

    # 5) Draw the polygon and vertices.
    # 5a) Draw the polygon lines.
    draw.polygon(px_coords, outline=LINE_COLOR, width=4 * ANTIALIAS)
    for i, (x, y) in enumerate(coords):
        p_x, p_y = px_coords[i]

    # 5b) Draw the polygon vertices that are on an edge.
    indices_on_edge = [
        i
        for i, (x, y) in enumerate(px_coords)
        if not all(
            SQUARE_PADDING + 0.001 < d < IMG_SIZE - SQUARE_PADDING - 0.001
            for d in (x, y)
        )
    ]
    for i in indices_on_edge:
        cx, cy = px_coords[i]
        r = HINT_VERT_RADIUS
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=LINE_COLOR)

    # 5c) Draw the center.
    cx, cy = px_center
    r = CENTER_VERT_RADIUS
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=LINE_COLOR)

    # 6) Draw the numbering labels for the polygon and its hint points.
    # 6a) Label each point of the polygon.
    if LABEL_POLY_VERTS:
        for index, (p_x, p_y) in enumerate(px_coords):
            text_pos = (p_x + LABEL_OFFSET_X, p_y + LABEL_OFFSET_Y)
            draw.text(text_pos, str(index + 1), fill="black", font=big_font)

    # 6b) Draw the hint point vertices and labels.
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
            draw.ellipse((p_x - r, p_y - r, p_x + r, p_y + r), fill=fill_color)

            main_point = px_coords[index]

            if LABEL_HINT_POINTS and p_x >= 0:
                # Label the hint point with a number
                # followed by "a" or "c".
                off = -1 if point_index == 0 else 1
                base_num = (index + off) % len(coords) + 1
                letter_str = f"{base_num}{LETTERS[point_index]}"
                text_pos = (p_x + LABEL_OFFSET_X, p_y + LABEL_OFFSET_Y)
                draw.text(text_pos, letter_str, fill=fill_color, font=big_font)
                draw.line(
                    [main_point, (p_x, p_y)], fill=fill_color, width=4 * ANTIALIAS
                )

    # 7) Return the finished PIL image.
    return img
