#!/usr/bin/env python3
"""Log posterior along the straight path between the two recorded modes of the final Cr-Ni fit (A_s4 -> A2_s5_flat).

theta(t) = theta_A + t (theta_A2 - theta_A), t from -0.25 to 1.25 (25 even steps of 1/16, plus t = +-0.03 around each mode).
Objective: the FIXED objective of crni-paper-fit-step4c-b@1.0.3, i.e. model3.GradTarget of the campaign
<campaigns>/crni-paper-fit-20261106 (sha256 pinned in the protocol, checked here) built from
steps/configs/step4c_b_hingefloor.json; one process, OMP_NUM_THREADS=1, PYTHONPATH = PhaseForgePlus src (as in the protocol).
Read only: nothing in the campaign is written (pd4 reference grids for the fine temperature windows are cached in the
scratch directory given as the second argument, never in the campaign).

Check first (fail closed, exit 3): the objective at A and A2 must equal the recorded values -5657.288636860 and
-5657.293148833 within 1e-6, by the analytic call (value and gradient, as in the multistart) and by value_only.

At every t: log posterior (value_only) and its parts by residual type; pd4 topology on the standard 2 K grid of evaluate.py
(eutectic = lowest T with liquid, CrNi2 top = highest T with CrNi2, phase sequence ok) and the same two temperatures on
0.1 K windows (1600-1630 K and 845-875 K).

usage: OMP_NUM_THREADS=1 PYTHONPATH=<PhaseForgePlus>/src <fit python> scripts/compute_mode_path.py \
           data/crni_mode_path.json SCRATCH_DIR
"""
import hashlib
import json
import os
import subprocess
import sys
import time
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402  (locations outside the repository: env or local/config.json)
CAMP = paths.loc("runs_root") / "crni-paper-fit-20261106"
SAGE = paths.loc("orchid_sage")
PFP = paths.loc("phaseforgeplus")
OUT, SCR = Path(sys.argv[1]), Path(sys.argv[2])
F = {"modes": CAMP / "results/uq/modes_step4c_b.json", "config": CAMP / "steps/configs/step4c_b_hingefloor.json",
     "model3": CAMP / "scripts/model3.py", "pd4": CAMP / "scripts/pd4.py",
     "protocol": SAGE / "protocols/specific/crni-paper-fit-step4c-b@1.0.3.yaml",
     "model3_addendum": SAGE / "assessments/crni-paper-fit-step4c-b/addendum-1.0.3/code/scripts/model3.py"}
REC = {"A_s4": -5657.288636860, "A2_s5_flat": -5657.293148833}
TOL = 1e-6
MODEL3_PIN = "a326d108139548ef15d7186f7efa4ba67c12d7346d17f59810027093ae9d2d66"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def git(d, *a):
    return subprocess.run(["git", "-C", str(d), *a], capture_output=True, text=True).stdout.strip()


assert os.environ.get("OMP_NUM_THREADS") == "1", "run with OMP_NUM_THREADS=1"
assert sha(F["model3"]) == MODEL3_PIN == sha(F["model3_addendum"]), "model3.py is not the 1.0.3 pin"
assert MODEL3_PIN in F["protocol"].read_text()
sys.path.insert(0, str(CAMP / "scripts"))
import model3  # noqa: E402
import pd4  # noqa: E402

modes = json.loads(F["modes"].read_text())
assert [m["name"] for m in modes] == ["A_s4", "A2_s5_flat"]
thA, thA2 = np.asarray(modes[0]["theta"], float), np.asarray(modes[1]["theta"], float)

t0 = time.time()
G = model3.GradTarget(str(F["config"]))
assert list(G.idx) == list(range(14))
t_build = time.time() - t0
print(f"GradTarget built in {t_build:.1f} s", flush=True)

# ---------------------------------------------------------------- check at the recorded modes (fail closed)
check = {}
for name, th in (("A_s4", thA), ("A2_s5_flat", thA2)):
    v, g = G(th / G.scale)
    vo = G.value_only(th)
    check[name] = {"recorded": REC[name], "call": float(v), "call_hex": float(v).hex(), "value_only": float(vo),
                   "diff_call": float(v) - REC[name], "diff_value_only": float(vo) - REC[name],
                   "grad_norm_q": float(np.linalg.norm(g)), "pass": abs(v - REC[name]) <= TOL and abs(vo - REC[name]) <= TOL}
    print(name, "%.9f" % v, "value_only %.9f" % vo, "recorded %.9f" % REC[name], "pass", check[name]["pass"], flush=True)
if not all(c["pass"] for c in check.values()):
    OUT.with_suffix(".check_failed.json").write_text(json.dumps(check, indent=1))
    print("CHECK FAILED: objective at the recorded modes differs by more than 1e-6; stopped", flush=True)
    sys.exit(3)

# ---------------------------------------------------------------- temperatures (pd4, as in evaluate.py, plus 0.1 K windows)
REF = pd4.ref_grid(pd4.TT)                       # standard grid, read from the campaign cache (exists)
pd4.R = SCR                                      # fine-window grids cached in the scratch directory only
(SCR / "data/cache").mkdir(parents=True, exist_ok=True)
TE_W, TC_W = np.round(np.arange(1600.0, 1630.0001, 0.1), 1), np.round(np.arange(845.0, 875.0001, 0.1), 1)
REF_E, REF_C = pd4.ref_grid(TE_W), pd4.ref_grid(TC_W)


def temps(th):
    top = pd4.topology(th, pd4.TT, REF)
    te = pd4.topology(th, TE_W, REF_E)["T_liquid_min"]
    tc = pd4.topology(th, TC_W, REF_C)["T_CrNi2_max"]
    assert TE_W[0] < te < TE_W[-1] and TC_W[0] < tc < TC_W[-1], (te, tc)   # transition inside the window
    return {"T_eut_2K": top["T_liquid_min"], "T_CrNi2_top_2K": top["T_CrNi2_max"], "topology_ok": top["ok"],
            "n_bad": top["n_bad"], "T_eut_0p1K": float(te), "T_CrNi2_top_0p1K": float(tc)}


# ---------------------------------------------------------------- the path
ts = sorted(set(np.round(np.linspace(-0.25, 1.25, 25), 6).tolist()) | {-0.03, 0.03, 0.97, 1.03})
rows = []
for t in ts:
    th = thA + t * (thA2 - thA)
    t1 = time.time()
    parts = G.parts(th, gradient=False)
    lp = sum(v for v, _ in parts.values()) + G.log_prior(th)
    r = {"t": t, "logpost": float(lp), "logpost_hex": float(lp).hex(),
         "parts": {k: float(v) for k, (v, _) in sorted(parts.items())}, "log_prior": G.log_prior(th),
         "theta": th.tolist(), **temps(th), "seconds": round(time.time() - t1, 1)}
    rows.append(r)
    print(f"t {t:+.4f} lp {lp:.9f} Teut {r['T_eut_2K']:.0f}/{r['T_eut_0p1K']:.1f} Tc2 {r['T_CrNi2_top_2K']:.0f}/"
          f"{r['T_CrNi2_top_0p1K']:.1f} ok {r['topology_ok']} {r['seconds']} s", flush=True)

lpA = next(r["logpost"] for r in rows if r["t"] == 0.0)
lpA2 = next(r["logpost"] for r in rows if r["t"] == 1.0)
inner = [r for r in rows if 0.0 <= r["t"] <= 1.0]
low = min(inner, key=lambda r: r["logpost"])
out = {"what": "log posterior along theta(t) = theta_A + t (theta_A2 - theta_A), modes A_s4 (t = 0) and A2_s5_flat (t = 1)",
       "objective": "crni-paper-fit-step4c-b@1.0.3: model3.GradTarget(steps/configs/step4c_b_hingefloor.json), value_only",
       "created": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "host": paths.machine(os.uname().nodename), "python": paths.tilde(sys.executable),
       "env": {"OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS"), "PYTHONPATH": paths.tilde(os.environ.get("PYTHONPATH") or "")},
       "inputs": {k: {"path": paths.tilde(p), "sha256": sha(p)} for k, p in F.items()},
       "code": {"script": "scripts/compute_mode_path.py", "paper_repo_commit_at_run": git(Path(__file__).resolve().parents[1], "rev-parse", "HEAD"),
                "orchid_sage_commit": git(SAGE, "rev-parse", "HEAD"),
                "orchid_sage_addendum_1_0_3_commit": git(SAGE, "log", "-1", "--format=%H", "--", "assessments/crni-paper-fit-step4c-b/addendum-1.0.3"),
                "phaseforgeplus_commit": git(PFP, "rev-parse", "HEAD"), "espei_version": {k: (paths.machine(v) if k == "host" else paths.tilde(v) if isinstance(v, str) else v)
                                                                                        for k, v in model3.espei_version().items()}},
       "check_at_modes": {"tol": TOL, "rows": check},
       "temperature_method": "pd4.topology (evaluate.py): eutectic = lowest T with liquid, CrNi2 top = highest T with CrNi2; "
                             "standard 2 K grid 600-2200 K and 0.1 K windows 1600-1630 K / 845-875 K",
       "summary": {"logpost_A": lpA, "logpost_A2": lpA2, "dlogpost_A2_minus_A": lpA2 - lpA,
                   "min_on_0_1": {"t": low["t"], "logpost": low["logpost"], "dlogpost_vs_A": low["logpost"] - lpA},
                   "barrier_vs_higher_end": low["logpost"] - lpA, "barrier_vs_lower_end": low["logpost"] - min(lpA, lpA2),
                   "T_eut_0p1K_range_0_1": [min(r["T_eut_0p1K"] for r in inner), max(r["T_eut_0p1K"] for r in inner)],
                   "T_CrNi2_0p1K_range_0_1": [min(r["T_CrNi2_top_0p1K"] for r in inner), max(r["T_CrNi2_top_0p1K"] for r in inner)],
                   "T_eut_2K_set": sorted({r["T_eut_2K"] for r in rows}), "T_CrNi2_2K_set": sorted({r["T_CrNi2_top_2K"] for r in rows}),
                   "topology_ok_all": all(r["topology_ok"] for r in rows)},
       "build_seconds": round(t_build, 1), "rows": rows}
OUT.write_text(json.dumps(out, indent=1))
print(json.dumps(out["summary"], indent=1))
