#!/usr/bin/env python3
"""Fig. 5 of the Cr-Ni paper: panels of the assessment dashboard of crni-paper-fit-step4c-b@1.0.0 as static figures.

Reads (paths and sha256 recorded in figs/fig_crni_dashboard_orchid_ids.json):
  orchid-sage:protocols/dashboards/crni-paper-fit-step4c-b-1.0.0/dashboard_data.json  (trajectory, projection)
  <campaigns>/crni-paper-fit-20261106/results/uq/laplace_step4c_b.draws.npy                 (1000 Laplace-mixture draws)
  <campaigns>/crni-paper-fit-20261106/results/uq/laplace_step4c_b.json                      (mode centres, weights)
(a) end objective of every start per step (steps 2-3b record start and end only); (b) step 4c-b, every evaluation of the
8 starts; (c) parameter traces along the lineage one-shot -> step 2 s7 -> step 3b s1 -> step 4c-b s4, in units of the prior
sd (the PCA scale); (d) the dashboard's fixed PCA basis: the lineage path coloured by topology class, the other starts, the
Laplace draws and the two mode centres. The draws are projected here and checked against the dashboard's uq_points.
Output: figs/fig_crni_dashboard.{pdf,png}, 183 x 118 mm, hero cards (letter + orchid heading, legends below the axes).
No ORCHID records are plotted (objective, parameters, draws), so no badge (orchid-brand figures.md).
"""
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style as st  # noqa: E402
from crni_fig_common import RUNS, SAGE_REPO, card, check_layout, legend_below, mm_axes, mm_canvas, sha, tilde  # noqa: E402

DASH = SAGE_REPO / "protocols/dashboards/crni-paper-fit-step4c-b-1.0.0/dashboard_data.json"
DRAWS = RUNS / "crni-paper-fit-20261106/results/uq/laplace_step4c_b.draws.npy"
LAP = RUNS / "crni-paper-fit-20261106/results/uq/laplace_step4c_b.json"
D = json.loads(DASH.read_text())
TR, PR = D["trajectory"], D["projection"]
L = json.loads(LAP.read_text())
B, CEN, SC = np.array(PR["basis"]), np.array(PR["center"]), np.array(PR["scale"])


def proj(th):
    return ((np.atleast_2d(np.asarray(th, float)) - CEN) / SC) @ B


dr = proj(np.load(DRAWS))
ref = np.array([q["xy"] for q in PR["uq_points"] if q["kind"] == "draw"])
assert np.max(np.abs(dr - ref)) < 1e-4, "draw projection differs from the dashboard"
runs = TR["runs"]
run = lambda step, start: next(r for r in runs if r["step"] == step and r["start"] == start)
PICKS = {s["step"]: s["pick"] for s in D["steps"]}
STEPS = [("step2_liquidus", "2"), ("step3_thermo", "3\n(failed)"), ("step3b_thermo_crni2free", "3b"),
         ("step4c_b_hingefloor", "4c-b")]

W, H = st.W2 / st.MM, 118.0
fig, cv = mm_canvas(W, H)
G = 2.0
DW = 70.0                                           # card d width
LW = W - 2.0 - G - DW                               # left block width
AW = 42.0                                           # card a width
TH = 56.0                                           # top-row height
YT = H - 1.0 - TH
CH = YT - G - 1.0
XD = 1.0 + LW + G
card(cv, 1.0, YT, AW, TH, "a", "End of every start")
card(cv, 1.0 + AW + G, YT, LW - AW - G, TH, "b", "Step 4c-b evaluations")
card(cv, 1.0, 1.0, LW, CH, "c", "Parameters along the lineage")
card(cv, XD, 1.0, DW, H - 2.0, "d", "Path in parameter space")
axa = mm_axes(fig, 14.0, YT + 18.5, AW - 16.0, TH - 18.5 - 8.0, W, H)
BX = 1.0 + AW + G
axb = mm_axes(fig, BX + 13.0, YT + 18.5, LW - AW - G - 16.0, TH - 18.5 - 8.0, W, H)
CW_ = (LW - 14.0 - 3 * 9.0 - 3.0) / 4
axc = [mm_axes(fig, 14.0 + k * (CW_ + 9.0), 1.0 + 15.5, CW_, CH - 15.5 - 11.0, W, H) for k in range(4)]
axd = mm_axes(fig, XD + 12.0, 1.0 + 30.0, DW - 15.0, H - 2.0 - 30.0 - 8.0, W, H)

# (a) end objectives per step
for k, (step, lab) in enumerate(STEPS):
    rs = [r for r in runs if r["step"] == step]
    ends = [(r["start"], r["points"][-1]["objective"]) for r in rs if r["points"][-1]["objective"] is not None]
    xs = k + np.linspace(-.18, .18, len(ends))
    for x, (s0, v) in zip(xs, sorted(ends, key=lambda e: e[1])):
        pick = s0 == PICKS[step]
        axa.plot(x, -v, "o", ms=3 if pick else 2.2, mfc=st.ACCENT if pick else "none", mec=st.ACCENT if pick else st.INK2,
                 mew=.5, zorder=4 if pick else 3)
axa.set_xticks(range(len(STEPS)), [s[1] for s in STEPS], fontsize=6)
axa.set_xlabel("Step")
axa.set_ylim(0, None)
axa.set_xlim(-.5, len(STEPS) - .5)
axa.set_ylabel("−log posterior")
legend_below(fig, [Line2D([], [], ls="none", marker="o", ms=3, mfc=st.ACCENT, mec=st.ACCENT, mew=.5),
                   Line2D([], [], ls="none", marker="o", ms=2.2, mfc="none", mec=st.INK2, mew=.5)],
             ["pick", "other starts"], 4.0, YT + 6.6, W, H, ncol=2)

# (b) step 4c-b every evaluation
for r in [r for r in runs if r["step"] == "step4c_b_hingefloor"]:
    pts = [p for p in r["points"] if p["objective"] is not None]
    e = np.array([p["eval"] for p in pts]); v = -np.array([p["objective"] for p in pts])
    pick = r.get("is_pick")
    axb.plot(e, v, color=st.ACCENT if pick else st.GREY_M, lw=.9 if pick else .5, zorder=4 if pick else 2)
    for p in pts:
        if p.get("topology_class") == "ok":
            axb.plot(p["eval"], -p["objective"], "o", ms=1.6, mfc=st.INK, mec="none", zorder=5)
        elif p.get("topology_class") == "wrong":
            axb.plot(p["eval"], -p["objective"], "x", ms=1.8, mec=st.INK2, mew=.4, zorder=5)
axb.set_yscale("log")
axb.set_ylim(4.5e3, None)
axb.set_xlabel("Evaluation"); axb.set_ylabel("−log posterior")
legend_below(fig, [Line2D([], [], color=st.ACCENT, lw=.9), Line2D([], [], color=st.GREY_M, lw=.5),
                   Line2D([], [], ls="none", marker="o", ms=1.6, mfc=st.INK, mec="none"),
                   Line2D([], [], ls="none", marker="x", ms=1.8, mec=st.INK2, mew=.4)],
             ["s4 (pick)", "other 7 starts", "accepted topology", "wrong topology"], BX + 3.0, YT + 9.4, W, H, ncol=2)

# (c) parameter traces along the lineage, in prior-sd units relative to the one-shot
one = np.array(TR["oneshot_theta"])
lin = [("step2_liquidus", PICKS["step2_liquidus"]), ("step3b_thermo_crni2free", PICKS["step3b_thermo_crni2free"]),
       ("step4c_b_hingefloor", PICKS["step4c_b_hingefloor"])]
xs, ths, seg_x, offs = [0.0], [one], [], 0.0
for step, start in lin:
    r = run(step, start)
    pts = r["points"]
    e = np.array([p["eval"] for p in pts], float)
    seg_x.append((offs, offs + e[-1], step))
    xs += list(offs + e); ths += [np.array(p["theta"]) for p in pts]
    offs += e[-1]
xs = np.array(xs); TH = (np.array(ths) - one) / SC
labels, phases = TR["parameter_labels"], TR["phase_of_parameter"]
lim = np.max(np.abs(TH)) * 1.08
for k, ph in enumerate(["LIQUID", "BCC_A2", "FCC_A1", "CRNI2"]):
    ax = axc[k]
    ax.set_ylim(-lim, lim)
    for j in [j for j, p in enumerate(phases) if p == ph]:
        lab = labels[j]
        col = st.INK2 if lab.startswith("L1") else st.INK          # L0 and CrNi2 terms ink, L1 terms grey
        ls = "-" if lab.endswith("_a") else (0, (2, 1))            # a terms solid, b (T) terms dashed
        ax.plot(xs, TH[:, j], color=col, lw=.6, ls=ls)
    js = sorted([j for j, p in enumerate(phases) if p == ph], key=lambda j: TH[-1, j])
    ylab, last = [], -9
    for j in js:                                               # end labels, pushed apart by at least 0.11 sd
        y = max(TH[-1, j], last + 0.11); ylab.append(y); last = y
    for j, y in zip(js, ylab):
        lab = labels[j]
        ax.text(xs[-1] * 1.03, y, lab.replace("_", " ").replace("liq", "").replace("bcc", "").replace("fcc", "")
                .replace("CrNi2 ", ""), fontsize=5.2, color=st.INK2 if lab.startswith("L1") else st.INK, va="center")
    for a0, a1, step in seg_x:
        ax.axvline(a1, color=st.GREY_L, lw=.5, zorder=0)
    ax.axhline(0, color=st.GREY_M, lw=.4, zorder=0)
    ax.set_xlim(0, xs[-1] * 1.22)
    ax.set_title({"LIQUID": "liquid", "BCC_A2": "bcc", "FCC_A1": "fcc", "CRNI2": "CrNi$_2$"}[ph], fontsize=6.5, pad=2,
                 fontweight="bold", color=st.INK)
    ax.set_xticks([(a0 + a1) / 2 for a0, a1, _ in seg_x], ["2", "3b", "4c-b"], fontsize=6)
    ax.tick_params(axis="x", length=0)
    if k:
        ax.set_yticklabels([])
    else:
        ax.set_ylabel("Δθ / prior sd")
axc[1].set_xlabel("Step", x=1.0 + 4.5 / CW_)
legend_below(fig, [Line2D([], [], color=st.INK, lw=.6), Line2D([], [], color=st.INK2, lw=.6),
                   Line2D([], [], color=st.INK, lw=.6), Line2D([], [], color=st.INK, lw=.6, ls=(0, (2, 1)))],
             ["L0 and CrNi$_2$ terms", "L1 terms", "a (constant)", "b (T term)"], 4.0, 1.0 + 6.4, W, H, ncol=4, colsp=2.0)

# (d) PCA path
ax = axd
ax.scatter(dr[:, 0], dr[:, 1], s=1.2, c=st.ACCENT, alpha=.25, lw=0, zorder=1, rasterized=True)
off_scale = []
for r in runs:
    if r["step"] in ("step2_liquidus", "step3_thermo", "step3b_thermo_crni2free") and r["points"][-1]["objective"] is not None:
        xy = proj(r["points"][-1]["theta"])[0]
        if xy[0] < -1.0:
            off_scale.append((r["step"], r["start"], xy.tolist())); continue
        ax.plot(*xy, "o", ms=1.8, mfc="none", mec=st.GREY_M, mew=.4, zorder=2)
    if r["step"] == "step4c_b_hingefloor" and not r.get("is_pick"):
        P = proj([p["theta"] for p in r["points"]])
        ax.plot(P[:, 0], P[:, 1], color=st.GREY_M, lw=.4, zorder=2)
path = proj(ths)
ax.plot(path[:, 0], path[:, 1], color=st.INK2, lw=.6, zorder=3)
cls = ["wrong"] + [p.get("topology_class") for step, start in lin for p in run(step, start)["points"]]
for (x, y), c in zip(path, cls):
    if c == "ok":
        ax.plot(x, y, "o", ms=2.2, mfc=st.INK, mec="none", zorder=5)
    elif c == "wrong":
        ax.plot(x, y, "x", ms=2.6, mec=st.INK2, mew=.5, zorder=5)
for m in [q for q in PR["uq_points"] if q["kind"] == "mode"]:
    ax.plot(*m["xy"], "D", ms=3.2, mfc=st.ACCENT, mec="white", mew=.4, zorder=6)
w = dict(zip(L["weights"]["names"], L["weights"]["laplace"]))
nodes = [("one-shot", path[0], (-10, -10)), ("step 2 end", proj(run(*lin[0])["points"][-1]["theta"])[0], (-8, -4)),
         ("step 3b end", proj(run(*lin[1])["points"][-1]["theta"])[0], (8, -6)),
         ("pick", proj(run(*lin[2])["points"][-1]["theta"])[0], (-6, 16))]
for lab, xy, off in nodes:
    ax.annotate(lab, xy=xy, xytext=off, textcoords="offset points", fontsize=6,
                color=st.ACCENT if "pick" in lab else st.INK, ha="right" if off[0] < 0 else "left",
                arrowprops=dict(arrowstyle="-", lw=.35, color=st.INK2, shrinkA=0, shrinkB=1))
ev = PR["explained_variance_ratio"]
ax.set_xlabel(f"PC 1 ({100 * ev[0]:.0f} % of variance)"); ax.set_ylabel(f"PC 2 ({100 * ev[1]:.0f} % of variance)")
ax.set_xlim(-1.0, 1.55); ax.set_ylim(-1.15, 0.85)
if off_scale:
    ax.annotate(f"{len(off_scale)} step-3 ends\nat PC 1 ≈ " + f"{np.mean([o[2][0] for o in off_scale]):.1f}".replace("-", "−"), xy=(-1.0, -0.95),
                xytext=(-0.93, -0.95), fontsize=5.5, color=st.INK2, va="center",
                arrowprops=dict(arrowstyle="<-", lw=.4, color=st.INK2, shrinkA=0, shrinkB=0))
legend_below(fig, [Line2D([], [], color=st.INK2, lw=.6),
                   Line2D([], [], ls="none", marker="o", ms=2.2, mfc=st.INK, mec="none"),
                   Line2D([], [], ls="none", marker="x", ms=2.6, mec=st.INK2, mew=.5),
                   Line2D([], [], color=st.GREY_M, lw=.4),
                   Line2D([], [], ls="none", marker="o", ms=1.8, mfc="none", mec=st.GREY_M, mew=.4),
                   Line2D([], [], ls="none", marker="o", ms=2, mfc=st.ACCENT, mec="none", alpha=.4),
                   Line2D([], [], ls="none", marker="D", ms=3.2, mfc=st.ACCENT, mec="white", mew=.4)],
             ["lineage path", "accepted topology", "wrong topology", "other 4c-b starts", "other starts, 2–3b",
              f"Laplace draws ({len(dr)})", "mode centres"], XD + 3.0, 1.0 + 19.0, W, H, ncol=2, colsp=1.0)

for ext in ("pdf", "png"):
    fig.savefig(ROOT / f"figs/fig_crni_dashboard.{ext}", dpi=600 if ext == "png" else None)
check_layout(fig, "fig_crni_dashboard")

ids = {"figure": "fig_crni_dashboard", "orchid_release": "provisional (" + D["orchid_release"] + ")",
       "specific_protocol": D["specific_protocol"],
       "inputs": [{"path": tilde(p), "sha256": sha(p)} for p in (DASH, DRAWS, LAP)],
       "labels": {}, "note": "No ORCHID records are plotted: the panels show the fit's objective, parameters and draws. The "
                              "objective is computed over the 695 states of the evidence bundle crni-paper-fit-step4c-b@1.0.0 "
                              "(ORC ids in fig_crni_sequence_orchid_ids.json).",
       "checks": {"draw_projection_max_abs_diff_vs_dashboard": float(np.max(np.abs(dr - ref)))},
       "off_scale_in_panel_d": off_scale}
(ROOT / "figs/fig_crni_dashboard_orchid_ids.json").write_text(json.dumps(ids, indent=1))
print("pick objective", run(*lin[2])["points"][-1]["objective"], "weights", w)
