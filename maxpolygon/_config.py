"""
Filename: maxpolygon._config.py
---
Author: TravisGK
Date: 24 July 2025

Description: This file defines constants that affect
			 different settings in the program's output.

			 If you need to modify the program, 
			 this is the best place to start.
"""

# Image output settings.
ANTIALIAS = 3  # Antialias factor.
IMG_SIZE = 1800 * ANTIALIAS  # Output image size (pixels)
CUT_OUT_PADDING = 50 * ANTIALIAS  # Padding around the square (if for cut out).
SQUARE_PADDING = 425 * ANTIALIAS  # Padding around the square (pixels)
TITLE_LOCATION = "bottom"  # "top", "bottom", or None.
TITLE_PADDING_PX = 75 * ANTIALIAS

# Program settings.
MAX_NUM_SIDES = 33  # used for creating a cache of poly points, 3 to n sides.

# Measurement settings.
TO_THE_32TH = True  # only applicable for inches.
METRIC_DECIMAL_PRECISION = 1  #  only applicable for metric.
UNITS_LABEL = "cm"  #  only applicable for metric.
BRACKET_THICKNESS_PX = 90 * ANTIALIAS
PX_PADDING_FROM_EDGE = 55 * ANTIALIAS  # between brackets and paper (in px).

# Vertex render settings.
CENTER_VERT_RADIUS = 8 * ANTIALIAS
HINT_VERT_RADIUS = 9 * ANTIALIAS

# Font settings.
TITLE_FONT_SIZE = 108 * ANTIALIAS
BIG_FONT_SIZE = 68 * ANTIALIAS  # used for the vertices.
MEASURE_FONT_SIZE = 80 * ANTIALIAS

# Label settings.
LABEL_POLY_VERTS = True
LABEL_HINT_POINTS = True
LABEL_OFFSET_X = 20 * ANTIALIAS
LABEL_OFFSET_Y = 0 * ANTIALIAS
LETTERS = "ac"  # a = anticlockwise, c = clockwise
CLOCKWISE_COLOR = (0, 200, 100)  # label color for clockwise.
ANTICLOCKWISE_COLOR = (0, 100, 200)  # label color for anticlockwise.
LINE_COLOR = (137, 137, 137)
SQUARE_BORDER_COLOR = (187, 187, 187)


# Bracket settings.
LABEL_MEASUREMENTS_TO_CENTER = True
CENTER_BRACKET_LABEL_COLOR = (200, 200, 200)
CENTER_BRACKET_COLOR = (225, 225, 225)
PX_OPEN = 45 * ANTIALIAS
BRACKET_LINE_WIDTH = 9 * ANTIALIAS
