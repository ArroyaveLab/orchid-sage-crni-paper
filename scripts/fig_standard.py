#!/usr/bin/env python3
"""Fig. 2 of the Cr-Ni paper (schematic): the ORCHID-SAGE standard.

general protocol -> specific protocol -> run cards -> TDB / dashboard / RO-Crate, with the PROV links the crate records
(prov:hadPlan run -> general step, instrument run -> specific protocol, object (used) run -> inputs, prov:wasGeneratedBy
TDB -> run, prov:wasDerivedFrom run -> run), the ORCHID-SAGE MCP executing steps (get_step, run_step, compare_outputs), and
judgement steps returning recorded decisions (record_decision -> decisions log of the specific protocol).

Every count in the boxes is read from the files (paths and sha256 in figs/fig_crni_standard_sources.json):
  orchid-sage:protocols/general/orchid-calphad-fit@2.1.2.yaml   (sections, steps and their kinds, package outputs)
  orchid-sage:protocols/specific/crni-paper-fit-step4c-b@1.0.4.yaml (inputs, runs, run cards, overrides, decisions,
      artifact, evidence bundle; the general protocol is taken from its `instantiates` pin, whose sha256 is checked)
  orchid-sage:assessments/crni-paper-fit-step4c-b/evidence/states@1.2.0.json (number of states; the bundle 1.0.4 uses)
  orchid-sage:sage_mcp/server.py (the MCP tool names drawn)
prov:hadPlan is counted from the run sequence of the specific protocol (each run names its general step). The RO-Crate of
crni-paper-fit-step4c-b is not read either (crates exist for 1.0.0 and 1.0.2-1.0.4); the crate box is generic.
7 Nov 2026: moved from orchid-calphad-fit@2.0.0 / crni-paper-fit-step4c-b@1.0.0 to 2.1.0 / 1.0.1 (the 1.0.0 version of this
script is in git history, commit c0b8377). 7 Nov 2026 (later): moved to the final versions, 2.1.2 / 1.0.4.
Vector schematic, brand colours, no data (no badge). Outputs: figs/fig_crni_standard.{pdf,png} (174 x 87.5 mm, stages left to
right) and figs/fig_crni_standard_1col.{pdf,png} (84 x 75.5 mm, stages top to bottom: general -> specific -> run cards ->
package -> people/agent; minimal text, PI 7 Nov: titles and one number per box, unlabelled arrows, details in the caption).
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, RegularPolygon, Rectangle

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style as st  # noqa: E402
from crni_fig_common import SAGE_REPO, check_layout, sha, tilde  # noqa: E402
import paths  # noqa: E402

SAGE = SAGE_REPO
sys.path.insert(0, str(SAGE / "protocols/tools"))
import yamlmini  # noqa: E402

SPEC_ID = "crni-paper-fit-step4c-b@1.0.4"   # the final specific protocol (instantiates orchid-calphad-fit@2.1.2)
F = {"specific": SAGE / f"protocols/specific/{SPEC_ID}.yaml"}
SPEC = yamlmini.load(str(F["specific"]))
_pin = SPEC["instantiates"][0]
F["general"] = paths.expand(_pin["file"]["path"])
assert sha(F["general"]) == _pin["file"]["sha256"], "general protocol differs from the instantiates pin"
F["states"] = SAGE / SPEC["evidence_selection"]["bundle"]["states"]["path"]
assert sha(F["states"]) == SPEC["evidence_selection"]["bundle"]["states"]["sha256"], "states file differs from its pin"
F["mcp"] = SAGE / "sage_mcp/server.py"
GEN = yamlmini.load(str(F["general"]))
assert f"{GEN['id']}@{GEN['version']}" == _pin["protocol"]
NSTATES = json.loads(F["states"].read_text())["n_states"]
MCP_TOOLS = set(re.findall(r"\b(\w+)\b", F["mcp"].read_text().split("TOOLS: list")[1].split("] = [")[1].split("]")[0]))
for t in ("get_step", "run_step", "compare_outputs", "record_decision"):
    assert t in MCP_TOOLS, t

secs = [(s["id"], [t["kind"] for t in s.get("steps", [])]) for s in GEN["sections"]]
kinds = Counter(k for _, ks in secs for k in ks)
n_steps = sum(kinds.values())
runs = SPEC["run_sequence"]
n_cards = sum(1 for r in runs if "run_card" in r)
n_dec = len(SPEC["decisions"])
who = Counter(d["who"].split(" ")[0] for d in SPEC["decisions"])
n_files = sum(len(i.get("files", [])) for i in SPEC["inputs"])
n_hadplan = sum(1 for r in runs if r.get("step"))
n_conf = sum(1 for o in SPEC.get("overrides", []) if o.get("conforms") is True)
crate_out = [o for o in GEN["outputs"] if o["kind"] == "ro_crate"][0]["name"]
art_sha = SPEC["artifact"]["file"]["sha256"]
gen_id = f"{GEN['id']}@{GEN['version']}"
spec_id = f"{SPEC['id']}@{SPEC['version']}"

W, H = 183., 92.
fig = plt.figure(figsize=(st.W2, st.W2 * H / W))   # 183-unit layout drawn at the double column (171 mm); text at final pt
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
MONO = st.MONO


def txt(x, y, s, size=6, color=st.INK, weight="normal", ha="left", va="center", family="Arial", z=9, **kw):
    return ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va, family=family, zorder=z, **kw)


def box(x, y, w, h, fc="white", ec=st.INK2, lw=.55, r=1.0, z=2, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, zorder=z, ls=ls))


def arrow(p0, p1, color=st.INK2, lw=.5, rad=0.0, z=6, ls="-", ms=5):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=ms, color=color, lw=lw, shrinkA=0, shrinkB=0,
                                 connectionstyle=f"arc3,rad={rad}", zorder=z, ls=ls))


def prov(x, y, s, ha="center", size=5.0):
    txt(x, y, s, size, st.INK2, ha=ha, family=MONO, bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none"))


def kind_glyph(x, y, k, s=.75):
    if k == "deterministic":
        ax.add_patch(Rectangle((x - s, y - s), 2 * s, 2 * s, fc=st.INK, ec="none", zorder=8))
    elif k == "numerical":
        ax.add_patch(Circle((x, y), s, fc=st.GREY_M, ec=st.INK2, lw=.3, zorder=8))
    else:  # judgement
        ax.add_patch(RegularPolygon((x, y), 4, radius=s * 1.35, fc="white", ec=st.ACCENT, lw=.6, zorder=8))


def person(x, y, s=1.0, color=st.INK2):
    ax.add_patch(Circle((x, y + 1.55 * s), .75 * s, fc=color, ec="none", zorder=8))
    ax.add_patch(FancyBboxPatch((x - 1.1 * s, y - 1.0 * s), 2.2 * s, 1.9 * s, boxstyle=f"round,pad=0,rounding_size={.8 * s}",
                                fc=color, ec="none", zorder=8))


def agent(x, y, s=1.0, color=st.INK2):
    ax.add_patch(FancyBboxPatch((x - 1.4 * s, y - 1.1 * s), 2.8 * s, 2.3 * s, boxstyle=f"round,pad=0,rounding_size={.5 * s}",
                                fc=color, ec="none", zorder=8))
    for dx in (-.6, .6):
        ax.add_patch(Circle((x + dx * s, y + .15 * s), .32 * s, fc="white", ec="none", zorder=9))
    ax.plot([x, x], [y + 1.2 * s, y + 1.9 * s], color=color, lw=.5, zorder=8)
    ax.add_patch(Circle((x, y + 2.05 * s), .3 * s, fc=color, ec="none", zorder=8))


def doc(x, y, w=3.0, h=3.8, ec=st.ACCENT):
    f = .8
    ax.add_patch(Polygon([(x, y), (x + w, y), (x + w, y + h - f), (x + w - f, y + h), (x, y + h)], closed=True, fc="white",
                         ec=ec, lw=.5, zorder=8))
    for k in range(3):
        ax.plot([x + .55, x + w - .55], [y + .8 + k * .75] * 2, color=st.GREY_M, lw=.35, zorder=9)


# ---------------------------------------------------------------- columns
TOP, BOT = 78.0, 34.0              # main row
HD = 88.0                          # stage headers
cols = [(3.0, 36.0), (52.0, 37.0), (103.0, 31.0), (146.0, 34.0)]
for (x, w), head in zip(cols, ["General protocol", "Specific protocol", "Run cards", "Package"]):
    txt(x, HD, head, 7.5, st.ACCENT, "bold")

# 1 general protocol: sections as rows of step glyphs
x, w = cols[0]
box(x, BOT, w, TOP - BOT, st.FILL["accent"], st.ACCENT, .75)
txt(x + 2, TOP - 3.2, gen_id, 5.4, st.INK, family=MONO)
txt(x + 2, TOP - 7.0, f"{len(secs)} sections, {n_steps} steps", 6, st.INK2)
names = {"s0_preflight": "preflight", "s1_evidence": "evidence", "s2_oneshot": "one-shot", "s3_fit_sequence": "fit sequence",
         "s4_checks_rank": "checks, pick", "s5_uq": "UQ", "s6_package": "package"}
for i, (sid, ks) in enumerate(secs):
    yy = TOP - 11.6 - i * 4.0
    txt(x + 2, yy, names.get(sid, sid), 5.6, st.INK)
    for j, k in enumerate(ks):
        kind_glyph(x + 15.5 + j * 1.65, yy, k, .55)
for j, (k, xx, yy) in enumerate((("deterministic", 3.0, BOT + 5.6), ("numerical", 20.0, BOT + 5.6), ("judgement", 3.0, BOT + 2.4))):
    kind_glyph(x + xx, yy, k, .55)
    txt(x + xx + 1.3, yy, f"{k} {kinds[k]}", 5.2, st.INK2)

# 2 specific protocol
x, w = cols[1]
SB = BOT + 13.0
box(x, SB, w, TOP - SB, st.FILL["accent"], st.ACCENT, .75)
txt(x + 2, TOP - 3.2, spec_id, 5.4, st.INK, family=MONO)
items = [(f"{n_files} input files", "sha256 each"), (f"{len(runs)} runs in sequence", f"{n_cards} with run cards"),
         (f"{len(SPEC.get('overrides', []))} overrides", f"of the general defaults ({n_conf} conform)"),
         (f"{n_dec} decisions", f"{who.get('PI', 0)} PI, {who.get('agent', 0)} agent: who, why, source")]
for k, (a, b) in enumerate(items):
    yy = TOP - 9.4 - k * 5.9
    box(x + 1.8, yy - 2.5, w - 3.6, 5.0, "white", st.ACCENT, .4, .7, 3)
    txt(x + 3.0, yy + .9, a, 5.9, st.INK)
    txt(x + 3.0, yy - 1.2, b, 5.2, st.INK2)
DEC_Y = TOP - 9.4 - 3 * 5.9 - 2.5          # bottom of the decisions box
# evidence bundle (used by the runs)
EX, EW = x, 21.0
box(EX, BOT, EW, 10.0, st.FILL["experimental"], st.C_EXP, .55)
txt(EX + 1.6, BOT + 6.8, "Evidence bundle", 6.5, st.INK, "bold")
txt(EX + 1.6, BOT + 3.0, f"{NSTATES} ORCHID states", 5.4, st.INK2)

# 3 run cards (stacked)
x, w = cols[2]
RB, RH = BOT + 13.0, TOP - BOT - 16.0
for k in range(3, 0, -1):
    box(x + k * 1.0, RB + k * 1.0, w - 3.0, RH, "white", st.GREY_M, .45, 1.0, 2)
box(x, RB, w - 3.0, RH, "white", st.INK2, .55, 1.0, 3)
txt(x + 2, RB + RH - 3.4, f"{n_cards} cards, one per run", 6, st.INK)
for k, s in enumerate(["host, interpreter", "packages, lock sha256", "seeds, threads", "data files sha256", "trajectory, pick"]):
    txt(x + 2.4, RB + RH - 8.0 - k * 3.2, s, 5.5, st.INK2)
# run -> run derivation (loop at the lower right of the card)
ax.add_patch(FancyArrowPatch((x + 1.6, RB + 2.6), (x + 5.6, RB + 2.6), arrowstyle="-|>", mutation_scale=4.5, color=st.INK2,
                             lw=.45, connectionstyle="arc3,rad=-1.2", zorder=6))
prov(x + 6.3, RB + 2.6, "prov:wasDerivedFrom", ha="left", size=5.0)

# 4 package
x, w = cols[3]
outs = [("TDB + header", f"sha256 {art_sha[:8]}…"), ("Dashboard", "trajectory, checks, UQ"), ("RO-Crate", crate_out.replace(" RO-", " "))]
OY = [TOP - 15.0, TOP - 28.5, TOP - 42.0]
for (a, b), yy in zip(outs, OY):
    box(x, yy, w, 10.0, st.FILL["accent"], st.ACCENT, .75)
    doc(x + 2.0, yy + 3.1)
    txt(x + 6.6, yy + 6.8, a, 6.5, st.ACCENT, "bold")
    txt(x + 6.6, yy + 3.0, b, 5.3, st.INK2, family=MONO if "sha" in b else "Arial")

# ---------------------------------------------------------------- PROV links (arrows point from the derived thing)
gx, gw = cols[0]; sx, sw = cols[1]; rx, rw = cols[2]; px, pw = cols[3]
arrow((sx - .2, 62.0), (gx + gw + .2, 62.0), st.ACCENT, .6)
txt((sx + gx + gw) / 2, 64.0, "instantiates", 5.5, st.ACCENT, ha="center")
arrow((rx - .2, 56.0), (sx + sw + .2, 56.0), st.INK2)
prov((rx + sx + sw) / 2, 58.2, "instrument", size=5.0)
# hadPlan: run cards -> general steps, routed above the boxes
HPY = 82.6
ax.plot([rx + 12, rx + 12, gx + 26], [RB + RH + 3.0, HPY, HPY], color=st.INK2, lw=.5, zorder=6)
arrow((gx + 26, HPY), (gx + 26, TOP + .2), st.INK2)
prov((sx + sw / 2), HPY, f"prov:hadPlan  ({n_hadplan} runs → general steps)", size=5.0)
# TDB generated by the run
arrow((px - .2, OY[0] + 5.0), (rx + rw - 3.0 + .2, OY[0] + 5.0), st.INK2)
prov(px, OY[0] + 11.6, "prov:wasGeneratedBy", ha="left", size=5.0)
# runs used the inputs
arrow((rx + 3.0, RB - .2), (EX + EW + .2, BOT + 5.0), st.INK2, rad=-.3)
prov(rx - 1.0, BOT + 1.6, "object (used)", ha="right", size=5.0)

# ---------------------------------------------------------------- bottom: people decide (left), agent through the MCP (right)
BY, BH = 4.0, 23.0
CY = BY + 16.0                     # chip row
box(3.0, BY, 86.0, BH, "white", st.GREY_M, .5)
person(9.0, BY + 7.0, 1.3)
txt(14.5, BY + 9.0, "People decide", 7.0, st.ACCENT, "bold")
kind_glyph(15.2, BY + 4.6, "judgement", .55)
txt(16.8, BY + 4.6, f"at the {kinds['judgement']} judgement steps; decisions return to the record", 6.0, st.INK2)
RDX = 58.0
box(RDX, CY, 24.0, 4.6, st.FILL["accent"], st.ACCENT, .4, .7, 3)
txt(RDX + 12.0, CY + 2.3, "record_decision", 5.4, st.INK, ha="center", family=MONO)
arrow((RDX + 12.0 + 10.0, CY + 4.7), (RDX + 22.0, DEC_Y - .2), st.ACCENT, .6)
txt(RDX + 23.2, BY + BH + 2.6, "who, why, source", 5.4, st.ACCENT)

box(95.0, BY, 85.0, BH, "white", st.GREY_M, .5)
agent(101.0, BY + 7.0, 1.3)
txt(106.5, BY + 9.0, "Agent through the ORCHID-SAGE MCP", 7.0, st.ACCENT, "bold")
txt(106.5, BY + 4.6, "runs the specific protocol step by step", 6.0, st.INK2)
cx = 106.5
for k, c in enumerate(["get_step", "run_step", "compare_outputs"]):
    cw = 3.6 + 1.7 * len(c)
    box(cx, CY, cw, 4.6, st.FILL["accent"], st.ACCENT, .4, .7, 3)
    txt(cx + cw / 2, CY + 2.3, c, 5.4, st.INK, ha="center", family=MONO)
    if c == "run_step":
        RUNX = cx + cw / 2
    if k < 2:
        arrow((cx + cw + .3, CY + 2.3), (cx + cw + 2.6, CY + 2.3), st.INK2)
    cx += cw + 2.9
arrow((RUNX, CY + 4.7), (rx + rw - 8.0, RB - .2), st.ACCENT, .6)
txt(RUNX + 0.5, BY + BH + 2.6, "writes run cards", 5.4, st.ACCENT)

fig.savefig(ROOT / "figs/fig_crni_standard.pdf")
fig.savefig(ROOT / "figs/fig_crni_standard.png", dpi=600)
probs = check_layout(fig, "fig_crni_standard")
plt.close(fig)

# ================================================================ one-column version (89 mm wide): stages top to bottom
# PI 7 Nov: "Too much text" -> each box carries a title and one number; arrows without PROV labels; the PROV predicates,
# protocol ids, hashes and the MCP tool names go to the caption.
W, H = 89., 80.
fig = plt.figure(figsize=(st.W1, st.W1 * H / W))   # 89-unit layout drawn at the single column (83 mm); text at final pt
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
X0, X1 = 2.0, 84.6                              # boxes span X0 .. X1; the hadPlan line runs at X1 + 2.0
XW = X1 - X0
GAP = 6.5


def title(x, y, s_, ver=None, xr=None):
    txt(x, y, s_, 7.0, st.ACCENT, "bold")
    if ver:
        txt(xr, y, ver, 6.0, st.INK2, ha="right")


def big(x, y, s_, ha="left", color=st.INK):
    txt(x, y, s_, 7.0, color, "bold", ha=ha)


# 1 general protocol: one glyph per step, grouped by section
GT, GH = H - 1.0, 15.0
GB = GT - GH
box(X0, GB, XW, GH, st.FILL["accent"], st.ACCENT, .75)
title(X0 + 1.8, GT - 3.0, "General protocol", GEN["version"], X1 - 1.8)
big(X0 + 1.8, GT - 7.4, f"{n_steps} steps")
gx = X0 + 19.0
for sid, ks in secs:
    for k in ks:
        kind_glyph(gx, GT - 7.4, k, .45)
        gx += 1.18
    gx += .9
assert gx < X1, gx
lx = X0 + 19.0
for k, dx in (("deterministic", 0.0), ("numerical", 9.0), ("judgement", 18.0)):
    kind_glyph(lx + dx, GT - 11.6, k, .55)
    txt(lx + dx + 1.4, GT - 11.6, f"{kinds[k]}", 6.0, st.INK2)

# 2 specific protocol
ST, SH = GB - GAP, 9.0
SB_ = ST - SH
box(X0, SB_, XW, SH, st.FILL["accent"], st.ACCENT, .75)
title(X0 + 1.8, ST - 3.0, "Specific protocol", SPEC["version"], X1 - 1.8)
big(X0 + 1.8, ST - 6.6, f"{n_files} inputs · {n_dec} decisions")
arrow((X0 + 30.0, ST + .1), (X0 + 30.0, GB - .1), st.ACCENT, .7)

# 3 evidence (left) <- run cards (right)
RT = SB_ - GAP
RH1, OFF = 10.0, 1.8
RX = X0 + 30.0
RW1 = X1 - RX - OFF
for k in range(3, 0, -1):
    box(RX + k * OFF / 3, RT - RH1 - OFF + k * OFF / 3, RW1, RH1, "white", st.GREY_M, .45, 1.0, 2)
RTOP = RT - OFF
RBOT = RTOP - RH1
box(RX, RBOT, RW1, RH1, "white", st.INK2, .55, 1.0, 3)
title(RX + 1.8, RTOP - 3.0, "Run cards")
big(RX + 1.8, RTOP - 6.8, f"{n_cards} cards")
ax.add_patch(FancyArrowPatch((RX + RW1 - 9.0, RBOT + 3.6), (RX + RW1 - 4.0, RBOT + 3.6), arrowstyle="-|>",
                             mutation_scale=4.5, color=st.INK2, lw=.45, connectionstyle="arc3,rad=-1.2", zorder=6))
box(X0, RBOT, 23.0, RH1, st.FILL["experimental"], st.C_EXP, .55)
txt(X0 + 1.6, RTOP - 3.0, "Evidence", 7.0, st.INK, "bold")
big(X0 + 1.6, RTOP - 6.8, f"{NSTATES} states")
arrow((RX - .2, RBOT + RH1 / 2), (X0 + 23.2, RBOT + RH1 / 2), st.INK2)
arrow((RX + 20.0, RT + .1), (RX + 20.0, SB_ - .1), st.INK2)
HX = X1 + 2.0                                   # run -> general step (hadPlan), along the right margin
ax.plot([X1 + .1, HX, HX], [RTOP - 4.0, RTOP - 4.0, GB + GH / 2], color=st.INK2, lw=.5, zorder=6)
arrow((HX, GB + GH / 2), (X1 + .2, GB + GH / 2), st.INK2)

# 4 package: TDB, dashboard, RO-Crate
PT = RBOT - GAP
PH_ = 11.0
box(X0, PT - PH_, XW, PH_, st.FILL["accent"], st.ACCENT, .75)
title(X0 + 1.8, PT - 3.0, "Package")
labs = ["TDB", "Dashboard", "RO-Crate"]
PW = (XW - 4.0) / 3
for k, l in enumerate(labs):
    xx = X0 + 2.0 + k * PW + 1.0
    doc(xx + 1.0, PT - PH_ + 1.4, 3.0, 3.8)
    txt(xx + 5.2, PT - PH_ + 3.3, l, 7.0, st.INK, "bold")
arrow((RX + 8.0, PT + .1), (RX + 8.0, RBOT - .1), st.INK2)

# 5 people decide (judgement steps) | agent runs the steps through the MCP
BT = PT - PH_ - 2.0
BH_ = 8.0
BB = BT - BH_
HALF = X0 + XW / 2
box(X0, BB, XW / 2 - .8, BH_, "white", st.GREY_M, .5)
person(X0 + 4.0, BB + 3.3, 1.0)
txt(X0 + 7.6, BB + BH_ / 2, "People decide", 7.0, st.ACCENT, "bold")
kind_glyph(X0 + XW / 2 - 4.4, BB + BH_ / 2, "judgement", .75)
txt(X0 + XW / 2 - 3.0, BB + BH_ / 2, str(kinds["judgement"]), 6.0, st.INK2)
box(HALF + .8, BB, XW / 2 - .8, BH_, "white", st.GREY_M, .5)
agent(HALF + 4.6, BB + 3.6, 1.0)
txt(HALF + 8.2, BB + BH_ / 2, "Agent runs (MCP)", 7.0, st.ACCENT, "bold")
assert BB > .4, BB
fig.savefig(ROOT / "figs/fig_crni_standard_1col.pdf")
fig.savefig(ROOT / "figs/fig_crni_standard_1col.png", dpi=600)
probs += check_layout(fig, "fig_crni_standard_1col")
src = {"figure": "fig_crni_standard", "kind": "schematic (no ORCHID records plotted; no badge)",
       "sources": [{"path": tilde(p), "sha256": sha(p), "role": k} for k, p in F.items()],
       "counts": {"general_sections": len(secs), "general_steps": n_steps, "step_kinds": dict(kinds),
                  "specific_input_files": n_files, "runs": len(runs), "run_cards": n_cards, "decisions": n_dec,
                  "decisions_by_who": dict(who), "overrides": len(SPEC.get("overrides", [])), "states": NSTATES,
                  "runs_with_general_step (prov:hadPlan)": n_hadplan, "overrides_conforming": n_conf,
                  "general_protocol": gen_id, "specific_protocol": spec_id, "crate_box": crate_out,
                  "crate_note": "nothing in the figure is read from the RO-Crate; the crate box is generic",
                  "tdb_sha256": art_sha}}
(ROOT / "figs/fig_crni_standard_sources.json").write_text(json.dumps(src, indent=1))
print(src["counts"]); print("layout problems:", len(probs))
