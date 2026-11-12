"""Single-column version of fig_oneshot_2col_orchid: the same two panels, stacked (a above b), same style and data."""
import matplotlib.pyplot as plt

import style as st
from crni_fig_common import card, check_layout, legend_below, mm_axes, mm_canvas
from fig_oneshot_2col_orchid import ROOT, draw_panel, legend_handles

OUT = ROOT / "figs/fig_crni_oneshot_1col_orchid"


def main() -> None:
    st.apply()
    card_h = 83.0
    top, gap = 1.0, 2.0
    width_mm, height_mm = st.W1 / st.MM, 2 * card_h + gap + 2.0
    fig, canvas = mm_canvas(width_mm, height_mm)
    card_w = width_mm - 2.0
    axis_h = card_h - 20.5 - 8.0
    titles = ("One-shot", "One-shot + liquid excess entropy")

    for i, variant in enumerate(("oneshot", "oneshot_Sex")):
        y = 1.0 + (1 - i) * (card_h + gap)
        card(canvas, 1.0, y, card_w, card_h, "ab"[i], titles[i])
        ax = mm_axes(fig, 1.0 + 14.0, y + 20.5, card_w - 17.0, axis_h, width_mm, height_mm)
        draw_panel(ax, variant, axis_h)
        handles, labels = legend_handles(variant)
        legend_below(fig, handles, labels, 1.0 + 3.0, y + 12.0, width_mm, height_mm, ncol=2, colsp=1.5)

    fig.savefig(OUT.with_suffix(".pdf"), facecolor="white")
    fig.savefig(OUT.with_suffix(".png"), dpi=600, facecolor="white")
    problems = check_layout(fig, OUT.stem)
    plt.close(fig)
    if problems:
        raise SystemExit("Layout check failed: " + "; ".join(problems))


if __name__ == "__main__":
    main()
