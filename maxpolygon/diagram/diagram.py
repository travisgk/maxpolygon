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
from maxpolygon.math.poly import generate_paper_points
from maxpolygon.math.sublengths import determine_sublengths
from maxpolygon._config import MEASURE_FONT_SIZE, TITLE_FONT_SIZE

"""
These are constants that influence the diagram output.
"""

from maxpolygon._config import *


def _to_label_str(units: float, use_inches: bool) -> str:
    """
    Takes the given measurement (in units) and returns a strings
    that format the measurement in a clean way.
    """
    if use_inches:
        return decimal_inches_to_fraction(units, to_32th=TO_THE_32TH) + '"'

    precision = METRIC_DECIMAL_PRECISION
    return f"{round(units, precision):.{precision}f}{UNITS_LABEL}"


def _add_title_to_img(
    my_img: Image.Image,
    paper_size: float,
    use_inches: bool,
    num_sides: int,
) -> Image.Image:
    """Adds a title to the image and returns it."""
    # 1) Determine the title string and load the font.
    measure = _to_label_str(paper_size, use_inches)
    title_str = f"{num_sides}-sided Polygon in a {measure} Square"
    current_file = Path(__file__).resolve()
    font_path = current_file.parent.parent / "res" / "font.otf"
    title_font = ImageFont.truetype(font_path, size=TITLE_FONT_SIZE)

    # 2) Use the bbox to draw the text in the center of a separate image.
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

    # 3) Add the title image.
    total_height = IMG_SIZE + h + TITLE_PADDING_PX
    combined = Image.new("RGB", (IMG_SIZE, total_height), "white")

    if TITLE_LOCATION == "top":
        combined.paste(title_img, (0, 0))
        combined.paste(my_img, (0, TITLE_PADDING_PX + title_img.height))
    else:
        combined.paste(my_img, (0, 0))
        combined.paste(title_img, (0, my_img.height + TITLE_PADDING_PX))

    return combined


def draw_diagram(
    num_sides: int,
    paper_size: float,
    use_inches: bool = True,
    for_cut_out: bool = False,
    subdivisions: list = [],
) -> Image.Image:
    """
    Draws a diagram and returns the PIL image object.

    Parameters:
        - num_sides (int): the number of sides the polygon will have.
        - paper_size (float): the side length of the square the polygon is inside.
        - use_inches (bool): if True, the measurements are given in fractions.
        - for_cut_out (bool): if True, the diagram is unlabeled
                              and made to be cut out.
        - subdivisions (list): an optional list of scale factors (floats)
                               ranging 0.0 to 1.0. 0.5 will draw a polygon
                               50% of the original size inside.

    Returns:
        Image.Image - the resulting diagram.
    """

    """
    1) Generate the polygon coords and hint points for each coord,
       then use those to generate a basic diagram.
    """
    invert_y = True
    coords, center, hints = generate_paper_points(num_sides, paper_size)

    img, labels_img = create_basic_diagram(
        coords,
        center,
        hints,
        paper_size,
        for_cut_out,
        subdivisions,
    )

    if for_cut_out:
        result = Image.new("RGBA", img.size, (255, 255, 255, 255))
        result = Image.alpha_composite(result, img)
        p = CUT_OUT_PADDING if for_cut_out else SQUARE_PADDING
        percent_used = (IMG_SIZE - p * 2) / IMG_SIZE
        square_size = paper_size * percent_used
        result = _add_title_to_img(result, square_size, use_inches, len(coords))
        result = result.resize(
            (result.width // ANTIALIAS, result.height // ANTIALIAS),
            resample=Image.LANCZOS,
        )
        return result

    """
    2) Determine the lengths
       of the subdivided side lengths for each edge,
       then label them.
    """
    right_sublengths, top_sublengths, left_sublengths, bottom_sublengths = (
        determine_sublengths(
            coords,
            hints,
            paper_size,
            invert_y,
        )
    )

    draw = ImageDraw.Draw(img)
    label_draw = ImageDraw.Draw(labels_img)

    def as_px(coord, invert: bool = False):
        return to_px(coord, paper_size, invert, for_cut_out=for_cut_out)

    px_right_x = as_px(paper_size) + PX_PADDING_FROM_EDGE
    last_y = 0
    for sublength in right_sublengths:
        px_y_start = as_px(last_y, invert=not invert_y)
        last_y += sublength
        px_y_end = as_px(last_y, invert=not invert_y)
        label_edge(
            label_str=_to_label_str(sublength, use_inches),
            draw=draw,
            label_draw=label_draw,
            start_xy=(px_right_x, px_y_start),
            end_xy=(px_right_x, px_y_end),
            px_open=PX_OPEN,
            stem_dir="right",
            bracket_thickness_px=BRACKET_THICKNESS_PX,
        )

    px_left_x = as_px(0) - PX_PADDING_FROM_EDGE
    last_y = 0
    for sublength in left_sublengths:
        px_y_start = as_px(last_y, invert=not invert_y)
        last_y += sublength
        px_y_end = as_px(last_y, invert=not invert_y)
        label_edge(
            label_str=_to_label_str(sublength, use_inches),
            draw=draw,
            label_draw=label_draw,
            start_xy=(px_left_x, px_y_start),
            end_xy=(px_left_x, px_y_end),
            px_open=PX_OPEN,
            stem_dir="left",
            bracket_thickness_px=BRACKET_THICKNESS_PX,
        )

    px_top_y = as_px(0) - PX_PADDING_FROM_EDGE
    last_x = 0
    for sublength in top_sublengths:
        px_x_start = as_px(last_x)
        last_x += sublength
        px_x_end = as_px(last_x)
        label_edge(
            label_str=_to_label_str(sublength, use_inches),
            draw=draw,
            label_draw=label_draw,
            start_xy=(px_x_start, px_top_y),
            end_xy=(px_x_end, px_top_y),
            px_open=PX_OPEN,
            stem_dir="up",
            bracket_thickness_px=BRACKET_THICKNESS_PX,
        )

    px_bottom_y = as_px(paper_size) + PX_PADDING_FROM_EDGE
    last_x = 0
    for sublength in bottom_sublengths:
        px_x_start = as_px(last_x)
        last_x += sublength
        px_x_end = as_px(last_x)
        label_edge(
            label_str=_to_label_str(sublength, use_inches),
            draw=draw,
            label_draw=label_draw,
            start_xy=(px_x_start, px_bottom_y),
            end_xy=(px_x_end, px_bottom_y),
            px_open=PX_OPEN,
            stem_dir="down",
            bracket_thickness_px=BRACKET_THICKNESS_PX,
        )

    """
    3) Label the center point.
    """
    if LABEL_MEASUREMENTS_TO_CENTER:
        # Create a new image layer so the brackets for the center
        # are rendered under everything else.
        under_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        under_draw = ImageDraw.Draw(under_layer)

        # Label the horizontal length that shows where the center is.
        start_x = as_px(0)
        end_x = as_px(center[0])
        const_y = as_px(center[1], invert=invert_y)
        label_edge(
            label_str=_to_label_str(center[0], use_inches),
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

        # Label the vertical length that shows where the center is.
        start_y = as_px(0, invert=invert_y)
        end_y = as_px(center[1], invert=invert_y)
        min_y = min(start_y, end_y)
        max_y = max(start_y, end_y)
        const_x = as_px(center[0])
        label_edge(
            label_str=_to_label_str(center[1], use_inches),
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

    # Collapse the labels layer down on top of the image.
    result = Image.new("RGBA", img.size, (255, 255, 255, 255))
    if LABEL_MEASUREMENTS_TO_CENTER:
        result = Image.alpha_composite(result, under_layer)
    result = Image.alpha_composite(result, img)
    result = Image.alpha_composite(result, labels_img)
    img = result.convert("RGB")

    if TITLE_LOCATION is not None:
        img = _add_title_to_img(img, paper_size, use_inches, len(coords))

    img = img.resize(
        (img.width // ANTIALIAS, img.height // ANTIALIAS),
        resample=Image.LANCZOS,
    )

    return img
