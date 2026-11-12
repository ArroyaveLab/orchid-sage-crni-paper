#!/usr/bin/env python3
"""Fig. 4 of the Cr-Ni paper: the fit sequence one-shot -> step 2 (liquidus) -> step 3b (thermochemistry) -> step 4c-b
(solid state + exclusions, the frozen pick of crni-paper-fit-step4c-b@1.0.0), with the ORCHID experimental states of the
evidence bundle overlaid.

Reads data/crni_paper_fit_figs.json only (written by scripts/export_crni_paper_fit.py, which records the path and sha256 of
every source file: the four step TDBs, the evidence bundle, the dashboard data). The sha256 of that JSON is written into
figs/fig_crni_sequence_orchid_ids.json. Diagrams are pd4 hull mappings on pycalphad G (600-2200 K, 2 K).

States: blue (experimental) when the step's objective contains them (liquid ZPF from step 2, solid ZPF and exclusion states
from step 4), light grey when not yet used. Thermochemical data of step 3b are not phase-diagram states and are not drawn.
Hero style (orchid-brand figures.md): each panel in a rounded card with letter + short orchid heading; one key card below.
Outputs: figs/fig_crni_sequence.{pdf,png} (174 x 150 mm) and figs/fig_crni_sequence_1col.{pdf,png} (84 x 97 mm, minimal
text: no field labels or invariant notes in d, which go to the caption).
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
from crni_fig_common import card, card_note, check_layout, draw_diagram, legend_below, mm_axes, mm_canvas, sha  # noqa: E402

SRC = ROOT / "data/crni_paper_fit_figs.json"
D = json.loads(SRC.read_text())
S = D["steps"]
EV = D["evidence"]["points"]
INV = {i["reaction"]: i for i in D["invariants"]}
EUT = next(i for k, i in INV.items() if "eutectic" in k)
C2 = next(i for k, i in INV.items() if "CrNi2" in k)

# key, heading (two-column), heading (one-column), objective groups in use, previous step, colour
PANELS = [("step1", "One-shot (step 1)", "One-shot", set(), None, st.C_MODEL),
          ("step2", "Liquidus (step 2)", "Liquidus", {"liq_c"}, "step1", st.ACCENT),
          ("step3b", "Thermochemistry (step 3b)", "Thermochemistry", {"liq_c"}, "step2", st.ACCENT),
          ("step4c_b", "Solid state + exclusions (step 4c-b)", "Solid + exclusions", {"liq_c", "solid_c", "zpf_susp", "hinge"},
           "step3b", st.ACCENT)]

# positions of ZPF records: hinge states at the same (x, T) are the same observation with its exclusions
zpf_xy = {(round(p["x"], 4), round(p["T"], 1)) for p in EV if p["group"] != "hinge"}
plotted_ids = {}


def states(ax, used, label_ids, sc=1.0):
    for p in EV:
        is_hinge = p["group"] == "hinge"
        if is_hinge and (round(p["x"], 4), round(p["T"], 1)) in zpf_xy:
            if label_ids and p["group"] in used and p["orchid_ids"]:
                plotted_ids.setdefault("Experimental states of the fit (panel d)", set()).update(p["orchid_ids"])
            continue                                                         # drawn once, as its ZPF record
        on = p["group"] in used
        special = [o for o in p["orchid_ids"] if o in EUT["orchid_ids"] + C2["orchid_ids"]]
        if special:
            continue                                                         # the two invariant records are drawn below
        if is_hinge:
            m, ms, kw = "+", 1.9, dict(mew=.3)
            fc = ec = st.C_EXP if on else st.GREY_M
        elif p["kind"] == "single_phase":
            m, ms, kw = "o", 2.0, dict(mew=.4)
            fc, ec = "none", (st.C_EXP if on else st.GREY_M)
        else:
            m, ms, kw = "o", 1.6, dict(mew=0)
            fc = ec = st.C_EXP if on else st.GREY_M
        ax.plot(p["x"], p["T"], m, ms=ms * sc, mfc=fc, mec=ec, zorder=4 if on else 2, **kw)
        if on and label_ids:
            for o in p["orchid_ids"]:
                plotted_ids.setdefault("Experimental states of the fit (panel d)", set()).add(o)
    # the two ORCHID invariant records (eutectic: three-phase state; CrNi2 ordering top)
    for rec, mk, used_from in ((EUT, "^", "liq_c"), (C2, "s", "solid_c")):
        on = used_from in used
        x = next(p["x"] for p in EV if rec["orchid_ids"][0] in p["orchid_ids"])
        ax.plot(x, rec["observed_K"], mk, ms=3.2 * sc, mfc=st.C_EXP if on else "none", mec=st.C_EXP if on else st.GREY_M,
                mew=.5, zorder=6)
        if label_ids:
            plotted_ids.setdefault("ORCHID invariant records (all panels)", set()).update(rec["orchid_ids"])


def panel(ax, k, compact):
    key, _, _, used, prev, col = PANELS[k]
    s = S[key]
    if prev:
        draw_diagram(ax, S[prev], st.GREY_M, lw=.55, z=1, ls=(0, (2.2, 1.2)))
    states(ax, used, key == "step4c_b", sc=.85 if compact else 1.0)
    draw_diagram(ax, s, col, lw=.8 if compact else .9, z=5)
    ax.set_xlim(0, 1); ax.set_ylim(600, 2200)
    ax.set_xlabel(r"$x_{\mathrm{Ni}}$", labelpad=1 if compact else 2)
    ax.set_ylabel("T (K)" if compact else "Temperature (K)", labelpad=1 if compact else 2)
    if compact:
        ax.set_xticks([0, .5, 1], ["0", "0.5", "1"]); ax.set_yticks([600, 1400, 2200])
    else:
        ax.set_xticks(np.linspace(0, 1, 6)); ax.set_yticks(range(600, 2201, 400))
    if key != "step4c_b" or compact:
        return
    BB = dict(boxstyle="square,pad=0.15", fc="white", ec="none", alpha=.85)
    for txt_, x, y in (("liquid", .62, 2120), ("fcc", .86, 1200), ("bcc + fcc", .27, 1000), ("bcc + CrNi$_2$", .30, 730)):
        ax.text(x, y, txt_, fontsize=6, color=st.INK, ha="center", va="center", zorder=7, bbox=BB)
    ax.annotate("bcc", xy=(0.006, 1150), xytext=(0.075, 1150), fontsize=6, color=st.INK, ha="left", va="center", zorder=8,
                bbox=BB, arrowprops=dict(arrowstyle="-", lw=.4, color=st.INK2, shrinkA=0, shrinkB=0))
    el = s["liquid_min_line"]
    ax.annotate(f"{s['T_liquid_min']:.0f} K\n(ORCHID {EUT['observed_K']} K)", xy=(el[1], s["T_liquid_min"]),
                xytext=(0.76, 1530), fontsize=6, color=st.ACCENT, ha="center", va="top", bbox=BB,
                arrowprops=dict(arrowstyle="-", lw=.4, color=st.ACCENT, shrinkA=0, shrinkB=1), zorder=8)
    cl = s["crni2_top_line"]
    ax.annotate(f"{s['T_CrNi2_max']:.0f} K\n(ORCHID {C2['observed_K']} K)", xy=(cl[1], s["T_CrNi2_max"]),
                xytext=(0.86, 960), fontsize=6, color=st.ACCENT, ha="center", va="bottom", bbox=BB,
                arrowprops=dict(arrowstyle="-", lw=.4, color=st.ACCENT, shrinkA=0, shrinkB=1), zorder=8)


def key_handles(compact):
    L = [("one-shot TDB", Line2D([], [], color=st.C_MODEL, lw=.9)),
         ("fit, this step", Line2D([], [], color=st.ACCENT, lw=.9)),
         ("previous step", Line2D([], [], color=st.GREY_M, lw=.55, ls=(0, (2.2, 1.2)))),
         ("single-phase state", Line2D([], [], ls="none", marker="o", ms=2.6, mfc="none", mec=st.C_EXP, mew=.5)),
         ("phase-boundary state", Line2D([], [], ls="none", marker="o", ms=2.4, mfc=st.C_EXP, mec=st.C_EXP, mew=0)),
         ("exclusions only", Line2D([], [], ls="none", marker="+", ms=2.6, mec=st.C_EXP, mew=.4)),
         ("ORCHID eutectic", Line2D([], [], ls="none", marker="^", ms=3.2, mfc=st.C_EXP, mec=st.C_EXP)),
         ("ORCHID CrNi$_2$ top", Line2D([], [], ls="none", marker="s", ms=3.2, mfc=st.C_EXP, mec=st.C_EXP)),
         ("not yet fitted", Line2D([], [], ls="none", marker="o", ms=2.6, mfc=st.GREY_M, mec=st.GREY_M, mew=.5))]
    return [h for _, h in L], [l for l, _ in L]


def save(fig, name):
    fig.savefig(ROOT / f"figs/{name}.pdf")
    fig.savefig(ROOT / f"figs/{name}.png", dpi=600)
    probs = check_layout(fig, name)
    plt.close(fig)
    return probs


def two_col():
    W, H = st.W2 / st.MM, 145.5
    fig, cv = mm_canvas(W, H)
    KH, TOP, G = 8.6, 1.0, 2.0                       # key card height, top margin (no badge strip), gap
    CW, CH = (W - 2 - G) / 2, (H - TOP - 1 - KH - 2 * G) / 2
    X = (1.0, 1.0 + CW + G); Y = (1.0 + KH + G + CH + G, 1.0 + KH + G)
    for k, (key, head, _, _, _, _) in enumerate(PANELS):
        cx, cy = X[k % 2], Y[k // 2]
        card(cv, cx, cy, CW, CH, "abcd"[k], head)
        panel(mm_axes(fig, cx + 14.0, cy + 9.5, CW - 17.0, CH - 9.5 - 8.0, W, H), k, False)
        s = S[key]
        if key != "step4c_b":
            card_note(cv, cx + CW - 2.0, cy + CH - 4.0,
                      f"lowest liquid {s['T_liquid_min']:.0f} K, CrNi$_2$ to {s['T_CrNi2_max']:.0f} K", ha="right")
    card(cv, 1.0, 1.0, W - 2, KH)
    h, l = key_handles(False)
    legend_below(fig, h, l, 4.0, 1.0 + KH - 1.6, W, H, ncol=5, colsp=2.6)
    return save(fig, "fig_crni_sequence")


def one_col():
    W, H = st.W1 / st.MM, 92.5
    fig, cv = mm_canvas(W, H)
    KH, TOP, G = 10.6, 1.0, 1.5
    CW, CH = (W - 2 - G) / 2, (H - TOP - 1 - KH - 2 * G) / 2
    X = (1.0, 1.0 + CW + G); Y = (1.0 + KH + G + CH + G, 1.0 + KH + G)
    for k, (key, _, head, _, _, _) in enumerate(PANELS):
        cx, cy = X[k % 2], Y[k // 2]
        card(cv, cx, cy, CW, CH, "abcd"[k], head, size=6.5)
        panel(mm_axes(fig, cx + 10.0, cy + 7.0, CW - 12.0, CH - 7.0 - 6.6, W, H), k, True)
    card(cv, 1.0, 1.0, W - 2, KH)
    h, l = key_handles(True)
    legend_below(fig, h, l, 3.0, 1.0 + KH - 1.8, W, H, ncol=3, size=6.0, colsp=1.0)
    return save(fig, "fig_crni_sequence_1col")


two_col()
one_col()

ids = {"figure": "fig_crni_sequence", "orchid_release": "provisional (" + D["orchid_release"] + ")",
       "source_data": {"path": "data/crni_paper_fit_figs.json", "sha256": sha(SRC)},
       "specific_protocol": "crni-paper-fit-step4c-b@1.0.0",
       "outputs": {"fig_crni_sequence": "174 x 150 mm, panels a-d in hero cards, key card below",
                   "fig_crni_sequence_1col": "84 x 97 mm, same panels and key, minimal text"},
       "labels": {k: sorted(v) for k, v in plotted_ids.items()},
       "state_ids": sorted({sid for p in EV for sid in p["state_ids"]}),
       "counts": {"states_in_bundle": D["evidence"]["n_states"],
                  "states_with_orc_id": sum(1 for p in EV if p["orchid_ids"]),
                  "states_without_orc_id": sum(1 for p in EV if not p["orchid_ids"])},
       "note": "All 695 states of the evidence bundle crni-paper-fit-step4c-b@1.0.0 are experimental. States without an ORC id "
               "come from ESPEI-format datasets or campaign-added exclusions and are pending intake (v2027.01)."}
(ROOT / "figs/fig_crni_sequence_orchid_ids.json").write_text(json.dumps(ids, indent=1))
print({k: s_["T_liquid_min"] for k, s_ in S.items()}, {k: s_["T_CrNi2_max"] for k, s_ in S.items()})
