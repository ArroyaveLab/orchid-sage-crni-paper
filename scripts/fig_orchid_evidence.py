#!/usr/bin/env python3
"""Single-column figure for Methods 2.2 (Evidence from ORCHID), in the ORCHID paper's hero tile style.

Six numbered tiles: (1) sources found and read by agents; (2) a state record and its ids; (3) the uncertainty sets each
weight; (4) excluded phases, their certainty tiers and the hinge floor; (5) the Cr-Ni phase-boundary points; (6) the
consistency check on the Pugliese and Fitterer activities.

7 Nov 2026 revision (panels 2 and 4 new, the others kept):
- Tile 2 shows a real record of the evidence: the Cr-Ni eutectic ORC-SV7H3CNRYS. Its record id is recomputed here from its
  locator (ORC- + base32(SHA-256(pid))[:10], orchid_ids/locator.py compact()) and must equal the id in the evidence bundle;
  the state id S-... is read from the bundle (states@1.1.0.json, registry coord-rule/2, arrives with ORCHID v2027.01). The
  provisional line (local:<ORCID>/<dataset-uuid>, alias record) is the generic form of docs/ID_SCHEME.md sections 6-7, not
  a Cr-Ni record (none of the Cr-Ni evidence uses the local: namespace).
- Tile 4 plots the hinge scale of every exclusion of the frozen fit (878 pairs) against its certainty tier (10/50/100
  J/mol-atom): sigma = max(tier, the state's T and x uncertainty converted to energy) (fit_protocol item 8, hinge floor).
  Tiers and scales are read from the hinge input the fit read (data/hinge/step4c_hinge_floor.json, cells -> penalize ->
  sigma and orchid.tiers), cross-checked against results/step4c_b_hinge_floor.json (878 pairs, 868 raised).
- Brand fixes: no class colour for non-class categories (phases in tile 5 by marker, in neutral inks; tiles 5 and 6 hold
  experimental data, so they take the experimental colour); every font >= 5 pt; no badge or logo (Digital Discovery; the figure plots ORCHID
  evidence, release tag "provisional" as in crni_fig_common, the fit uses records not yet released).
Sources and sha256: figs/fig_orchid_evidence_sources.json; plotted ORC ids: figs/fig_orchid_evidence_orchid_ids.json.
"""
from pathlib import Path
import base64, hashlib, json, sys, glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle, Polygon

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style as st  # noqa: E402
from crni_fig_common import RUNS, SAGE_REPO, sha, tilde  # noqa: E402

SAGE = SAGE_REPO
CAMP = RUNS / "crni-paper-fit-20261106"
# hero_data: the ZPF points of tile 5, kept byte-identical (sha256 a5b623cb...) as data/hero_crni_zpf_points.json
# when the hero rework (e6a8b7e) replaced data/hero_crni.json with the final-fit tiles
F = {"hero_data": ROOT / "data/hero_crni_zpf_points.json", "activities": ROOT / "data/fig_orchid_activities.json",
     "states": SAGE / "assessments/crni-paper-fit-step4c-b/evidence/states@1.1.0.json",
     "hinge_input": CAMP / "data/hinge/step4c_hinge_floor.json",
     "hinge_floor": CAMP / "results/step4c_b_hinge_floor.json"}

D = json.loads(F["hero_data"].read_text())
if not F["activities"].exists():
    src = RUNS / "cr-ni-rebuild-20261105/inputs/chapter-input-data"
    rows = []
    for f in sorted(glob.glob(str(src / "activity_*pugliese*.json"))):
        d = json.loads(Path(f).read_text())
        T = d["conditions"]["T"]; xs = d["conditions"]["X_CR"]
        for x, v in zip(xs, np.asarray(d["values"]).ravel()):
            rows.append([float(T), float(x), float(v)])
    F["activities"].write_text(json.dumps({"source": "Pugliese and Fitterer 1970, Table II (ESPEI datasets)", "T_xCr_aCr": rows}))
A = json.loads(F["activities"].read_text())["T_xCr_aCr"]

# ---- tile 2: the eutectic record of the evidence bundle
SB = json.loads(F["states"].read_text())
REC_ID = "ORC-SV7H3CNRYS"
rec = [s for s in SB["states"] if s["orchid_ids"] == [REC_ID]]
assert len(rec) == 1, REC_ID
rec = rec[0]; link = rec["orchid_links"][0]
PID = link["pid"]
recomputed = "ORC-" + base64.b32encode(hashlib.sha256(PID.encode()).digest()).decode()[:10]
assert recomputed == REC_ID == link["id"], (recomputed, REC_ID)
STATE_ID = link["state_id"]
PH = {"LIQUID": "L", "BCC_A2": "bcc", "FCC_A1": "fcc"}
STATE_TXT = "Cr–Ni, " + " + ".join(PH[p] for p in ("LIQUID", "BCC_A2", "FCC_A1") if p in rec["expected"]) + f", {rec['T_K']:.0f} K"

# ---- tile 4: certainty tiers and the hinge floor, from the hinge input the fit read (tier and sigma per excluded phase)
TIER_J = {"certain": 10.0, "less_certain": 50.0, "uncertain": 100.0}
HIN = json.loads(F["hinge_input"].read_text())
sig = {t: [] for t in TIER_J}
for cell in HIN["cells"]:
    for p in cell["penalize"]:
        t = cell["orchid"]["tiers"][p]["tier"]
        s = float(cell["sigma"][p])
        assert s >= TIER_J[t] - 1e-9, (cell["T"], cell["x"], p)     # the floor rule holds for every pair
        sig[t].append(s)
TIER_N = {t: len(v) for t, v in sig.items()}
N_PAIRS = sum(TIER_N.values())
N_RAISED = sum(1 for t, v in sig.items() for s in v if s > TIER_J[t] + 1e-9)
HF = json.loads(F["hinge_floor"].read_text())             # build record of the floor: same pairs, same number raised
assert (HF["pairs"], HF["raised"]) == (N_PAIRS, N_RAISED), (HF["pairs"], HF["raised"], N_PAIRS, N_RAISED)
# The evidence bundle's tier counts (states@1.1.0.json "counts"): from bundle 1.1.0 they are copied from this hinge input
# (bundle 1.0.0 re-derived them with its own classifier: 526 / 343 / 9); reported, not used.
BUNDLE_TIERS = SB["counts"]["exclusions"]

H_MM = 89.0                                               # square 89-unit layout (no badge strip)
fig = plt.figure(figsize=(st.W1, st.W1 * H_MM / 89.0), dpi=600)   # 89-unit layout drawn at the single column (83 mm); text at final pt
ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")


def txt(x, y, s, size=5.4, color=st.INK, weight="normal", ha="left", va="center", z=9, family="Arial", **kw):
    return ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va, family=family, zorder=z, **kw)


def box(x, y, w, h, fc="white", ec=st.INK2, lw=.5, r=.9, z=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.3,rounding_size={r}", fc=fc, ec=ec, lw=lw * 1.6, zorder=z))


def line(xs, ys, c=st.INK2, lw=.5, ls="-", z=5):
    ax.plot(xs, ys, color=c, lw=lw * 1.7, ls=ls, zorder=z, solid_capstyle="round")


def arrow(x0, y0, x1, y1, c=st.INK2, lw=.5, z=6, ls="-"):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=4.5, color=c, lw=lw,
                                 shrinkA=0, shrinkB=0, zorder=z, ls=ls))


def dot(x, y, r, c, ec="none", lw=.3, z=7):
    ax.add_patch(Circle((x, y), r, fc=c, ec=ec, lw=lw, zorder=z))


def doc(x, y, w=5.0, h=6.4, c=st.C_EXP):
    ax.add_patch(Polygon([(x, y), (x + w, y), (x + w, y + h - 1.4), (x + w - 1.4, y + h), (x, y + h)], closed=True,
                         fc="white", ec=st.INK2, lw=.7, zorder=6))
    for k in range(4):
        line([x + .8, x + w - .8], [y + h - 1.9 - k * 1.2] * 2, st.GREY_M, .35, z=7)
    ax.add_patch(Rectangle((x + .8, y + .7), 1.0, 1.0, fc=c, ec="none", zorder=7))


def mag(x, y, r=1.2):
    ax.add_patch(Circle((x, y), r, fc="white", ec=st.INK, lw=.9, zorder=8))
    line([x + .7 * r, x + 1.6 * r], [y - .7 * r, y - 1.6 * r], st.INK, .8, z=8)


def icon_gauss(x, y, w, h, c=st.ACCENT):
    u = np.linspace(-3, 3, 50)
    line(x + (u + 3) / 6 * w, y + h * np.exp(-u ** 2 / 2), c, .6)
    line([x + w / 2] * 2, [y, y + h], st.INK2, .35, "--")
    txt(x + w * .80, y + h * .75, "σ", 5.2, c, "bold", ha="center")


# ---------------------------------------------------------------- tiled (2 x 3), ORCHID-hero tile style
TW, TH = 25.0, 16.4
cols = [-25.6, 0.6]; rows = [9.0, -8.5, -26.0]


def motif_sources(x, y):
    doc(x - 6.0, y - 4.0, 6.0, 8.2); doc(x - 2.0, y - 5.2, 6.0, 8.2); mag(x + 3.4, y - 3.0, 1.8)


def motif_ids(x0, y0):
    """Tile 2: locator -> record id; canonical state -> state id; provisional id -> alias -> released id."""
    L = x0 + 2.2
    R = x0 + TW - .2
    a, b = PID.split("/p", 1)
    txt(L, y0 + 12.0, a, 5.0, st.INK2, family=st.MONO)                 # split before "/p" so that both lines fit the
    txt(L, y0 + 10.8, "/p" + b, 5.0, st.INK2, family=st.MONO)          # tile at 83 mm (5 pt monospace)
    txt(L, y0 + 9.2, "→", 5.6, st.ACCENT, "bold")
    txt(L + 1.6, y0 + 9.2, REC_ID, 5.6, st.ACCENT, "bold", family=st.MONO)
    txt(R, y0 + 9.2, "record id", 5.0, st.INK2, ha="right")
    txt(L, y0 + 7.4, STATE_TXT, 5.0, st.INK2)
    txt(L, y0 + 6.0, "→", 5.6, st.ACCENT, "bold")
    txt(L + 1.6, y0 + 6.0, STATE_ID, 5.6, st.ACCENT, "bold", family=st.MONO)
    txt(R, y0 + 6.0, "state id", 5.0, st.INK2, ha="right")
    line([L, R], [y0 + 4.75] * 2, st.GREY_M, .3)
    txt(L, y0 + 3.6, "local:<ORCID>/<uuid>/…", 5.0, st.INK2, family=st.MONO)
    txt(R, y0 + 3.6, "provisional", 5.0, st.INK2, ha="right")
    txt(L, y0 + 2.1, "→", 5.6, st.INK2, "bold")
    txt(L + 1.6, y0 + 2.1, "alias record → released ORC id", 5.0, st.INK2)


def motif_tiers(x0, y0):
    """Tile 4: hinge sigma of each exclusion against its tier (log scale); tier = floor."""
    px0, px1 = x0 + 6.6, x0 + TW - 1.2
    py0, py1 = y0 + 5.4, y0 + TH - 4.2
    lo, hi = np.log10(5.0), np.log10(5000.0)
    Y = lambda v: py0 + (np.log10(v) - lo) / (hi - lo) * (py1 - py0)
    line([px0, px0, px1], [py1, py0, py0], st.INK2, .4)
    for v in (10, 100, 1000):
        line([px0 - .45, px0], [Y(v)] * 2, st.INK2, .4)
        txt(px0 - .7, Y(v), f"{v:g}", 5.0, st.INK2, ha="right")
    txt(x0 + 1.9, (py0 + py1) / 2, "σ (J/mol-atom)", 5.0, st.INK2, ha="center", rotation=90)
    cw = (px1 - px0) / 3
    rng = np.random.default_rng(7)
    for k, t in enumerate(("certain", "less_certain", "uncertain")):
        cx = px0 + cw * (k + .5)
        v = np.asarray(sig[t])
        jit = rng.uniform(-.32, .32, len(v)) * cw
        ax.scatter(cx + jit, Y(v), s=.35, c=st.INK2, lw=0, zorder=6, alpha=.55)
        line([cx - .42 * cw, cx + .42 * cw], [Y(TIER_J[t])] * 2, st.ACCENT, .9, z=8)
        txt(cx, py0 - 1.0, f"{TIER_J[t]:g}", 5.0, st.ACCENT, "bold", ha="center")
        txt(cx, py0 - 2.2, f"{TIER_N[t]}", 5.0, st.INK2, ha="center")
    txt(px0 - .7, py0 - 1.0, "tier", 5.0, st.ACCENT, "bold", ha="right")
    txt(px0 - .7, py0 - 2.2, "n", 5.0, st.INK2, ha="right")


PHM = {"BCC_A2": dict(fc=st.INK, ec="none"), "FCC_A1": dict(fc="white", ec=st.INK), "LIQUID": dict(fc=st.GREY_M, ec="none")}


def motif_data(x, y):
    x0, y0, w0, h0 = x - 7.0, y - 5.4, 14.0, 10.6
    line([x0, x0, x0 + w0], [y0 + h0, y0, y0], st.INK2, .4)
    for xn, tt, ph in D["zpf_points"]:
        m = PHM[ph]
        dot(x0 + xn * w0, y0 + (tt - 800) / 1400 * h0, .26, m["fc"], m["ec"], .3)
    lx = x0 + w0 - 2.6
    for k, (ph, lab) in enumerate((("LIQUID", "L"), ("BCC_A2", "bcc"), ("FCC_A1", "fcc"))):
        m = PHM[ph]
        dot(lx, y0 + 3.6 - k * 1.35, .3, m["fc"], m["ec"], .3)
        txt(lx + .7, y0 + 3.6 - k * 1.35, lab, 5.0, st.INK2)


def motif_check(x, y):
    x0, y0, w0, h0 = x - 7.0, y - 5.4, 14.0, 10.6
    line([x0, x0, x0 + w0], [y0 + h0, y0, y0], st.INK2, .4)
    Ts = sorted({r[0] for r in A}); shades = ["#BFD8EC", "#8DBADD", "#5A9BCC", "#2B79B7", st.C_EXP]
    for T, xc, a in A:
        dot(x0 + xc * w0, y0 + a * h0, .22, shades[Ts.index(T) % len(shades)])
    for T, xc, a in [r for r in A if abs(r[2] - 0.112) < 1e-6]:
        ax.add_patch(Circle((x0 + xc * w0, y0 + a * h0), .95, fc="none", ec="#C00000", lw=.85, zorder=8))


tiles = [("Sources", "found and read by agents", st.C_EXP, st.FILL["experimental"], motif_sources, True, False),
         ("State record and ids", "", st.ACCENT, st.FILL["accent"], motif_ids, False, True),
         ("Uncertainty", "σ sets each weight", st.ACCENT, "white", lambda x, y: icon_gauss(x - 7.0, y - 4.8, 14.0, 9.6), False, False),
         ("Excluded phases", f"σ = max(tier, state σ); {N_RAISED} of {N_PAIRS} raised", st.ACCENT, st.FILL["accent"], motif_tiers, False, True),
         ("Cr–Ni boundaries", f"{len(D['zpf_points'])} points, by phase", st.C_EXP, st.FILL["experimental"], motif_data, True, False),
         ("Consistency check", f"{len(A)} a$_{{Cr}}$; one value flagged", st.C_EXP, st.FILL["experimental"], motif_check, True, False)]
for i, (head, sub, col, fill, motif, ai, whole) in enumerate(tiles):
    x = cols[i % 2]; y = rows[i // 2]
    # hero heading (ORCHID paper fig_coverage_states): bold number (the caption cites (1)-(6)) + bold orchid heading on one
    # baseline; class frame 0.6 pt for evidence tiles, 0.75 pt orchid for ORCHID objects; no side strip, no number disc
    box(x, y, TW, TH, fill, col, (.75 if col == st.ACCENT else .6) / 1.6, .9, 2)
    txt(x + 1.0, y + TH - 2.3, str(i + 1), 7.0, st.INK, "bold", va="baseline")
    txt(x + 2.5, y + TH - 2.3, head, 6.0, st.ACCENT, "bold", va="baseline")
    txt(x + 1.0, y + 1.6, sub, 5.9 if "$" in sub else 5.0, st.INK2)   # subscripts >= 5 pt
    if whole:
        motif(x, y)
    else:
        motif(x + TW / 2 + 1.0, y + TH / 2 - .2)
    if ai:
        dot(x + TW - 1.9, y + TH - 1.7, 1.3, st.ACCENT); txt(x + TW - 1.9, y + TH - 1.7, "AI", 5.0, "white", "bold", ha="center")

ax.set_xlim(-26.2, 26.2); ax.set_ylim(-26.4, 26.0)
out = ROOT / "figs"; out.mkdir(exist_ok=True)
fig.savefig(out / "fig_orchid_evidence.pdf"); fig.savefig(out / "fig_orchid_evidence.png", dpi=300)
from crni_fig_common import check_layout  # noqa: E402
check_layout(fig, "fig_orchid_evidence")
(out / "fig_orchid_evidence_sources.json").write_text(json.dumps({
    "figure": "fig_orchid_evidence", "kind": "data figure (ORCHID records, tag provisional; no badge or logo)",
    "sources": [{"path": tilde(p), "sha256": sha(p), "role": k} for k, p in F.items()],
    "tile2": {"record_id": REC_ID, "pid": PID, "record_id_recomputed": recomputed, "state_id": STATE_ID,
              "state_class_id": link.get("state_class_id"), "orchid_release": rec.get("orchid_release"),
              "provisional_line": "generic form (docs/ID_SCHEME.md sections 6-7), not a Cr-Ni record"},
    "tile4": {"pairs": N_PAIRS, "raised_by_floor": N_RAISED, "tier_counts": TIER_N, "tier_J": TIER_J,
              "bundle_tier_counts_not_used": BUNDLE_TIERS,
              "sigma_median_by_tier": {t: float(np.median(v)) for t, v in sig.items()}},
    "tile5_points": len(D["zpf_points"]), "tile6_activities": len(A)}, indent=1))
(out / "fig_orchid_evidence_orchid_ids.json").write_text(json.dumps({
    "figure": "fig_orchid_evidence", "release": "provisional (state ids arrive with ORCHID v2027.01)",
    "labels": {"tile 2 record": {"id": REC_ID, "pid": PID, "state_id": STATE_ID}},
    "note": "tiles 4-6 plot evidence-bundle states (crni-paper-fit-step4c-b states@1.1.0.json); their ORC links, or the reason a link is missing, are in that file"},
    indent=1))
print(out / "fig_orchid_evidence.pdf")
