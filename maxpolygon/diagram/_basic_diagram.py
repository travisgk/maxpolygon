"""
Filename: maxpolygon.diagram._basic_diagram.py
---
Author: TravisGK
Date: 20 July 2025

Description: This file defines a function which uses PIL
             to draw and return a basic diagram of a specified
             polygon contained within a square.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from maxpolygon._config import *
from maxpolygon.math.poly import scale_around_point


def to_px(val, paper_size, invert: bool = False, for_cut_out: bool = False):
    if val == -1:
        return -999999  # renders point out-of-bounds.
    percent = val / paper_size
    if invert:
        percent = 1 - percent

    if for_cut_out:
        return percent * (IMG_SIZE - 2 * CUT_OUT_PADDING) + CUT_OUT_PADDING
    return percent * (IMG_SIZE - 2 * SQUARE_PADDING) + SQUARE_PADDING


def create_basic_diagram(
    coords: list,
    center: tuple,
    indexed_hint_points: list,
    paper_size,
    for_cut_out: bool = False,
    subdivisions: list = [],
) -> Image.Image:
    current_file = Path(__file__).resolve()
    font_path = current_file.parent.parent / "res" / "font.otf"
    big_font = ImageFont.truetype(font_path, size=BIG_FONT_SIZE)

    def as_px(val, invert: bool = False):
        # A helper func that inserts <paper_size> for readability.
        return to_px(val, paper_size, invert, for_cut_out=for_cut_out)

    """
    Convert the units into pixels.
    """

    img = Image.new("RGBA", (IMG_SIZE, IMG_SIZE), (0, 0, 0, 0))
    labels_img = Image.new("RGBA", (IMG_SIZE, IMG_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    labels_draw = ImageDraw.Draw(labels_img)

    """
    Draw the border, the polygon, and any subdivisions of the polygon.
    """
    p = CUT_OUT_PADDING if for_cut_out else SQUARE_PADDING
    draw.rectangle(
        [
            p,
            p,
            IMG_SIZE - p,
            IMG_SIZE - p,
        ],
        outline=SQUARE_BORDER_COLOR,
        width=6 * ANTIALIAS,
    )

    px_coords = [(as_px(x), as_px(y, invert=True)) for x, y in coords]
    px_center = (as_px(center[0]), as_px(center[1], invert=True))
    px_indexed_hints = [
        [(as_px(x), as_px(y, invert=True)) for x, y in hints]
        for hints in indexed_hint_points
    ]
    draw.polygon(px_coords, outline=LINE_COLOR, width=6 * ANTIALIAS)

    for scale in subdivisions:
        sub_points = scale_around_point(px_coords, px_center, scale=scale)
        draw.polygon(sub_points, outline=CENTER_BRACKET_COLOR, width=4 * ANTIALIAS)

    """
    Draw the vertices of the poly that are on the edge, then the center point.
    """
    if not for_cut_out:
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

    cx, cy = px_center
    if for_cut_out:
        fill = CENTER_BRACKET_COLOR
        r = max(CENTER_VERT_RADIUS * 0.5, 4 * ANTIALIAS)
    else:
        fill = LINE_COLOR
        r = CENTER_VERT_RADIUS
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill)

    """
    Draw the numbering labels for the polygon and its hint points.
    """
    if not for_cut_out and LABEL_POLY_VERTS:
        for index, (p_x, p_y) in enumerate(px_coords):  # each point of poly.
            text_pos = (p_x + LABEL_OFFSET_X, p_y + LABEL_OFFSET_Y)
            labels_draw.text(text_pos, str(index + 1), fill="black", font=big_font)

    r = HINT_VERT_RADIUS
    for index, points in enumerate(px_indexed_hints):
        for point_index, (p_x, p_y) in enumerate(points):  # each hint point.
            if p_x == -1:
                continue

            if point_index == 0:
                fill_color = ANTICLOCKWISE_COLOR
            else:
                fill_color = CLOCKWISE_COLOR

            if not for_cut_out:
                draw.ellipse((p_x - r, p_y - r, p_x + r, p_y + r), fill=fill_color)

            if p_x >= 0:
                main_point = px_coords[index]  # hint point stems from this point.

                draw.line(
                    [main_point, (p_x, p_y)], fill=fill_color, width=4 * ANTIALIAS
                )

                if not for_cut_out and LABEL_HINT_POINTS:
                    # Label the hint point with a number
                    # followed by "a" or "c".
                    off = -1 if point_index == 0 else 1
                    base_num = (index + off) % len(coords) + 1
                    letter_str = f"{base_num}{LETTERS[point_index]}"
                    text_pos = (p_x + LABEL_OFFSET_X, p_y + LABEL_OFFSET_Y)
                    labels_draw.text(
                        text_pos, letter_str, fill=fill_color, font=big_font
                    )

    return img, labels_img
