#!/usr/bin/env python3
"""Fig. 1 / graphical abstract of the Cr-Ni paper: ORCHID-SAGE, the record as the product of an assessment (PI, 7 Nov 2026).

Frame: the three record levels wrap the assessment - general protocol (the method, in steps of three kinds) -> specific
protocol (inputs and decisions) -> run cards (each execution) - and the record is packaged (TDB, dashboard, RO-Crate) and
regenerated from itself (scripted rerun on a DGX Spark; AI agent through the ORCHID-SAGE MCP server on the Mac Studio), with
the same predictions within tolerance. Inside the frame, condensed: the inputs (ORCHID evidence, PhaseForge one-shot, liquid
MD, physical checks), the PhaseForge+ sequence liquid -> thermochemistry -> solid, uncertainty, people decide, back to ORCHID.

Data (every plotted value from recorded files; nothing typed by hand):
  record counts         figs/fig_crni_standard_sources.json (counts read by fig_standard.py from orchid-calphad-fit@2.1.2 and
                        crni-paper-fit-step4c-b@1.0.4, with their sha256)
  three step panels     data/hero_crni.json (scripts/export_hero_crni.py): step-2 liquidus pick with the liquid states; liquid
                        enthalpy of mixing of the step-3b pick with the liquid HM_MIX data; the final pick with the
                        phase-boundary states
  regeneration tile     data/hero_repro_crni.json (scripts/export_hero_repro_crni.py): the original final fit and its two
                        regenerations overlaid, their eutectic and CrNi2-top temperatures and check counts
Schematic (labelled "schematic" in the figure): the icons of the inputs, the uncertainty icons and the document glyphs.
Model lines orange (model class), experimental states blue (experimental class), ORCHID-SAGE objects orchid purple.
Output: figs/fig_hero.pdf and .png, 174 mm (template \\textwidth), drawn at final size, every text >= 5 pt (subscripted
labels >= 5.9 pt so that the subscripts stay >= 5 pt). The earlier workflow-centred version is in git history (51450d7).
"""
from pathlib import Path
import json
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle, Ellipse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style as st  # noqa: E402
from crni_fig_common import check_layout  # noqa: E402

D = json.loads((ROOT / "data/hero_crni.json").read_text())
RP = json.loads((ROOT / "data/hero_repro_crni.json").read_text())
NS = json.loads((ROOT / "figs/fig_crni_standard_sources.json").read_text())["counts"]

W, H = 174.0, 124.0                                  # layout units (the 174 mm layout), drawn at the double column
fig = plt.figure(figsize=(st.W2, st.W2 * H / W), dpi=600)   # 171 mm (Digital Discovery); text and lines at final pt
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
LIGHT = {"outer": "#EFE7F4", "mid": "#F6F2F9"}


def txt(x, y, s, size=6, color=st.INK, weight="normal", ha="left", va="center", z=9, **kw):
    return ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va, family="Arial", zorder=z, **kw)


def box(x, y, w, h, fc="white", ec=st.INK2, lw=.55, r=1.3, z=2, ls="-"):
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, zorder=z, ls=ls)
    ax.add_patch(p); return p


def line(xs, ys, color=st.INK2, lw=.6, ls="-", z=5):
    ax.plot(xs, ys, color=color, lw=lw, ls=ls, zorder=z, solid_capstyle="butt")


def arrow(x0, y0, x1, y1, color=st.INK2, lw=.6, z=6, ms=6, rad=0.0, ls="-"):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=ms, color=color, lw=lw, ls=ls,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0, zorder=z))


def dot(x, y, r, c, ec="white", lw=.3, z=7):
    ax.add_patch(Circle((x, y), r, fc=c, ec=ec, lw=lw, zorder=z))


def axes_icon(x, y, w, h):
    line([x, x, x + w], [y + h, y, y], st.INK2, .4)


def doc(x, y, w=4.2, h=5.4, ec=st.ACCENT):
    """Document glyph (schematic)."""
    c = 1.2
    ax.add_patch(plt.Polygon([(x, y), (x + w, y), (x + w, y + h - c), (x + w - c, y + h), (x, y + h)], closed=True, fc="white",
                             ec=ec, lw=.5, zorder=8))
    for k in range(3):
        line([x + .8, x + w - .8], [y + 1.0 + k * 1.1] * 2, st.GREY_M, .35, z=9)


# ---------------------------------------------------------------- schematic icons
def icon_records(x, y, w, h):
    for i, c in enumerate([st.C_EXP, st.C_EXP, st.C_MODEL, st.C_LITDFT]):
        yy = y + h - .8 - i * (h - 1.0) / 3
        ax.add_patch(Rectangle((x, yy - .5), 1.0, 1.0, fc=c, ec="none", zorder=6))
        line([x + 1.6, x + w], [yy, yy], st.GREY_M, .4)


def icon_sqs(x, y, w, h):
    n = 4; s = min(w, h) / n
    rng = np.random.default_rng(3)
    for i in range(n):
        for j in range(n):
            dot(x + (i + .5) * s, y + (j + .5) * s, s * .33, st.C_MP if rng.random() < .5 else "#9AD3C1", lw=.2)


def icon_md(x, y, w, h):
    rng = np.random.default_rng(7)
    ax.add_patch(Rectangle((x, y), w, h, fc="white", ec=st.GREY_M, lw=.4, zorder=5))
    for _ in range(16):
        u, v = rng.random(2)
        dot(x + .5 + u * (w - 1.0), y + .5 + v * (h - 1.0), .35, st.C_MP if rng.random() < .5 else "#9AD3C1", lw=.15)


def icon_gx(x, y, w, h, color=st.C_ASSESSED):
    axes_icon(x, y, w, h)
    u = np.linspace(0.02, 0.98, 80)
    g = 2.6 * u * (1 - u) + 0.9 * (u * np.log(u) + (1 - u) * np.log(1 - u))
    g = (g - g.min()) / (g.max() - g.min())
    line(x + u * w, y + .12 * h + .7 * h * g, color, .7)


def icon_modes(x, y, w, h):
    axes_icon(x, y, w, h)
    ax.add_patch(Ellipse((x + .33 * w, y + .52 * h), .34 * w, .55 * h, fc=LIGHT["outer"], ec=st.ACCENT, lw=.5, zorder=6))
    ax.add_patch(Ellipse((x + .74 * w, y + .44 * h), .22 * w, .36 * h, fc="white", ec=st.ACCENT, lw=.5, ls="--", zorder=6))
    rng = np.random.default_rng(1)
    for cx, cy, sx, sy, n in [(.33, .52, .08, .12, 12), (.74, .44, .05, .07, 4)]:
        for _ in range(n):
            dot(x + (cx + rng.normal(0, sx)) * w, y + (cy + rng.normal(0, sy)) * h, .25, st.ACCENT, ec="none", z=7)


def icon_band(x, y, w, h):
    axes_icon(x, y, w, h)
    u = np.linspace(0, 1, 40); m = .25 + .55 * u ** .7; s = .07 + .05 * np.sin(3 * u) ** 2
    ax.fill_between(x + u * w, y + h * (m - s), y + h * (m + s), color=LIGHT["outer"], lw=0, zorder=5)
    line(x + u * w, y + h * m, st.ACCENT, .7)


# ---------------------------------------------------------------- computed panels (recorded files)
def tracks(tr, x, y, w, h, t0, t1, col, lw, z=6, hot=lambda k: True, cold=st.GREY_M, ls="-", alpha=1.0):
    def Y(tt): return y + (np.asarray(tt, float) - t0) / (t1 - t0) * h
    for key, pts in tr.items():
        a = np.asarray(sorted(pts))
        c, l = (col, lw) if hot(key) else (cold, .4)
        brk = np.where((np.diff(a[:, 0]) > 2.5) | (np.abs(np.diff(a[:, 1])) > 0.04))[0] + 1
        for sg in np.split(a, brk):
            if len(sg) > 1:
                ax.plot(x + sg[:, 1] * w, Y(sg[:, 0]), color=c, lw=l, ls=ls, alpha=alpha, zorder=z, solid_capstyle="butt")
    return Y


def step_diagram(x, y, w, h, tile, liquid_only=False, states=True):
    axes_icon(x, y, w, h)
    hot = (lambda k: "LIQUID" in k) if liquid_only else (lambda k: True)
    Y = tracks(tile["tracks"], x, y, w, h, 600., 2200., st.C_MODEL, .65, hot=hot)
    c2 = np.asarray(tile["crni2"]); col = st.GREY_M if liquid_only else st.C_MODEL
    if len(c2):
        ax.plot([x + c2[0, 1] * w] * 2, Y([c2[:, 0].min(), c2[:, 0].max()]), color=col, lw=.4 if liquid_only else .65, zorder=6)
    for k, t, c in (("liquid_min_line", "T_liquid_min", st.C_MODEL), ("crni2_top_line", "T_CrNi2_max", col)):
        if tile.get(k):
            ax.plot(x + np.asarray(tile[k]) * w, Y([tile[t]] * 2), color=c, lw=.65 if c != st.GREY_M else .4, zorder=6)
    if states:
        for xn, tt in tile["states"]:
            dot(x + xn * w, float(Y(tt)), .2, st.C_EXP, ec="none", z=7)
    txt(x + w / 2, y - .8, "x$_{Ni}$", 5.9, st.INK2, ha="center", va="top")
    txt(x - .5, y + h / 2, "T", 5.0, st.INK2, ha="right")


def hmix_panel(x, y, w, h):
    axes_icon(x, y, w, h)
    t = D["tiles"]["2_thermo"]; m = t["hmix_model"]
    lo, hi = -5.5, 1.5
    def Y(v): return y + (np.asarray(v) - lo) / (hi - lo) * h
    line([x, x + w], [float(Y(0))] * 2, st.GREY_M, .35)
    for xn, v in t["hmix_data_kJ"]:
        assert lo <= v <= hi
        dot(x + xn * w, float(Y(v)), .2, st.C_EXP, ec="none", z=7)
    ax.plot(x + np.asarray(m["x"]) * w, Y(m["H_kJ"]), color=st.C_MODEL, lw=.7, zorder=8)
    txt(x + w / 2, y - .8, "x$_{Ni}$", 5.9, st.INK2, ha="center", va="top")
    txt(x - .4, y + h / 2, "ΔH$_{mix}$", 5.9, st.INK2, ha="right", rotation=90, va="center")


# ================================================================ header
txt(2.0, 119.6, "ORCHID-SAGE", 12.0, st.ACCENT, "bold")
txt(2.0, 113.6, "A recorded, regenerable CALPHAD assessment, shown for Cr–Ni", 7.5, st.INK2)

# ================================================================ the record: three nested levels around the assessment
FX0, FX1 = 2.0, 117.0
box(FX0, 2.0, FX1 - FX0, 106.0, LIGHT["outer"], st.ACCENT, 1.0, 2.0, 1)
txt(FX0 + 2.0, 104.6, "General protocol", 7.5, st.ACCENT, "bold")
txt(FX1 - 2.0, 104.6, f"the method: {NS['general_steps']} steps, deterministic · numerical · judgement", 5.5, st.INK2, ha="right")
box(FX0 + 2.0, 4.0, FX1 - FX0 - 4.0, 97.8, LIGHT["mid"], st.ACCENT, .8, 1.8, 2)
txt(FX0 + 4.0, 98.5, "Specific protocol", 7.5, st.ACCENT, "bold")
txt(FX1 - 4.0, 98.5, f"Cr–Ni: {NS['specific_input_files']} inputs · {NS['decisions']} decisions", 5.5, st.INK2, ha="right")
box(FX0 + 4.0, 6.0, FX1 - FX0 - 8.0, 89.6, "white", st.ACCENT, .6, 1.6, 3)
txt(FX0 + 6.0, 92.4, "Run cards", 7.5, st.ACCENT, "bold")
txt(FX1 - 6.0, 92.4, f"{NS['run_cards']} executions, each with its inputs, code and outputs", 5.5, st.INK2, ha="right")
IX0, IX1 = FX0 + 6.0, FX1 - 6.0                          # inner content span

# ---- inputs (schematic icons)
inputs = [("ORCHID", "states, σ, ids", st.FILL["experimental"], st.C_EXP, icon_records),
          ("PhaseForge", "MLIP one-shot", st.FILL["mp"], st.C_MP, icon_sqs),
          ("Liquid MD", "H$_{mix}$, S$_{ex}$", st.FILL["oqmd"], st.C_OQMD, icon_md),
          ("Physics", "checks, gaps", st.FILL["assessed"], st.C_ASSESSED, icon_gx)]
gw = (IX1 - IX0 - 3 * 1.6) / 4
for k, (head, body, fc, ec, icon) in enumerate(inputs):
    x = IX0 + k * (gw + 1.6)
    box(x, 74.0, gw, 14.6, fc, ec, .55, 1.0, 4)
    txt(x + 1.4, 85.6, head, 6.5, st.INK, "bold")
    txt(x + 1.4, 81.4, body, 5.9, st.INK2)
    icon(x + gw - 7.6, 75.4, 6.2, 5.4)
    arrow(x + gw / 2, 73.6, x + gw / 2, 70.4, st.INK2, .5, ms=5)
txt(IX1, 89.6, "icons schematic", 5.0, st.GREY_M, ha="right", va="bottom")
txt(FX1, 109.8, "The record of the assessment", 7.5, st.ACCENT, "bold", ha="right", va="bottom")

# ---- PhaseForge+ sequence (computed)
box(IX0, 35.0, IX1 - IX0, 35.0, LIGHT["outer"], st.C_MODEL, .55, 1.2, 4)
txt(IX0 + 1.6, 67.0, "PhaseForge+: liquid first, then down in temperature", 6.5, st.INK, "bold")
txt(IX1 - 1.6, 67.0, "Cr–Ni, computed", 5.0, st.INK2, ha="right")
sw = (IX1 - IX0 - 3.2 - 2 * 3.4) / 3
for k, (n, lab) in enumerate((("1", "Liquid"), ("2", "Thermochemistry"), ("3", "Solid + exclusions"))):
    x = IX0 + 1.6 + k * (sw + 3.4)
    box(x, 37.0, sw, 27.0, "white", st.ACCENT, .5, 1.0, 5)
    dot(x + 2.4, 61.4, 1.5, st.ACCENT, ec="none", z=8); txt(x + 2.4, 61.4, n, 5.9, "white", "bold", ha="center")
    txt(x + 4.6, 61.4, lab, 6.0, st.INK, "bold")
    if k == 0:
        step_diagram(x + 4.0, 41.6, sw - 6.0, 16.0, D["tiles"]["1_liquid"], liquid_only=True)
    elif k == 1:
        hmix_panel(x + 4.6, 41.6, sw - 6.6, 16.0)
    else:
        step_diagram(x + 4.0, 41.6, sw - 6.0, 16.0, D["tiles"]["3_solid"])
    if k < 2:
        arrow(x + sw + .3, 50.0, x + sw + 3.1, 50.0, st.ACCENT, .6, ms=5)

# ---- uncertainty and people (schematic)
UW = 50.0
box(IX0, 8.0, UW, 24.0, "white", st.ACCENT, .55, 1.0, 4)
txt(IX0 + 1.6, 29.0, "Uncertainty", 6.5, st.INK, "bold")
txt(IX0 + 1.6, 24.8, "Laplace mixture of the modes;", 5.5, st.INK2)
txt(IX0 + 1.6, 22.0, "bands, invariants, topology", 5.5, st.INK2)
icon_modes(IX0 + 3.0, 10.4, 18.0, 9.0)
icon_band(IX0 + 26.0, 10.4, 20.0, 9.0)
txt(IX0 + UW - 1.4, 29.0, "schematic", 5.0, st.GREY_M, ha="right")
arrow(IX0 + UW / 2, 34.6, IX0 + UW / 2, 32.4, st.INK2, .5, ms=5)
PX = IX0 + UW + 2.0
box(PX, 8.0, IX1 - PX, 24.0, st.FILL["neutral"], st.C_EXP, .55, 1.0, 4)
dot(PX + 4.0, 26.6, 2.3, st.C_EXP, ec="none", z=8); txt(PX + 4.0, 26.6, "PI", 6.0, "white", "bold", ha="center")
txt(PX + 7.6, 27.6, "People decide", 6.5, st.C_EXP, "bold")
txt(PX + 7.6, 24.4, "what agents may not settle alone", 5.5, st.INK2)
for k, s in enumerate(("rules and models, e.g. liquid first", "approvals, logged with the evidence",
                       "second readers before records count")):
    txt(PX + 1.8, 19.4 - k * 3.6, "•  " + s, 5.5, st.INK2)

# ================================================================ right: package and regeneration
RX0, RX1 = 121.0, W - 1.5
RW = RX1 - RX0
arrow(FX1 + .4, 96.0, RX0 - .4, 96.0, st.ACCENT, .9, ms=7)
box(RX0, 85.0, RW, 23.0, LIGHT["outer"], st.ACCENT, .9, 1.4, 3)
txt(RX0 + 1.8, 104.6, "Package", 7.5, st.ACCENT, "bold")
for k, s in enumerate(("TDB", "dashboard", "RO-Crate")):
    xx = RX0 + 2.6 + k * RW / 3
    doc(xx, 90.4)
    txt(xx + 2.1, 88.6, s, 5.9, st.INK, ha="center", va="top")
txt(RX1 - 1.6, 104.6, "schematic", 5.0, st.GREY_M, ha="right")
arrow(RX0 + RW / 2, 84.6, RX0 + RW / 2, 80.4, st.ACCENT, .9, ms=7)

box(RX0, 17.0, RW, 63.0, "white", st.ACCENT, .9, 1.4, 3)
txt(RX0 + 1.8, 76.8, "Regenerated from the record", 7.0, st.ACCENT, "bold")
C = RP["checks"]
for k, (who, sub, e) in enumerate((("scripted rerun", C["dgx_spark"]["machine"], dict(color=st.INK, lw=.55, ls="-")),
                                   ("AI agent, ORCHID-SAGE MCP", C["ai_agent"]["machine"], dict(color=st.ACCENT, lw=.8, ls=(0, (2.2, 1.6)))))):
    yy = 71.6 - k * 5.2
    line([RX0 + 2.0, RX0 + 6.0], [yy] * 2, e["color"], e["lw"], e["ls"], z=9)
    txt(RX0 + 7.2, yy, who, 6.0, st.INK, "bold")
    txt(RX1 - 1.8, yy, sub, 5.5, st.INK2, ha="right")
yy = 61.2
line([RX0 + 2.0, RX0 + 6.0], [yy] * 2, st.ACCENT, 2.4, z=8); ax.lines[-1].set_alpha(.30)
txt(RX0 + 7.2, yy, "original fit", 6.0, st.INK)
# overlay of the three databases (computed: data/hero_repro_crni.json)
OX, OY, OW, OH = RX0 + 6.0, 32.0, RW - 9.0, 24.0
axes_icon(OX, OY, OW, OH)
for key, e in (("original", dict(col=st.ACCENT, lw=2.0, alpha=.30, ls="-", z=6)),
               ("dgx_spark", dict(col=st.INK, lw=.5, alpha=1.0, ls="-", z=7)),
               ("ai_agent", dict(col=st.ACCENT, lw=.7, alpha=1.0, ls=(0, (2.2, 1.6)), z=8))):
    g = RP["diagrams"][key]
    Y = tracks(g["tracks"], OX, OY, OW, OH, 600., 2200., e["col"], e["lw"], z=e["z"], ls=e["ls"], alpha=e["alpha"])
    c2 = np.asarray(g["crni2"])
    ax.plot([OX + c2[0, 1] * OW] * 2, Y([c2[:, 0].min(), c2[:, 0].max()]), color=e["col"], lw=e["lw"], ls=e["ls"],
            alpha=e["alpha"], zorder=e["z"])
    for k, t in (("liquid_min_line", "T_liquid_min"), ("crni2_top_line", "T_CrNi2_max")):
        ax.plot(OX + np.asarray(g[k]) * OW, Y([g[t]] * 2), color=e["col"], lw=e["lw"], ls=e["ls"], alpha=e["alpha"], zorder=e["z"])
txt(OX + OW / 2, OY - .8, "x$_{Ni}$", 5.9, st.INK2, ha="center", va="top")
txt(OX - .5, OY + OH / 2, "T", 5.0, st.INK2, ha="right")
G = RP["diagrams"]
te = {G[k]["T_liquid_min"] for k in G}; tc = {G[k]["T_CrNi2_max"] for k in G}
assert len(te) == len(tc) == 1 and all(C[k]["pass"] and C[k]["n"] == 13 for k in C)
txt(RX0 + 1.8, 24.4, "Same predictions, all three", 6.0, st.INK, "bold")
txt(RX0 + 1.8, 20.8, f"eutectic {te.pop():.0f} K · CrNi$_2$ top {tc.pop():.0f} K · {C['dgx_spark']['n']}/13 checks", 5.9, st.INK2)

# ---- back to ORCHID
box(RX0, 2.0, RW, 12.0, st.FILL["experimental"], st.C_EXP, .55, 1.2, 3)
txt(RX0 + 1.8, 10.6, "Back to ORCHID", 6.5, st.INK, "bold")
txt(RX0 + 1.8, 6.4, "new records and corrections, with ids", 5.5, st.INK2)
arrow(RX0 + RW / 2, 16.6, RX0 + RW / 2, 14.4, st.C_EXP, .6, ms=5)

probs = check_layout(fig, "fig_hero")
out = ROOT / "figs"; out.mkdir(exist_ok=True)
fig.savefig(out / "fig_hero.pdf"); fig.savefig(out / "fig_hero.png", dpi=300)
print(out / "fig_hero.pdf", "problems:", len(probs))
