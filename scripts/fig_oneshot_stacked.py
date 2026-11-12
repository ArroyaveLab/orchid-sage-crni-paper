"""Stack the existing vector phase-diagram panels for a single-column figure."""
from __future__ import annotations

from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "figs/fig_crni_oneshot_2col.pdf"
OUTPUT = ROOT / "figs/fig_crni_oneshot_stacked.pdf"
MM = 72 / 25.4
WIDTH_MM, HEIGHT_MM = 83.0, 166.0
PANEL_WIDTH_MM, GAP_MM = 75.0, 2.0
PANEL_HEIGHT_MM = 80.4
X_MARGIN_MM = (WIDTH_MM - PANEL_WIDTH_MM) / 2
Y_MARGIN_MM = (HEIGHT_MM - 2 * PANEL_HEIGHT_MM - GAP_MM) / 2


def main() -> None:
    source = fitz.open(SOURCE)
    doc = fitz.open()
    page = doc.new_page(width=WIDTH_MM * MM, height=HEIGHT_MM * MM)

    # Source cards are 83.5 x 89.5 mm at x = 1 and 86.5 mm, y = 1 mm.
    source_cards = [
        fitz.Rect(1 * MM, 1 * MM, 84.5 * MM, 90.5 * MM),
        fitz.Rect(86.5 * MM, 1 * MM, 170 * MM, 90.5 * MM),
    ]
    for i, clip in enumerate(source_cards):
        top = (Y_MARGIN_MM + i * (PANEL_HEIGHT_MM + GAP_MM)) * MM
        target = fitz.Rect(X_MARGIN_MM * MM, top,
                           (X_MARGIN_MM + PANEL_WIDTH_MM) * MM,
                           top + PANEL_HEIGHT_MM * MM)
        page.show_pdf_page(target, source, 0, clip=clip, keep_proportion=True)

    doc.set_metadata({
        "title": "Cr-Ni one-shot phase diagrams, stacked single-column layout",
        "subject": "Vector-preserving vertical arrangement of the original panels",
    })
    doc.save(OUTPUT, garbage=4, deflate=True)
    pix = page.get_pixmap(matrix=fitz.Matrix(4, 4), alpha=False)
    pix.save(OUTPUT.with_suffix(".png"))
    doc.close()
    source.close()


if __name__ == "__main__":
    main()
