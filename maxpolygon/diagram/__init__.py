"""
Filename: maxpolygon.diagram.__init__.py
---
Author: TravisGK
Date: 23 July 2025

Description: This file contains the function 
             for drawing a polygon diagram using PIL
             given vertices and hint points.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from ._fraction_str import decimal_inches_to_fraction
from ._basic_diagram import to_px, create_basic_diagram
from ._label_edge import label_edge
from maxpolygon.math.sublengths import determine_sublengths

"""
These are constants that influence the diagram output.
"""

# Measurement settings.
USING_INCHES = True  # if True, uses fractions.
TO_THE_32TH = True  # only applicable for inches.
BRACKET_THICKNESS_PX = 60
PX_PADDING_FROM_EDGE = 30  # margin between brackets and paper (in px).

# Bracket settings.
PX_OPEN = 30


def draw_diagram(
    coords: list,
    center: tuple,
    indexed_hint_points: list,
    paper_size,
    invert_y: bool = True,
):
    """
    Draws a diagram and returns the PIL image object.
    ---
    Params:
    - coords (list): a list of (x, y) points (usually in inches).
    - center (x, y): the center of the polygon.
    - indexed_hint_points (list): a list of lists, where each index holds
                                  a list of points that can be used to help
                                  one determine the point
                                  of the point <coords[i]>.
    - paper_size (number): the side length of the square the polygon is inside.
    - invert_y (bool): if True, the diagram is drawn with the Y-coords flipped.

    Returns a PIL Image of the resulting diagram.
    """
    # 1) Load the fonts.
    current_file = Path(__file__).resolve()
    font_path = current_file.parent.parent / "res" / "font.otf"
    # big_font = ImageFont.truetype(font_path, size=41)
    measure_font = ImageFont.truetype(font_path, size=38)

    # 2) Create the image and draw shapes.
    img = create_basic_diagram(
        coords, center, indexed_hint_points, paper_size, invert_y
    )
    draw = ImageDraw.Draw(img)

    # 3) Determine the lengths
    #    of the subdivided side lengths for each edge.
    right_sublengths, top_sublengths, left_sublengths, bottom_sublengths = (
        determine_sublengths(
            coords,
            indexed_hint_points,
            paper_size,
            invert_y,
        )
    )

    # 4) Label the sublengths along the edges.
    def to_label_string(units) -> str:
        """
        Takes the given measurement (in units) and returns a strings
        that format the measurement in a clean way.
        """
        if USING_INCHES:
            return decimal_inches_to_fraction(units, to_32th=TO_THE_32TH) + '"'
        else:
            return f"{round(units, 1):.1f}"

    def to_label_strings(units_x, units_y):
        return (to_label_string(units_x), to_label_string(units_y))

    # 4a) Label the right side.
    px_right_x = to_px(paper_size, paper_size=paper_size) + PX_PADDING_FROM_EDGE
    last_y = 0
    for sublength in right_sublengths:
        px_y_start = to_px(last_y, paper_size=paper_size, invert=not invert_y)
        last_y += sublength
        px_y_end = to_px(last_y, paper_size=paper_size, invert=not invert_y)
        label_edge(
            label_str=to_label_string(sublength),
            draw=draw,
            start_xy=(px_right_x, px_y_start),
            end_xy=(px_right_x, px_y_end),
            px_open=PX_OPEN,
            stem_dir="right",
            bracket_thickness_px=BRACKET_THICKNESS_PX,
        )

    # 4b) Label the left side.
    px_left_x = to_px(0, paper_size=paper_size) - PX_PADDING_FROM_EDGE
    last_y = 0
    for sublength in left_sublengths:
        px_y_start = to_px(last_y, paper_size=paper_size, invert=not invert_y)
        last_y += sublength
        px_y_end = to_px(last_y, paper_size=paper_size, invert=not invert_y)
        label_edge(
            label_str=to_label_string(sublength),
            draw=draw,
            start_xy=(px_left_x, px_y_start),
            end_xy=(px_left_x, px_y_end),
            px_open=PX_OPEN,
            stem_dir="left",
            bracket_thickness_px=BRACKET_THICKNESS_PX,
        )

    # 4c) Label the top side.
    px_top_y = to_px(0, paper_size=paper_size) - PX_PADDING_FROM_EDGE
    last_x = 0
    for sublength in top_sublengths:
        px_x_start = to_px(last_x, paper_size=paper_size)
        last_x += sublength
        px_x_end = to_px(last_x, paper_size=paper_size)
        label_edge(
            label_str=to_label_string(sublength),
            draw=draw,
            start_xy=(px_x_start, px_top_y),
            end_xy=(px_x_end, px_top_y),
            px_open=PX_OPEN,
            stem_dir="up",
            bracket_thickness_px=BRACKET_THICKNESS_PX,
        )

    # 4d) Label the bottom side.
    px_bottom_y = to_px(paper_size, paper_size=paper_size) + PX_PADDING_FROM_EDGE
    last_x = 0
    for sublength in bottom_sublengths:
        px_x_start = to_px(last_x, paper_size=paper_size)
        last_x += sublength
        px_x_end = to_px(last_x, paper_size=paper_size)
        label_edge(
            label_str=to_label_string(sublength),
            draw=draw,
            start_xy=(px_x_start, px_bottom_y),
            end_xy=(px_x_end, px_bottom_y),
            px_open=PX_OPEN,
            stem_dir="down",
            bracket_thickness_px=BRACKET_THICKNESS_PX,
        )

    return img
