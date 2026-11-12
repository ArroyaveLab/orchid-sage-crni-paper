#!/usr/bin/env python3
"""Appendix A figure: pair entropy of chemical mixing in the liquid (methods figure, computed benchmarks only).

a  schematic: species labels on a 2-D cartoon of a liquid neighbour graph (two species, neutral fills), one bond i-j
   highlighted; the quantities x_i (site fraction), y_ij (bond fraction), w_i (bond-end fraction) and zbar (mean number of
   neighbours) named, and the pair estimator S_chem/R = -sum x ln x - (zbar/2) sum y ln[y/(w w)] set once.
b  ideal limit, random labels on a z = 12 lattice (thermodynamic limit): the pair estimator (markers) equals the ideal
   mixing entropy -R sum x ln x (line) at every composition.
c  ordered benchmark, Bethe lattice z = 12, x_B = 0.5: excess chemical entropy vs Warren-Cowley alpha; exact (line) and
   pair estimator (markers) coincide.
Outputs: figs/fig_pair_entropy.{pdf,png} (171 mm, three cards in a row) and figs/fig_pair_entropy_1col.{pdf,png} (83 mm,
the template column; schematic on top, b and c below; no text below 5 pt). Computed/methods figure without ORCHID records: no badge, neutral inks only (orchid-brand
figures.md). Every plotted number is read from the result files listed with their sha256 in
figs/fig_pair_entropy_sources.json. Run with the fit interpreter (ESPEI gradient PR 9039ea2 + pycalphad).
"""
import json
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import paths  # noqa: E402
import style as st  # noqa: E402
from crni_fig_common import card, check_layout, legend_below, mm_axes, mm_canvas, sha, tilde  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Circle  # noqa: E402

RUN = paths.loc("runs_root") / "hongliu-chemical-mixing-20261105/results"
F_RAND, F_ORD = RUN / "benchmark_random.json", RUN / "benchmark_ordered.json"
RAND = json.loads(F_RAND.read_text())
ORD = json.loads(F_ORD.read_text())

Z_LAT = "z=12"          # random-label benchmark lattice shown in b (closest to the Cr-Ni liquid, zbar about 13)
Z_BETHE, X_BETHE = 12, 0.5

# ---- ORCHID brand palette only (orchid-brand design-system/tokens.json; PI 7 Nov: "more color within the orchid palette").
# No evidence-class colours, no column gold; brand-sage is excluded (its usage: logo contours only, 2.15:1 on white).
# Contrast of every line / marker colour on white >= 3:1 (computed in tok_contrast()).
TOK_FILE = paths.loc("orchid_brand") / "design-system/tokens.json"
TOK = {t["name"]: t["value"] for t in json.loads(TOK_FILE.read_text())["color"]["tokens"]}
ORCHID, INKB, PETAL = TOK["brand-orchid"], TOK["brand-ink"], TOK["brand-petal"]
MUTED, FILL_OR = TOK["muted"]["light"], TOK["fill-orchid"]


def _lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + .055) / 1.055) ** 2.4 for x in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]


def tok_contrast(h, bg="#FFFFFF"):
    a, b = sorted((_lum(h), _lum(bg)), reverse=True)
    return (a + .05) / (b + .05)
UNIT = r"J K$^{-1}$ mol$^{-1}$"
FORMULA = (r"$S_{\mathrm{chem}}/R = -\sum_i\, x_i \ln x_i \;-\; (\bar{z}/2)\,\sum_{ij}\, y_{ij}"
           r"\ln[\,y_{ij}/(w_i w_j)\,]$")


PAIR_MK = dict(ms=3.0, mfc=ORCHID, mec="white", mew=0.4)   # pair estimator: filled brand-orchid


FBOX = dict(boxstyle="round,pad=0.5,rounding_size=0.4", fc=FILL_OR, ec=ORCHID, lw=0.75)  # ORCHID box: our estimator


def rand_rows():
    q = [r for r in RAND["rows"] if r["case"] == "thermodynamic_limit" and r["lattice"] == Z_LAT]
    return sorted(q, key=lambda r: r["x_B"])


def ord_rows():
    q = [r for r in ORD["rows"] if r["case"] == "bethe_lattice_quasichemical_analytic" and r["z"] == Z_BETHE
         and abs(r["x_B"] - X_BETHE) < 1e-12]
    return sorted(q, key=lambda r: r["warren_cowley_alpha"])


# ---------------------------------------------------------------- a: neighbour-graph cartoon
def graph_nodes():
    """Fixed cartoon: jittered triangular patch, two species, neighbours within a cut-off (layout only, not data)."""
    rng = np.random.default_rng(7)
    P = []
    for r in range(4):
        for c in range(6):
            P.append((c + 0.5 * (r % 2), r * 0.87))
    P = np.asarray(P) + rng.normal(0, 0.09, (len(P), 2))
    lab = np.array([0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0])
    E = [(i, j) for i in range(len(P)) for j in range(i + 1, len(P)) if np.hypot(*(P[i] - P[j])) < 1.25]
    return P, lab, E


def draw_graph(ax, x0, y0, s, r_node):
    P, lab, E = graph_nodes()
    P = P * s + np.array([x0, y0])
    hi = (8, 14)                                    # the highlighted bond i-j (two different species)
    for i, j in E:
        if (i, j) != hi:
            ax.plot(*P[[i, j]].T, color=st.GREY_M, lw=0.5, zorder=1, solid_capstyle="round")
    ax.plot(*P[list(hi)].T, color=ORCHID, lw=1.6, zorder=2, solid_capstyle="round")
    for k, (p, l) in enumerate(zip(P, lab)):
        ax.add_patch(Circle(p, r_node, fc=(ORCHID if l else PETAL), ec=INKB, lw=0.5, zorder=3))
    for k, name, side in zip(hi, ("i", "j"), (1, -1)):
        ax.text(P[k, 0] + side * (r_node + 0.4), P[k, 1], name, fontsize=7, fontweight="bold",
                ha="left" if side > 0 else "right", va="center", zorder=4)
    return P


def key_text(ax, x, y, dy, size=6.5):
    rows = [(r"$x_i$", "site fraction"), (r"$y_{ij}$", "bond fraction"), (r"$w_i$", "bond-end fraction"),
            (r"$\bar{z}$", "mean neighbours")]
    for k, (sym, s) in enumerate(rows):
        ax.text(x, y - k * dy, sym, fontsize=size + 0.5, ha="left", va="baseline", color=ORCHID)
        ax.text(x + 5.0, y - k * dy, s, fontsize=size, ha="left", va="baseline", color=MUTED)


# ---------------------------------------------------------------- b and c
def plot_b(b):
    q = rand_rows()
    x = np.array([r["x_B"] for r in q])
    xx = np.r_[0, x, 1]
    b.plot(xx, np.r_[0, [r["ideal"] for r in q], 0], color=INKB, lw=0.9, zorder=2, solid_capstyle="butt")
    b.plot(x[1::2], [r["pair_corrected"] for r in q][1::2], "o", **PAIR_MK, zorder=4)
    b.set_xlim(0, 1); b.set_xticks([0, 0.5, 1]); b.set_xticklabels(["0", "0.5", "1"])
    b.set_xlabel(r"$x_{\mathrm{B}}$", labelpad=1)
    b.set_ylabel(r"$S_{\mathrm{chem}}$ (" + UNIT + ")", labelpad=1)
    top = max(r["ideal"] for r in q)
    b.set_ylim(0, np.ceil(top) + 1)


def plot_c(c):
    q = ord_rows()
    a = np.array([r["warren_cowley_alpha"] for r in q])
    # exact Bethe-lattice excess entropy at x_B = 0.5, z = 12, drawn densely; checked against the benchmark rows
    def bethe(al, z=12, R=8.314462618):
        return -R * (z / 2) * ((1 + al) / 2 * np.log1p(al) + (1 - al) / 2 * np.log1p(-al))
    assert max(abs(bethe(r["warren_cowley_alpha"]) - r["exact_excess"]) for r in q) < 1e-3
    ad = np.linspace(a.min(), a.max(), 241)
    c.plot(ad, bethe(ad), color=INKB, lw=0.9, zorder=2, solid_capstyle="butt")
    c.plot(a, [r["pair_corrected_excess"] for r in q], "o", **PAIR_MK, zorder=4)
    c.axhline(0, color=st.GREY_M, lw=0.4, zorder=0)
    c.axvline(0, color=st.GREY_M, lw=0.4, zorder=0)
    lo = min(r["exact_excess"] for r in q)
    c.set_ylim(np.floor(lo / 2) * 2 - 0.5, 1.0)
    c.set_xlim(a.min() - 0.08, a.max() + 0.08)
    c.set_xlabel(r"Warren$-$Cowley $\alpha$", labelpad=1)
    c.set_ylabel(r"$S_{\mathrm{chem,ex}}$ (" + UNIT + ")", labelpad=1)


def handles():
    h = [Line2D([], [], color=INKB, lw=0.9), Line2D([], [], marker="o", ls="", **PAIR_MK)]
    lab = ["ideal (b), exact (c)", "pair estimator"]
    return h, lab


def save(fig, name, dpi=600):
    fig.savefig(ROOT / f"figs/{name}.pdf")
    fig.savefig(ROOT / f"figs/{name}.png", dpi=dpi)
    probs = check_layout(fig, name)
    plt.close(fig)
    return probs


# ---------------------------------------------------------------- two-column: three cards in a row
def two_col():
    W, H = st.W2 / st.MM, 72.0
    fig, cv = mm_canvas(W, H)
    G = 2.0
    WA = 64.0
    WB = (W - 2.0 - WA - 2 * G) / 2
    XA, XB, XC = 1.0, 1.0 + WA + G, 1.0 + WA + G + WB + G
    CH = H - 2.0
    card(cv, XA, 1.0, WA, CH, "a", "Labels on the neighbour graph")
    card(cv, XB, 1.0, WB, CH, "b", "Ideal limit")
    card(cv, XC, 1.0, WB, CH, "c", "Ordered benchmark")
    # a
    draw_graph(cv, XA + 6.0, 1.0 + 30.0, 5.4, 1.15)
    key_text(cv, XA + 38.0, 1.0 + 48.5, 4.2)
    cv.text(XA + WA / 2, 1.0 + 15.0, FORMULA, fontsize=6.5, ha="center", va="baseline", bbox=FBOX)
    # b, c
    b = mm_axes(fig, XB + 12.5, 1.0 + 23.0, WB - 15.0, CH - 23.0 - 9.0, W, H)
    c = mm_axes(fig, XC + 12.5, 1.0 + 23.0, WB - 15.0, CH - 23.0 - 9.0, W, H)
    plot_b(b)
    plot_c(c)
    h, lab = handles()
    legend_below(fig, h, ["ideal", "pair estimator"], XB + 3.0, 1.0 + 12.0, W, H, ncol=1, size=6.0)
    legend_below(fig, h, ["exact", "pair estimator"], XC + 3.0, 1.0 + 12.0, W, H, ncol=1, size=6.0)
    return save(fig, "fig_pair_entropy")


# ---------------------------------------------------------------- one-column: schematic on top, b and c below
def one_col():
    W, H = st.W1 / st.MM, 88.0                         # Digital Discovery single column (83 mm)
    fig, cv = mm_canvas(W, H)
    G = 1.5
    HA = 36.0
    HB = H - 2.0 - HA - G
    CW = (W - 2.0 - G) / 2
    YA = 1.0 + HB + G
    card(cv, 1.0, YA, W - 2.0, HA, "a", "Labels on the neighbour graph", size=6.5)
    card(cv, 1.0, 1.0, CW, HB, "b", "Ideal limit", size=6.5)
    card(cv, 1.0 + CW + G, 1.0, CW, HB, "c", "Ordered benchmark", size=6.5)
    draw_graph(cv, 5.5, YA + 10.5, 4.4, 1.0)
    key_text(cv, 43.0, YA + HA - 10.0, 3.8, size=6.0)
    cv.text(W / 2, YA + 5.0, FORMULA, fontsize=6.0, ha="center", va="baseline", bbox=FBOX)
    b = mm_axes(fig, 1.0 + 11.0, 1.0 + 12.5, CW - 13.0, HB - 12.5 - 7.4, W, H)
    c = mm_axes(fig, 1.0 + CW + G + 11.0, 1.0 + 12.5, CW - 13.0, HB - 12.5 - 7.4, W, H)
    plot_b(b)
    plot_c(c)
    h, lab = handles()
    legend_below(fig, h, ["ideal", "pair estimator"], 3.0, 1.0 + 4.6, W, H, ncol=2, size=5.5, colsp=0.8)
    legend_below(fig, h, ["exact", "pair estimator"], 1.0 + CW + G + 2.0, 1.0 + 4.6, W, H, ncol=2, size=5.5,
                 colsp=0.8)
    return save(fig, "fig_pair_entropy_1col")


def write_sources():
    rb, ro = rand_rows(), ord_rows()
    allb = [r for r in ORD["rows"] if r["case"] == "bethe_lattice_quasichemical_analytic"]
    nums = {"b_random_labels": {"lattice": Z_LAT, "case": "thermodynamic_limit",
                                "rows": [{"x_B": r["x_B"], "ideal": r["ideal"], "pair_corrected": r["pair_corrected"]}
                                         for r in rb],
                                "max_abs_pair_minus_ideal_shown": max(abs(r["pair_minus_ideal"]) for r in rb),
                                "max_abs_pair_minus_ideal_thermodynamic_limit_all": RAND["max_abs_pair_minus_ideal_thermodynamic_limit"],
                                "max_abs_pair_minus_ideal_finite_all": RAND["max_abs_pair_minus_ideal_finite"]},
            "c_bethe": {"z": Z_BETHE, "x_B": X_BETHE,
                        "rows": [{"alpha": r["warren_cowley_alpha"], "exact_excess": r["exact_excess"],
                                  "pair_corrected_excess": r["pair_corrected_excess"]} for r in ro],
                        "max_abs_pair_minus_exact_all_bethe_rows": max(abs(r["pair_corrected_excess"] - r["exact_excess"])
                                                                       for r in allb)},
            "units": RAND["units"]}
    src = {"figure": "fig_pair_entropy", "kind": "methods figure (computed benchmarks; no ORCHID records, no badge)",
           "outputs": {"fig_pair_entropy": "174 x 72 mm, cards a (schematic), b, c",
                       "fig_pair_entropy_1col": "83 x 88 mm (single column), a on top, b and c below"},
           "script": "scripts/fig_pair_entropy.py",
           "sources": [{"path": tilde(F_RAND), "sha256": sha(F_RAND), "role": "random-label benchmark (b)"},
                       {"path": tilde(F_ORD), "sha256": sha(F_ORD), "role": "ordered Bethe-lattice benchmark (c)"}],
           "numbers": nums}
    (ROOT / "figs/fig_pair_entropy_sources.json").write_text(json.dumps(src, indent=1))
    return nums


if __name__ == "__main__":
    for nm, h in [("pair (brand-orchid)", ORCHID), ("ideal/exact (brand-ink)", INKB)]:
        print(f"contrast on white {nm}: {tok_contrast(h):.2f}")
    probs = two_col() + one_col()
    n = write_sources()
    print("problems:", len(probs))
    print("max |pair-ideal| shown:", n["b_random_labels"]["max_abs_pair_minus_ideal_shown"],
          "max |pair-exact| bethe:", n["c_bethe"]["max_abs_pair_minus_exact_all_bethe_rows"])
