"""Extract dashboard panels as separate square, vector-preserving figures."""
from __future__ import annotations

from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "figs/fig_crni_dashboard.pdf"
MM = 72 / 25.4
SIDE_MM = 83.0
OUTPUTS = {
    # Source card locations in the 171 x 118 mm dashboard PDF.
    "fig_crni_dashboard_panel_a": fitz.Rect(1 * MM, 1 * MM, 43 * MM, 57 * MM),
    "fig_crni_dashboard_panel_b": fitz.Rect(45 * MM, 1 * MM, 98 * MM, 57 * MM),
    "fig_crni_dashboard_panel_c": fitz.Rect(1 * MM, 59 * MM, 98 * MM, 117 * MM),
    # Keep the PCA axes, annotations, and axis labels; the legend moves to the
    # figure caption so the plotted data can remain full size on a square page.
    "fig_crni_dashboard_panel_d": fitz.Rect(99.5 * MM, 7 * MM, 170 * MM, 97 * MM),
}


def main() -> None:
    source = fitz.open(SOURCE)
    for name, clip in OUTPUTS.items():
        doc = fitz.open()
        side = SIDE_MM * MM
        page = doc.new_page(width=side, height=side)
        page.show_pdf_page(fitz.Rect(0, 0, side, side), source, 0,
                           clip=clip, keep_proportion=True)
        doc.set_metadata({
            "title": name.replace("_", " "),
            "subject": "Vector-preserving square panel from the Cr-Ni assessment dashboard",
        })
        output = ROOT / "figs" / f"{name}.pdf"
        doc.save(output, garbage=4, deflate=True)
        doc[0].get_pixmap(matrix=fitz.Matrix(4, 4), alpha=False).save(
            output.with_suffix(".png"))
        doc.close()
    source.close()


if __name__ == "__main__":
    main()
