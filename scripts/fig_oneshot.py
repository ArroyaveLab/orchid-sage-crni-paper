#!/usr/bin/env python3
"""Cr-Ni PhaseForge one-shot phase diagram (pycalphad; SGTE91 unaries; MLIP mixing energies), computed from the TDB files the
run wrote, with ORCHID Cr-Ni phase-equilibrium evidence overlaid by evidence class and id.

a  one-shot (liquid b_k = 0), b  one-shot + corrected Hong-Liu liquid excess entropy (b_k from S_ex at 2200 K),
Phases LIQUID, BCC_A2, FCC_A1 (PI 6 Nov: disordered FCC_A1 only; ordered cells, CrNi2 included, unused).
Faint reference: CrNi-92Lee-LB (SGTE binary, Lee 1992) from the open-tdb repository, labelled.
ORCHID overlay: assessed phase-diagram assemblages (Nash/Okamoto, class assessed_phase_diagram; one point per field, two-phase
points at the tie-line hyperplane composition) and printed invariant/transition temperatures of the binary (no composition is
assumed for them: they are drawn as ticks in a strip at the right of each panel). Records naming Al-Cr-Ni phases (gamma', beta)
are excluded. Hero style (orchid-brand figures.md): cards with orchid headings, legends below the axes, no badge or logo (Digital Discovery);
labels >= 5 pt; record ids in the caption. Outputs: figs/fig_crni_oneshot.{pdf,png} (89 x 90 mm, one card: one-shot + liquid
S_ex solid, without S_ex dashed) and figs/fig_crni_oneshot_2col.{pdf,png} (183 x 96 mm, a without, b with the liquid S_ex).
Lines: `<python with pycalphad 0.11.2> scripts/fig_oneshot.py --compute` (pycalphad 0.11.2) writes data/crni_oneshot_lines.json;
plotting (any venv) reads it and checks the TDB hashes.
"""
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pycalphad import Database, equilibrium, variables as v

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style as st  # noqa: E402
import crni_pf_data as D  # noqa: E402
from crni_fig_common import card, check_layout, legend_below, mm_axes, mm_canvas  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
import json  # noqa: E402

RELEASE = "v2026.10"            # CR-NI records of the orchid-data release (released 28 Oct 2026)
REF_TDB = D.paths.loc("open_tdb") / "databases/sgte-binary/CrNi-92Lee-LB.tdb"
TMIN, TMAX = 600, 2400


def boundaries(tdb, phases, dT=10, dx=0.005):
    """Phase-boundary points from a grid of equilibria: for each two-phase (x,T), the compositions of the coexisting phases."""
    db = Database(str(tdb))
    eq = equilibrium(db, ["CR", "NI", "VA"], phases, {v.X("NI"): (dx, 1 - dx / 2, dx), v.T: (TMIN, TMAX + 1, dT), v.P: 101325, v.N: 1})
    ph = eq.Phase.squeeze(); X = eq.X.sel(component="NI").squeeze()
    pts = []
    names = ph.values; xs = X.values; Ts = eq.T.values
    it = np.argwhere(np.sum(names != "", axis=-1) == 2)
    for (iT, ix) in it:   # dims after squeeze: T, X_NI, vertex
        for k in range(names.shape[-1]):
            if names[iT, ix, k]:
                pts.append((float(xs[iT, ix, k]), float(Ts[iT])))
    return np.array(sorted(set(pts)))


def overlay_items():
    pts, ref = D.orchid_assessed()
    temps = sorted([t for t in D.orchid_temperatures() if not set(t["phases"]) & {"γ'", "β", "α"}], key=lambda t: -t["T"])
    return pts, temps


def overlay(ax, pts, temps):
    """Assessed points numbered A1..; temperature records as ticks on the right edge numbered T1.. (ids in the caption)."""
    for k, p in enumerate(pts, 1):
        ax.plot(p["x_Ni"], p["T"], "D" if p["kind"] == "two_phase" else "o", ms=3, mfc=st.C_ASSESSED, mec="white", mew=0.3, zorder=6)
        ax.annotate(f"A{k}", (p["x_Ni"], p["T"]), xytext=(2.5, 1.5), textcoords="offset points", fontsize=4.5, color=st.C_ASSESSED)
    last = None
    for k, t in enumerate(temps, 1):
        col = st.EVC.get(t["evidence_class"], st.C_UNSPEC)
        ax.plot([0.965, 1.0], [t["T"], t["T"]], color=col, lw=1.0, zorder=7, solid_capstyle="butt")
        dy = 0 if last is None or last - t["T"] > 22 else -(22 - (last - t["T"]))
        ax.annotate(f"T{k}", (0.965, t["T"]), xytext=(-1, dy * 0.25), textcoords="offset points", fontsize=4, color=col, ha="right", va="center")
        last = t["T"] + dy


def boundary_lines(tdb, phases):
    """Phase-boundary and invariant lines as pycalphad's binplot computes them (mapping), returned as (x, T) arrays."""
    from pycalphad import binplot
    f, ax0 = plt.subplots()
    binplot(Database(str(tdb)), ["CR", "NI", "VA"], phases, {v.X("NI"): (0, 1, 0.01), v.T: (TMIN, TMAX, 10), v.P: 101325, v.N: 1},
            plot_kwargs={"ax": ax0})
    out = [(np.asarray(l.get_xdata(), float), np.asarray(l.get_ydata(), float)) for l in ax0.lines]
    plt.close(f)
    return out


LINES = ROOT / "data/crni_oneshot_lines.json"


def compute_lines():
    """pycalphad binplot mapping lines of the reference and both one-shot TDBs, cached in data/crni_oneshot_lines.json with the
    pycalphad version and the sha256 of each TDB. Compute with `--compute` under pycalphad 0.11.2 (a separate environment): the
    0.11.3.dev of the fit interpreter stops the fcc + liquid boundaries near x_Ni 0.86 (1900 K) instead of reaching pure Ni."""
    import pycalphad
    from crni_fig_common import sha, tilde
    meta = D.res("oneshot_tdb.json")
    out = {"pycalphad": pycalphad.__version__, "T_range_K": [TMIN, TMAX, 10], "x_step": 0.01, "tdbs": {}, "lines": {}}
    srcs = {"ref": (REF_TDB, ["LIQUID", "BCC_A2", "FCC_A1"])}
    for var in ("oneshot", "oneshot_Sex"):
        tdb = Path(meta["tdbs"][var]["path"])
        srcs[var] = (tdb, [p for p in ("LIQUID", "BCC_A2", "FCC_A1", "CRNI2") if p in Database(str(tdb)).phases])
    for k, (tdb, phs) in srcs.items():
        out["tdbs"][k] = {"path": tilde(tdb), "sha256": sha(tdb), "phases": phs}
        out["lines"][k] = [[x.tolist(), y.tolist()] for x, y in boundary_lines(tdb, phs)]
    LINES.write_text(json.dumps(out))
    return out


def load_lines():
    from crni_fig_common import sha
    d = json.loads(LINES.read_text())
    meta = D.res("oneshot_tdb.json")
    paths = {"ref": REF_TDB, "oneshot": Path(meta["tdbs"]["oneshot"]["path"]), "oneshot_Sex": Path(meta["tdbs"]["oneshot_Sex"]["path"])}
    for k, p in paths.items():
        assert sha(p) == d["tdbs"][k]["sha256"], f"{k}: TDB changed since the lines were computed; rerun with --compute"
    return {k: [(np.asarray(x, float), np.asarray(y, float)) for x, y in v] for k, v in d["lines"].items()}


def draw(ax, lines, pts, temps, show, dashed=None, ax_h_mm=60.0):
    """Reference (grey), the variant(s) in `show` (ink, solid), `dashed` (ink, dashed), ORCHID overlay."""
    for x, y in lines["ref"]:
        ax.plot(x, y, color=st.GREY_M, lw=0.6, zorder=1)
    for var in show:
        for x, y in lines[var]:
            ax.plot(x, y, color=st.INK, lw=0.9, zorder=3)
    if dashed:
        for x, y in lines[dashed]:
            ax.plot(x, y, color=st.INK, lw=0.5, ls=(0, (3, 2)), zorder=2)
    for k, p in enumerate(pts, 1):
        ax.plot(p["x_Ni"], p["T"], "D" if p["kind"] == "two_phase" else "o", ms=3, mfc=st.C_ASSESSED, mec="white", mew=0.3, zorder=6)
        ax.annotate(f"A{k}", (p["x_Ni"], p["T"]), xytext=(2.5, 1.5), textcoords="offset points", fontsize=5, color=st.C_ASSESSED)
    # printed temperatures: ticks at the right edge; labels staggered so that close values do not overlap (>= 2.1 mm apart)
    TLO, THI = TMIN, TMAX
    gap = 2.1 * (THI - TLO) / ax_h_mm
    pos = []
    for t in temps:                       # descending T: push down to keep a minimum spacing
        y = t["T"] if not pos or pos[-1] - t["T"] >= gap else pos[-1] - gap
        pos.append(y)
    lo = TLO + gap / 2
    for i in range(len(pos) - 1, -1, -1):  # then push up from the bottom so nothing leaves the axes
        floor_ = lo if i == len(pos) - 1 else pos[i + 1] + gap
        if pos[i] < floor_:
            pos[i] = floor_
    for k, (t, y) in enumerate(zip(temps, pos), 1):
        col = st.EVC.get(t["evidence_class"], st.C_UNSPEC)
        ax.plot([0.965, 1.0], [t["T"], t["T"]], color=col, lw=1.0, zorder=7, solid_capstyle="butt")
        ax.text(0.925, y, f"T{k}", fontsize=5, color=col, ha="right", va="center", zorder=7)
        ax.plot([0.928, 0.963], [y, t["T"]], color=col, lw=0.3, zorder=7)
    ax.set_xlim(0, 1); ax.set_ylim(TLO, THI); ax.set_yticks(range(600, 2401, 300))
    ax.set_xlabel(r"$x_{\mathrm{Ni}}$"); ax.set_ylabel("Temperature (K)")


def handles(n_pts, n_t, variants):
    h = [Line2D([], [], color=st.GREY_M, lw=.6)] + [Line2D([], [], color=st.INK, lw=lw, ls=ls) for lw, ls, _ in variants] + \
        [Line2D([], [], ls="none", marker="D", ms=3, mfc=st.C_ASSESSED, mec="white", mew=.3),
         Line2D([], [], color=st.C_EXP, lw=1.0), Line2D([], [], color=st.C_MODEL, lw=1.0)]
    l = ["SGTE (Lee 1992)"] + [lab for _, _, lab in variants] + \
        [f"ORCHID assessed (A1–A{n_pts})", "ORCHID experimental T", "ORCHID model T"]
    return h, l


def save(fig, name):
    fig.savefig(ROOT / f"figs/{name}.pdf")
    fig.savefig(ROOT / f"figs/{name}.png", dpi=600)
    probs = check_layout(fig, name)
    plt.close(fig)
    return probs


def one_col(lines, pts, temps):
    W, H = st.W1 / st.MM, 85.5
    fig, cv = mm_canvas(W, H)
    TOP = 1.0
    CH = H - TOP - 1.0
    card(cv, 1.0, 1.0, W - 2, CH, None, "One-shot diagram", size=6.5)
    AH = CH - 21.0 - 7.0
    ax = mm_axes(fig, 13.0, 1.0 + 21.0, W - 2 - 15.0, AH, W, H)
    draw(ax, lines, pts, temps, ["oneshot_Sex"], dashed="oneshot", ax_h_mm=AH)
    h, l = handles(len(pts), len(temps), [(.9, "-", "one-shot + liquid S$_{ex}$"), (.5, (0, (3, 2)), "no liquid S$_{ex}$")])
    legend_below(fig, h, l, 4.0, 1.0 + 11.6, W, H, ncol=2, size=6.0, colsp=1.0)
    return save(fig, "fig_crni_oneshot")


def two_col(lines, pts, temps):
    W, H = st.W2 / st.MM, 91.5
    fig, cv = mm_canvas(W, H)
    TOP, G = 1.0, 2.0
    CW, CH = (W - 2 - G) / 2, H - TOP - 1.0
    heads = ("One-shot", "One-shot + liquid excess entropy")
    AH = CH - 20.5 - 8.0
    for k in range(2):
        cx = 1.0 + k * (CW + G)
        card(cv, cx, 1.0, CW, CH, "ab"[k], heads[k])
        ax = mm_axes(fig, cx + 14.0, 1.0 + 20.5, CW - 17.0, AH, W, H)
        if k == 0:
            draw(ax, lines, pts, temps, ["oneshot"], ax_h_mm=AH)
            h, l = handles(len(pts), len(temps), [(.9, "-", "one-shot")])
        else:
            draw(ax, lines, pts, temps, ["oneshot_Sex"], dashed="oneshot", ax_h_mm=AH)
            h, l = handles(len(pts), len(temps), [(.9, "-", "+ liquid S$_{ex}$"), (.5, (0, (3, 2)), "panel a")])
        legend_below(fig, h, l, cx + 3.0, 1.0 + 12.0, W, H, ncol=2, colsp=1.5)
    return save(fig, "fig_crni_oneshot_2col")


def main():
    if "--compute" in sys.argv:
        compute_lines()
        print("wrote", LINES); return
    pts, temps = overlay_items()
    lines = load_lines()
    one_col(lines, pts, temps)
    two_col(lines, pts, temps)
    (ROOT / "figs/fig_crni_oneshot_overlay_ids.json").write_text(json.dumps(
        {"assessed": {f"A{k}": p for k, p in enumerate(pts, 1)}, "temperatures": {f"T{k}": t for k, t in enumerate(temps, 1)}},
        indent=1, ensure_ascii=False))
    print("wrote figs/fig_crni_oneshot(_2col)")


if __name__ == "__main__":
    main()
