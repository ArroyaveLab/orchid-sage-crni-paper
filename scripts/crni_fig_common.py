"""Shared helpers for Figs. 2, 4, 5 and 6 of the Cr-Ni paper: hero-style cards, computed-diagram drawing, file hashes.

No logo or badge is drawn (Digital Discovery: no logos, trademarks or brand marks in figures; 7 Nov 2026). The ORCHID
badge of orchid-brand design-system/figures.md was removed from every figure; colours and evidence classes are kept.
The paper fit uses records not yet released (v2026.10.1 pending), so their release tag is "provisional".
"""
import hashlib
from pathlib import Path

import numpy as np

import paths  # noqa: E402  (locations outside the repository: env or local/config.json)
import style as st

RUNS, SAGE_REPO = paths.loc("runs_root"), paths.loc("orchid_sage")
RELEASE_TAG = "provisional"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tilde(p):
    return paths.tilde(p)


# ---------------------------------------------------------------- hero-style panel cards (ORCHID paper fig_coverage_states)
# Every panel sits in a rounded card (fig-box-round 1 mm, 0.5 pt fig-grey-m frame, white or light fill); the bold 8 pt panel
# letter at the top-left and, on the same baseline, a short heading in bold brand-orchid; legends below the axes inside the
# card; an optional one-line summary in fig-ink2 at the bottom. Coordinates are mm on a canvas axes spanning the figure.
CARD_EC, CARD_LW, CARD_R = st.GREY_M, 0.5, 1.0


def mm_canvas(W, H):
    """Figure W x H mm with a full-size, axis-free underlay axes in mm (cards, schematics); data axes added later sit above."""
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(W * st.MM, H * st.MM))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
    return fig, ax


def mm_axes(fig, x, y, w, h, W, H):
    a = fig.add_axes([x / W, y / H, w / W, h / H])
    a.patch.set_alpha(0)
    return a


def card(ax, x, y, w, h, letter=None, title=None, size=7.0, fc="white", ec=None, lw=None, z=0.5, inset=2.0, base=4.0,
         gap=3.9, title_color=None):
    """Hero card on the mm canvas `ax`; returns the baseline y of the heading."""
    from matplotlib.patches import FancyBboxPatch
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={CARD_R}", fc=fc,
                                ec=CARD_EC if ec is None else ec, lw=CARD_LW if lw is None else lw, zorder=z))
    yb = y + h - base
    if letter:
        ax.text(x + inset, yb, letter, fontsize=8, fontweight="bold", color=st.INK, va="baseline", ha="left", zorder=9)
    if title:
        ax.text(x + inset + (gap if letter else 0), yb, title, fontsize=size, fontweight="bold",
                color=title_color or st.ACCENT, va="baseline", ha="left", zorder=9)
    return yb


def card_note(ax, x, y, s, size=6.0, ha="left"):
    """One-line summary in fig-ink2 at the bottom of a card (baseline at y)."""
    return ax.text(x, y, s, fontsize=size, color=st.INK2, va="baseline", ha=ha, zorder=9)


def legend_below(fig, handles, labels, x, y, W, H, ncol=2, size=6.5, colsp=1.2):
    """Compact legend with its upper-left corner at (x, y) mm, below the axes inside the card."""
    return fig.legend(handles, labels, loc="upper left", bbox_to_anchor=(x / W, y / H), bbox_transform=fig.transFigure,
                      ncol=ncol, fontsize=size, frameon=False, handlelength=1.4, handletextpad=.4, columnspacing=colsp,
                      labelspacing=.3, borderaxespad=0, borderpad=0)


def draw_diagram(ax, step, color, lw=0.8, z=3, ls="-", alpha=1.0):
    """Computed boundaries of one step (tracks of data/crni_paper_fit_figs.json), CrNi2 line and invariant lines."""
    for key, pts in step["tracks"].items():
        a = np.asarray(sorted(pts))
        brk = np.where((np.diff(a[:, 0]) > 2.5) | (np.abs(np.diff(a[:, 1])) > 0.04))[0] + 1
        for seg in np.split(a, brk):
            if len(seg) > 1:
                ax.plot(seg[:, 1], seg[:, 0], color=color, lw=lw, zorder=z, ls=ls, alpha=alpha, solid_capstyle="butt")
    c2 = np.asarray(step["crni2"])
    if len(c2):
        ax.plot([c2[0, 1]] * 2, [c2[:, 0].min() - 2, c2[:, 0].max()], color=color, lw=lw, zorder=z, ls=ls, alpha=alpha)
    for k, t in (("liquid_min_line", "T_liquid_min"), ("crni2_top_line", "T_CrNi2_max")):
        if step.get(k):
            ax.plot(step[k], [step[t]] * 2, color=color, lw=lw, zorder=z, ls=ls, alpha=alpha)


def check_layout(fig, name, min_pt=5.0, ignore_pairs=()):
    """Print every text below min_pt (mathtext sub/superscripts counted at style.MATHTEXT_SHRINK), every text that leaves the
    canvas and every pair of texts whose boxes overlap (both drawn, non-empty). Returns the list of problems."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    fb = fig.bbox
    hidden = set()          # tick labels of ticks outside the view interval are not drawn
    for a_ in fig.axes:
        for axis in (a_.xaxis, a_.yaxis):
            drawn = {id(x) for tk in axis._update_ticks() for x in (tk.label1, tk.label2)} if a_.axison else set()
            hidden |= {id(x) for tk in axis.get_major_ticks() + axis.get_minor_ticks() for x in (tk.label1, tk.label2)
                       if id(x) not in drawn}
    T = [t for t in fig.findobj(matplotlib_text_Text) if t.get_visible() and t.get_text().strip() and t.figure is fig
         and id(t) not in hidden]
    probs = []
    boxes = []
    for t in T:
        s = t.get_text()
        eff = t.get_fontsize() * (st.MATHTEXT_SHRINK if ("_" in s or "^" in s) and "$" in s else 1.0)
        if eff < min_pt - 1e-6:
            probs.append(f"small {eff:.2f} pt: {s!r}")
        b = t.get_window_extent(r)
        if b.width < 1 or b.height < 1:
            continue
        if b.x0 < fb.x0 - .5 or b.y0 < fb.y0 - .5 or b.x1 > fb.x1 + .5 or b.y1 > fb.y1 + .5:
            probs.append(f"clipped: {s!r}")
        boxes.append((s, b.shrunk(.97, .80)))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            (s1, b1), (s2, b2) = boxes[i], boxes[j]
            if b1.overlaps(b2) and (s1, s2) not in ignore_pairs and (s2, s1) not in ignore_pairs:
                probs.append(f"overlap: {s1!r} / {s2!r}")
    print(f"[{name}] layout check: {len(probs)} problem(s)")
    for p in probs:
        print("   ", p)
    return probs


from matplotlib.text import Text as matplotlib_text_Text  # noqa: E402
