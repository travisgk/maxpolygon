"""
MaxPolygon

Author: TravisGK
Date: 30 June 2025
---
This script determines the points of the largest possible perfect polygon
on a square sheet of paper, then draws and saves a diagram.

A graphical representation is saved under "poly.png",
while a more precise text representation is saved under "poly.txt".

There are the expected points of the polygon itself 
that are calculated and rendered, but there are also
additional points along the edges that are provided,
which can be used to draw lines that will help plot
the other points of the polygon that do not lie on the paper's edge.

"""

import math
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Constants: change these if you like

N_SIDES = 11  # Number of polygon sides
SQUARE_SIZE = 13.4  # Size of the square (inches)
USING_INCHES = True

IMG_SIZE = 1200  # Output image size (pixels)
PADDING = 150  # Padding around the square (pixels)

MEASURE_TO_CLOSEST_SIDE = True
SHOW_LABELS = True  # Toggle vertex numbering on/off
SHOW_CENTER = True  # Toggle center point display on/off
SHOW_HINTS = True

LETTERS = "ac" # a = anticlockwise, c = clockwise
CLOCKWISE_COLOR = (0, 200, 100)
ANTICLOCKWISE_COLOR = (0, 100, 200)
LINE_COLOR = (137, 137, 137)


def decimal_inches_to_unicode_fraction(inches):
    # Unicode single-character fractions for common fractions
    unicode_fractions = {
        0: "",
        1/16: "¹⁄₁₆",  # no single char, so superscript+subscript notation
        1/8: "⅛",
        3/16: "³⁄₁₆",
        1/4: "¼",
        5/16: "⁵⁄₁₆",
        3/8: "⅜",
        7/16: "⁷⁄₁₆",
        1/2: "½",
        9/16: "⁹⁄₁₆",
        5/8: "⅝",
        11/16: "¹¹⁄₁₆",
        3/4: "¾",
        13/16: "¹³⁄₁₆",
        7/8: "⅞",
        15/16: "¹⁵⁄₁₆"
    }

    # Round to nearest 1/16
    whole = int(inches)
    frac = inches - whole
    sixteenths = round(frac * 16) / 16

    # Fix rounding overflow (e.g. 0.9999 rounds to 1)
    if sixteenths >= 1:
        whole += 1
        sixteenths = 0

    # Try to get the Unicode fraction or fallback
    fraction_str = unicode_fractions.get(sixteenths, "")

    # Build result string
    if whole == 0 and fraction_str != "":
        return fraction_str  # just fraction, e.g. ½
    elif fraction_str == "":
        return str(whole)     # whole number only
    else:
        return f"{whole}{fraction_str}"  # whole + fraction

def unit_polygon_coords(n, rotation=0.0):
    angles = np.linspace(0, 2*np.pi, n, endpoint=False) + rotation
    return np.column_stack((np.cos(angles), np.sin(angles)))

def bounding_box_size(coords):
    min_x, max_x = coords[:,0].min(), coords[:,0].max()
    min_y, max_y = coords[:,1].min(), coords[:,1].max()
    return max_x - min_x, max_y - min_y, min_x, min_y

def main():
    # 1) Find optimal rotation to minimize max bounding-box dimension
    angle_candidates = np.linspace(0, np.pi/N_SIDES, 3601)
    best = None

    for angle in angle_candidates:
        coords = unit_polygon_coords(N_SIDES, rotation=angle)
        w, h, min_x, min_y = bounding_box_size(coords)
        max_dim = max(w, h)
        if best is None or max_dim < best[0]:
            best = (max_dim, angle, min_x, min_y)

    min_max_dim, best_angle, umin_x, umin_y = best

    # 2) Compute scale factor and generate final, shifted coords (in inches)
    scale = SQUARE_SIZE / min_max_dim
    raw = unit_polygon_coords(N_SIDES, rotation=best_angle) * scale
    shift_x = -umin_x * scale
    shift_y = -umin_y * scale
    final_coords = raw + np.array([shift_x, shift_y])

    # Compute centroid of polygon in inches
    centroid = final_coords.mean(axis=0)

    # Determine which points are not along an edge
    edgeless_indices = [i for i, (x, y) in enumerate(final_coords) if all(0.001 < d < SQUARE_SIZE - 0.001 for d in (x, y))]
    indexed_hint_points = [[] for _ in final_coords]

    # Determine the hint points that are projected 
    # by the line formed by a point on and edge and a point not on an edge
    for i in edgeless_indices:
        neighbor_indices = [x if x not in edgeless_indices else -1 for x in [(i - 1) % N_SIDES, (i + 1) % N_SIDES]]
        if len(neighbor_indices) > 0:
            x1, y1 = final_coords[i]

            for neighbor_index in neighbor_indices:
                if neighbor_index == -1:
                    indexed_hint_points[i].append((-1, -1))
                    continue

                x2, y2 = final_coords[neighbor_index]
                
                # Calculate the angle pointing from the neighbor to the edgeless
                rads = math.atan2(y2 - y1, x2 - x1)
                rads -= math.pi  # flips 180°.
                while rads < 0: 
                    rads += 2 * math.pi   # forces the radians within 0 and 2 pi.
                while rads >= 2 * math.pi:
                    rads -= 2 * math.pi  # forces the radians within 0 and 2 pi.

                # Determine the known coord and which coord is being looked for
                if rads < math.pi/4 or rads >= 7*math.pi/4:  # hits right.
                    known_x = SQUARE_SIZE
                    known_y = None
                elif rads < 3*math.pi/4:  # hits top.
                    known_x = None
                    known_y = SQUARE_SIZE
                elif rads < 5*math.pi/4:  # hits left.
                    known_x = 0
                    known_y = None
                elif rads < 7*math.pi/4:  # hits bottom.
                    known_x = None
                    known_y = 0

                # Calculate the intercept
                slope = (y2 - y1) / (x2 - x1)  # 0 division shouldn't occur logically.
                if known_y is None:
                    known_y = slope * (known_x - x1) + y1  # point-slope form
                elif known_x is None:
                    known_x = (known_y - y1) / slope + x1


                indexed_hint_points[i].append((known_x, known_y))


    # 3) Write the coordinates to file
    out_str = ""
    out_str += f"Regular {N_SIDES}-gon optimized to fit a {SQUARE_SIZE:.1f}×{SQUARE_SIZE:.1f} square\n"
    out_str += f"Optimal rotation: {best_angle:.2f} rad\n"
    out_str += f"Coordinates (x, y) in inches within [0, {SQUARE_SIZE:.1f}]:\n"
    for i, (x, y) in enumerate(final_coords, start=1):
        out_str += f"\n\tPoint {i:>2}: ({x:.2f}, {y:.2f})\n"
        for j, (cx, cy) in enumerate(indexed_hint_points[i - 1]):
            if cx != -1:
                x = -1 if j == 0 else 1
                out_str += f"\t\tPoint {(i - 1 + x) % N_SIDES + 1:>2}{LETTERS[j]}: ({cx:.2f}, {cy:.2f})\n"

    out_str += f"\nCenter point: ({centroid[0]:.2f}, {centroid[1]:.2f})\n"

    x1, y1 = final_coords[0]
    x2, y2 = final_coords[1]
    distance = math.hypot(x2 - x1, y2 - y1)
    out_str += f"\nSide Distance: {distance:.2f}\n"

    with open("poly.txt", "w") as file:
        file.write(out_str)

    # 4) Convert inch-coords to pixel-coords
    def to_pixel(val, invert: bool=False):
        if val == -1:
            return -9 ** 5
        result = (val / SQUARE_SIZE) 
        if invert:
            result = 1 - result
        return result * (IMG_SIZE - 2 * PADDING) + PADDING

    def from_pixel(val, invert: bool=False):
        if val < -1000:
            return -1

        val -= PADDING
        val /= (IMG_SIZE - 2 * PADDING)
        if invert:
            val = 1 - val

        result = val * SQUARE_SIZE
        return result


    pixel_coords = [(to_pixel(x), to_pixel(y, invert=True)) for x, y in final_coords]
    hint_pixel_coords = [[(to_pixel(x), to_pixel(y, invert=True)) for x, y in hints] for hints in indexed_hint_points]
    pixel_centroid = (to_pixel(centroid[0]), to_pixel(centroid[1], invert=True))

    # 5) Create and draw image.
    img = Image.new("RGB", (IMG_SIZE, IMG_SIZE), "white")
    draw = ImageDraw.Draw(img)
    current_dir = os.path.dirname(__file__)
    font_path = os.path.join(current_dir, "font.otf")
    big_font = ImageFont.truetype(font_path, size=41)  # Change size here
    font = ImageFont.truetype(font_path, size=38)  # Change size here

    # Draw square border.
    draw.rectangle(
        [PADDING, PADDING, IMG_SIZE - PADDING, IMG_SIZE - PADDING],
        outline=(187, 187, 187),
        width=4
    )

    # Draw polygon.
    draw.polygon(pixel_coords, outline=LINE_COLOR, width=4)

    # Draw vertex labels.
    if SHOW_LABELS:
        for idx, (cx, cy) in enumerate(pixel_coords):
            draw.text((cx + 3, cy - 10), str(idx + 1), fill="black", font=big_font)
            inches_x = from_pixel(cx)
            inches_y = from_pixel(cy, invert=True)

            if MEASURE_TO_CLOSEST_SIDE:
                if inches_x > SQUARE_SIZE / 2:
                    inches_x = SQUARE_SIZE - inches_x
                if inches_y > SQUARE_SIZE / 2:
                    inches_y = SQUARE_SIZE - inches_y

            if USING_INCHES:
                x_str = decimal_inches_to_unicode_fraction(inches_x) + '"'
                y_str = decimal_inches_to_unicode_fraction(inches_y) + '"'
            else:
                x_str = f"{inches_x:.1f}"
                y_str = f"{inches_y:.1f}"

            if all(0.001 <= z <= SQUARE_SIZE - 0.001 for z in [inches_x, inches_y]):
                display_str = f"({x_str}, {y_str})"
            else:
                if inches_x < 0.001 or inches_x > SQUARE_SIZE - 0.001:
                    important_dim = inches_y
                else:
                    important_dim = inches_x
                if USING_INCHES:
                    display_str = "(" + decimal_inches_to_unicode_fraction(important_dim) + '")'
                else:
                    display_str = f"({important_dim:.1f})"

            draw.text((cx - 35, cy + 40), display_str, fill="black", font=font)


    # Draw center point.
    if SHOW_CENTER:
        r = 8  # radius of center marker
        cx, cy = pixel_centroid
        draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=LINE_COLOR)

        inches_x = from_pixel(cx)
        inches_y = from_pixel(cy, invert=True)

        if MEASURE_TO_CLOSEST_SIDE:
            if inches_x > SQUARE_SIZE / 2:
                inches_x = SQUARE_SIZE - inches_x
            if inches_y > SQUARE_SIZE / 2:
                inches_y = SQUARE_SIZE - inches_y

        if USING_INCHES:
            x_str = decimal_inches_to_unicode_fraction(inches_x) + '"'
            y_str = decimal_inches_to_unicode_fraction(inches_y) + '"'
        else:
            x_str = f"{inches_x:.1f}"
            y_str = f"{inches_y:.1f}"

        draw.text((cx - 35, cy + 40), f"({x_str}, {y_str})", fill=LINE_COLOR, font=font)

    # Draw vertex labels for hint points.
    if SHOW_HINTS:
        r = 8
        for idx, points in enumerate(hint_pixel_coords):
            for p_index, (cx, cy) in enumerate(points):
                if cx == -1:
                    continue

                fill_color = ANTICLOCKWISE_COLOR if p_index == 0 else CLOCKWISE_COLOR
                draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=fill_color)
                if SHOW_LABELS:
                    x = -1 if p_index == 0 else 1
                    letter_str = f"{(idx + x) % N_SIDES + 1}{LETTERS[p_index]}"
                    inches_x = from_pixel(cx)
                    inches_y = from_pixel(cy, invert=True)

                    if MEASURE_TO_CLOSEST_SIDE:
                        if inches_x > SQUARE_SIZE / 2:
                            inches_x = SQUARE_SIZE - inches_x
                        if inches_y > SQUARE_SIZE / 2:
                            inches_y = SQUARE_SIZE - inches_y

                    if USING_INCHES:
                        x_str = decimal_inches_to_unicode_fraction(inches_x) + '"'
                        y_str = decimal_inches_to_unicode_fraction(inches_y) + '"'
                    else:
                        x_str = f"{inches_x:.1f}"
                        y_str = f"{inches_y:.1f}"

                    draw.text((cx + 5, cy + 5), letter_str, fill=fill_color, font=big_font)

                    if all(0.001 <= z <= SQUARE_SIZE - 0.001 for z in [inches_x, inches_y]):
                        display_str = f"({x_str}, {y_str})"
                    else:
                        if inches_x < 0.001 or inches_x > SQUARE_SIZE - 0.001:
                            important_dim = inches_y
                        else:
                            important_dim = inches_x
                        if USING_INCHES:
                            display_str = "(" + decimal_inches_to_unicode_fraction(important_dim) + '")'
                        else:
                            display_str = f"({important_dim:.1f})"

                    draw.text((cx - 35, cy + 40), display_str, fill=fill_color, font=font)

    if USING_INCHES:
        paper_size_str = decimal_inches_to_unicode_fraction(SQUARE_SIZE) + '"'
    else:
        paper_size_str = f"{SQUARE_SIZE:.1f}"
    draw.text((IMG_SIZE // 2 - 120, 10), f"Paper Size: {paper_size_str}", fill=LINE_COLOR, font=font)
    draw.text((IMG_SIZE // 2 - 60, 60), f"{N_SIDES} sides", fill=LINE_COLOR, font=font)

    # 6) Display using PIL's show()
    img.save(f"poly-{N_SIDES}.png")
    #img.show()

if __name__ == "__main__":
    main()