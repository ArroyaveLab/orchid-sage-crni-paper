#!/usr/bin/env python3
"""Gates and ranking (Cr-Ni paper, Methods 2.1): schematic, no data plotted, no badge.

(a) Gates (hard): the nine gates of orchid-calphad-fit@2.1.2 (section "gates"; unchanged since 2.1.0), each with the steps of the general protocol
    that carry it (steps[*].gates). Gates concern the integrity of the process and of the record; an assessment that fails
    one is incomplete, however well it fits.
(b) Ranking (soft): R1 plausible energies -> R2 topology -> R3 quantitative (section "ranking_criteria"), with their
    thresholds and first clause read from the YAML, the steps that apply them (steps[*].ranking_criteria) and the PI
    decision that replaced pass/fail on fits by ranking (decisions).
The gate boxes are drawn empty: no gate pass/fail status is recorded for Cr-Ni, so the figure does not claim that any
gate passed (7 Nov 2026; earlier versions drew ticked boxes).
Labels are the gate and criterion ids with underscores as spaces; every number and clause is read from the YAML.

Why a schematic: no ranking of candidate fits by R1 -> R2 -> R3 is recorded for Cr-Ni as such. The campaign records
per-step start rankings (steps/*/evaluation.json, "PLAN.md ranking (0.3)"), which in step 4c-b hold one mode (all 8 starts
with the same topology and invariants), and the step-4 variant yardsticks (results/step4_tests_comparison.json,
results/pick_rule_step4_variants.json), whose pick was a PI decision on the hinge floor, not an R1-R3 ranking.
Outputs: figs/fig_gates_ranking.{pdf,png} (drawn at 174 x 79.9 mm, a | b side by side) and figs/fig_gates_ranking_1col.{pdf,png}
(drawn at 84 x 81.2 mm, a above b, short labels only); sources in figs/fig_gates_ranking_sources.json.
"""
import json
import sys
import textwrap
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style as st  # noqa: E402
from crni_fig_common import SAGE_REPO, card, check_layout, sha, tilde  # noqa: E402

SAGE = SAGE_REPO
sys.path.insert(0, str(SAGE / "protocols/tools"))
import yamlmini  # noqa: E402

F = {"general": SAGE / "protocols/general/orchid-calphad-fit@2.1.2.yaml"}   # general protocol of the final specific protocol 1.0.4
GEN = yamlmini.load(str(F["general"]))
gen_id = f"{GEN['id']}@{GEN['version']}"
gate_at, rank_at = defaultdict(list), defaultdict(list)
for s in GEN["sections"]:
    for t in s.get("steps", []):
        for g in t.get("gates", []) or []:
            gate_at[g].append(t["id"])
        for r in t.get("ranking_criteria", []) or []:
            rank_at[r].append(t["id"])
GATES = GEN["gates"]; RANK = GEN["ranking_criteria"]
assert len(GATES) == 9 and [r["id"][:2] for r in RANK] == ["R1", "R2", "R3"]
dec = [d for d in GEN["decisions"] if "rank fits" in d["decision"]][0]


def name(i):
    return i.split("_", 1)[1].replace("_", " ")


def first_clause(r):
    s = r["text"]
    if ":" in s.split(";")[0]:
        s = s.split(":", 1)[1]
    return s.split(";")[0].strip()


MONO = st.MONO
fig = ax = None
W = H = 0.0


def canvas(w, h):
    global fig, ax, W, H
    W, H = w, h
    FW = st.W2 if w > 100 else st.W1             # layout in w-unit (mm) coordinates, drawn at the journal width:
    fig = plt.figure(figsize=(FW, FW * h / w))   # double column 171 mm or single column 83 mm; text and lines at final pt
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")


def txt(x, y, s, size=6, color=st.INK, weight="normal", ha="left", va="center", family="Arial", z=9, **kw):
    return ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va, family=family, zorder=z, **kw)


def box(x, y, w, h, fc="white", ec=st.INK2, lw=.55, r=1.0, z=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, zorder=z))


def empty_box(x, y, s=1.1):
    """An unticked check box: the gate exists, no pass/fail status is recorded for Cr-Ni."""
    ax.add_patch(Rectangle((x - s, y - s), 2 * s, 2 * s, fc="white", ec=st.ACCENT, lw=.6, zorder=8))


def gates_panel(x0, top, w, pitch, head_dx=4.0, step_size=5.5, name_size=6.0, bottom=None, sub_lines=None):
    """Panel a: heading at `top`, then the gate box; returns the y of the box bottom."""
    gt = top
    gb = gt - 4.6 - len(GATES) * pitch - .6 if bottom is None else bottom
    box(x0, gb, w, gt - gb, st.FILL["accent"], st.ACCENT, .75)
    txt(x0 + 2.0, gt - 3.0, gen_id, 5.5, st.INK, family=MONO)
    txt(x0 + w - 2.0, gt - 3.0, "checked at step", 5.5, st.INK2, ha="right")
    for k, g in enumerate(GATES):
        y = gt - 4.6 - (k + .5) * pitch
        empty_box(x0 + 3.0, y, .95 if pitch < 5 else 1.1)
        txt(x0 + 5.4, y, g["id"].split("_")[0], name_size, st.ACCENT, "bold")
        txt(x0 + 10.0, y, name(g["id"]), name_size, st.INK)
        txt(x0 + w - 2.0, y, ", ".join(gate_at[g["id"]]), step_size, st.INK2, ha="right", family=MONO)
    return gb


def ranking_panel(x0, x1, top, bottom, n_cand=19, wrap=58, letter="b", dec_lines=None):
    """Panel b between x0 and x1 (mm), from `top` down to `bottom`."""
    txt(x0 + 2.0, top, "candidate fits (all starts of a step, after polishing)", 5.5, st.INK2)
    CY = top - 3.4
    dec_lines = None
    span = (x1 - x0) - 10.0
    for k in range(n_cand):
        ax.add_patch(Circle((x0 + 5.0 + k * span / (n_cand - 1), CY), .9, fc=st.GREY_M, ec=st.INK2, lw=.3, zorder=6))
    FT = CY - 2.6
    PH = 7.0 if dec_lines else 8.0             # pick box height
    APPLIED = bottom + 1.6
    PY = APPLIED + (2.3 if dec_lines else 2.6)
    FB = PY + PH + (3.2 if dec_lines else 4.2)
    left0, right0 = x0 + 1.0, x1
    hgt = (FT - FB) / len(RANK)
    shrink = lambda yy: (FT - yy) / (FT - FB) * (right0 - left0) * .14
    cx = (left0 + right0) / 2
    for k, r in enumerate(RANK):
        yt, yb = FT - k * hgt, FT - (k + 1) * hgt
        pts = [(left0 + shrink(yt), yt), (right0 - shrink(yt), yt), (right0 - shrink(yb), yb + .6), (left0 + shrink(yb), yb + .6)]
        ax.add_patch(Polygon(pts, closed=True, fc=st.FILL["accent"] if k % 2 == 0 else "white", ec=st.ACCENT, lw=.6, zorder=3))
        lab = f"{r['id'].split('_')[0]}  {name(r['id'])}"
        if r.get("threshold") is not None:
            lab += f"  (threshold {r['threshold']:g} {r['unit']})"
        if hgt >= 10:
            txt(cx, yt - hgt * .30, lab, 6.0, st.ACCENT, "bold", ha="center")
            txt(cx, yt - hgt * .66, textwrap.fill(first_clause(r), wrap), 5.5, st.INK2, ha="center", linespacing=1.15)
        else:               # compact tiers (one-column): label, then the clause hanging below it
            txt(cx, yt - 1.9, lab, 6.0, st.ACCENT, "bold", ha="center")
            txt(cx, yt - 3.3, textwrap.fill(first_clause(r), wrap), 5.5, st.INK2, ha="center", va="top", linespacing=1.1)
    box(cx - 24.0, PY, 48.0, PH, "white", st.ACCENT, .75)
    ax.add_patch(Circle((cx - 20.5, PY + PH / 2), 1.3, fc=st.ACCENT, ec="none", zorder=6))
    txt(cx - 17.6, PY + PH / 2 + 1.4, "pick: the most reasonable fit", 6.0, st.INK, "bold")
    txt(cx - 17.6, PY + PH / 2 - 1.7, "misses are reported as notes, not rejections", 5.5, st.INK2)
    ax.add_patch(FancyArrowPatch((cx, FB + .4), (cx, PY + PH + .1), arrowstyle="-|>", mutation_scale=5, color=st.ACCENT,
                                 lw=.6, zorder=6))
    order = [t["id"] for sec in GEN["sections"] for t in sec.get("steps", [])]
    steps_r = sorted(set(sum(rank_at.values(), [])), key=order.index)
    txt(x0 + 2.0, APPLIED, "applied at " + ", ".join(steps_r), 5.5, st.INK2, family=MONO)


def save(name_):
    fig.savefig(ROOT / f"figs/{name_}.pdf")
    fig.savefig(ROOT / f"figs/{name_}.png", dpi=600)
    p = check_layout(fig, name_)
    plt.close(fig)
    return p


# ---------------------------------------------------------------- two-column version (183 x 84 mm)
canvas(183.0, 84.0)
card(ax, 1.0, 1.0, 89.5, H - 2.0, "a", "Gates (hard): integrity of process and record")
gates_panel(3.0, H - 8.4, 85.5, 7.4, bottom=3.0)
card(ax, 92.5, 1.0, 89.5, H - 2.0, "b", "Ranking (soft): the most reasonable fit")
ranking_panel(94.5, W - 3.0, H - 9.4, 1.6, n_cand=17)
probs = save("fig_gates_ranking")

# ---------------------------------------------------------------- one-column version (89 x 86 mm): a above b, minimal text
# PI 7 Nov: "Too much text" -> short labels only; step names, thresholds, clauses and the PI decision go to the caption.
canvas(89.0, 86.0)
X0, X1 = 3.0, 86.0


def width_mm(t):
    fig.canvas.draw()
    bb = t.get_window_extent()
    return (bb.x1 - bb.x0) / fig.dpi * 25.4


def centred_pair(xc, y, a_, b_, gap=1.6):
    """Bold accent id + plain name, the pair centred on xc."""
    t1 = txt(0, y, a_, 7.0, st.ACCENT, "bold"); t2 = txt(0, y, b_, 7.0, st.INK)
    w1, w2 = width_mm(t1), width_mm(t2)
    x = xc - (w1 + gap + w2) / 2
    t1.set_x(x); t2.set_x(x + w1 + gap)

GT = H - 7.6
NR = (len(GATES) + 1) // 2
GP = 5.0
GB = GT - NR * GP - 1.6
box(X0, GB, X1 - X0, GT - GB, st.FILL["accent"], st.ACCENT, .75)
for k, g in enumerate(GATES):
    col, row = divmod(k, NR)
    x = X0 + 2.6 + col * 41.5
    y = GT - 3.3 - row * GP
    empty_box(x, y, 1.1)
    txt(x + 2.4, y, g["id"].split("_")[0], 6.5, st.ACCENT, "bold")
    txt(x + 7.4, y, name(g["id"]), 6.5, st.INK)
card(ax, 1.0, GB - 2.0, 87.0, H - 1.0 - (GB - 2.0), "a", "Gates (hard)", size=6.5, z=0.1)
yb = GB - 3.5
card(ax, 1.0, 1.0, 87.0, yb - 1.0, "b", "Ranking (soft)", size=6.5, z=0.1)
CY = yb - 8.6
n_cand = 15
for k in range(n_cand):
    ax.add_patch(Circle((X0 + 6.0 + k * (X1 - X0 - 12.0) / (n_cand - 1), CY), 1.0, fc=st.GREY_M, ec=st.INK2, lw=.3, zorder=6))
FT, FB = CY - 2.8, 14.0
hgt = (FT - FB) / len(RANK)
shrink = lambda yy: (FT - yy) / (FT - FB) * (X1 - X0) * .22
cxm = (X0 + X1) / 2
for k, r in enumerate(RANK):
    yt, yb_ = FT - k * hgt, FT - (k + 1) * hgt
    pts = [(X0 + shrink(yt), yt), (X1 - shrink(yt), yt), (X1 - shrink(yb_), yb_ + .6), (X0 + shrink(yb_), yb_ + .6)]
    ax.add_patch(Polygon(pts, closed=True, fc=st.FILL["accent"] if k % 2 == 0 else "white", ec=st.ACCENT, lw=.6, zorder=3))
    centred_pair(cxm, (yt + yb_ + .6) / 2, r["id"].split("_")[0], name(r["id"]))
PY, PH = 2.8, 7.0
box(cxm - 9.0, PY, 18.0, PH, "white", st.ACCENT, .75)
ax.add_patch(Circle((cxm - 3.6, PY + PH / 2), 1.4, fc=st.ACCENT, ec="none", zorder=6))
txt(cxm - 1.2, PY + PH / 2, "pick", 7.0, st.INK, "bold")
ax.add_patch(FancyArrowPatch((cxm, FB + .4), (cxm, PY + PH + .1), arrowstyle="-|>", mutation_scale=5, color=st.ACCENT,
                             lw=.6, zorder=6))
probs += save("fig_gates_ranking_1col")

(ROOT / "figs/fig_gates_ranking_sources.json").write_text(json.dumps({
    "figure": "fig_gates_ranking", "kind": "schematic (no data; no badge)",
    "sources": [{"path": tilde(p), "sha256": sha(p), "role": k} for k, p in F.items()],
    "gates": {g["id"]: gate_at[g["id"]] for g in GATES}, "ranking": {r["id"]: rank_at[r["id"]] for r in RANK},
    "decision": dec,
    "gate_status": "none recorded for Cr-Ni; boxes drawn empty",
    "outputs": {"fig_gates_ranking": "174 x 79.9 mm, hero cards", "fig_gates_ranking_1col": "84 x 81.2 mm (a above b), minimal text; step names, thresholds, clauses and the PI decision in the caption"},
    "why_schematic": "no R1->R2->R3 ranking of candidate fits is recorded for Cr-Ni; per-step start rankings in step 4c-b are one mode; the step-4 variant comparison was decided by the PI on the hinge floor"},
    indent=1))
print("layout problems:", len(probs))
