"""
Filename: maxpolygon.diagram._label_edge.py
---
Author: TravisGK
Date: 23 July 2025

Description: This file contains the function 
             that labels a section of the paper's edge
             with a bracket and a length displayed.
"""

from ._arc import draw_arc
from ._basic_diagram import ANTIALIAS
from maxpolygon.math.bracket import calc_bracket_points
from pathlib import Path
from PIL import ImageFont

_measure_font = None


def label_edge(
    label_str: str,
    draw,
    start_xy: tuple,
    end_xy: tuple,
    px_open,
    stem_dir: str,
    bracket_thickness_px,
    fill="gray",
):
    global _measure_font
    WIDTH = 6 * ANTIALIAS  # line width.

    def inc_angle(angle, add, exclude_360: bool):
        return (angle + add) % (360.0001 if exclude_360 else 360.0)

    g0, g1, branch, b0, b1, stem = calc_bracket_points(
        start_xy, end_xy, px_open, stem_dir, bracket_thickness_px
    )

    # 1) Determine the angle of arcs depending on the bracket's stem direction.
    if stem_dir == "right":
        g0_start = 270
        g0_end = 360
        g1_start = 0
        g1_end = 90
    elif stem_dir == "up":
        g0_start = 180
        g0_end = 270
        g1_start = 270
        g1_end = 360
    elif stem_dir == "left":
        g0_start = 180  # inc_angle(270, 180)
        g0_end = 270  # inc_angle(360, 180)
        g1_start = 90
        g1_end = 180
    else:  # down.
        g0_start = 90
        g0_end = 180
        g1_start = 0
        g1_end = 90

    # 2) Draw the curves from the ends toward the center.
    draw_arc(
        draw,
        start_xy,
        g0,
        start_angle=g0_start,
        end_angle=g0_end,
        fill=fill,
        width=WIDTH,
    )
    draw_arc(
        draw,
        end_xy,
        g1,
        start_angle=g1_start,
        end_angle=g1_end,
        fill=fill,
        width=WIDTH,
    )

    # 3) Draw the curves to the branch point.
    exclude_360 = stem_dir in ["left", "down"]
    draw_arc(
        draw,
        b0,
        branch,
        start_angle=inc_angle(g0_start, 180, exclude_360=exclude_360),
        end_angle=inc_angle(g0_end, 180, exclude_360=exclude_360),
        fill=fill,
        width=WIDTH,
    )
    draw_arc(
        draw,
        b1,
        branch,
        start_angle=inc_angle(g1_start, 180, exclude_360=exclude_360),
        end_angle=inc_angle(g1_end, 180, exclude_360=exclude_360),
        fill=fill,
        width=WIDTH,
    )

    # 4) Draw the connecting lines between the curves.
    def draw_connection(g: tuple, b: tuple):
        W = WIDTH / 2
        if stem_dir in ["up", "down"]:
            # Y is mostly constant (line moving horizontally).
            min_x, max_x = min(g[0], b[0]), max(g[0], b[0])
            draw.rectangle(
                [
                    (min_x - W, g[1] - W),
                    (max_x + W, g[1] + W),
                ],
                fill=fill,
            )
        else:
            # X is constant (line moving vertically).
            min_y, max_y = min(g[1], b[1]), max(g[1], b[1])
            draw.rectangle(
                [
                    (g[0] - W, min_y - W),
                    (g[0] + W, max_y + W),
                ],
                fill=fill,
            )

    draw_connection(g=g0, b=b0)
    draw_connection(g=g1, b=b1)

    # 5) Draw the stem.
    W = WIDTH / 2
    if stem is not None:
        min_x, max_x = min(branch[0], stem[0]), max(branch[0], stem[0])
        min_y, max_y = min(branch[1], stem[1]), max(branch[1], stem[1])
    else:
        min_x, max_x = branch[0], branch[0]
        min_y, max_y = branch[1], branch[1]

    draw.rectangle(
        [(min_x - W, min_y - W), (max_x + W, max_y + W)],
        fill=fill,
    )

    # 6) Determine the text box position.
    if stem_dir == "right":
        text_pos = (max_x + W, (min_y + max_y) / 2)
    elif stem_dir == "left":
        text_pos = (min_x - W, (min_y + max_y) / 2)
    elif stem_dir == "up":
        text_pos = ((min_x + max_x) / 2, min_y - W)
    else:
        text_pos = ((min_x + max_x) / 2, max_y + W)

    # 7) Load the font if not yet loaded.
    if _measure_font is None:
        current_file = Path(__file__).resolve()
        font_path = current_file.parent.parent / "res" / "font.otf"
        _measure_font = ImageFont.truetype(font_path, size=38 * ANTIALIAS)

    # 8) Center the text box.
    bbox = _measure_font.getbbox(label_str)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_pos = (text_pos[0] - text_w / 2, text_pos[1] - text_h)

    F = 0.8
    if stem_dir == "right":
        text_pos = (text_pos[0] + text_w * F, text_pos[1])
    elif stem_dir == "left":
        text_pos = (text_pos[0] - text_w * F, text_pos[1])
    elif stem_dir == "up":
        text_pos = (text_pos[0], text_pos[1] - text_h)
    else:
        text_pos = (text_pos[0], text_pos[1] + text_h)

    # 9) Label the bracket with the measurement.
    draw.text(text_pos, label_str, fill=fill, font=_measure_font)
