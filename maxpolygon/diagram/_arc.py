"""
Filename: maxpolygon.diagram._arc.py
---
Author: TravisGK
Date: 23 July 2025

Description: This file contains the function 
             that draws an a quarter circle within
             a given bbox. This simplifies the process of
             drawing brackets with PIL.
"""


def draw_arc(
    draw,
    start_xy,
    end_xy,
    start_angle,
    end_angle,
    fill="green",
    width=6,
):
    """
    Draws an arc from one coord to another
    with a (start) and (end) angle.

    """

    def make_bbox(start_xy, end_xy):
        x0, y0 = start_xy
        x1, y1 = end_xy
        return (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))

    bbox = make_bbox(start_xy, end_xy)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Determine how the bbox should be expanded by the angles.
    expand_right = 90 <= start_angle <= 270 and 90 <= end_angle <= 270
    expand_down = 180 <= start_angle <= 360 and 180 <= end_angle <= 360

    # Expand the bbox.
    if expand_right:  # expanding rightward.
        bbox = (bbox[0] - width / 2, bbox[1], bbox[2] + w, bbox[3])
    else:  # expanding leftward.
        bbox = (bbox[0] - w, bbox[1], bbox[2] + width / 2, bbox[3])

    if expand_down:  # expanding downward.
        bbox = (bbox[0], bbox[1] - width / 2, bbox[2], bbox[3] + h)
    else:  # expanding upward.
        bbox = (bbox[0], bbox[1] - h, bbox[2], bbox[3] + width / 2)

    draw.arc(
        bbox,
        start=start_angle,
        end=end_angle,
        fill=fill,
        width=width,
    )
