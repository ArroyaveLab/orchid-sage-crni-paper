#!/usr/bin/env python3
"""Protocol verification (Cr-Ni paper, Methods 2.1): how a protocol and a rerun are verified.

(a) The validator: schema conformity, file hashes, step order (no input used before it is produced).
(b) The reproduction comparison by step kind for the two final independent reruns (7 Nov 2026): the scripted rerun of
    crni-paper-fit-step4c-b@1.0.3 on a DGX Spark (aarch64 Linux; fit inputs byte-identical to 1.0.4, which is 1.0.3 with record
    fixes only and names this rerun as its scripted rerun) and the rerun of the final 1.0.4 by an AI agent through the
    ORCHID-SAGE MCP server (Mac Studio); the 1.0.1 reruns used before 7 Nov evening are in git history (commit 2cd69fa):
    deterministic -> byte-identical; numerical -> |difference| / tolerance (log axis, pass below 1; a zero difference is drawn
    at the "0" position left of the axis break); judgement -> the rule and who set it. Parameter differences are drawn in grey
    as notes, never as part of the verdict.
(c) The flat direction: the two recorded minima of the basin (A_s4, A2_s5_flat) and the converged starts of the Studio and
    the DGX Spark in the plane of the two parameters that differ most in units of their tolerance (L1 bcc a, L1 fcc a), with the 10b
    tolerance boxes (+-50 J/mol).
(d) Along the path A -> A2: the log posterior (objective of crni-paper-fit-step4c-b@1.0.3, model3) at
    theta(t) = theta_A + t (theta_A2 - theta_A), t from -0.25 to 1.25, relative to A; dashed line at -0.01, the reproduction
    tolerance on the objective (data/crni_mode_path.json, written by scripts/compute_mode_path.py).
(e) The predictions at every start: eutectic and CrNi2 top, against the +-2 K tolerance and the ORCHID records.

Every number is read from the files below (paths and sha256 in figs/fig_verification_sources.json):
  orchid-sage:protocols/general/orchid-calphad-fit@2.1.2.yaml (steps, supply links, kinds, pick rule, tolerances)
  orchid-sage:protocols/specific/crni-paper-fit-step4c-b@1.0.4.yaml (file references, schema, decisions, independent_rerun)
  orchid-sage:protocols/specific/crni-paper-fit-step4c-b@1.0.3.yaml (the protocol of the scripted rerun; evidence pins)
  orchid-sage:protocols/reproduce/crni-paper-fit-step4c-b-1.0.3-<spark1>/{reproduce_report.json, rerun/pick10a_rerun.json,
      rerun/evaluation.json, rerun/thermo_compare.json}
  orchid-sage:protocols/reproduce/crni-paper-fit-step4c-b-1.0.4-mcp-studio/{README.md, comparison.json, comparison.md,
      plan_compare.json} (13 checks), rerun/{pick10a_rerun.json, thermo_compare.json, evaluation.json},
      session/{PROMPT.txt, mcp-only.json} (the agent had only the orchid-sage MCP)
  orchid-sage:assessments/crni-paper-fit-step4c-b/evidence/reference_outputs/results/uq/modes_step4c_b@1.1.0.json (the 1.0.4
      record of the two minima, A_s4_perturbed and B_s5_perturbed: theta checked equal to the campaign file below)
  <campaigns>/crni-paper-fit-20261106/results/uq/modes_step4c_b.json (the two recorded minima)
  <campaigns>/crni-paper-fit-20261106/results/uq/laplace_step4c_b.json (mixture weights, invariants per mode)
  <campaigns>/crni-paper-fit-20261106/steps/step4c_b_hingefloor/evaluation.json (the Studio starts)
  orchid-sage:assessments/crni-paper-fit-step4c-b/evidence/states@1.2.0.json (ORCHID eutectic and CrNi2 records; bundle of 1.0.4)
  data/validate_orchid-sage_20261107_final.txt (output of protocols/tools/validate.py, run read-only on 7 Nov 2026, with 1.0.4)
  data/crni_mode_path.json (log posterior along the path between the two recorded modes; scripts/compute_mode_path.py)

Outputs (all written by one run):
  figs/fig_verification.{pdf,png}        174 x 119.8 mm (hero cards), panels a-e; data figure (ORCHID records drawn).
  figs/fig_verification_1col_1.{pdf,png}  84 x 88.7 mm, (a) validator + (b) reproduction by step kind; no ORCHID records
                                          drawn.
  figs/fig_verification_1col_2.{pdf,png}  84 x 113.3 mm, (a) flat direction, (b) path A -> A2, (c) predictions at every start;
                                          ORCHID records drawn. No figure carries a badge or logo (Digital Discovery).
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle, RegularPolygon

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import paths  # noqa: E402
import style as st  # noqa: E402
from crni_fig_common import RUNS, SAGE_REPO, card, card_note, check_layout, sha, tilde  # noqa: E402

SAGE = SAGE_REPO
sys.path.insert(0, str(SAGE / "protocols/tools"))
import yamlmini  # noqa: E402

CAMP = RUNS / "crni-paper-fit-20261106"
RR = SAGE / f"protocols/reproduce/crni-paper-fit-step4c-b-1.0.3-{paths.host('spark1')}"   # scripted rerun (DGX Spark)
MR = SAGE / "protocols/reproduce/crni-paper-fit-step4c-b-1.0.4-mcp-studio"                # AI-agent rerun (Mac Studio)
F = {"general": SAGE / "protocols/general/orchid-calphad-fit@2.1.2.yaml",
     "specific": SAGE / "protocols/specific/crni-paper-fit-step4c-b@1.0.4.yaml",
     "spark_specific": SAGE / "protocols/specific/crni-paper-fit-step4c-b@1.0.3.yaml",
     "rerun_report": RR / "reproduce_report.json",
     "rerun_pick": RR / "rerun/pick10a_rerun.json", "rerun_eval": RR / "rerun/evaluation.json",
     "rerun_thermo": RR / "rerun/thermo_compare.json",
     "modes": CAMP / "results/uq/modes_step4c_b.json", "laplace": CAMP / "results/uq/laplace_step4c_b.json",
     "studio_eval": CAMP / "steps/step4c_b_hingefloor/evaluation.json",
     "modes_record": SAGE / "assessments/crni-paper-fit-step4c-b/evidence/reference_outputs/results/uq/modes_step4c_b@1.1.0.json",
     "states": SAGE / "assessments/crni-paper-fit-step4c-b/evidence/states@1.2.0.json",
     "validator": ROOT / "data/validate_orchid-sage_20261107_final.txt",
     "mode_path": ROOT / "data/crni_mode_path.json",
     "mcp_readme": MR / "README.md", "mcp_comparison": MR / "comparison.json", "mcp_comparison_md": MR / "comparison.md",
     "mcp_plan_compare": MR / "plan_compare.json", "mcp_pick": MR / "rerun/pick10a_rerun.json",
     "mcp_thermo": MR / "rerun/thermo_compare.json", "mcp_eval": MR / "rerun/evaluation.json",
     "mcp_prompt": MR / "session/PROMPT.txt", "mcp_config": MR / "session/mcp-only.json"}
J = lambda k: json.loads(F[k].read_text())
GEN = yamlmini.load(str(F["general"])); SPEC = yamlmini.load(str(F["specific"])); SPEC_B = yamlmini.load(str(F["spark_specific"]))
REP, PICK, REV, RTH = J("rerun_report"), J("rerun_pick"), J("rerun_eval"), J("rerun_thermo")
MODES, LAP, SEV, SB = J("modes"), J("laplace"), J("studio_eval"), J("states")
MC, MPC, MPK, MTH, MEV = J("mcp_comparison"), J("mcp_plan_compare"), J("mcp_pick"), J("mcp_thermo"), J("mcp_eval")
README_M = F["mcp_readme"].read_text()
VAL = F["validator"].read_text()

# ---------------------------------------------------------------- numbers
gen_id = f"{GEN['id']}@{GEN['version']}"; spec_id = f"{SPEC['id']}@{SPEC['version']}"
assert SPEC["instantiates"][0]["protocol"] == gen_id
steps = [t for s in GEN["sections"] for t in s.get("steps", [])]
n_steps = len(steps)
n_supply = sum(len(t.get("supply", [])) for t in steps)
n_refs = len(re.findall(r"\bsha256:\s*[0-9a-f]{64}", F["specific"].read_text()))
schema_v = SPEC["schema_version"]
val_err = re.findall(r"ERROR (\S+)", VAL)
val_ours = [e for e in val_err if e.startswith((f"general/{gen_id}", f"specific/{spec_id}"))]
assert f"general/{gen_id}.yaml" in VAL and f"specific/{spec_id}.yaml" in VAL
n_err_total = int(re.search(r"^errors: (\d+)", VAL, re.M).group(1))
n_warn_total = int(re.search(r"^warnings: (\d+)", VAL, re.M).group(1))

spec_b_id = f"{SPEC_B['id']}@{SPEC_B['version']}"
assert spec_b_id == "crni-paper-fit-step4c-b@1.0.3" and SPEC_B["instantiates"][0]["protocol"] == gen_id
assert "crni-paper-fit-step4c-b-1.0.3-" in SPEC["reproduce"]["independent_rerun"]          # 1.0.4 names the 1.0.3 scripted rerun as its own
n_staged = None                                    # the 1.0.3 report checks the staged files by manifest; no count recorded
items = {it["id"]: it for it in REP["items"]}
assert REP["pass"] is True and REP["specific_protocol"] == spec_b_id and REP["spec_sha256"] == sha(F["spark_specific"])
n_checks_b = sum(len(it["checks"]) for it in REP["items"])
assert all(c["pass"] for it in REP["items"] for c in it["checks"])
ev = items["evaluate_states"]["checks"][0]
assert ev["pass"] and ev["rerun"].startswith(SPEC_B["evidence_selection"]["bundle"]["states_evaluated"]["sha256"][:12])
n_states = SB["n_states"]
ps = items["phase_sequence"]["checks"][0]

# MCP-only rerun (Studio, 7 Nov 2026): every number from its comparison files
assert MC["protocol"] == spec_id and MC["pass"] is True and not MC["not_run"] and not MC["running_or_unrecorded"]
mchk = [c for c in MC["checks"] if "rule" in c]
n_checks_m = MC["compared"]
assert len(mchk) == n_checks_m and all(c["pass"] for c in mchk)
assert MPC["specific_protocol"] == spec_id and MPC["spec_sha256"] == sha(F["specific"]) and MPC["pass"] is True
assert "only the orchid-sage MCP tools" in F["mcp_prompt"].read_text().replace("\n", " ")
assert list(json.loads(F["mcp_config"].read_text())["mcpServers"]) == ["orchid-sage"]
mitems = {it["id"]: it for it in MPC["items"]}
mby = lambda item: [c for c in mchk if c["item"] == item]
m10a, mg, mlw = mby("check10a"), mby("global_10c"), mby("laplace_weights")[0]
mev = mitems["evaluate_states"]["checks"][0]; mps = mitems["phase_sequence"]["checks"][0]
assert mev["pass"] and mev["rerun"].startswith(SPEC["evidence_selection"]["bundle"]["states_evaluated"]["sha256"][:12])
n_staged_m = int(re.search(r"\| verify_inputs \|[^|]*\| (\d+) files \|", README_M).group(1))   # files verified by sha256
M_HOST, M_MACH = paths.machine(MPC["host"]), MPC["machine"]   # machine class, not the host name
assert MPK["pick"] == "s4_perturbed"


def num_rows_of(c, g, lw, thermo):
    """(label, |diff|/tol, pass) in a fixed order; c = the four check10a checks, g = the two global_10c checks."""
    return [("objective of the 10a pick", abs(c[0]["diff"]) / c[0]["abs_tol"], c[0]["pass"]),
            ("basin-hopping best", abs(g[0]["diff"]) / g[0]["abs_tol"], g[0]["pass"]),
            ("dual-annealing best", abs(g[1]["diff"]) / g[1]["abs_tol"], g[1]["pass"]),
            ("eutectic temperature", abs(c[2]["diff"]) / c[2]["abs_tol"], c[2]["pass"]),
            ("CrNi$_2$ top temperature", abs(c[3]["diff"]) / c[3]["abs_tol"], c[3]["pass"]),
            (f"thermochemistry ({thermo['n_compared']} datasets)", thermo["max_abs_diff_rms_z"] / thermo["tol_z"],
             thermo["within_tol"]),
            ("Laplace weight of mode A", abs(lw["diff"]) / lw["abs_tol"], lw["pass"])]


c = items["check10a"]["checks"]
num_rows = num_rows_of(c, items["global_10c"]["checks"], items["laplace_weights"]["checks"][0], RTH)
num_rows_m = num_rows_of(m10a, mg, mlw, MTH)
assert [r[0] for r in num_rows] == [r[0] for r in num_rows_m] and all(r[2] for r in num_rows + num_rows_m)
assert (m10a[2]["reference"], m10a[3]["reference"]) == (c[2]["reference"], c[3]["reference"])
P = PICK["parameters"]
TA, TB = P["tol_a"], P["tol_b"]
thA, thA2 = np.asarray(MODES[0]["theta"]), np.asarray(MODES[1]["theta"])
assert MODES[0]["name"] == "A_s4" and MODES[1]["name"] == "A2_s5_flat"
_MR = J("modes_record")                         # 1.0.4 record: same minima, renamed A_s4_perturbed / B_s5_perturbed
_MR = _MR["modes"] if isinstance(_MR, dict) else _MR
assert [m["name"] for m in _MR] == ["A_s4_perturbed", "B_s5_perturbed"]
assert np.array_equal(np.asarray(_MR[0]["theta"]), thA) and np.array_equal(np.asarray(_MR[1]["theta"]), thA2)
tol = np.array([TA if k % 2 == 0 else TB for k in range(len(thA))])      # a-terms (J/mol), b-terms (J/mol/K) alternate
dz = np.abs(thA2 - thA) / tol
note_rows = [("parameters, rerun pick vs recorded", P["max_diff_over_tol_to_each_recorded_mode"]["A_s4"],
              MPK["parameters"]["max_diff_over_tol_to_each_recorded_mode"]["A_s4_perturbed"]),
             ("parameters, recorded mode A2 vs A", None, None)]
DZMAX = float(dz.max())

OBJ_TOL = c[0]["abs_tol"]                                      # reproduction tolerance on the objective (check10a)
assert OBJ_TOL == 0.01, OBJ_TOL
MP = J("mode_path")                                            # scripts/compute_mode_path.py (objective of 1.0.3)
assert MP["inputs"]["modes"]["sha256"] == sha(F["modes"]) and all(r["pass"] for r in MP["check_at_modes"]["rows"].values())
assert np.allclose(MP["rows"][[r["t"] for r in MP["rows"]].index(1.0)]["theta"], thA2, rtol=0, atol=1e-9)
MP_LPA = MP["summary"]["logpost_A"]

lab = list(REV["evaluations"][0]["theta_labeled"].keys())
za = [(dz[k], k) for k in range(0, len(dz), 2)]                 # a-terms only (J/mol): one tolerance box in the plane
i1, i2 = [k for _, k in sorted(za, reverse=True)[:2]]
assert {lab[i1], lab[i2]} == {"L1bcc_a", "L1fcc_a"}, (lab[i1], lab[i2])
ib, iff = lab.index("L1bcc_a"), lab.index("L1fcc_a")
assert [m["name"] for m in LAP["modes"]] == ["A_s4", "A2_s5_flat"]
dlogpost = LAP["modes"][0]["logpost"] - LAP["modes"][1]["logpost"]
wA = LAP["weights"]["laplace"][0]


def mode_of(th):
    th = np.asarray(th)
    return "A" if np.max(np.abs(th - thA) / tol) < np.max(np.abs(th - thA2) / tol) else "A2"


def starts(evals, machine):
    out = []
    for e in evals:
        th = np.asarray(e["theta"])
        out.append(dict(machine=machine, start=e["start"], mode=mode_of(th), d=th - thA, Te=e["topology"]["T_liquid_min"],
                        Tc=e["topology"]["T_CrNi2_max"]))
    return out


S = starts(SEV["evaluations"], "Studio") + starts(REV["evaluations"], "spark")
cnt = {(m, k): sum(1 for s in S if s["machine"] == m and s["mode"] == k) for m in ("Studio", "spark") for k in ("A", "A2")}
ref_pick = [s for s in S if s["machine"] == "Studio" and s["start"] == SEV["pick"]][0]
T_EUT_REF, T_CRNI2_REF = ref_pick["Te"], ref_pick["Tc"]
assert (T_EUT_REF, T_CRNI2_REF) == (c[2]["reference"], c[3]["reference"])
b_pick_mode = [s for s in S if s["machine"] == "spark" and s["start"] == PICK["pick"]][0]["mode"]
m_pick_mode = mode_of([e for e in MEV["evaluations"] if e["start"] == MPK["pick"]][0]["theta"])
assert ref_pick["mode"] == b_pick_mode == m_pick_mode == "A"
T_TOL = [t for t in GEN["tolerances"] if "invariant" in t["quantity"]][0]["value"]
orc = {s["orchid_ids"][0]: s for s in SB["states"] if s["orchid_ids"] in (["ORC-SV7H3CNRYS"], ["ORC-X3KVP7D3PO"])}
T_EUT_ORC, T_CRNI2_ORC = orc["ORC-SV7H3CNRYS"]["T_K"], orc["ORC-X3KVP7D3PO"]["T_K"]
pick_rule = [t for t in steps if t["id"] == "pick_solid"][0]
assert pick_rule["kind"] == "judgement"
dec = [d for d in SPEC["decisions"] if "predictions only" in d["decision"]][0]
dec_10a = [d for d in SPEC["decisions"] if d["decision"].startswith("'10a accepts") or "10a accepts" in d["decision"]][0]
SHOW = {"Studio": "Mac Studio", "spark": "DGX Spark"}   # machine classes shown in the figure
B_HOST = "DGX Spark"           # machine class of the scripted rerun (its host name stays in the record)
s_lab = lambda p: p.split("_")[0]
pick_line = (f"picked: Mac Studio {s_lab(SEV['pick'])}; reruns {B_HOST} {s_lab(PICK['pick'])} and MCP {s_lab(MPK['pick'])}; "
             f"all in mode A")

# ---------------------------------------------------------------- drawing helpers (one canvas at a time, sizes in mm)
MONO = st.MONO
fig = ax = None
W = H = 0.0
MK = {"spark": dict(marker="s", s=9), "mcp": dict(marker="^", s=12), "rec": dict(marker="o", s=10)}


def canvas(w, h):
    global fig, ax, W, H
    W, H = w, h
    FW = st.W2 if w > 100 else st.W1             # layout in w-unit (mm) coordinates, drawn at the journal width:
    fig = plt.figure(figsize=(FW, FW * h / w))   # double column 171 mm or single column 83 mm; text and lines at final pt
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")


def axes_mm(x, y, w, h):
    return fig.add_axes([x / W, y / H, w / W, h / H])


def txt(x, y, s, size=6, color=st.INK, weight="normal", ha="left", va="center", family="Arial", z=9, **kw):
    return ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va, family=family, zorder=z, **kw)


def box(x, y, w, h, fc="white", ec=st.INK2, lw=.55, r=1.0, z=2, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, zorder=z, ls=ls))


def arrow(p0, p1, color=st.INK2, lw=.5, rad=0.0, z=6, ms=5):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=ms, color=color, lw=lw, shrinkA=0, shrinkB=0,
                                 connectionstyle=f"arc3,rad={rad}", zorder=z))


def kind_glyph(x, y, k, s=.9):
    if k == "deterministic":
        ax.add_patch(Rectangle((x - s, y - s), 2 * s, 2 * s, fc=st.INK, ec="none", zorder=8))
    elif k == "numerical":
        ax.add_patch(Circle((x, y), s, fc=st.GREY_M, ec=st.INK2, lw=.3, zorder=8))
    else:
        ax.add_patch(RegularPolygon((x, y), 4, radius=s * 1.35, fc="white", ec=st.ACCENT, lw=.7, zorder=8))


def letter(x, y, s):
    txt(x, y, s, 8, st.INK, "bold", va="top")


def mark(x, y, who, verdict=True, size=1.0):
    """A rerun marker drawn on the canvas (mm): square = DGX Spark (scripted), triangle = MCP-only agent, circle = recorded."""
    m = MK[who]
    ax.scatter([x], [y], marker=m["marker"], s=m["s"] * size, fc=st.ACCENT if verdict else st.GREY_M,
               ec=st.ACCENT if verdict else st.INK2, lw=.4, zorder=9)


def step_order_motif(x0, y):
    """s1 -> s2 -> s3 and a forbidden use of s3's output in s1 (red arc with a cross); 26 mm wide."""
    for j, xx in enumerate((x0, x0 + 8.0, x0 + 16.0)):
        box(xx, y - 1.4, 5.4, 2.8, "white", st.INK2, .4, .5, 4)
        txt(xx + 2.7, y, f"s{j + 1}", 5.0, st.INK2, ha="center")
    arrow((x0 + 5.4, y), (x0 + 8.0, y), st.INK2, .45, ms=4)
    arrow((x0 + 13.4, y), (x0 + 16.0, y), st.INK2, .45, ms=4)
    ax.add_patch(FancyArrowPatch((x0 + 18.7, y + 1.5), (x0 + 2.7, y + 1.5), arrowstyle="-|>", mutation_scale=4,
                                 color="#C00000", lw=.5, connectionstyle="arc3,rad=0.3", zorder=6))
    txt(x0 + 10.7, y + 4.0, "×", 7.0, "#C00000", "bold", ha="center")


ZERO, BREAK = 1e-12, 10 ** -11.4


SHORT = {"objective of the 10a pick": "objective", "basin-hopping best": "basin-hopping", "dual-annealing best": "annealing",
         "eutectic temperature": "eutectic T", "CrNi$_2$ top temperature": "CrNi$_2$ top T",
         f"thermochemistry ({RTH['n_compared']} datasets)": "thermochemistry", "Laplace weight of mode A": "Laplace weight",
         "parameters, rerun pick vs recorded": "parameters", "parameters, recorded mode A2 vs A": "mode A2 vs A"}


def num_plot(bx, label_x_pad=1.7, short=False):
    """|rerun - recorded| / tolerance for both reruns: verdict rows (accent) and parameter notes (grey band).
    A zero difference is drawn at the "0" position left of the axis break."""
    rows = [(a, v, vm, True) for (a, v, _), (_, vm, _) in zip(num_rows, num_rows_m)]
    rows += [(a, vb, vm, False) for a, vb, vm in note_rows]
    n = len(rows)
    for k, (a, vb, vm, verdict) in enumerate(rows):
        yy = n - 1 - k
        fc = st.ACCENT if verdict else st.GREY_M
        ec = st.ACCENT if verdict else st.INK2
        if vb is None:      # recorded modes, not a rerun
            bx.scatter([DZMAX], [yy], marker=MK["rec"]["marker"], s=MK["rec"]["s"], fc=fc, ec=ec, lw=.4, zorder=4)
        else:
            bx.scatter([max(vb, ZERO)], [yy + .2], marker="s", s=MK["spark"]["s"], fc=fc, ec=ec, lw=.4, zorder=4)
            bx.scatter([max(vm, ZERO)], [yy - .2], marker="^", s=MK["mcp"]["s"], fc=fc, ec=ec, lw=.4, zorder=4)
        bx.text(ZERO / label_x_pad / 1.5, yy, SHORT[a] if short else a, fontsize=6.0, color=st.INK if verdict else st.INK2, va="center", ha="right")
    bx.axvline(1.0, color=st.INK, lw=.6, ls="--")
    bx.text(.75, n - .55, "tolerance", fontsize=5.5, color=st.INK, va="center", ha="right")
    bx.axhspan(-.5, len(note_rows) - .5, color=st.GREY_L, lw=0, zorder=0)
    bx.set_xscale("log"); bx.set_xlim(ZERO / 2.5, 30); bx.set_ylim(-.6, n - .4)
    bx.set_yticks([]); bx.spines["left"].set_visible(False)
    bx.set_xticks([ZERO, 1e-9, 1e-6, 1e-3, 1])
    bx.set_xticklabels(["0", "10$^{-9}$", "10$^{-6}$", "10$^{-3}$", "1"])
    bx.tick_params(axis="x", labelsize=6.0)
    bx.minorticks_off()
    # axis break between 0 and the smallest non-zero difference
    xb = BREAK
    assert min(v for _, v, _ in num_rows + num_rows_m if v > 0) > 10 * BREAK
    for dx in (.82, 1.22):
        bx.plot([xb * dx / 1.25, xb * dx * 1.25], [-.6 - .25, -.6 + .25], color=st.INK, lw=.5, clip_on=False, zorder=5)
    bx.plot([xb * .82, xb * 1.22], [-.6, -.6], color="white", lw=1.6, clip_on=False, zorder=4)


def draw_flat(cx, legend_anchor=(1.0, 1.02), note_dx=45, note_dy=30, minimal=False):
    for (m, mk) in (("Studio", "o"), ("spark", "s")):
        for k in ("A", "A2"):
            ss = [s for s in S if s["machine"] == m and s["mode"] == k]
            if ss:
                d = np.array([s["d"] for s in ss])
                cx.scatter(d[:, ib], d[:, iff], s=14 if m == "Studio" else 9, marker=mk,
                           facecolor=st.ACCENT if k == "A" else "white", edgecolor=st.ACCENT, lw=.6, zorder=4,
                           label=f"{SHOW[m]}, {k}" if minimal else f"{SHOW[m]}: {len(ss)} start{'s' if len(ss) > 1 else ''} in {k}")
    for th in (thA, thA2):
        cxy = th - thA
        cx.add_patch(Rectangle((cxy[ib] - TA, cxy[iff] - TA), 2 * TA, 2 * TA, fc="none", ec=st.INK2, lw=.5, ls="--", zorder=2))
    cxy2 = thA2 - thA
    cx.annotate("", xy=(cxy2[ib] + TA * .9, cxy2[iff] - TA * .9), xytext=(-TA * .9, TA * .9),
                arrowprops=dict(arrowstyle="<->", lw=.5, color=st.INK2, shrinkA=0, shrinkB=0))
    if minimal:
        cx.text(cxy2[ib] / 2 + 22, cxy2[iff] / 2 + 8, f"{DZMAX:.1f} × tol.", fontsize=6.0, color=st.INK2, ha="left",
                va="center")
        cx.text(TA * 1.15, -TA * .9, "A", fontsize=6.5, color=st.INK, va="top", fontweight="bold")
        cx.text(cxy2[ib] - TA, cxy2[iff] + TA * 1.1, "A2", fontsize=6.5, color=st.INK, va="bottom", fontweight="bold")
    else:
        notes_flat(cx, cxy2, note_dx, note_dy)
    cx.set_xlabel("Δ L$^1_{bcc}$ a (J mol$^{-1}$)", fontsize=6.5)
    cx.set_ylabel("Δ L$^1_{fcc}$ a (J mol$^{-1}$)", fontsize=6.5)
    cx.set_xlim(cxy2[ib] - 110, 140); cx.set_ylim(-140, cxy2[iff] + 110)
    cx.set_aspect("equal", adjustable="box")
    cx.tick_params(labelsize=6.0)
    cx.legend(loc="upper left", bbox_to_anchor=legend_anchor, fontsize=6.0 if minimal else 5.5, handletextpad=.2,
              borderaxespad=.2, labelspacing=.3)


def notes_flat(cx, cxy2, note_dx, note_dy):
    cx.text(cxy2[ib] / 2 + note_dx, cxy2[iff] / 2 + note_dy, f"{DZMAX:.1f} × tolerance apart", fontsize=5.5, color=st.INK2,
            ha="left", va="bottom")
    cx.text(cxy2[ib] / 2 + note_dx, cxy2[iff] / 2 + note_dy - 8, f"Δ log posterior {dlogpost:.4f}", fontsize=5.5,
            color=st.INK2, ha="left", va="top")
    cx.text(TA * 1.15, -TA * 1.0, f"mode A\n(weight {wA:.2f})", fontsize=5.5, color=st.INK, va="top")
    cx.text(cxy2[ib] - TA * 1.1, cxy2[iff] + TA * 1.1, "mode A2", fontsize=5.5, color=st.INK, va="bottom")
    cx.text(TA * 1.15, TA * 1.05, f"±{TA:.0f} J/mol", fontsize=5.5, color=st.INK2, va="bottom")


def draw_path(px, tick_size=6.0):
    """Δ log posterior along theta(t) = theta_A + t (theta_A2 - theta_A), relative to A; A at t = 0, A2 at t = 1; dashed line
    at -0.01, the reproduction tolerance on the objective (scale only)."""
    t = np.array([r["t"] for r in MP["rows"]]); d = np.array([r["logpost"] for r in MP["rows"]]) - MP_LPA
    px.axhline(0.0, color=st.GREY_M, lw=.4, zorder=0)
    px.axhline(-OBJ_TOL, color=st.INK2, lw=.6, ls="--", zorder=1)
    px.plot(t, d, color=st.ACCENT, lw=.8, zorder=3)
    px.scatter(t, d, s=3, color=st.ACCENT, lw=0, zorder=3)
    for tt, lab, fc in ((0.0, "A", st.ACCENT), (1.0, "A2", "white")):
        dd = d[t == tt][0]
        px.scatter([tt], [dd], s=16, marker="o", fc=fc, ec=st.ACCENT, lw=.7, zorder=5)
        px.annotate(lab, (tt, dd), xytext=(0, 4), textcoords="offset points", fontsize=6.5, fontweight="bold",
                    color=st.INK, ha="center", va="bottom")
    px.text(1.25, -OBJ_TOL, f"−{OBJ_TOL:g}", fontsize=6.0, color=st.INK2, ha="right", va="bottom")
    px.set_xlim(-.27, 1.27)
    px.set_xticks([0, .5, 1]); px.set_xticklabels(["0", "0.5", "1"])
    px.set_xlabel("t (A → A2)", fontsize=6.5, labelpad=1.0)
    px.set_ylabel("Δ log posterior", fontsize=6.5)
    px.tick_params(labelsize=tick_size)


PRED = (("Te", T_EUT_REF, T_EUT_ORC, "ORC-SV7H3CNRYS", "Eutectic"),
        ("Tc", T_CRNI2_REF, T_CRNI2_ORC, "ORC-X3KVP7D3PO", "CrNi$_2$ top"))


def draw_pred(px, j, tick_size=6.5, minimal=False, ms=1.0, wrap=False):
    key, ref, orcT, orcid, ttl = PRED[j]
    px.axhspan(ref - T_TOL, ref + T_TOL, color=st.GREY_L, lw=0, zorder=0)
    px.axhline(orcT, color=st.C_EXP, lw=.6, ls="--", zorder=1)
    px.text(len(S) - .5, orcT + .25, "ORCHID" if minimal else f"ORCHID {orcT:.0f} K", fontsize=6.0 if minimal else 5.5,
            color=st.C_EXP, ha="right", va="bottom")
    if not minimal:
        px.text(len(S) - .5, ref - T_TOL + .2, f"±{T_TOL:g} K", fontsize=5.5, color=st.INK2, ha="right", va="bottom")
    for k, s in enumerate(S):
        px.scatter(k, s[key], marker="o" if s["machine"] == "Studio" else "s", s=(12 if s["machine"] == "Studio" else 8) * ms,
                   facecolor=st.ACCENT if s["mode"] == "A" else "white", edgecolor=st.ACCENT, lw=.6 * min(1.0, ms ** .5), zorder=4)
    nS = sum(1 for s in S if s["machine"] == "Studio")
    px.axvline(nS - .5, color=st.GREY_M, lw=.4)
    px.set_xticks([(nS - 1) / 2, nS + (len(S) - nS - 1) / 2]); px.set_xticklabels([SHOW["Studio"].replace(" ", "\n"), B_HOST.replace(" ", "\n")] if wrap else [SHOW["Studio"], B_HOST])
    px.tick_params(axis="x", length=0)
    px.tick_params(labelsize=tick_size)
    px.set_xlim(-.8, len(S) - .2); px.set_ylim(min(ref, orcT) - 4, max(ref, orcT) + 4)
    px.set_ylabel(f"{ttl} (K)", fontsize=6.5)


def save(name):
    fig.savefig(ROOT / f"figs/{name}.pdf")
    fig.savefig(ROOT / f"figs/{name}.png", dpi=600)
    probs = check_layout(fig, name)
    plt.close(fig)
    return probs


ours = "0 errors" if not val_ours else f"{len(val_ours)} errors"
dec_10a_s = f"fit_protocol 10a; {dec_10a['who']}, {dec_10a['date']}"
dec_s = f"{dec['who']}, {dec['date']}"


# ================================================================ two-column version (183 x 126 mm), hero cards
def two_col():
    canvas(183.0, 122.0)
    T = H - 1.0                                    # top margin (no badge strip)
    # (a) validator
    card(ax, 1.0, 54.5, 60.0, T - 54.5, "a", "Validator")
    AX, AW = 3.0, 56.0
    checks = [("Schema", f"every document conforms to\n{schema_v.split('@')[0]}", f"({schema_v.split('@')[1]})"),
              ("File hashes", f"{n_refs} file references in\n{spec_id}; sha256 match", ""),
              ("Step order", f"{n_supply} supply links, {n_steps} steps;\nno input before it is produced", "")]
    CY0, PITCH, TH = T - 7.5, 16.6, 14.6
    for k, (h, b, c2) in enumerate(checks):
        y = CY0 - k * PITCH
        box(AX, y - TH, AW, TH, st.FILL["accent"], st.ACCENT, .6)
        txt(AX + 2.0, y - 2.6, h, 6.5, st.ACCENT, "bold")
        txt(AX + 2.0, y - 4.6, b, 5.5, st.INK2, linespacing=1.15, va="top")
        if c2:
            txt(AX + 17.0, y - 2.6, c2, 5.5, st.INK2)
    step_order_motif(AX + 31.5, CY0 - 2 * PITCH - 10.8)
    card_note(ax, AX, 57.2, f"validate.py, both protocols: {ours}")

    # (b) reproduction by step kind, two reruns
    card(ax, 63.0, 54.5, 119.0, T - 54.5, "b", "Reproduction by step kind")
    LX, LW = 65.0, 115.0
    y0 = T - 7.5 - 9.4
    box(LX, y0, LW, 9.4, "white", st.INK2, .5)
    kind_glyph(LX + 3.0, y0 + 6.6, "deterministic")
    txt(LX + 5.2, y0 + 6.6, "Deterministic: byte-identical", 6.0, st.INK, "bold")
    txt(LX + 5.2, y0 + 2.6, f"staged by sha256: every file ({B_HOST}), {n_staged_m} (MCP)", 5.5, st.INK2)
    txt(LX + 58.0, y0 + 6.6, f"{n_states} states evaluated: {ev['rerun'][:8]}… in both", 5.5, st.INK2)
    txt(LX + 58.0, y0 + 2.6, f"phase sequence: {ps['n_differing']} and {mps['n_differing']} of "
        f"{ps['compositions']} compositions differ", 5.5, st.INK2)
    y1 = y0 - 33.6
    box(LX, y1, LW, 32.4, "white", st.INK2, .5)
    kind_glyph(LX + 3.0, y1 + 29.6, "numerical")
    txt(LX + 5.2, y1 + 29.6, "Numerical: within tolerance", 6.0, st.INK, "bold")
    ly = y1 + 22.0
    for k, (who, s1, s2) in enumerate((("spark", f"{paths.machine(REP['host'])} ({REP['machine']}), scripted", ""),
                                        ("mcp", f"Mac Studio ({M_MACH}), AI agent", "through the orchid-sage MCP"),
                                        ("rec", "recorded modes (Mac Studio)", ""))):
        yy = ly - k * 3.4 - (1.6 if k == 2 else 0)
        mark(LX + 6.0, yy, who)
        txt(LX + 8.0, yy, s1, 5.5, st.INK2)
        if s2:
            txt(LX + 8.0, yy - 2.4, s2, 5.5, st.INK2)
    txt(LX + 5.2, y1 + 2.4, f"{n_checks_b}/{n_checks_b} checks pass ({B_HOST}); {n_checks_m}/{n_checks_m} (MCP)", 5.5,
        st.INK)
    bx = axes_mm(LX + 70.0, y1 + 4.4, LW - 75.0, 23.0)
    num_plot(bx)
    y2 = y1 - 14.0
    box(LX, y2, LW, 12.8, "white", st.INK2, .5)
    kind_glyph(LX + 3.0, y2 + 10.0, "judgement")
    txt(LX + 5.2, y2 + 10.0, "Judgement: the rule and who set it", 6.0, st.INK, "bold")
    txt(LX + 5.2, y2 + 6.2, f"pick: eligible starts first, then the objective ({dec_10a_s})", 5.5, st.INK2)
    txt(LX + 5.2, y2 + 2.6, f"{pick_line}; verdict by predictions only ({dec_s})", 5.5, st.INK2)
    assert y2 > 55.0, y2

    # (c) flat direction
    card(ax, 1.0, 1.0, 66.0, 52.0, "c", "A flat direction")
    cx = axes_mm(13.0, 10.0, 33.0, 35.0)
    draw_flat(cx, legend_anchor=(1.04, 1.0), minimal=True)
    cx.set_anchor("W")
    # (d) log posterior along the path A -> A2
    card(ax, 69.0, 1.0, 52.0, 52.0, "d", "Along the path A→A2")
    draw_path(axes_mm(83.0, 10.0, 35.0, 35.0))
    # (e) predictions
    card(ax, 123.0, 1.0, 59.0, 52.0, "e", "Predictions at every start")
    for j in range(2):
        draw_pred(axes_mm(134.0 + j * 28.0, 10.0, 18.5, 35.0), j, tick_size=6.0, minimal=True, ms=.45, wrap=True)
    return save("fig_verification")


# ================================================================ one-column versions (89 mm wide)
def n_checks(items_, kinds_):
    return sum(len(it["checks"]) for it in items_ if it["kind"] in kinds_ and it["checks"])


ND_B, NN_B = n_checks(REP["items"], ("deterministic",)), n_checks(REP["items"], ("numerical",))
ND_M, NN_M = n_checks(MPC["items"], ("deterministic",)), n_checks(MPC["items"], ("numerical",))
assert ND_B + NN_B == n_checks_b and ND_M + NN_M == n_checks_m


def tile_doc(x, y, sym):
    """A small document glyph (3.2 x 4.2 mm, lower-left at x, y) with a symbol on it."""
    f = .9
    ax.add_patch(plt.Polygon([(x, y), (x + 3.2, y), (x + 3.2, y + 4.2 - f), (x + 3.2 - f, y + 4.2), (x, y + 4.2)],
                             closed=True, fc="white", ec=st.ACCENT, lw=.55, zorder=8))
    txt(x + 1.6, y + 1.9, sym, 6.0, st.ACCENT, "bold", ha="center", z=9)


def one_col_1():
    """(a) validator as three tiles, (b) reproduction by step kind (both reruns), in hero cards. Minimal text; details in the
    caption. No ORCHID records drawn."""
    canvas(89.0, 94.0)
    X0, XW = 3.0, 83.0
    AT = H - 1.0
    card(ax, 1.0, AT - 19.4, 87.0, 19.4, "a", "Validator", size=6.5)
    TY, TH = AT - 6.6 - 10.8, 10.8
    TW = 19.6
    labels = ["schema", "file hashes", "step order"]
    for k, l in enumerate(labels):
        x = X0 + k * (TW + 1.8)
        box(x, TY, TW, TH, st.FILL["accent"], st.ACCENT, .6)
        txt(x + TW / 2, TY + 2.0, l, 6.0, st.ACCENT, "bold", ha="center")
        if k == 0:
            tile_doc(x + TW / 2 - 1.6, TY + 4.4, "{ }")
        elif k == 1:
            tile_doc(x + TW / 2 - 4.0, TY + 4.4, "#"); tile_doc(x + TW / 2 + .8, TY + 4.4, "#")
    # step-order motif inside the third tile, scaled to it
    x = X0 + 2 * (TW + 1.8) + .5; y = TY + 5.6
    for j, xx in enumerate((x, x + 6.4, x + 12.8)):
        box(xx, y - 1.2, 5.0, 2.4, "white", st.INK2, .4, .5, 4)
        txt(xx + 2.5, y, f"s{j + 1}", 5.0, st.INK2, ha="center")
    arrow((x + 5.0, y), (x + 6.4, y), st.INK2, .45, ms=3.5)
    arrow((x + 11.4, y), (x + 12.8, y), st.INK2, .45, ms=3.5)
    ax.add_patch(FancyArrowPatch((x + 15.3, y + 1.3), (x + 2.5, y + 1.3), arrowstyle="-|>", mutation_scale=3.5,
                                 color="#C00000", lw=.5, connectionstyle="arc3,rad=0.35", zorder=6))
    txt(x + 8.9, y + 3.6, "×", 6.5, "#C00000", "bold", ha="center")
    gx = X0 + 3 * (TW + 1.8)
    txt(gx + (X0 + XW - gx) / 2, TY + TH / 2 + 1.6, "0", 11.0, st.ACCENT, "bold", ha="center")
    txt(gx + (X0 + XW - gx) / 2, TY + TH / 2 - 3.0, "errors", 6.0, st.INK2, ha="center")

    # (b) reproduction
    BT = AT - 19.4 - 1.5
    card(ax, 1.0, 1.0, 87.0, BT - 1.0, "b", "Reproduction by step kind", size=6.5)
    ly = BT - 8.6
    mark(X0 + 1.6, ly, "spark"); txt(X0 + 3.4, ly, "scripted rerun (DGX Spark)", 6.0, st.INK2)
    mark(X0 + 41.0, ly, "mcp"); txt(X0 + 42.8, ly, "AI agent through MCP (Mac Studio)", 6.0, st.INK2)

    def lane(y_top, h, kind, title, nb, nm, tail=None):
        box(X0, y_top - h, XW, h, "white", st.INK2, .5)
        kind_glyph(X0 + 2.6, y_top - 2.6, kind, .8)
        txt(X0 + 4.8, y_top - 2.6, title, 6.5, st.INK, "bold")
        if nb is not None:
            mark(X0 + 55.0, y_top - 2.6, "spark"); txt(X0 + 56.8, y_top - 2.6, f"{nb}/{nb}", 6.0, st.INK)
            mark(X0 + 68.0, y_top - 2.6, "mcp"); txt(X0 + 69.8, y_top - 2.6, f"{nm}/{nm}", 6.0, st.INK)
        if tail:
            txt(X0 + 55.0, y_top - 2.6, tail, 6.0, st.INK)
        return y_top - h

    y = lane(ly - 3.2, 5.2, "deterministic", "Deterministic: identical", ND_B, ND_M)
    y1t = y - 1.0
    yb1 = lane(y1t, 45.6, "numerical", "Numerical: within tolerance", NN_B, NN_M)
    bx = axes_mm(X0 + 24.0, yb1 + 7.4, XW - 26.5, 45.6 - 12.8)
    num_plot(bx, short=True)
    bx.set_xlabel("|rerun − recorded| / tolerance", fontsize=6.0, labelpad=1.0)
    y2 = lane(yb1 - 1.0, 5.2, "judgement", "Judgement: by rule", None, None, tail="pick in mode A, all three")
    assert y2 > 2.0, y2
    return save("fig_verification_1col_1")


def one_col_2():
    """(a) flat direction, (b) log posterior along the path A -> A2, (c) predictions at every start, in hero cards;
    ORCHID records drawn (no badge or logo)."""
    canvas(89.0, 116.0)
    T = H - 1.0                                    # top margin (no badge strip)
    YA = 78.0
    card(ax, 1.0, YA, 87.0, T - YA, "a", "A flat direction", size=6.5)
    fx = axes_mm(14.0, YA + 7.0, 38.0, T - YA - 14.0)
    draw_flat(fx, legend_anchor=(1.06, 1.0), minimal=True)
    fx.set_anchor("W")
    YB = 41.5
    card(ax, 1.0, YB, 87.0, YA - 1.5 - YB, "b", "Along the path A→A2", size=6.5)
    draw_path(axes_mm(17.0, YB + 7.0, 66.0, YA - 1.5 - YB - 14.8))   # 0.8 lower top: the 'A' label clears the heading at 83 mm
    card(ax, 1.0, 1.0, 87.0, YB - 2.5, "c", "Same predictions", size=6.5)
    for j in range(2):
        draw_pred(axes_mm(13.0 + j * 43.0, 6.0, 30.0, YB - 2.5 - 13.5), j, tick_size=6.0, minimal=True)
    return save("fig_verification_1col_2")


probs = two_col() + one_col_1() + one_col_2()

src = {"figure": "fig_verification", "kind": "data figure (ORCHID records, tag provisional; no badge or logo)",
       "outputs": {"fig_verification": "171 x 114.0 mm, panels a-e in hero cards",
                   "fig_verification_1col_1": "83 x 87.7 mm, hero cards, minimal text: (a) validator, (b) reproduction by step kind; no ORCHID records",
                   "fig_verification_1col_2": "83 x 108.2 mm, hero cards, minimal text: (a) flat direction, (b) log posterior along the path A -> A2, (c) predictions at every start"},
       "sources": [{"path": tilde(p), "sha256": sha(p), "role": k} for k, p in F.items()],
       "numbers": {"general_steps": n_steps, "supply_links": n_supply, "file_refs_in_specific": n_refs, "schema": schema_v,
                   "validator_errors_total": n_err_total, "validator_warnings_total": n_warn_total,
                   "validator_errors_listed": val_err, "validator_errors_for_these_protocols": val_ours,
                   "staged_files": n_staged, "states": n_states, "phase_sequence": [ps["n_differing"], ps["compositions"]],
                   "checks_pass_spark": [n_checks_b, n_checks_b],
                   "checks_by_kind": {"spark": {"deterministic": ND_B, "numerical": NN_B},
                                      "mcp": {"deterministic": ND_M, "numerical": NN_M}},
                   "numerical_diff_over_tol": {a: v for a, v, _ in num_rows},
                   "notes_diff_over_tol": {note_rows[0][0]: note_rows[0][1], note_rows[1][0]: DZMAX},
                   "mcp_rerun": {"host": M_HOST, "machine": M_MACH, "label": "Mac Studio, AI agent through the orchid-sage MCP server (and read-only file tools)",
                                 "created": MC["created"], "compared": n_checks_m, "pass": MC["pass"],
                                 "staged_files": n_staged_m, "states_evaluated_sha256": mev["rerun"],
                                 "phase_sequence": [mps["n_differing"], mps["compositions"]],
                                 "numerical_diff_over_tol": {a: v for a, v, _ in num_rows_m},
                                 "parameters_rerun_pick_vs_recorded": note_rows[0][2],
                                 "pick": MPK["pick"], "pick_mode": m_pick_mode},
                   "pick_spark": PICK["pick"], "pick_mode_spark": b_pick_mode,
                   "flat_plane": [lab[ib], lab[iff]],
                   "A2_minus_A": dict(zip(lab, (thA2 - thA).round(4).tolist())), "dlogpost_A_A2": dlogpost,
                   "laplace_weight_A": wA, "mode_path": MP["summary"], "objective_tol": OBJ_TOL, "starts_by_machine_and_mode": {f"{m}/{k}": v for (m, k), v in cnt.items()},
                   "T_eut_ref": T_EUT_REF, "T_CrNi2_ref": T_CRNI2_REF, "T_tol": T_TOL,
                   "orchid": {"ORC-SV7H3CNRYS": T_EUT_ORC, "ORC-X3KVP7D3PO": T_CRNI2_ORC},
                   "starts": [{k: (v if not isinstance(v, np.ndarray) else None) for k, v in s.items()} for s in S]}}
(ROOT / "figs/fig_verification_sources.json").write_text(json.dumps(src, indent=1))
(ROOT / "figs/fig_verification_orchid_ids.json").write_text(json.dumps({
    "figure": "fig_verification", "release": "provisional",
    "labels": {"ORCHID eutectic line (e; 1col_2 c)": {"id": "ORC-SV7H3CNRYS", "T_K": T_EUT_ORC,
                                                      "state_id": orc["ORC-SV7H3CNRYS"]["state_ids"]},
               "ORCHID CrNi2 line (e; 1col_2 c)": {"id": "ORC-X3KVP7D3PO", "T_K": T_CRNI2_ORC,
                                                  "orchid_link": orc["ORC-X3KVP7D3PO"]["orchid_link"],
                                                  "note": "single reader, not yet released"}}}, indent=1))
print(json.dumps(src["numbers"]["numerical_diff_over_tol"]), json.dumps(src["numbers"]["mcp_rerun"]["numerical_diff_over_tol"]))
print("layout problems:", len(probs))
