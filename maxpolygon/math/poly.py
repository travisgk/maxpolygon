"""
Filename: maxpolygon.math.poly.py
---
Author: TravisGK
Date: 19 July 2025

Description: This file contains functionality 
             to determine the points of the largest possible perfect polygon
             inscribed inside a square.
"""

import math
import numpy as np

# Create a cache of normalized polygon points 
# to optimize finding the best angle.
_angles_cache = {
    n: np.linspace(0, 2*np.pi, n, endpoint=False) for n in range(3,33)
}


def generate_polygon_coords(n: int, rotation=0.0):
    """ 
    Generates the coordinates of a regular polygon with n sides 
    inscribed in a unit circle, optionally rotated by rotation radians.
    """
    angles = _angles_cache.get(n) + rotation
    return np.column_stack((np.cos(angles), np.sin(angles)))


def calc_bbox_size(coords):
    """ 
    Returns a tuple of (width, height, min_x, min_y) for the bbox of coords.
    """
    min_x, max_x = coords[:,0].min(), coords[:,0].max()
    min_y, max_y = coords[:,1].min(), coords[:,1].max()
    return max_x - min_x, max_y - min_y, min_x, min_y


def calc_polygon_area(coords: np.ndarray) -> float:
    """
    Shoelace formula for a closed polygon.
    coords should be an (n,2) array of (x,y) points in order.
    """
    # Roll shift the points so that (x[i],y[i]) pairs with (x[i+1],y[i+1]).
    x = coords[:, 0]
    y = coords[:, 1]

    # Append the first point at the end to close the loop.
    x_next = np.roll(x, -1)
    y_next = np.roll(y, -1)
    
    return 0.5 * abs(np.dot(x, y_next) - np.dot(y, x_next))


def find_rotation_of_smallest_bbox(n: int):
    """
    Returns the radian rotation that gives a perfect polygon 
    of <n> sides whose bounding box is covered the most percent-wise.
    """
    radian_candidates = np.linspace(0, np.pi/n, 100_001)
    poly_area = calc_polygon_area(generate_polygon_coords(n))
    
    best_angle = 0
    best_bbox_coverage = 0

    # Search for the angle that provides the most covered bbox.
    for angle in radian_candidates:
        coords = generate_polygon_coords(n, rotation=angle)
        w, h, min_x, min_y = calc_bbox_size(coords)
        max_dim = max(w, h)
        bbox_area = max_dim ** 2  # since polygon must fit into a square
        percent_bbox_covered = poly_area / bbox_area
        if percent_bbox_covered > best_bbox_coverage:
            best_angle = angle
            best_bbox_coverage = percent_bbox_covered

    return best_angle


def scale_to_square(coords, paper_size):
    """
    Scale and translate a set of 2D points so they fit proportionally
    inside a square [0, paper_size] × [0, paper_size], with the
    minimum x and minimum y both at 0 (bottom‑left alignment).
    """
    coords = np.asarray(coords, dtype=float)

    # 1) Compute original bounding box.
    min_x, min_y = coords.min(axis=0)
    max_x, max_y = coords.max(axis=0)
    width, height = max_x - min_x, max_y - min_y

    # 2) Determine uniform scale factor so the larger dimension == paper_size.
    scale = paper_size / max(width, height) if max(width, height) > 0 else 1.0

    # 3) Shift coords so min is at (0, 0), then scale.
    #    This automatically leaves min_x'=0 and min_y'=0 after scaling.
    scaled = (coords - [min_x, min_y]) * scale

    return scaled


def determine_hint_points(coords, paper_size):
    """
    Returns a list of lists for each index of <coords>.
    Each subsequent list contains points that are along the edges
    of the paper and thus can be used in conjunction with
    another polygon point to form an intersection,
    which produces the result of a polygon point that isn't along an edge.

    i.e. my_result[3] will give any hint points (x, y) for element 3 of <coords>.
    """
    n = len(coords)
    indexed_hint_points = [[] for _ in coords]

    # 1) Determine which points are not along an edge.
    edgeless = [
        i for i, (x, y) in enumerate(coords)
        if all(0.001 < d < paper_size - 0.001 for d in (x, y))
    ]

    # 2) Determine the hint points that are projected 
    #    by the line formed by a point on and edge and a point not on an edge.
    for i in edgeless:
        # 2a) Find the neighbor indices (prev and next elements).
        neighbor_indices = [
            x if x not in edgeless else -1 
            for x in [(i - 1) % n, (i + 1) % n]
        ]

        if len(neighbor_indices) > 0:
            x1, y1 = coords[i]

            # 2b) Iterate through both neighbors and see if any
            #     hint points along the edges can be made.
            for neighbor_i in neighbor_indices:
                if neighbor_i == -1:
                    # This neighbor point isn't on an edge,
                    # but the next neighbor point could be,
                    # and that point being the 1st element (not 0th)
                    # is important for labeling later, so we append a dummy.
                    indexed_hint_points[i].append((-1, -1))
                    continue

                x2, y2 = coords[neighbor_i]

                # 3) Calculate the angle pointing from the neighbor to edgeless.
                rads = math.atan2(y2 - y1, x2 - x1)
                rads -= math.pi  # flips 180°.
                while rads < 0: 
                    rads += 2 * math.pi  # forces radians within 0 and 2 pi.
                while rads >= 2 * math.pi:
                    rads -= 2 * math.pi  # forces radians within 0 and 2 pi.

                # 4) Determine which two borders are being intersected,
                #    but only if the angle isn't directly orthogonal.
                #    In that case, we don't need to do any trig,
                #    we can just add the intersecting hint point.
                if rads == 0:  # right.
                    indexed_hint_points[i].append((paper_size, y2))
                    continue  # to the next neighbor.
                elif rads == math.pi/2:  # up.
                    indexed_hint_points[i].append((x2, paper_size))
                    continue  # to the next neighbor.
                elif rads == math.pi:  # left.
                    indexed_hint_points[i].append((0, y2))
                    continue  # to the next neighbor.
                elif rads == 3*math.pi/2:  # down.
                    indexed_hint_points[i].append((x2, 0))
                    continue  # to the next neighbor.
                elif rads < math.pi/2:
                    border_x = paper_size
                    border_y = paper_size
                elif rads < math.pi:
                    border_x = 0
                    border_y = paper_size
                elif rads < 3*math.pi/2:
                    border_x = 0
                    border_y = 0
                else:
                    border_x = paper_size
                    border_y = 0

                # 5) Calculate the intercepts on the X and Y axes.
                slope = (y2 - y1) / (x2 - x1)  # 0 division won't happen.
                known_y = slope * (border_x - x1) + y1  # matches to border_x.
                known_x = (border_y - y1) / slope + x1  # matches to border_y.

                # 6) Determine which point was closest to the neighbor
                #    and use that one as the hint point.
                p = np.array([x2, y2])
                a = np.array([border_x, known_y])
                b = np.array([known_x, border_y])

                a_distance = np.linalg.norm(a - p)
                b_distance = np.linalg.norm(b - p)

                choice = a if a_distance < b_distance else b

                # 7) Add the intersection along the edge.
                indexed_hint_points[i].append(choice)

    return [[(x, y) for (x, y) in l] for l in indexed_hint_points]


def generate_paper_points(n: int, paper_size):
    """ 
    Returns a list of coords, the center point, 
    and hint points by index for each in <coords>.
    
    Params:
    - n (int): The number of sides the polygon has.
    - paper_size: The side length of the square piece of paper.
    """
    # Find the polygon rotation that has the most covered bounding box.
    best_angle = find_rotation_of_smallest_bbox(n)

    # Generate polygon coords oriented with the angle
    # that will create the smallest bounding box.
    coords = generate_polygon_coords(n, best_angle)

    # Add the center point to the geometry.
    center = np.array([0.0, 0.0])
    coords = np.vstack([coords, center])

    # Scale all the coords from [-1, 1] to [0, paper_size].
    coords = scale_to_square(coords, 13.4)
    coords = [(x, y) for (x, y) in coords]

    # Separate the center point from the coords list.
    center = coords[-1]
    coords = coords[:-1]

    # Use the coords to determine the location of any hint points.
    indexed_hint_points = determine_hint_points(coords, paper_size)

    return coords, center, indexed_hint_points