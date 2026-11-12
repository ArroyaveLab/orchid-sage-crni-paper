#!/usr/bin/env python3
"""Cr-Ni PhaseForge energetics (computed results only).

a  bcc (A2) and fcc (A1) SQS mixing enthalpies vs x_Ni, relative to the same-lattice MLIP pure elements (the PhaseForge/sqs2tdb
   convention), protocol value = volume + ions relaxed (shape fixed); error bars = staged interval [fully relaxed, unrelaxed];
   both MLIPs; L0, L1 Redlich-Kister curves used in the one-shot TDB; ORCHID DFT records (same reference convention) with ids.
b  liquid mixing enthalpy from MLIP MD (1900 K, 2200 K) with its RK fit used in the TDB (2200 K).
c  Pt2Mo-type CrNi2 (stoichiometric compound in the TDB) vs the disordered fcc SQS lower hull (fcc Cr, fcc Ni references);
   L12, L10, D022 are computed but not used (PI 6 Nov) and not shown.
Hero style (orchid-brand figures.md): panels in rounded cards with letter + short orchid heading, legends below the axes,
no badge or logo (Digital Discovery; the DFT records of a are ORCHID records, release v2026.10). RK values, potentials and units of the legend text
are in the caption. Outputs: figs/fig_crni_energetics.{pdf,png} (174 x 80 mm) and figs/fig_crni_energetics_1col.{pdf,png}
(84 x 96 mm). Run with the fit interpreter (ESPEI gradient PR 9039ea2 + pycalphad).
"""
from pathlib import Path
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
import crni_pf_data as D  # noqa: E402
from crni_fig_common import card, check_layout, legend_below, mm_axes, mm_canvas  # noqa: E402

RELEASE = "v2026.10"            # CR-NI records of the orchid-data release (orchid-literature 2026-10-23, released 28 Oct 2026)
MK = {"BCC_A2": "s", "FCC_A1": "o"}
MCOL = {D.MAIN: st.INK, "GRACE-2L-OMAT": st.GREY_M}
UNIT = r"kJ mol$^{-1}$"


def rk(x, L):
    x = np.asarray(x)
    return x * (1 - x) * sum(l * (1 - 2 * x) ** k for k, l in enumerate(L))


def panel_a(a, compact):
    tdb = D.res("oneshot_tdb.json") if (D.RES / "oneshot_tdb.json").exists() else None
    xx = np.linspace(0, 1, 201)
    for model in (D.MAIN, "GRACE-2L-OMAT"):
        s = D.solids(model)
        if not s:
            continue
        off = 0.004 if model != D.MAIN else 0.0
        for lat in ("BCC_A2", "FCC_A1"):
            t = s["phases"][lat]["table"]
            x = np.array([q["x_Ni"] for q in t]) + off
            y = np.array([q["H_mix_s2_mean"] for q in t])
            lo = y - np.array([q["H_mix_s3_mean"] for q in t]); hi = np.array([q["H_mix_s0_mean"] for q in t]) - y
            ms = (3.2 if model == D.MAIN else 2.6) * (.85 if compact else 1)
            a.errorbar(x, y, yerr=[np.clip(lo, 0, None), np.clip(hi, 0, None)], fmt=MK[lat], ms=ms,
                       mfc=MCOL[model] if lat == "BCC_A2" else "white", mec=MCOL[model], ecolor=MCOL[model], elinewidth=0.5,
                       capsize=1.2, capthick=0.5, lw=0, zorder=4 if model == D.MAIN else 3)
        if model == D.MAIN:
            for lat in ("BCC_A2", "FCC_A1"):
                L = [s["phases"][lat]["RK_s2_J_mol"]["L0"] / 1000, s["phases"][lat]["RK_s2_J_mol"]["L1"] / 1000]
                if tdb:
                    L = [v / 1000 for v in tdb["solid_L_J_mol"][lat]]
                a.plot(xx, rk(xx, L), color=st.C_MODEL, lw=0.8, ls="-" if lat == "BCC_A2" else "--", zorder=2)
    dft_ids = {}
    for lat in ("BCC_A2", "FCC_A1"):
        recs = D.orchid_mixing(lat)
        for r in recs:
            k = len(dft_ids) + 1; dft_ids[f"D{k}"] = r
            a.plot(r["x_Ni"], r["value"], MK[lat], ms=3.4 if not compact else 3.0, mfc=st.C_LITDFT if lat == "BCC_A2" else "white",
                   mec=st.C_LITDFT, mew=0.8, zorder=5)
            same_x = [q for q in recs if q["x_Ni"] == r["x_Ni"]]
            left = len(same_x) > 1 and r["value"] > min(q["value"] for q in same_x)    # two records at one x: label one left
            dx, dy = (-3, 0) if left else (3, 2 if lat == "BCC_A2" else -5)
            a.annotate(f"D{k}", (r["x_Ni"], r["value"]), xytext=(dx, dy), textcoords="offset points", fontsize=5,
                       color=st.C_LITDFT, ha="right" if left else "left", va="center" if left else "baseline")
    a.axhline(0, color=st.GREY_M, lw=0.4, zorder=0)
    a.set_xlabel(r"$x_{\mathrm{Ni}}$"); a.set_ylabel(r"$\Delta H_{\mathrm{mix}}$ (" + UNIT + ")")
    a.set_xlim(0, 1); a.set_ylim(-19, 14)
    return dft_ids


def panel_b(b, compact):
    tdb = D.res("oneshot_tdb.json") if (D.RES / "oneshot_tdb.json").exists() else None
    xx = np.linspace(0, 1, 201)
    p = D.RES / "liquid_checks_enthalpy.json"
    if p.exists():
        h = D.res("liquid_checks_enthalpy.json")["H_mix"]
        for T, col, mk in ((2200, st.INK, "o"), (1900, st.INK2, "s")):
            q = sorted([v for v in h.values() if v["T_K"] == T], key=lambda v: v["x_Ni"])
            if not q:
                continue
            x = [0] + [v["x_Ni"] for v in q] + [1]; y = [0] + [v["H_mix_kJ_mol_atom"] for v in q] + [0]
            e = [0] + [v["H_mix_SE_kJ_mol_atom"] for v in q] + [0]
            fl = [True] + [v["all_liquid"] for v in q] + [True]
            for xi, yi, ei, ok in zip(x, y, e, fl):
                b.errorbar(xi, yi, yerr=ei, fmt=mk, ms=3.2 if not compact else 2.8, mfc=col if ok else "white", mec=col, ecolor=col,
                           elinewidth=0.5, capsize=1.2)
        if tdb:
            b.plot(xx, rk(xx, [v / 1000 for v in tdb["liquid_a_J_mol"]]), color=st.C_MODEL, lw=0.8)
    b.axhline(0, color=st.GREY_M, lw=0.4, zorder=0)
    b.set_xlabel(r"$x_{\mathrm{Ni}}$"); b.set_ylabel(r"$\Delta H_{\mathrm{mix}}^{\mathrm{liq}}$ (" + UNIT + ")")
    b.set_xlim(0, 1); b.set_ylim(-5.6, 2.8)


def panel_c(c, compact):
    s = D.solids(D.MAIN)
    fo = s["phases"]["FCC_A1"]; t = fo["table"]
    hx = np.array([0.0] + [q["x_Ni"] for q in t] + [1.0]); hy = np.array([0.0] + [q["H_mix_s2_mean"] for q in t] + [0.0])
    lo = []
    for pt in sorted(zip(hx, hy)):
        while len(lo) >= 2 and (lo[-1][0] - lo[-2][0]) * (pt[1] - lo[-2][1]) - (lo[-1][1] - lo[-2][1]) * (pt[0] - lo[-2][0]) <= 0:
            lo.pop()
        lo.append(pt)
    c.errorbar(hx[1:-1], hy[1:-1], yerr=[np.clip(hy[1:-1] - np.array([q["H_mix_s3_mean"] for q in t]), 0, None),
                                         np.clip(np.array([q["H_mix_s0_mean"] for q in t]) - hy[1:-1], 0, None)],
               fmt="o", ms=2.6, mfc="white", mec=st.INK, ecolor=st.GREY_M, elinewidth=0.4, capsize=1)
    c.plot([q[0] for q in lo], [q[1] for q in lo], color=st.INK2, lw=0.6)
    r = [v for k, v in s["phases"]["FCC_ORDERED"]["cells"].items() if "Pt2Mo" in k][0]
    y = r["stages"]["s2_volume_ions"]["H_form_fcc_ref_kJ_mol_atom"]
    c.errorbar(r["x_Ni"], y, yerr=[[max(y - r["stages"]["s3_full"]["H_form_fcc_ref_kJ_mol_atom"], 0)],
                                   [max(r["stages"]["s0_unrelaxed"]["H_form_fcc_ref_kJ_mol_atom"] - y, 0)]],
               fmt="*", ms=5, color=st.INK, elinewidth=0.5, capsize=1.2)
    c.axhline(0, color=st.GREY_M, lw=0.4, zorder=0); c.set_xlim(0, 1)
    c.set_xlabel(r"$x_{\mathrm{Ni}}$"); c.set_ylabel(r"$\Delta H$ vs fcc Cr, fcc Ni (" + UNIT + ")")


def handles():
    a = ([Line2D([], [], marker="s", ls="", ms=3, mfc=st.INK, mec=st.INK), Line2D([], [], marker="o", ls="", ms=3, mfc="white", mec=st.INK),
          Line2D([], [], marker="s", ls="", ms=2.6, mfc=st.GREY_M, mec=st.GREY_M),
          Line2D([], [], color=st.C_MODEL, lw=.8), Line2D([], [], color=st.C_MODEL, lw=.8, ls="--"),
          Line2D([], [], marker="s", ls="", ms=3, mfc=st.C_LITDFT, mec=st.C_LITDFT)],
         ["bcc SQS", "fcc SQS", "second MLIP", "bcc, one-shot TDB", "fcc, one-shot TDB", "ORCHID DFT (D1–D7)"])
    b = ([Line2D([], [], marker="o", ls="", ms=3, color=st.INK), Line2D([], [], marker="s", ls="", ms=3, color=st.INK2),
          Line2D([], [], color=st.C_MODEL, lw=.8)], ["MD, 2200 K", "MD, 1900 K", "one-shot TDB"])
    c = ([Line2D([], [], marker="o", ls="", ms=2.6, mfc="white", mec=st.INK), Line2D([], [], color=st.INK2, lw=.6),
          Line2D([], [], marker="*", ls="", ms=5, color=st.INK)], ["fcc SQS", "fcc lower hull", "Pt$_2$Mo-type CrNi$_2$"])
    return a, b, c


def save(fig, name):
    fig.savefig(ROOT / f"figs/{name}.pdf")
    fig.savefig(ROOT / f"figs/{name}.png", dpi=600)
    probs = check_layout(fig, name)
    plt.close(fig)
    return probs


def two_col():
    W, H = st.W2 / st.MM, 75.5
    fig, cv = mm_canvas(W, H)
    TOP, G = 1.0, 2.0
    CW = [72.0, 0.0, 0.0]
    CW[1] = CW[2] = (W - 2 - 2 * G - CW[0]) / 2
    X = [1.0, 1.0 + CW[0] + G, 1.0 + CW[0] + CW[1] + 2 * G]
    CH = H - TOP - 1.0
    heads = ("Solid solutions", "Liquid", "CrNi$_2$ and the fcc hull")
    LG = (14.5, 11.0, 11.0)                                            # legend block height below the x label (mm)
    AX = []
    for k in range(3):
        card(cv, X[k], 1.0, CW[k], CH, "abc"[k], heads[k])
        AX.append(mm_axes(fig, X[k] + 13.0, 1.0 + 8.0 + LG[k], CW[k] - 15.5, CH - 8.0 - LG[k] - 8.0, W, H))
    ids = panel_a(AX[0], False); panel_b(AX[1], False); panel_c(AX[2], False)
    for k, (h, l) in enumerate(handles()):
        legend_below(fig, h, l, X[k] + 3.0, 1.0 + LG[k] + 0.6, W, H, ncol=2 if k == 0 else 1, colsp=1.0)
    save(fig, "fig_crni_energetics")
    return ids


def one_col():
    W, H = st.W1 / st.MM, 91.5
    fig, cv = mm_canvas(W, H)
    TOP, G = 1.0, 1.5
    AH = 48.0
    card(cv, 1.0, H - TOP - AH, W - 2, AH, "a", "Solid solutions", size=6.5)
    a = mm_axes(fig, 12.0, H - TOP - AH + 8.0, 40.0, AH - 8.0 - 7.5, W, H)
    BH = H - TOP - AH - G - 1.0
    CWb = (W - 2 - G) / 2
    card(cv, 1.0, 1.0, CWb, BH, "b", "Liquid", size=6.5)
    card(cv, 1.0 + CWb + G, 1.0, CWb, BH, "c", "CrNi$_2$", size=6.5)
    b = mm_axes(fig, 1.0 + 10.5, 1.0 + 15.5, CWb - 12.5, BH - 15.5 - 7.0, W, H)
    c = mm_axes(fig, 1.0 + CWb + G + 10.5, 1.0 + 15.5, CWb - 12.5, BH - 15.5 - 7.0, W, H)
    panel_a(a, True); panel_b(b, True); panel_c(c, True)
    for ax_ in (a, b, c):
        ax_.set_xticks([0, .5, 1], ["0", "0.5", "1"])
    a.set_ylabel(r"$\Delta H_{\mathrm{mix}}$ (" + UNIT + ")"); b.set_ylabel(r"$\Delta H^{\mathrm{liq}}_{\mathrm{mix}}$ (" + UNIT + ")")
    c.set_ylabel(r"$\Delta H$ (" + UNIT + ")")
    ha, hb, hc = handles()
    legend_below(fig, *ha, 55.5,  # beside the axes, inside the card: the one-column card is wider than tall
                 H - TOP - AH + AH - 9.0, W, H, ncol=1, size=6.0)
    legend_below(fig, *hb, 4.0, 1.0 + 8.6, W, H, ncol=1, size=6.0)
    legend_below(fig, hc[0], ["fcc SQS", "fcc hull", "Pt$_2$Mo-type"], 1.0 + CWb + G + 3.0,
                 1.0 + 8.6, W, H, ncol=1, size=6.0)
    save(fig, "fig_crni_energetics_1col")


def main():
    ids = two_col()
    one_col()
    (ROOT / "figs/fig_crni_energetics_orchid_ids.json").write_text(json.dumps(ids, indent=1, ensure_ascii=False))
    print("wrote figs/fig_crni_energetics(_1col)")


if __name__ == "__main__":
    main()
