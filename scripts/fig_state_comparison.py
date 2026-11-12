"""Draw the SI summary of observed-state and calculated-assemblage agreement."""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

import style as st

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data/state_comparison.csv"
OUT = ROOT / "figs/fig_state_comparison_1col"


def main() -> None:
    st.apply()
    rows = list(csv.DictReader(CSV.open(newline="")))
    kinds = [
        ("single_phase", "Single-phase states"),
        ("tie_line", "Tie lines"),
        ("partial_tie_line", "Partial tie lines"),
        ("3-phase", "Three-phase state"),
    ]
    counts = defaultdict(lambda: [0, 0, 0])
    for row in rows:
        c = counts[row["kind"]]
        c[0] += 1
        c[1] += row["match"] == "yes"
        c[2] += row["contains_observed"] == "yes"

    W, H = 80, 160
    fig = plt.figure(figsize=(W * st.MM, H * st.MM), facecolor="white")
    canvas = fig.add_axes([0, 0, 1, 1])
    canvas.set(xlim=(0, W), ylim=(0, H))
    canvas.axis("off")
    margin, gap_y = 1, 1.2
    cw, ch = W - 2 * margin, (H - 2 * margin - 3 * gap_y) / 4
    for i, (key, title) in enumerate(kinds):
        x, y = margin, H - margin - ch - i * (ch + gap_y)
        canvas.add_patch(FancyBboxPatch((x, y), cw, ch,
                            boxstyle="round,pad=0,rounding_size=1.1",
                            facecolor="white", edgecolor=st.GREY_M, linewidth=0.5))
        n, exact, included = counts[key]
        canvas.text(x + 3, y + ch - 5, chr(97 + i), fontsize=9.5, weight="bold",
                    color=st.INK, va="baseline")
        canvas.text(x + 10, y + ch - 5, title, fontsize=8.5, weight="bold",
                    color=st.ACCENT, va="baseline")
        canvas.text(x + cw - 3, y + ch - 5, f"n = {n}", fontsize=7.5,
                    color=st.INK2, ha="right", va="baseline")
        metrics = [("Observed phases included", included, st.C_EXP),
                   ("Exact assemblage", exact, st.C_MODEL)]
        for j, (label, value, color) in enumerate(metrics):
            label_y = y + ch - 15 - j * 12
            frac = value / n if n else 0
            canvas.text(x + 3, label_y, label, fontsize=7.2, color=st.INK2, va="center")
            pct = f"{100*frac:.1f}%"
            canvas.text(x + cw - 3, label_y, f"{value}/{n}  ({pct})", fontsize=7.2,
                        color=st.INK2, ha="right", va="center")
            bx, bar_y, bar_w = x + 4, label_y - 3.5, cw - 8
            canvas.add_patch(FancyBboxPatch((bx, bar_y - 1.2), bar_w, 2.4,
                                boxstyle="round,pad=0,rounding_size=0.8",
                                facecolor=st.GREY_L, edgecolor="none"))
            if frac:
                canvas.add_patch(FancyBboxPatch((bx, bar_y - 1.2), bar_w * frac, 2.4,
                                    boxstyle="round,pad=0,rounding_size=0.8",
                                    facecolor=color, edgecolor="none"))
    fig.savefig(OUT.with_suffix(".pdf"), facecolor="white")
    fig.savefig(OUT.with_suffix(".png"), dpi=300, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
