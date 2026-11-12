#!/usr/bin/env python3
"""Export the computed Cr-Ni panels of the hero schematic (fig_hero.py) from the final fit sequence. Nothing is drawn by hand.

The three small panels of "Liquid first, then down in temperature" show the recorded step databases of the final sequence
(crni-paper-fit-step4c-b; the same data as fig_crni_sequence and fig:repro):
  1 Liquid and melting phases : step 2 (liquidus) pick, tdb/step2_liquidus_pick.tdb - diagram (boundaries with the liquid
                                highlighted) and the liquid phase-boundary states it was fitted to (group liq_c);
  2 Thermochemistry           : step 3b (thermochemistry, CrNi2 free) pick, tdb/step3b_thermo_crni2free_pick.tdb - the liquid
                                enthalpy of mixing, pycalphad HM_MIX of LIQUID (temperature independent for these parameters),
                                with the four liquid HM_MIX datasets of the evidence bundle (files/thermo/*HM_MIX-LIQUID*);
  3 Solid state, excluded phases : step 4c-b, the final pick (sha256 3692243...; the database of specific protocol 1.0.4) -
                                diagram and the phase-boundary states of the fit (groups liq_c and solid_c).
Diagrams and states are copied from data/crni_paper_fit_figs.json (scripts/export_crni_paper_fit.py: pd4 hull mapping of
each step TDB, 600-2200 K, with every source file and sha256 recorded); its sha256 is written here.
The earlier version (set E optimum of the 5 Nov rebuild campaign) is in git history (commit 2cd69fa).
Run with the fit interpreter (ESPEI gradient PR 9039ea2 + pycalphad). Writes data/hero_crni.json.
"""
import glob
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402  (locations outside the repository: env or local/config.json)
ROOT = Path(__file__).resolve().parents[1]
FIGS = ROOT / "data/crni_paper_fit_figs.json"
THERMO = paths.loc("orchid_sage") / "assessments/crni-paper-fit-step4c-b/evidence/files/thermo"
PICK_SHA = "3692243331691fd6f48921a805f77ef136a280be8e23a0e454685eb4853f7b78"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


F = json.loads(FIGS.read_text())
S = F["steps"]
assert S["step4c_b"]["sha256"] == PICK_SHA
prov = [{"path": "data/crni_paper_fit_figs.json", "sha256": sha(FIGS), "role": "step diagrams and evidence states"}]
keep = ("tracks", "crni2", "T_liquid_min", "T_CrNi2_max", "liquid_min_line", "crni2_top_line", "tdb", "sha256")
out = {"T_grid": F["T_grid"], "tiles": {}}
out["tiles"]["1_liquid"] = {"step": "step2", **{k: S["step2"][k] for k in keep},
                            "states": [[p["x"], p["T"]] for p in F["evidence"]["points"] if p["group"] == "liq_c"]}
out["tiles"]["3_solid"] = {"step": "step4c_b", **{k: S["step4c_b"][k] for k in keep},
                           "states": [[p["x"], p["T"]] for p in F["evidence"]["points"] if p["group"] in ("liq_c", "solid_c")]}

# tile 2: liquid enthalpy of mixing of the step-3b database and the liquid HM_MIX data of the bundle
from pycalphad import Database, calculate  # noqa: E402
tdb3 = paths.expand(S["step3b"]["tdb"])
assert sha(tdb3) == S["step3b"]["sha256"]
x = np.linspace(0.005, 0.995, 199)
r = calculate(Database(str(tdb3)), ["CR", "NI", "VA"], "LIQUID", T=1873.0, P=101325, N=1, points=np.stack([1 - x, x], 1),
              output="HM_MIX")
data = []
for f in sorted(glob.glob(str(THERMO / "*HM_MIX-LIQUID*.json"))):
    d = json.loads(Path(f).read_text())
    assert d["output"] == "HM_MIX" and d["phases"] == ["LIQUID"]
    assert d["solver"]["sublattice_configurations"][0][0] == ["CR", "NI"]
    vals = np.asarray(d["values"]).ravel()
    xs = [occ[0][1] for occ in d["solver"]["sublattice_occupancies"]]
    data += [[float(a), float(v) / 1000] for a, v in zip(xs, vals)]
    prov.append({"path": paths.tilde(f), "sha256": sha(f), "role": "liquid HM_MIX dataset of the evidence bundle"})
out["tiles"]["2_thermo"] = {"step": "step3b", "tdb": S["step3b"]["tdb"], "sha256": S["step3b"]["sha256"],
                            "hmix_model": {"x": x.tolist(), "H_kJ": (np.asarray(r.HM_MIX).ravel() / 1000).tolist(), "T_K": 1873.0},
                            "hmix_data_kJ": data}
out["provenance"] = {"script": "scripts/export_hero_crni.py", "pycalphad": __import__("pycalphad").__version__, "files": prov}
(ROOT / "data/hero_crni.json").write_text(json.dumps(out))
print("tiles:", {k: (v["step"], v["sha256"][:12], len(v.get("states", v.get("hmix_data_kJ", [])))) for k, v in out["tiles"].items()},
      "H range", min(out["tiles"]["2_thermo"]["hmix_model"]["H_kJ"]), [min(d[1] for d in data), max(d[1] for d in data)])
