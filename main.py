#!/usr/bin/env python3

"""
MaxPolygon
"""

import maxpolygon

def main():
    PAPER_SIZE = 13.4
    for n in range(3, 14):
        coords, center, indexed_hint_points = maxpolygon.generate_paper_points(n, PAPER_SIZE)
        img = maxpolygon.draw_diagram(coords, center, indexed_hint_points, PAPER_SIZE)
        img.save(f"poly-{n}.png")

if __name__ == "__main__":
    main()