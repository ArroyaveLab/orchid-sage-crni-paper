#!/usr/bin/env python3
"""Reproduction figure of the Cr-Ni paper (Results, sec:reproduction; label fig:repro), figure* at \\textwidth (174 mm).

The final fit as recorded and its two regenerations, overlaid:
  original  : the recorded pick (start s4, Mac Studio)
  DGX Spark : scripted rerun of the specific protocol (1.0.3, the same science as the final 1.0.4: record fixes only)
  AI agent  : rerun of the final specific protocol 1.0.4 by an AI agent through the ORCHID-SAGE MCP server, Mac Studio
(a) the three computed phase diagrams on one plot (600-2200 K); (b) the eutectic and (c) the CrNi2 top enlarged, with the
invariant temperature of each database; (d) the 13 checks of each rerun, grouped by step kind: deterministic ones as
identical, numerical ones as |rerun - recorded| / tolerance.
Reads data/hero_repro_crni.json only (scripts/export_hero_repro_crni.py, which records every source file with its sha256).
No ORCHID records are plotted (computed diagrams and check results only), so no badge (orchid-brand figures.md).
Hero cards (letter + orchid heading, legends below the axes). Machine names as classes only.
Output: figs/fig_hero_repro.{pdf,png}, 174 x 78 mm; sources in figs/fig_hero_repro_sources.json.
The earlier graphical-abstract version of this script (step4-s1 draft campaign) is in git history (commit dab9bff).
"""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style as st  # noqa: E402
from crni_fig_common import card, card_note, check_layout, legend_below, mm_axes, mm_canvas, sha  # noqa: E402

DATA = ROOT / "data/hero_repro_crni.json"
D = json.loads(DATA.read_text())
G = D["diagrams"]; C = D["checks"]
# encodings: the recorded fit as a wide light orchid band, the two regenerations as thin lines on top of it
ENC = {"original": dict(color=st.ACCENT, lw=2.6, alpha=0.30, ls="-", z=2),
       "dgx_spark": dict(color=st.INK, lw=0.55, alpha=1.0, ls="-", z=4),
       "ai_agent": dict(color=st.ACCENT, lw=0.8, alpha=1.0, ls=(0, (2.2, 1.6)), z=5)}
LAB = {"original": "original fit (Mac Studio)",
       "dgx_spark": f"regenerated, scripted ({C['dgx_spark']['machine']})",
       "ai_agent": f"regenerated, AI agent ({C['ai_agent']['machine']})"}


def draw(ax, g, e):
    """Two-phase boundaries, CrNi2 line, eutectic and CrNi2-top lines of one database (same breaks as draw_diagram)."""
    kw = dict(color=e["color"], lw=e["lw"], alpha=e["alpha"], ls=e["ls"], zorder=e["z"], solid_capstyle="butt")
    for pts in g["tracks"].values():
        a = np.asarray(sorted(pts))
        brk = np.where((np.diff(a[:, 0]) > 2.5) | (np.abs(np.diff(a[:, 1])) > 0.04))[0] + 1
        for seg in np.split(a, brk):
            if len(seg) > 1:
                ax.plot(seg[:, 1], seg[:, 0], **kw)
    c2 = np.asarray(g["crni2"])
    if len(c2):
        ax.plot([c2[0, 1]] * 2, [c2[:, 0].min() - 2, c2[:, 0].max()], **kw)
    for k, t in (("liquid_min_line", "T_liquid_min"), ("crni2_top_line", "T_CrNi2_max")):
        if g.get(k):
            ax.plot(g[k], [g[t]] * 2, **kw)


def sci(v):
    """|diff|/tol as printed in the check panel: 0, or a x 10^n with one significant figure."""
    if v == 0:
        return "0"
    e = int(np.floor(np.log10(v))); m = v / 10 ** e
    m = int(round(m))
    if m == 10:
        m, e = 1, e + 1
    return (f"{m}×" if m != 1 else "") + f"10$^{{{e}}}$"


W, H = st.W2 / st.MM, 78.0
fig, cv = mm_canvas(W, H)
G1 = 1.5
AW, BW = 78.0, 40.0
DW = W - 2.0 - AW - BW - 2 * G1
XA, XB = 1.0, 1.0 + AW + G1
XD = XB + BW + G1
BH = (H - 2.0 - G1) / 2

# ---------------------------------------------------------------- a: the three diagrams
card(cv, XA, 1.0, AW, H - 2.0, "a", "Three databases, one phase diagram")
a = mm_axes(fig, XA + 11.0, 1.0 + 21.0, AW - 14.0, H - 2.0 - 21.0 - 9.5, W, H)
for k in ("original", "dgx_spark", "ai_agent"):
    draw(a, G[k], ENC[k])
a.set_xlim(0, 1); a.set_ylim(600, 2200)
a.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0]); a.set_xticklabels(["0", "0.2", "0.4", "0.6", "0.8", "1"])
a.set_yticks([600, 1000, 1400, 1800, 2200])
a.set_xlabel(r"$x_{\mathrm{Ni}}$", labelpad=1); a.set_ylabel("Temperature (K)", labelpad=2)
for x, y, s in ((0.62, 1950, "liquid"), (0.12, 1150, "bcc"), (0.88, 1150, "fcc"), (0.40, 1100, "bcc + fcc")):
    a.text(x, y, s, fontsize=6, color=st.INK2, ha="center", va="center")
o = G["original"]
for (lo, hi), lab in ((((0.30, 0.56), (1560, 1660)), "b"), (((0.56, 0.80), (820, 900)), "c")):
    a.add_patch(plt.Rectangle((lo[0], hi[0]), lo[1] - lo[0], hi[1] - hi[0], fc="none", ec=st.INK2, lw=0.4, ls=":", zorder=6))
    a.text(lo[1] + 0.012, hi[1], lab, fontsize=6.5, fontweight="bold", color=st.INK2, ha="left", va="top")
hs = [Line2D([], [], color=ENC[k]["color"], lw=ENC[k]["lw"], alpha=ENC[k]["alpha"], ls=ENC[k]["ls"]) for k in ENC]
legend_below(fig, hs, [LAB[k] for k in ENC], XA + 3.0, 1.0 + 11.8, W, H, ncol=1, size=6.0)

# ---------------------------------------------------------------- b, c: the two invariants enlarged
zoom = [("b", "Eutectic", "T_liquid_min", (0.30, 0.56), (1560, 1660), 1.0 + BH + G1),
        ("c", "CrNi$_2$ top", "T_CrNi2_max", (0.56, 0.80), (820, 900), 1.0)]
for letter, head, key, xl, yl, y0 in zoom:
    card(cv, XB, y0, BW, BH, letter, head)
    z = mm_axes(fig, XB + 10.5, y0 + 9.6, BW - 13.0, BH - 9.6 - 7.4, W, H)
    for k in ("original", "dgx_spark", "ai_agent"):
        draw(z, G[k], ENC[k])
    z.set_xlim(*xl); z.set_ylim(*yl)
    z.set_xticks([xl[0] + 0.04, xl[1] - 0.04] if letter == "b" else [0.6, 0.75])
    z.set_xticklabels([f"{v:.2f}".rstrip("0") for v in z.get_xticks()])
    z.set_yticks([yl[0] + 20, yl[1] - 20] if letter == "b" else [840, 880])
    z.set_xlabel(r"$x_{\mathrm{Ni}}$", labelpad=1); z.set_ylabel("T (K)", labelpad=1)
    vals = [G[k][key] for k in ("original", "dgx_spark", "ai_agent")]
    same = len(set(vals)) == 1
    card_note(cv, XB + BW - 2.0, y0 + BH - 4.0, (f"all three: {vals[0]:.0f} K" if same else
                                                 " / ".join(f"{v:.0f}" for v in vals) + " K"), ha="right")

# ---------------------------------------------------------------- d: the 13 checks of each rerun
card(cv, XD, 1.0, DW, H - 2.0, "d", "13 checks per rerun")
L = XD + 2.0
C1, C2 = XD + DW - 21.0, XD + DW - 7.6          # column centres: DGX Spark, AI agent
yh = H - 11.0
for xc, k, sub in ((C1, "dgx_spark", "scripted"), (C2, "ai_agent", "AI agent")):
    cv.text(xc, yh, C[k]["machine"], fontsize=6, fontweight="bold", color=st.INK, ha="center", va="baseline")
    cv.text(xc, yh - 2.6, sub, fontsize=5.5, color=st.INK2, ha="center", va="baseline")
    cv.text(xc, yh - 5.2, C[k]["protocol"].split("@")[1], fontsize=5.5, color=st.INK2, ha="center", va="baseline")
    e = ENC[k]
    cv.plot([xc - 3.5, xc + 3.5], [yh + 2.6] * 2, color=e["color"], lw=e["lw"], ls=e["ls"], solid_capstyle="butt")
cv.text(L, yh - 5.2, "specific protocol", fontsize=5.5, color=st.INK2, ha="left", va="baseline")
rows_s, rows_m = C["dgx_spark"]["rows"], C["ai_agent"]["rows"]
assert [r[0] for r in rows_s] == [r[0] for r in rows_m]
y = yh - 9.4
STEP = 3.45
for kind, head in (("deterministic", "Deterministic: identical"), ("numerical", "Numerical: |Δ| / tolerance")):
    cv.text(L, y, head, fontsize=6, fontweight="bold", color=st.INK, ha="left", va="baseline")
    y -= STEP
    for rs, rm in zip(rows_s, rows_m):
        if rs[1] != kind:
            continue
        cv.text(L + 1.0, y, rs[0], fontsize=6, color=st.INK2, ha="left", va="baseline")
        for xc, r in ((C1, rs), (C2, rm)):
            assert r[3] is True
            s = "identical" if kind == "deterministic" else ("equal" if r[2] is None else sci(r[2]))
            cv.text(xc, y, s, fontsize=6, color=st.INK, ha="center", va="baseline")
        y -= STEP
    y -= 1.0
n_pass = {k: sum(1 for r in C[k]["rows"] if r[3]) for k in C}
assert all(C[k]["pass"] and C[k]["n"] == 13 for k in C)
card_note(cv, L, 3.2, "all 13 passed in both reruns")

probs = check_layout(fig, "fig_hero_repro")
out = ROOT / "figs"
fig.savefig(out / "fig_hero_repro.pdf"); fig.savefig(out / "fig_hero_repro.png", dpi=600)
src = {"figure": "fig_hero_repro", "label": "fig:repro", "size_mm": [round(W, 1), H],
       "kind": "computed figure (phase diagrams of three TDBs; rerun check results); no ORCHID records, no badge",
       "data": {"path": "data/hero_repro_crni.json", "sha256": sha(DATA)},
       "sources": D["provenance"]["files"], "campaign_code_read_only": D["provenance"]["campaign_code_read_only"],
       "protocols": {k: C[k]["protocol"] for k in C}, "machines": {k: C[k]["machine"] for k in C},
       "invariants_K": {k: [G[k]["T_liquid_min"], G[k]["T_CrNi2_max"]] for k in G},
       "boundaries_vs_original": {k: G[k]["vs_original"] for k in ("dgx_spark", "ai_agent")},
       "checks": {k: C[k]["rows"] for k in C}}
(out / "fig_hero_repro_sources.json").write_text(json.dumps(src, indent=1))
print("problems:", len(probs))
