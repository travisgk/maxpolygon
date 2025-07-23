"""
Filename: maxpolygon.math.bracket.py
---
Author: TravisGK
Date: 23 July 2025

Description: This file defines a function to draw a bracket ("{").
             It's given a start point and an end point,
             how big to make the clamp, the direction of the bracket's stem,
             and how thick (wide) the bracket can be,
             then draws the bracket accordingly.
"""

def calc_bracket_points(
    start_xy: tuple,
    end_xy: tuple,
    px_open,
    stem_dir: str,
    bracket_thickness_px,
):
    """
    Return six (x, y) points:
        - where the start_xy curves to.
        - where the end_xy curves to.
        - the branch point.
        - the point closest to start_xy that curves to the branch point.
        - the point closest to end_xy that curves to the branch point.
        - the stem point.
    """
    # 1) Define variables for drawing the clamp.
    start_x, start_y = start_xy
    end_x, end_y = end_xy

    t = bracket_thickness_px  # thickness.
    
    vertical_stem = stem_dir in ["up", "down"]
    if vertical_stem:
        l = abs(end_x - start_x)  # length.
    else:
        l = abs(end_y - start_y)  # length.

    g = px_open  # radius of grabber.

    # 2) Determine the points the outer claws curve down to.
    g0 = (
        start_x + g * ((stem_dir != "left") * 2 - 1),
        start_y + g * ((stem_dir != "up") * 2 - 1),
    )
    g1 = (
        end_x + g * ((stem_dir == "right") * 2 - 1),
        end_y + g * ((stem_dir == "down") * 2 - 1),
    )

    # 3) Determine the point where the two clamps will meet.
    b = min(l/2 - g, bracket_thickness_px - g)
    if vertical_stem:
        branch = (
            start_x + l/2,
            start_y + (g + b) * ((stem_dir == "down") * 2 - 1),
        )
    else:
        branch = (
            start_x + (g + b) * ((stem_dir == "right") * 2 - 1),
            start_y + l/2,
        )

    # 4) Determine the points that the clamps curve from to the branch point.
    branch_x, branch_y = branch
    b0 = (
        branch_x - b * ((stem_dir != "left") * 2 - 1),
        branch_y - b * ((stem_dir != "up") * 2 - 1),
    )
    b1 = (
        branch_x - b * ((stem_dir == "right") * 2 - 1),
        branch_y - b * ((stem_dir == "down") * 2 - 1),
    )

    # 5) Determine the final stem point that comes from the branch.
    s = t - g - b
    if vertical_stem:
        stem = (l/2, branch_y + s * ((stem_dir == "down") * 2 - 1))
    else:
        stem = (branch_x + s * ((stem_dir == "right") * 2 - 1))

    return g0, g1, branch, b0, b1, stem