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
    PAPER_SIZE = 8.5  # inches

    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(base_dir, "output")
    os.makedirs(img_dir, exist_ok=True)

    png_out_dir = os.path.join(img_dir, "png")
    os.makedirs(png_out_dir, exist_ok=True)

    pdf_out_dir = os.path.join(img_dir, "pdf")
    os.makedirs(pdf_out_dir, exist_ok=True)

    for use_cut_out in [False, True]:
        if use_cut_out:
            print("\n\nCreating diagrams that can be directly cut out.")
            print("-" * 60)
            subdivisions = [
                1 / 7,
            ]
        else:
            print("\n\nCreating diagrams with measurements.")
            print("-" * 60)
            subdivisions = []
        for n in range(3, 14):
            # Draw the diagram.
            img = maxpolygon.draw_diagram(
                n,
                PAPER_SIZE,
                use_inches=True,
                for_cut_out=use_cut_out,
                subdivisions=subdivisions,
            )

            # Save the diagram.
            add = "cut-out-" if use_cut_out else ""
            img_path = os.path.join(png_out_dir, f"{add}poly-{n}.png")
            img.save(img_path)
            print(f"A diagram for an {n}-sided polygon was saved under:\n\t{img_path}")

            # Save the image as a PDF.
            pdf_path = os.path.join(pdf_out_dir, f"{add}poly-{n}.pdf")
            print(f"A PDF for an {n}-sided polygon was saved under:\n\t{pdf_path}\n")
            maxpolygon.save_img_as_pdf(img_path, output_path=pdf_path)


if __name__ == "__main__":
    main()
