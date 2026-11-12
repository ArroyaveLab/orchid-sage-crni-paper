"""Restyle the Cr--Ni one-shot comparison in the manuscript's figure palette.

Phase-boundary coordinates and ORCHID observations are read from the recorded
figure data. Only curve and panel styling changes; no thermodynamic line is
recomputed or moved.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

import style as st
from crni_fig_common import card, check_layout, legend_below, mm_axes, mm_canvas

ROOT = Path(__file__).resolve().parents[1]
LINES = json.loads((ROOT / "data/crni_oneshot_lines.json").read_text())["lines"]
OVERLAY = json.loads((ROOT / "figs/fig_crni_oneshot_overlay_ids.json").read_text())
PTS = list(OVERLAY["assessed"].values())
TEMPS = sorted(OVERLAY["temperatures"].values(), key=lambda q: -q["T"])
TMIN, TMAX = 600, 2400
OUT = ROOT / "figs/fig_crni_oneshot_2col_orchid"


def draw_panel(ax, variant: str, axis_height_mm: float) -> None:
    """Draw the original boundary samples with the paper's semantic colors."""
    for x, y in LINES["ref"]:
        ax.plot(x, y, color=st.GREY_M, lw=0.6, zorder=1)
    if variant == "oneshot":
        for x, y in LINES["oneshot"]:
            ax.plot(x, y, color=st.C_MODEL, lw=0.9, zorder=3)
    else:
        for x, y in LINES["oneshot"]:
            ax.plot(x, y, color=st.C_MODEL, lw=0.55, ls=(0, (3, 2)), zorder=2)
        for x, y in LINES["oneshot_Sex"]:
            ax.plot(x, y, color=st.ACCENT, lw=0.9, zorder=3)

    for k, point in enumerate(PTS, 1):
        marker = "D" if point["kind"] == "two_phase" else "o"
        ax.plot(point["x_Ni"], point["T"], marker, ms=3,
                mfc=st.C_ASSESSED, mec="white", mew=0.3, zorder=6)
        ax.annotate(f"A{k}", (point["x_Ni"], point["T"]),
                    xytext=(2.5, 1.5), textcoords="offset points",
                    fontsize=5, color=st.C_ASSESSED)

    # Printed transition temperatures remain at their recorded values; only
    # their labels are staggered to retain the original legibility.
    gap = 2.1 * (TMAX - TMIN) / axis_height_mm
    positions = []
    for item in TEMPS:
        y = item["T"] if not positions or positions[-1] - item["T"] >= gap else positions[-1] - gap
        positions.append(y)
    floor = TMIN + gap / 2
    for i in range(len(positions) - 1, -1, -1):
        lower = floor if i == len(positions) - 1 else positions[i + 1] + gap
        if positions[i] < lower:
            positions[i] = lower
    for k, (item, y) in enumerate(zip(TEMPS, positions), 1):
        color = st.EVC.get(item["evidence_class"], st.C_UNSPEC)
        ax.plot([0.965, 1.0], [item["T"], item["T"]], color=color,
                lw=1.0, zorder=7, solid_capstyle="butt")
        ax.text(0.925, y, f"T{k}", fontsize=5, color=color,
                ha="right", va="center", zorder=7)
        ax.plot([0.928, 0.963], [y, item["T"]], color=color,
                lw=0.3, zorder=7)

    ax.set_xlim(0, 1)
    ax.set_ylim(TMIN, TMAX)
    ax.set_yticks(range(600, 2401, 300))
    ax.set_xlabel(r"$x_{\mathrm{Ni}}$")
    ax.set_ylabel("Temperature (K)")


def legend_handles(variant: str):
    handles = [Line2D([], [], color=st.GREY_M, lw=0.6)]
    labels = ["SGTE (Lee 1992)"]
    if variant == "oneshot":
        handles.append(Line2D([], [], color=st.C_MODEL, lw=0.9))
        labels.append("one-shot")
    else:
        handles.extend([
            Line2D([], [], color=st.ACCENT, lw=0.9),
            Line2D([], [], color=st.C_MODEL, lw=0.55, ls=(0, (3, 2))),
        ])
        labels.extend(["+ liquid $S_{ex}$", "one-shot"])
    handles.extend([
        Line2D([], [], ls="none", marker="D", ms=3, mfc=st.C_ASSESSED, mec="white", mew=0.3),
        Line2D([], [], color=st.C_EXP, lw=1.0),
        Line2D([], [], color=st.C_MODEL, lw=1.0),
    ])
    labels.extend(["ORCHID assessed (A1–A7)", "ORCHID experimental T", "ORCHID model T"])
    return handles, labels


def main() -> None:
    st.apply()
    width_mm, height_mm = st.W2 / st.MM, 91.5
    fig, canvas = mm_canvas(width_mm, height_mm)
    top, gap = 1.0, 2.0
    card_w = (width_mm - 2.0 - gap) / 2
    card_h = height_mm - top - 1.0
    axis_h = card_h - 20.5 - 8.0
    titles = ("One-shot", "One-shot + liquid excess entropy")

    for i, variant in enumerate(("oneshot", "oneshot_Sex")):
        x = 1.0 + i * (card_w + gap)
        card(canvas, x, 1.0, card_w, card_h, "ab"[i], titles[i])
        ax = mm_axes(fig, x + 14.0, 1.0 + 20.5,
                     card_w - 17.0, axis_h, width_mm, height_mm)
        draw_panel(ax, variant, axis_h)
        handles, labels = legend_handles(variant)
        legend_below(fig, handles, labels, x + 3.0, 1.0 + 12.0,
                     width_mm, height_mm, ncol=2, colsp=1.5)

    fig.savefig(OUT.with_suffix(".pdf"), facecolor="white")
    fig.savefig(OUT.with_suffix(".png"), dpi=600, facecolor="white")
    problems = check_layout(fig, OUT.stem)
    plt.close(fig)
    if problems:
        raise SystemExit("Layout check failed: " + "; ".join(problems))


if __name__ == "__main__":
    main()
