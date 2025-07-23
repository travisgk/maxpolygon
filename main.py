#!/usr/bin/env python3
import os

"""
MaxPolygon
"""

import maxpolygon


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    PAPER_SIZE = 13.4
    for n in range(3, 14):
        coords, center, indexed_hint_points = maxpolygon.generate_paper_points(
            n, PAPER_SIZE
        )
        img = maxpolygon.draw_diagram(coords, center, indexed_hint_points, PAPER_SIZE)
        img_dir = os.path.join(base_dir, "output")
        os.makedirs(img_dir, exist_ok=True)
        img_path = os.path.join(img_dir, f"poly-{n}.png")
        img.save(img_path)
        print(f"A diagram for an {n}-sided polygon was saved under {img_path}.")


if __name__ == "__main__":
    main()
