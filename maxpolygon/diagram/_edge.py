"""
Filename: maxpolygon.diagram._edge.py
---
Author: TravisGK
Date: 23 July 2025

Description: This file contains the function 
             that labels a section of the paper's edge
             with a bracket and a length displayed.
"""

from ._arc import draw_arc
from maxpolygon.math.bracket import calc_bracket_points


def label_edge(
    draw,
    start_xy: tuple,
    end_xy: tuple,
    px_open,
    stem_dir: str,
    bracket_thickness_px,
):
    def inc_angle(angle, add, exclude_360: bool):
        return (angle + add) % (360.0001 if exclude_360 else 360.0)

    g0, g1, branch, b0, b1, stem = calc_bracket_points(
        start_xy, end_xy, px_open, stem_dir, bracket_thickness_px
    )

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

    # Draw the curves from the ends toward the center.
    draw_arc(
        draw,
        start_xy,
        g0,
        start_angle=g0_start,
        end_angle=g0_end,
    )
    draw_arc(
        draw,
        end_xy,
        g1,
        start_angle=g1_start,
        end_angle=g1_end,
        fill="blue",
    )

    # Draw the curves to the branch point.
    exclude_360 = stem_dir in ["left", "down"]
    draw_arc(
        draw,
        b0,
        branch,
        start_angle=inc_angle(g0_start, 180, exclude_360=exclude_360),
        end_angle=inc_angle(g0_end, 180, exclude_360=exclude_360),
        fill="orange",
    )
    draw_arc(
        draw,
        b1,
        branch,
        start_angle=inc_angle(g1_start, 180, exclude_360=exclude_360),
        end_angle=inc_angle(g1_end, 180, exclude_360=exclude_360),
        fill="pink",
    )

    draw.ellipse((g0[0] - 3, g0[1] - 3, g0[0] + 3, g0[1] + 3), fill="cyan")
    draw.ellipse((b0[0] - 3, b0[1] - 3, b0[0] + 3, b0[1] + 3), fill="yellow")
    draw.ellipse(
        (branch[0] - 3, branch[1] - 3, branch[0] + 3, branch[1] + 3), fill="purple"
    )
    """
    k_point_a = (q_point_a[0], z_point[1] - abs(z_point[0] - q_point_a[0]))
    k_point_b = (q_point_b[0], z_point[1] + abs(z_point[0] - q_point_b[0]))
    draw_arc(
        k_point_a, 
        z_point, 
        start=90, 
        end=180, 
        expand_right=increasing_x, 
        expand_down=False,
    )
    draw_arc(
        k_point_b, 
        z_point, 
        start=180,
        end=270,
        fill="blue",
        expand_right=increasing_x,
        expand_down=True,
    )"""
