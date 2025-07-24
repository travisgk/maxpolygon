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
from ._basic_diagram import ANTIALIAS, to_px, create_basic_diagram
from ._label_edge import label_edge
from maxpolygon.math.sublengths import determine_sublengths
from maxpolygon._config import MEASURE_FONT_SIZE, TITLE_FONT_SIZE

"""
These are constants that influence the diagram output.
"""

from maxpolygon._config import *


def draw_diagram(
    coords: list,
    center: tuple,
    indexed_hint_points: list,
    paper_size,
    invert_y: bool = True,
    use_inches: bool = True,
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
    - use_inches (bool): if True, the measurements are given in fractions.

    Returns a PIL Image of the resulting diagram.
    """
    # 1) Load the fonts.
    current_file = Path(__file__).resolve()
    font_path = current_file.parent.parent / "res" / "font.otf"
    measure_font = ImageFont.truetype(font_path, size=MEASURE_FONT_SIZE)

    # 2) Create the image and draw shapes.
    img, labels_img = create_basic_diagram(
        coords, center, indexed_hint_points, paper_size, invert_y
    )
    draw = ImageDraw.Draw(img)
    label_draw = ImageDraw.Draw(labels_img)

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
        if use_inches:
            return decimal_inches_to_fraction(units, to_32th=TO_THE_32TH) + '"'

        precision = METRIC_DECIMAL_PRECISION
        return f"{round(units, precision):.{precision}f}{UNITS_LABEL}"

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
            label_draw=label_draw,
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
            label_draw=label_draw,
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
            label_draw=label_draw,
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
            label_draw=label_draw,
            start_xy=(px_x_start, px_bottom_y),
            end_xy=(px_x_end, px_bottom_y),
            px_open=PX_OPEN,
            stem_dir="down",
            bracket_thickness_px=BRACKET_THICKNESS_PX,
        )

    # 5) Label the measurements to the center point.
    if LABEL_MEASUREMENTS_TO_CENTER:
        # 5a) Create a new image layer so the brackets for the center
        #     are rendered under everything else.
        under_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        under_draw = ImageDraw.Draw(under_layer)

        # 5b) Label the horizontal length that shows where the center is.
        start_x = to_px(0, paper_size=paper_size)
        end_x = to_px(center[0], paper_size=paper_size)
        const_y = to_px(center[1], paper_size=paper_size, invert=invert_y)
        label_edge(
            label_str=to_label_string(center[0]),
            draw=under_draw,
            label_draw=label_draw,
            start_xy=(start_x, const_y),
            end_xy=(end_x, const_y),
            px_open=PX_OPEN,
            stem_dir="up",
            bracket_thickness_px=BRACKET_THICKNESS_PX,
            fill=CENTER_BRACKET_COLOR,
            label_fill=CENTER_BRACKET_LABEL_COLOR,
        )

        # 5c) Label the vertical length that shows where the center is.
        start_y = to_px(0, paper_size=paper_size, invert=invert_y)
        end_y = to_px(center[1], paper_size=paper_size, invert=invert_y)
        min_y = min(start_y, end_y)
        max_y = max(start_y, end_y)
        const_x = to_px(center[0], paper_size=paper_size)
        label_edge(
            label_str=to_label_string(center[1]),
            draw=under_draw,
            label_draw=label_draw,
            start_xy=(const_x, min_y),
            end_xy=(const_x, max_y),
            px_open=PX_OPEN,
            stem_dir="right",
            bracket_thickness_px=BRACKET_THICKNESS_PX,
            fill=CENTER_BRACKET_COLOR,
            label_fill=CENTER_BRACKET_LABEL_COLOR,
        )

    # 6) Collapse the labels layer down on top of the image.
    result = Image.new("RGBA", img.size, (255, 255, 255, 255))
    if LABEL_MEASUREMENTS_TO_CENTER:
        result = Image.alpha_composite(result, under_layer)
    result = Image.alpha_composite(result, img)
    result = Image.alpha_composite(result, labels_img)
    # img = Image.alpha_composite(img, labels_img)
    img = result.convert("RGB")

    # 6) Size the image down and return it if the title is disabled.
    if TITLE_LOCATION is None:
        img = img.resize(
            (img.width // ANTIALIAS, img.height // ANTIALIAS),
            resample=Image.LANCZOS,
        )
        return img

    # 7) Add a title to the image.
    # 7a) Determine the title string and load the font.
    measure = to_label_string(paper_size)
    title_str = f"{len(coords)}-sided Polygon in a {measure} Square"
    title_font = ImageFont.truetype(font_path, size=TITLE_FONT_SIZE)

    # 7b) Use the bbox to draw the text in the center of a separate image.
    bbox = title_font.getbbox(title_str)
    w, h = bbox[2] - bbox[0], int((bbox[3] - bbox[1]) * 2.5)
    title_img = Image.new("RGB", (IMG_SIZE, h), "white")
    title_draw = ImageDraw.Draw(title_img)
    title_draw.text(
        (IMG_SIZE / 2 - w / 2, 0),
        title_str,
        fill="gray",
        font=title_font,
    )

    # 7c) Add the title image.
    total_height = IMG_SIZE + h + TITLE_PADDING_PX
    # Create a new blank image with combined height
    combined = Image.new("RGB", (IMG_SIZE, total_height), "white")

    # 7d) Paste the images on top of each other
    if TITLE_LOCATION == "top":
        combined.paste(title_img, (0, 0))
        combined.paste(img, (0, TITLE_PADDING_PX + title_img.height))
    else:
        combined.paste(img, (0, 0))
        combined.paste(title_img, (0, img.height + TITLE_PADDING_PX))

    # 7e) Size the image down and return it.
    combined = combined.resize(
        (combined.width // ANTIALIAS, combined.height // ANTIALIAS),
        resample=Image.LANCZOS,
    )

    return combined
