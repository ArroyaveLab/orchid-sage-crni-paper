#!/usr/bin/env python3
"""Fig. 6 of the Cr-Ni paper: physics and uncertainty of the frozen pick (crni-paper-fit-step4c-b@1.0.0, step 4c-b s4).

Reads data/crni_paper_fit_figs.json only (scripts/export_crni_paper_fit.py; that file records the path and sha256 of the pick
TDB, results/physics_step4c_b.json, results/uq/laplace_step4c_b.json, results/uq/classified_mixture_draws_step4c_b.json,
the Cahn inputs and the dashboard data). Its sha256 goes into figs/fig_crni_physics_uq_orchid_ids.json.
(a) stable diagram of the pick with the metastable BCC_A2 miscibility gap computed from the pick: binodal (lower hull of
    G_bcc alone), chemical spinodal, Cahn coherent spinodal (k base; low-high band), and the design point (x_Ni 0.52, 1473 K);
(b) incoherent T_c estimates of the bcc gap (results/physics_step4c_b.json: regular-solution, SRO factor, SRO + vibrational
    entropy, from the MLIP one-shot, Liu 2016 DFT and the fit) against the spinodal tops of the fit;
(c) Laplace-mixture mode weights and the accepted-topology fraction of each component's draws;
(d) probabilities from the 1000 mixture draws and, for contrast, from independent marginals (columns permuted);
(e) the draws' eutectic and CrNi2-top temperatures against the ORCHID records.
The fcc-suppressed prediction of the book chapter is not part of this figure.
Output: figs/fig_crni_physics_uq.{pdf,png}, 174 x 124 mm, hero cards (letter + orchid heading, legends below the axes);
mode statistics, quantiles and other numbers in the caption. MLIP estimates in neutral ink (not an evidence class).
"""
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style as st  # noqa: E402
from crni_fig_common import card, check_layout, draw_diagram, legend_below, mm_axes, mm_canvas, sha  # noqa: E402

SRC = ROOT / "data/crni_paper_fit_figs.json"
D = json.loads(SRC.read_text())
P = D["steps"]["step4c_b"]
G_ = D["bcc_gap"]
PF = D["physics_file"]["bcc"]
U = D["uq"]
INV = {i["reaction"]: i for i in D["invariants"]}
EUT = next(i for k, i in INV.items() if "eutectic" in k)
C2 = next(i for k, i in INV.items() if "CrNi2" in k)
DP = D["design_point"]
# the export recomputes the gap curves; their tops must equal the campaign's physics file
assert G_["chemical_spinodal_top_K"] == PF["chemical_spinodal_top_K"]
assert G_["coherent_spinodal_top_K"] == PF["coherent_spinodal_top_K"]

W, H = st.W2 / st.MM, 119.5
fig, cv = mm_canvas(W, H)
TOP, G = 1.0, 2.0
AW = 66.0                                                   # card a width (mm)
RX = 1.0 + AW + G
RW = (W - 1.0 - RX - G) / 2
H1 = 62.0                                                   # top-row card height
YT = H - TOP - H1                                           # top-row card bottom
H2 = YT - G - 1.0                                           # bottom-row card height
card(cv, 1.0, 1.0, AW, H - TOP - 1.0, "a", "Metastable bcc gap")
card(cv, RX, YT, RW, H1, "b", "Gap T$_c$ estimates")
card(cv, RX, 1.0, RW, H2, "c", "Laplace mixture")
card(cv, RX + RW + G, YT, RW, H1, "d", "Probabilities")
card(cv, RX + RW + G, 1.0, RW, H2, "e", "Invariants of the draws")
axa = mm_axes(fig, 13.0, 21.0, AW - 15.0, H - TOP - 1.0 - 21.0 - 8.0 + 1.0, W, H)
axb = mm_axes(fig, RX + 20.5, YT + 19.0, RW - 23.0, H1 - 19.0 - 8.5, W, H)
axc = mm_axes(fig, RX + 4.0, 1.0 + 14.0, RW - 7.0, H2 - 14.0 - 9.0, W, H)
axd = mm_axes(fig, RX + RW + G + 23.5, YT + 15.5, RW - 26.5, H1 - 15.5 - 8.5, W, H)
axe = mm_axes(fig, RX + RW + G + 12.5, 1.0 + 18.5, RW - 15.0, H2 - 18.5 - 8.0, W, H)


def curve(rows):
    a = np.asarray(rows)
    return np.concatenate([a[:, 1], a[::-1, 2]]), np.concatenate([a[:, 0], a[::-1, 0]])


# (a) stable diagram + metastable bcc gap
ax = axa
draw_diagram(ax, P, st.ACCENT, lw=.9, z=3)
x, y = curve(G_["binodal"]); ax.plot(x, y, color=st.INK, lw=.7, zorder=4)
x, y = curve(G_["chemical_spinodal"]); ax.plot(x, y, color=st.INK, lw=.7, ls=(0, (3, 1.5)), zorder=4)
lo, hi = np.asarray(G_["coherent_spinodal"]["low"]), np.asarray(G_["coherent_spinodal"]["high"])
xl, yl = curve(lo); ax.fill(xl, yl, color=st.GREY_L, zorder=1, lw=0)
xh, yh = curve(hi); ax.fill(xh, yh, color="white", zorder=1, lw=0)
x, y = curve(G_["coherent_spinodal"]["base"]); ax.plot(x, y, color=st.INK2, lw=.7, ls=(0, (1, 1)), zorder=4)
ax.plot(DP["x_Ni"], DP["T_K"], "*", ms=5.5, mfc="white", mec=st.INK, mew=.6, zorder=6)
ax.annotate("design point", xy=(DP["x_Ni"], DP["T_K"]), xytext=(0.66, 1475),
            fontsize=6, color=st.INK, va="center", arrowprops=dict(arrowstyle="-", lw=.4, color=st.INK2, shrinkA=0, shrinkB=3))
ax.text(0.20, 1405, f"{G_['chemical_spinodal_top_K']:.0f} K", fontsize=6, color=st.INK, ha="center", va="bottom")
ax.text(0.86, 1250, "fcc", fontsize=6, color=st.INK2, ha="center")
ax.text(0.45, 1760, "liquid", fontsize=6, color=st.INK2, ha="center")
ax.set_xlim(0, 1); ax.set_ylim(600, 2200)
ax.set_xlabel(r"$x_{\mathrm{Ni}}$"); ax.set_ylabel("Temperature (K)")
legend_below(fig, [Line2D([], [], color=st.ACCENT, lw=.9), Line2D([], [], color=st.INK, lw=.7),
                   Line2D([], [], color=st.INK, lw=.7, ls=(0, (3, 1.5))), Line2D([], [], color=st.INK2, lw=.7, ls=(0, (1, 1))),
                   Patch(fc=st.GREY_L, ec="none")],
             ["stable (pick)", "bcc binodal", "chemical spinodal", "coherent spinodal", "coherent, strain range"],
             4.0, 12.6, W, H, ncol=2, colsp=1.0)

# (b) T_c estimates: source on the y axis, estimate kind by marker; MLIP in neutral ink (not an evidence class)
ax = axb
EST = [("MLIP_oneshot_s2", "MLIP one-shot", st.INK), ("DFT_Liu2016", "DFT (Liu 2016)", st.C_LITDFT), ("fit", "this fit", st.ACCENT)]
KIND = [("Tc_MF_K", "MF", "o"), ("Tc_SRO_K", "SRO", "s"), ("Tc_SRO_vib_K", "SRO + vib", "D")]
yt, yl_ = [], []
for i, (key, lab, col) in enumerate(EST):
    e = PF["incoherent_estimates"][key]
    for j, (k, kl, m) in enumerate(KIND):
        yy = i * 3.6 + j
        ax.plot(e[k], yy, m, ms=3, mfc=col, mec=col, zorder=4)
        if k == "Tc_SRO_vib_K":
            ax.plot(e["Tc_SRO_vib_range_K"], [yy] * 2, color=col, lw=1.2, zorder=3)
            ax.plot(e["Tc_SRO_vib_sigmaOmega_range_K"], [yy] * 2, color=col, lw=.4, zorder=2)
    yt.append(i * 3.6 + 1); yl_.append(lab)
for t, ls_ in ((G_["chemical_spinodal_top_K"], (0, (3, 1.5))), (G_["coherent_spinodal_top_K"]["base"], (0, (1, 1)))):
    ax.axvline(t, color=st.INK2, lw=.5, ls=ls_, zorder=1)
ax.set_yticks(yt, yl_)
ax.set_ylim(9.7, -.7)
ax.set_xlim(0, 2400)
ax.set_xlabel("T$_c$ estimate (K)")
ax.tick_params(axis="y", length=0)
legend_below(fig, [Line2D([], [], ls="none", marker=m, ms=3, mfc=st.INK2, mec=st.INK2) for _, _, m in KIND]
             + [Line2D([], [], color=st.INK2, lw=.5, ls=(0, (3, 1.5))), Line2D([], [], color=st.INK2, lw=.5, ls=(0, (1, 1)))],
             [kl for _, kl, _ in KIND] + ["chemical top", "coherent top"], RX + 3.0, YT + 9.6, W, H, ncol=3, colsp=.9)

# (c) mode weights
ax = axc
names = U["weights"]["names"]
wts = U["weights"]["laplace"]
cnt = U["draw_component_counts"]
left = 0
for k, (n, w) in enumerate(zip(names, wts)):
    ax.barh(0, w, left=left, height=.6, color=st.ACCENT if k == 0 else st.FILL["accent"], ec=st.ACCENT, lw=.5)
    ax.text(left + w / 2, 0, f"{w:.3f}", fontsize=6, color="white" if k == 0 else st.INK, ha="center", va="center", fontweight="bold")
    ax.text(left + w / 2, .4, n.split("_")[0], fontsize=6.5, color=st.INK, ha="center", va="bottom")
    ax.text(left + w / 2, -.4, f"{cnt[n]} draws", fontsize=6, color=st.INK2, ha="center", va="top")
    left += w
ax.set_xlim(0, 1); ax.set_ylim(-1.7, 1.7)
ax.set_yticks([]); ax.spines["left"].set_visible(False)
ax.set_xlabel("Mode weight")

# (d) probabilities, mixture vs independent marginals
ax = axd
M, I = U["mixture"], U["independent_marginals"]
rows = [("accepted topology", "P_topology_ok", "se_ok"), ("eutectic in window", "P_eutectic_ok", None),
        ("CrNi$_2$ top in window", "P_crni2_ok", None), ("fcc at design point", "P_FCC_x052_1473K", "se_fcc")]
yy = np.arange(len(rows))
for k, (lab, key, se) in enumerate(rows):
    for src, dy, col in ((M, -.18, st.ACCENT), (I, .18, st.GREY_M)):
        p = src[key]
        e = src[se] if se else np.sqrt(p * (1 - p) / src["n"])
        ax.barh(k + dy, p, height=.34, color=col, xerr=e, error_kw=dict(lw=.4, capsize=1, ecolor=st.INK))
        ax.text(p + .05 if p < .75 else p - .05, k + dy, f"{p:.3f}", fontsize=5.5, va="center",
                ha="left" if p < .75 else "right", color="white" if (p >= .75 and src is M) else st.INK)
ax.set_yticks(yy, [r[0] for r in rows])
ax.set_ylim(len(rows) - .45, -.45); ax.set_xlim(0, 1); ax.set_xticks([0, .5, 1], ["0", "0.5", "1"])
ax.tick_params(axis="y", length=0)
ax.set_xlabel(f"Probability ({M['n']} draws)")
legend_below(fig, [Patch(fc=st.ACCENT, ec="none"), Patch(fc=st.GREY_M, ec="none")], ["mixture", "independent marginals"],
             RX + RW + G + 3.0, YT + 6.2, W, H, ncol=2, colsp=1.0)

# (e) draws: T_eut vs T_CrNi2
ax = axe
dr = np.asarray([[d[0], d[1]] for d in U["draws"]], float)
ok = np.array([d[2] for d in U["draws"]])
rng = np.random.default_rng(0)
jit = rng.uniform(-1.2, 1.2, dr.shape)                                   # draws sit on a 5 K grid; jitter for display only
ax.scatter(dr[ok, 0] + jit[ok, 0], dr[ok, 1] + jit[ok, 1], s=1.5, c=st.ACCENT, alpha=.3, lw=0, rasterized=True, zorder=2)
ax.scatter(dr[~ok, 0] + jit[~ok, 0], dr[~ok, 1] + jit[~ok, 1], s=4, marker="x", c=st.INK, lw=.4, zorder=3)
ax.axvline(EUT["observed_K"], color=st.C_EXP, lw=.6, zorder=1)
ax.axhline(C2["observed_K"], color=st.C_EXP, lw=.6, zorder=1)
ax.axhspan(C2["observed_K"] - 25, C2["observed_K"] + 25, color=st.FILL["experimental"], zorder=0, lw=0)
ax.plot(P["T_liquid_min"], P["T_CrNi2_max"], "D", ms=3.2, mfc=st.ACCENT, mec="white", mew=.4, zorder=5)
ax.set_xlabel("Eutectic T (K)"); ax.set_ylabel("CrNi$_2$ top T (K)")
ax.set_ylim(min(735, np.nanmin(np.where(np.isfinite(dr[:, 1]), dr[:, 1], np.nan)) - 5), 985)
legend_below(fig, [Line2D([], [], ls="none", marker="o", ms=2, mfc=st.ACCENT, mec="none", alpha=.5),
                   Line2D([], [], ls="none", marker="x", ms=2.5, mec=st.INK, mew=.4),
                   Line2D([], [], ls="none", marker="D", ms=3.2, mfc=st.ACCENT, mec="white"),
                   Line2D([], [], color=st.C_EXP, lw=.6)],
             ["accepted draw", "not accepted", "pick", "ORCHID records"], RX + RW + G + 3.0, 1.0 + 9.4, W, H, ncol=2, colsp=1.0)

for ext in ("pdf", "png"):
    fig.savefig(ROOT / f"figs/fig_crni_physics_uq.{ext}", dpi=600 if ext == "png" else None)
check_layout(fig, "fig_crni_physics_uq")

ids = {"figure": "fig_crni_physics_uq", "orchid_release": "provisional (" + D["orchid_release"] + ")",
       "source_data": {"path": "data/crni_paper_fit_figs.json", "sha256": sha(SRC)},
       "specific_protocol": "crni-paper-fit-step4c-b@1.0.0",
       "labels": {"ORCHID eutectic record (panel e, vertical line)": EUT["orchid_ids"],
                  "ORCHID CrNi2 ordering record (panel e, horizontal line)": C2["orchid_ids"]},
       "note": "ORC-X3KVP7D3PO is a single-reader record not yet in a release (pending intake). Panels a-d plot no ORCHID records."}
(ROOT / "figs/fig_crni_physics_uq_orchid_ids.json").write_text(json.dumps(ids, indent=1))
print("chem", G_["chemical_spinodal_top_K"], "coh", G_["coherent_spinodal_top_K"], "binodal top", G_["binodal_top_K"],
      "weights", wts, "P_ok", M["P_topology_ok"], "P_fcc", M["P_FCC_x052_1473K"], "design phase", DP["phase_at_pick"])
