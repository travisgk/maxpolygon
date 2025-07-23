"""
Filename: maxpolygon.math.sublengths.py
---
Author: TravisGK
Date: 20 July 2025

Description: This file contains a function which will take a list of coords
             and a list of sublists of hint points.

             The indexed_hint_points is a list of lists for each index of <coords>.
             Each subsequent list contains points that are along the edges
             of the paper and thus can be used in conjunction with
             another polygon point to form an intersection,
             which produces the result of a polygon point that isn't along an edge.

             Some hint coords are (-1, -1), in this case, these are ignored;
             these are present because they offset the next coord in the list
             so that the program correctly recognizes the next coord as being
             a "clockwise" hint point rather than an "anticlockwise" one.
"""

def determine_sublengths(
    coords: list,
    indexed_hint_points: list,
    paper_size,
    invert_y: bool,
):
    """
    Params:
        - coords (list): a list of (x, y) coords in units.
        - indexed_hint_points (list): a list of lists.
        - paper_size (number): the length (in units) of the square's side.
        - invert_y (bool): inverts the Y coordinates if true.

    Returns four lists of sublengths (in units) for each side in this order:
        - right
        - top
        - left
        - bottom
    """
    # 1) Initialize the four lists that will hold the 1D coords
    #    where each edge has a vertex.
    right_y_breaks = []  # Y-coords where the right edge is divided. high X.
    top_x_breaks = []  # X-coords where the top edge is divided. low Y.
    left_y_breaks = []  # Y-coords where the left edge is divided. low X.
    bottom_x_breaks = []  # X-coords where the bottom edge is divided. high Y.
    
    # 2a) Define a helper function to sort into those four lists.
    def sort_vert_to_edge(x, y):
        """
        Takes the point (x, y) and sorts it 
        under the appropriate list (if any).
        """
        D = 0.01  # accuracy to be considered on an edge.

        def on_vert_edge(x) -> bool:
            return -D < x < D or paper_size - D < x < paper_size + D

        def on_horiz_edge(y) -> bool:
            return -D < y < D or paper_size - D < y < paper_size + D

        if -D < x < D:  # on the left edge.
            if not on_horiz_edge(y):  # not in a corner
                left_y_breaks.append(y)
        elif -D < y < D:  # on the top edge.
            if not on_vert_edge(x):  # not in a corner
                top_x_breaks.append(x)
        if paper_size - D < x < paper_size + D:  # on the right edge.
            if not on_horiz_edge(y):  # not in a corner.
                right_y_breaks.append(y)
        elif paper_size - D < y < paper_size + D:  # on the bottom edge.
            if not on_vert_edge(x):  # not in a corner
                bottom_x_breaks.append(x)

    # 2b) Find all the vertices that divide each of the four edges 
    #     using the function.
    for x, y in coords:
        sort_vert_to_edge(x, y)

    for hints in indexed_hint_points:
        for x, y in hints:
            sort_vert_to_edge(x, y)


    # 3) Edge-dividing points are inverted to match the output graphic.
    if invert_y:
        placeholder = top_x_breaks
        top_x_breaks = bottom_x_breaks
        bottom_x_breaks = placeholder
        left_y_breaks = [paper_size - y for y in left_y_breaks]
        right_y_breaks = [paper_size - y for y in right_y_breaks]

    # 4) Sort the coordinates.
    right_y_breaks.sort()
    top_x_breaks.sort()
    left_y_breaks.sort()
    bottom_x_breaks.sort()

    # 5) Now the distances between the dividing points are calculated
    #    using a helper function.
    def calc_sublengths(breaks: list) -> list:
        """ 
        Returns a list of segment lengths that the side is divided into.
        """
        if len(breaks) == 0:
            return []

        sublengths = []
        last = 0
        for current in breaks:
            sublengths.append(current - last)
            last = current
        sublengths.append(paper_size - last)

        return sublengths

    right_sublengths = calc_sublengths(right_y_breaks)
    top_sublengths = calc_sublengths(top_x_breaks)
    left_sublengths = calc_sublengths(left_y_breaks)
    bottom_sublengths = calc_sublengths(bottom_x_breaks)

    return right_sublengths, top_sublengths, left_sublengths, bottom_sublengths