#!/usr/bin/env python3
"""Cr-Ni liquid excess entropy from the corrected Hong-Liu estimator (computed results only).

a  total excess entropy S_ex = S_vib,ex + S_chem,ex vs x_Ni at 1900 K and 2200 K (pure-liquid references at the same T),
   uncertainty = block SE and cut-off spread in quadrature (potential and method error not included); states where any of the
   three trajectories was not liquid are drawn open.
b  ideal-mixing check: species labels permuted at random on the MD neighbour graphs; the pair (quasi-chemical) chemical term
   must return the ideal mixing entropy, i.e. S_chem,ex = 0; ideal curve shown for scale.
c  components at 2200 K and 1900 K: vibrational (VACF) and chemical (pair-corrected) excess terms.
d  finite-size check at Cr50Ni50, 2200 K: vibrational entropy and chemical excess term for 108 and 864 atoms (<5 % rule).
Outputs: figs/fig_crni_entropy.{pdf,png} (174 x 120 mm, hero cards: letter + orchid heading, legends below the axes) and
figs/fig_crni_entropy_1col.{pdf,png} (84 x 90 mm, same four panels with minimal text: short headings, short axis labels,
no legends; the encodings and numbers go to the caption). Computed results only, no ORCHID records, so no badge
(orchid-brand figures.md); neutral inks only (no evidence-class colours). Every number is read from the result files listed
with their sha256 in figs/fig_crni_entropy_sources.json. Run with the fit interpreter (ESPEI gradient PR 9039ea2 + pycalphad).
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
import style as st  # noqa: E402
import crni_pf_data as D  # noqa: E402
from crni_fig_common import card, card_note, check_layout, legend_below, mm_axes, mm_canvas, sha, tilde  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
GREY_FILL = st.GREY_L

R = 8.314462618
TCOL = {2200: st.INK, 1900: st.INK2}
TMK = {2200: "o", 1900: "s"}
UNIT_S = r"J K$^{-1}$ mol$^{-1}$"   # per mole of atoms (stated in the caption)


F_E, F_I = "liquid_excess_entropy.json", "liquid_ideal_mixing_check.json"
E = D.res(F_E)
I = D.res(F_I)
K108, K864 = "Cr50Ni50_N108_T2200", "Cr50Ni50_N864_T2200"


def by_T(T):
    return sorted([v for v in E["states"].values() if v["T_K"] == T], key=lambda v: v["x_Ni"])


def two_col():
    """174 x 120 mm: four hero cards (letter + orchid heading), legends below the axes inside each card."""
    W, H = st.W2 / st.MM, 120.0
    fig, cv = mm_canvas(W, H)
    CW, CH, G = (W - 2.0 - 2.0) / 2, (H - 2.0 - 2.0) / 2, 2.0
    X = (1.0, 1.0 + CW + G); Y = (1.0 + CH + G, 1.0)
    heads = ("Excess entropy of the liquid", "Ideal-mixing check", "Vibrational and chemical terms", "Cell-size check")
    AX = []
    for k, (letter, head) in enumerate(zip("abcd", heads)):
        cx, cy = X[k % 2], Y[k // 2]
        card(cv, cx, cy, CW, CH, letter, head)
        AX.append(mm_axes(fig, cx + 15.0, cy + 17.0, CW - 20.0, CH - 17.0 - 8.5, W, H))
    a, b, c, d = AX
    LG = lambda k: (X[k % 2] + 15.0, Y[k // 2] + 7.6)          # legend corner (mm), below the x label
    xx = np.linspace(1e-4, 1 - 1e-4, 200)
    xn = r"$x_{\mathrm{Ni}}$"
    # a
    for T in (2200, 1900):
        q = by_T(T)
        for v in q:
            ok = v["all_states_liquid"] and E["ideal_mixing_check_passed"]
            a.errorbar(v["x_Ni"] + (0.006 if T == 1900 else 0), v["S_excess_total"], yerr=v["S_excess_total_u"], fmt=TMK[T], ms=3.4,
                       mfc=TCOL[T] if ok else "white", mec=TCOL[T], ecolor=TCOL[T], elinewidth=0.5, capsize=1.2)
        if q:
            a.plot([0] + [v["x_Ni"] for v in q] + [1], [0] + [v["S_excess_total"] for v in q] + [0], color=TCOL[T], lw=0.5, ls=":")
    a.axhline(0, color=st.GREY_M, lw=0.4, zorder=0)
    a.set_xlim(0, 1); a.set_xlabel(xn); a.set_ylabel(r"$S_{\mathrm{ex}}^{\mathrm{liq}}$ (" + UNIT_S + ")")
    legend_below(fig, [Line2D([], [], marker=TMK[T], ls=":", lw=.5, ms=3.4, color=TCOL[T]) for T in (2200, 1900)],
                 ["2200 K", "1900 K"], *LG(0), W, H)
    # b
    b.plot(xx, -R * (xx * np.log(xx) + (1 - xx) * np.log(1 - xx)), color=st.GREY_M, lw=0.8)
    for s, v in I["states"].items():
        b.errorbar(v["x_Ni"] + (0.012 if v["T_K"] == 1900 else 0), v["S_chem_pair_shuffled"], fmt=TMK[v["T_K"]], ms=3.2, color=TCOL[v["T_K"]], mfc="white")
    ax2 = b.inset_axes([0.33, 0.06, 0.34, 0.32])
    for s, v in I["states"].items():
        ax2.errorbar(v["x_Ni"] + (0.03 if v["T_K"] == 1900 else 0), v["S_chem_excess_shuffled"], yerr=v["block_SE"], fmt=TMK[v["T_K"]], ms=2.4, color=TCOL[v["T_K"]],
                     mfc="white", elinewidth=0.4, capsize=1)
    ax2.axhline(0, color=st.GREY_M, lw=0.4); ax2.set_xlim(0, 1); ax2.tick_params(labelsize=5)
    ax2.set_ylabel(r"$S_{\mathrm{chem,ex}}$", fontsize=6); ax2.set_xticks([0, 0.5, 1])
    b.set_xlim(0, 1); b.set_ylim(0, 7); b.set_xlabel(xn); b.set_ylabel(r"$S_{\mathrm{chem}}$ (" + UNIT_S + ")")
    legend_below(fig, [Line2D([], [], color=st.GREY_M, lw=.8),
                       Line2D([], [], marker="o", ls="", ms=3.2, mfc="white", mec=TCOL[2200]),
                       Line2D([], [], marker="s", ls="", ms=3.2, mfc="white", mec=TCOL[1900])],
                 ["ideal mixing", "permuted labels, 2200 K", "permuted labels, 1900 K"], *LG(1), W, H)
    # c
    for T in (2200, 1900):
        q = by_T(T)
        dx = 0.008 if T == 1900 else -0.008
        for v in q:
            c.errorbar(v["x_Ni"] + dx, v["S_vib_excess"], yerr=v["S_vib_excess_SE"], fmt=TMK[T], ms=3, color=TCOL[T] if T == 2200 else st.GREY_M,
                       elinewidth=0.5, capsize=1.2)
            c.errorbar(v["x_Ni"] + dx, v["S_chem_excess"], yerr=v["S_chem_excess_u"], fmt=TMK[T], ms=3, mfc="white",
                       color=TCOL[T] if T == 2200 else st.GREY_M, elinewidth=0.5, capsize=1.2)
    c.axhline(0, color=st.GREY_M, lw=0.4, zorder=0)
    c.set_xlim(0, 1); c.set_xlabel(xn); c.set_ylabel("Excess term (" + UNIT_S + ")")
    legend_below(fig, [Line2D([], [], marker="o", ls="", ms=3, color=st.INK),
                       Line2D([], [], marker="o", ls="", ms=3, mfc="white", mec=st.INK),
                       Line2D([], [], marker="o", ls="", ms=3, color=st.INK),
                       Line2D([], [], marker="s", ls="", ms=3, color=st.GREY_M)],
                 ["vibrational (filled)", "chemical (open)", "2200 K", "1900 K"], *LG(2), W, H)
    # d: finite-size check as points with error bars (no truncated bars)
    fs = E.get("finite_size")
    if fs:
        vib = E["vibrational"]
        vals = [vib[K108]["S_vib_full_3ps"], vib[K864]["S_vib_full_3ps"]]
        errs = [vib[K108]["S_vib_block_SE"], vib[K864]["S_vib_block_SE"]]
        d.errorbar([0, 1], vals, yerr=errs, fmt="o", ms=3.4, color=st.INK, elinewidth=0.6, capsize=1.5)
        d.axhspan(vals[1] * 0.95, vals[1] * 1.05, color=GREY_FILL, lw=0, zorder=0)
        d.set_xlim(-0.6, 1.6); d.set_ylim(vals[1] * 0.93, vals[1] * 1.07)
        d.set_xticks([0, 1]); d.set_xticklabels(["108", "864"]); d.set_xlabel("Atoms in the cell")
        d.set_ylabel(r"$S_{\mathrm{vib}}$ (" + UNIT_S + ")")
        ch = d.inset_axes([0.62, 0.62, 0.34, 0.3])
        ch.plot([0, 1], [fs["S_chem_excess_N108"], fs["S_chem_excess_N864"]], "o", ms=2.6, mfc="white", mec=st.INK)
        ch.axhline(0, color=st.GREY_M, lw=0.4); ch.set_xlim(-0.5, 1.5); ch.set_xticks([0, 1]); ch.set_xticklabels(["108", "864"], fontsize=5)
        ch.tick_params(labelsize=5); ch.set_ylabel(r"$S_{\mathrm{chem,ex}}$", fontsize=6)
        legend_below(fig, [Patch(fc=GREY_FILL, ec="none")], ["±5 % of the 864-atom value"], *LG(3), W, H, ncol=1)
        card_note(cv, X[1] + CW - 2.5, Y[1] + 2.4, f"Cr$_{{50}}$Ni$_{{50}}$, 2200 K; difference {fs['relative_difference_percent']:.2f} %", ha="right")
    return save(fig, "fig_crni_entropy")


def save(fig, name, dpi=600):
    fig.savefig(ROOT / f"figs/{name}.pdf")
    fig.savefig(ROOT / f"figs/{name}.png", dpi=dpi)
    probs = check_layout(fig, name)
    plt.close(fig)
    return probs


# ================================================================ one-column version (89 x 90 mm), minimal text
W1, H1 = st.W1 / st.MM, 90.0          # template \columnwidth
UNIT_1 = r"J K$^{-1}$ mol$^{-1}$"


def one_col():
    """84 x 90 mm: four hero cards, short orchid headings, direct labels instead of legends."""
    fig, cv = mm_canvas(W1, H1)
    CW, CH, G = (W1 - 2.0 - 1.5) / 2, (H1 - 2.0 - 1.5) / 2, 1.5
    X = (1.0, 1.0 + CW + G); Y = (1.0 + CH + G, 1.0)
    AX = []
    for k, (letter, head) in enumerate(zip("abcd", ("Excess entropy", "Ideal limit", "Components", "Size check"))):
        cx, cy = X[k % 2], Y[k // 2]
        card(cv, cx, cy, CW, CH, letter, head, size=6.5)
        AX.append(mm_axes(fig, cx + 11.0, cy + 8.6, CW - 13.0, CH - 8.6 - 7.4, W1, H1))
    a, b, c, d = AX
    xx = np.linspace(1e-4, 1 - 1e-4, 200)
    xn = r"$x_{\mathrm{Ni}}$"
    for ax_ in (a, b, c):
        ax_.set_xlim(0, 1); ax_.set_xticks([0, 0.5, 1]); ax_.set_xticklabels(["0", "0.5", "1"]); ax_.set_xlabel(xn, labelpad=1)
    # a: total excess entropy, 2200 K filled black circles, 1900 K dark-grey squares
    for T in (2200, 1900):
        q = by_T(T)
        dx = 0.012 if T == 1900 else -0.012
        a.plot([0] + [v["x_Ni"] for v in q] + [1], [0] + [v["S_excess_total"] for v in q] + [0], color=TCOL[T], lw=0.5, ls=":")
        for v in q:
            ok = v["all_states_liquid"] and E["ideal_mixing_check_passed"]
            a.errorbar(v["x_Ni"] + dx, v["S_excess_total"], yerr=v["S_excess_total_u"], fmt=TMK[T], ms=2.8,
                       mfc=TCOL[T] if ok else "white", mec=TCOL[T], ecolor=TCOL[T], elinewidth=0.5, capsize=1.0)
    a.axhline(0, color=st.GREY_M, lw=0.4, zorder=0)
    a.set_ylim(-1.45, 0.25); a.set_yticks([-1.2, -0.8, -0.4, 0])
    a.text(0.62, 0.03, "2200 K", color=TCOL[2200], fontsize=6, ha="left", va="bottom")
    q19 = by_T(1900)
    a.text(0.5, q19[1]["S_excess_total"] - q19[1]["S_excess_total_u"] - 0.04, "1900 K", color=TCOL[1900], fontsize=6,
           ha="center", va="top")
    a.set_ylabel(r"$S_{\mathrm{ex}}$ (" + UNIT_1 + ")", labelpad=1)
    # b: pair estimator on permuted labels vs the ideal mixing entropy; inset S_chem,ex x 10^3
    b.plot(xx, -R * (xx * np.log(xx) + (1 - xx) * np.log(1 - xx)), color=st.GREY_M, lw=0.8)
    for v in I["states"].values():
        b.plot(v["x_Ni"] + (0.02 if v["T_K"] == 1900 else -0.02), v["S_chem_pair_shuffled"], TMK[v["T_K"]], ms=2.6,
               mfc="white", mec=TCOL[v["T_K"]], mew=0.6)
    b.set_ylim(0, 7); b.set_yticks([0, 2, 4, 6])
    b.set_ylabel(r"$S_{\mathrm{chem}}$ (" + UNIT_1 + ")", labelpad=1)
    ins = b.inset_axes([0.34, 0.07, 0.32, 0.36])
    for v in I["states"].values():
        ins.errorbar(v["x_Ni"] + (0.05 if v["T_K"] == 1900 else -0.05), 1e3 * v["S_chem_excess_shuffled"], yerr=1e3 * v["block_SE"],
                     fmt=TMK[v["T_K"]], ms=1.9, mfc="white", mec=TCOL[v["T_K"]], ecolor=TCOL[v["T_K"]], mew=0.5,
                     elinewidth=0.4, capsize=0.8)
    ins.axhline(0, color=st.GREY_M, lw=0.4)
    ins.set_xlim(0.1, 0.9); ins.set_xticks([]); ins.set_ylim(-4.5, 0.8); ins.set_yticks([-4, 0])
    ins.tick_params(labelsize=5, length=1.2, pad=1)
    # what the inset shows: S_chem,ex of the permuted labels, in 10^-3 of the panel unit (values 1e3 x the file's J/K/mol)
    ins.text(0.5, 1.04, r"$S_{\mathrm{chem,ex}}$ ($10^{-3}$)", transform=ins.transAxes, fontsize=5.9, ha="center",
             va="bottom", color=st.INK)
    for sp in ins.spines.values():
        sp.set_linewidth(0.4)
    # c: vibrational (filled) and chemical (open) excess terms; 1900 K light grey squares
    ccol = {2200: st.INK, 1900: st.GREY_M}
    for T in (2200, 1900):
        dx = 0.02 if T == 1900 else -0.02
        for v in by_T(T):
            c.errorbar(v["x_Ni"] + dx, v["S_vib_excess"], yerr=v["S_vib_excess_SE"], fmt=TMK[T], ms=2.6, color=ccol[T],
                       elinewidth=0.5, capsize=1.0)
            c.errorbar(v["x_Ni"] + dx, v["S_chem_excess"], yerr=v["S_chem_excess_u"], fmt=TMK[T], ms=2.6, mfc="white",
                       mec=ccol[T], ecolor=ccol[T], mew=0.6, elinewidth=0.5, capsize=1.0)
    c.axhline(0, color=st.GREY_M, lw=0.4, zorder=0)
    c.set_ylim(-1.45, 0.25); c.set_yticks([-1.2, -0.8, -0.4, 0])
    c.text(0.04, 0.12, "chem", fontsize=6, ha="left", va="bottom")
    c.text(0.04, -0.30, "vib", fontsize=6, ha="left", va="top")
    c.set_ylabel(r"$S_{\mathrm{ex}}$ term (" + UNIT_1 + ")", labelpad=1)
    # d: 108 vs 864 atoms at Cr50Ni50, 2200 K; grey band = +-5 % of the 864-atom value
    fs, vib = E["finite_size"], E["vibrational"]
    vals = [vib[K108]["S_vib_full_3ps"], vib[K864]["S_vib_full_3ps"]]
    errs = [vib[K108]["S_vib_block_SE"], vib[K864]["S_vib_block_SE"]]
    d.axhspan(vals[1] * 0.95, vals[1] * 1.05, color=GREY_FILL, lw=0, zorder=0)
    d.errorbar([0, 1], vals, yerr=errs, fmt="o", ms=2.8, color=st.INK, elinewidth=0.6, capsize=1.2)
    d.set_xlim(-0.6, 1.6); d.set_ylim(vals[1] * 0.93, vals[1] * 1.07)
    d.set_xticks([0, 1]); d.set_xticklabels(["108", "864"]); d.set_xlabel("Atoms", labelpad=1)
    d.set_ylabel(r"$S_{\mathrm{vib}}$ (" + UNIT_1 + ")", labelpad=1)
    d.text(0.5, 0.97, f"{fs['relative_difference_percent']:.2f} %", transform=d.transAxes, ha="center", va="top", fontsize=6)
    return save(fig, "fig_crni_entropy_1col")


def write_sources():
    files = {"excess_entropy": D.RES / F_E, "ideal_mixing_check": D.RES / F_I}
    nums = {"states": {k: {f: v[f] for f in ("x_Ni", "T_K", "S_excess_total", "S_excess_total_u", "S_vib_excess",
                                              "S_vib_excess_SE", "S_chem_excess", "S_chem_excess_u", "all_states_liquid")}
                       for k, v in E["states"].items()},
            "ideal_mixing_check": {k: {f: v[f] for f in ("x_Ni", "T_K", "S_ideal", "S_chem_pair_shuffled",
                                                          "S_chem_excess_shuffled", "block_SE")} for k, v in I["states"].items()},
            "ideal_mixing_criterion": I["criterion"], "ideal_mixing_passed": I["passed"],
            "finite_size": E["finite_size"],
            "S_vib_size_check": {k: {"S_vib_full_3ps": E["vibrational"][k]["S_vib_full_3ps"],
                                     "S_vib_block_SE": E["vibrational"][k]["S_vib_block_SE"]} for k in (K108, K864)}}
    src = {"figure": "fig_crni_entropy", "kind": "computed figure (MLIP molecular dynamics; no ORCHID records, no badge)",
           "outputs": {"fig_crni_entropy": "174 x 120 mm, panels a-d in hero cards, legends below the axes",
                       "fig_crni_entropy_1col": f"{W1:.0f} x {H1:.0f} mm, panels a-d, minimal text (details in the caption)"},
           "script": "scripts/fig_entropy.py",
           "sources": [{"path": tilde(p), "sha256": sha(p), "role": k} for k, p in files.items()],
           "numbers": nums}
    (ROOT / "figs/fig_crni_entropy_sources.json").write_text(json.dumps(src, indent=1))


if __name__ == "__main__":
    probs = two_col() + one_col()
    write_sources()
    print("problems:", len(probs))
