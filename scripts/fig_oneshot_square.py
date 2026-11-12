"""Add a square canvas around the two-panel Cr--Ni one-shot phase diagram.

The original vector panels are centered unchanged; the added canvas is white
space only, so phase boundaries, labels, and panel geometry are preserved.
"""
from __future__ import annotations

from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "figs/fig_crni_oneshot_2col.pdf"
OUT = ROOT / "figs/fig_crni_oneshot_square.pdf"
MM = 72 / 25.4
SIDE_MM = 171.0


def main() -> None:
    source = fitz.open(SOURCE)
    source_page = source[0]
    side = SIDE_MM * MM
    doc = fitz.open()
    page = doc.new_page(width=side, height=side)
    page.show_pdf_page(fitz.Rect(0, 0, side, side), source, 0,
                       keep_proportion=True, overlay=True)
    doc.set_metadata({
        "title": "Square Cr--Ni one-shot phase diagram",
        "subject": "Original two-panel vector figure centered on a square canvas",
    })
    doc.save(OUT, garbage=4, deflate=True)
    doc.close()
    source.close()


if __name__ == "__main__":
    main()
