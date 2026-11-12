"""Make a square, vector-preserving version of the Cr--Ni assessment dashboard.

The existing dashboard is embedded without redrawing or distorting any panel.
A short title and reading note use the unused vertical space in the square canvas.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "figs/fig_crni_dashboard.pdf"
OUT = ROOT / "figs/fig_crni_dashboard_square"
MM = 72 / 25.4
SIDE_MM = 171.0
SOURCE_H_MM = 118.0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    doc = fitz.open()
    side = SIDE_MM * MM
    page = doc.new_page(width=side, height=side)
    source = fitz.open(SOURCE)
    rect = fitz.Rect(0, (SIDE_MM - SOURCE_H_MM) * MM / 2, side,
                     (SIDE_MM + SOURCE_H_MM) * MM / 2)
    page.show_pdf_page(rect, source, 0, keep_proportion=True)
    # Keep the note inside the added white space, using the ORCHID figure
    # palette and Arial-compatible Helvetica typography.
    purple = (123 / 255, 63 / 255, 160 / 255)
    gray = (77 / 255, 77 / 255, 77 / 255)
    page.insert_textbox(fitz.Rect(12 * MM, 4 * MM, (SIDE_MM - 12) * MM, 15 * MM),
                        "Assessment trajectory of the Cr-Ni fit", fontname="hebo",
                        fontsize=10, color=purple, align=fitz.TEXT_ALIGN_CENTER)
    page.insert_textbox(fitz.Rect(12 * MM, (SIDE_MM - 16) * MM,
                                  (SIDE_MM - 12) * MM, (SIDE_MM - 4) * MM),
                        "Objective values are comparable only within a fitting step; parameter changes are scaled by prior standard deviations.",
                        fontname="helv", fontsize=7, color=gray,
                        align=fitz.TEXT_ALIGN_CENTER)
    doc.set_metadata({"title": "Square Cr–Ni assessment dashboard",
                      "subject": "Vector-preserving square composition of fig_crni_dashboard.pdf"})
    doc.save(OUT.with_suffix(".pdf"), garbage=4, deflate=True)
    source.close()
    doc.close()

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    image = fitz.open(OUT.with_suffix(".pdf"))
    pix = image[0].get_pixmap(matrix=fitz.Matrix(3, 3), alpha=False)
    pix.save(OUT.with_suffix(".png"))
    image.close()
    record = (ROOT / "figs/fig_crni_dashboard_square.provenance.txt")
    record.write_text(f"Source: figs/fig_crni_dashboard.pdf\nSHA-256: {sha256(SOURCE)}\n")


if __name__ == "__main__":
    main()
