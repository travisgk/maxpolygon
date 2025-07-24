#!/usr/bin/env python3
import os

"""
MaxPolygon
---
This main script generates a diagram 
for every 3-sided to 13-sided perfect polygon
that will be inscribed as large as possible inside a square.
"""

import maxpolygon


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    PAPER_SIZE = 8.5  # inches
    for n in range(3, 14):
        # Generate the polygon coords and hint points for each coord.
        coords, center, indexed_hint_points = maxpolygon.generate_paper_points(
            n, PAPER_SIZE
        )

        # Draw the diagram.
        img = maxpolygon.draw_diagram(
            coords,
            center,
            indexed_hint_points,
            PAPER_SIZE,
            use_inches=True,
        )

        # Save the diagram.
        img_dir = os.path.join(base_dir, "output")
        os.makedirs(img_dir, exist_ok=True)
        img_path = os.path.join(img_dir, f"poly-{n}.png")
        img.save(img_path)
        print(f"A diagram for an {n}-sided polygon was saved under {img_path}.")


if __name__ == "__main__":
    main()
