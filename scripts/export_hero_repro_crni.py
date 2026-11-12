#!/usr/bin/env python3
"""Export the computed data of the reproduction figure (fig_hero_repro.py, label fig:repro). Nothing is drawn by hand.

Three databases of the final Cr-Ni fit (crni-paper-fit-step4c-b), each read from its record:
  original  : orchid-sage:assessments/crni-paper-fit-step4c-b/evidence/artifact/step4c_b_hingefloor_pick.tdb
              (the recorded pick, start s4 on the Mac Studio; sha256 3692243...)
  dgx_spark : orchid-sage:protocols/reproduce/crni-paper-fit-step4c-b-1.0.3-<spark1>/rerun/step4c_b_hingefloor_pick10a.tdb
              (scripted rerun of the specific protocol 1.0.3 on a DGX Spark, 7 Nov 2026; 1.0.4 is 1.0.3 with record
              fixes only, and the 1.0.4 record names this rerun as the scripted rerun of the same science)
  ai_agent  : orchid-sage:protocols/reproduce/crni-paper-fit-step4c-b-1.0.4-mcp-studio/rerun/step4c_b_hingefloor_pick10a.tdb
              (rerun of the final specific protocol 1.0.4 by an AI agent through the ORCHID-SAGE MCP server, Mac Studio)
Diagrams: the campaign's own method (pd4.py of <campaigns>/crni-paper-fit-20261106/scripts, imported read-only), as in
export_crni_paper_fit.py: G_ref + ideal by pycalphad `calculate` from EACH TDB with every VV = 0, lower convex hull at every
temperature (600-2200 K, 2 K; 1201 compositions); the eutectic (lowest liquid temperature) and the CrNi2 top from
pd4.topology. Checks: the 13 compared checks of each rerun, copied from its comparison record (reproduce_report.json of the
DGX Spark rerun; comparison.json and plan_compare.json of the agent rerun) and thermo_compare.json of each.
The earlier version of this script (step4-s1 draft campaign, graphical abstract) is in git history (commit dab9bff).
Run with the fit interpreter (ESPEI gradient PR 9039ea2 + pycalphad). Writes data/hero_repro_crni.json; cache in $FIG_CACHE.
"""
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402  (locations outside the repository: env or local/config.json)
RUN = paths.loc("runs_root") / "crni-paper-fit-20261106"
SAGE = paths.loc("orchid_sage")
REPRO = SAGE / "protocols/reproduce"
SPARK = REPRO / f"crni-paper-fit-step4c-b-1.0.3-{paths.host('spark1')}"
MCP = REPRO / "crni-paper-fit-step4c-b-1.0.4-mcp-studio"
ROOT = Path(__file__).resolve().parents[1]
CACHE = Path(os.environ.get("FIG_CACHE", "/tmp"))
PICK_SHA = "3692243331691fd6f48921a805f77ef136a280be8e23a0e454685eb4853f7b78"

sys.path.insert(0, str(RUN / "scripts"))
import model  # noqa: E402  (read_theta only)
import pd4  # noqa: E402  (diagram / topology on a supplied ref grid)

TDB = {"original": SAGE / "assessments/crni-paper-fit-step4c-b/evidence/artifact/step4c_b_hingefloor_pick.tdb",
       "dgx_spark": SPARK / "rerun/step4c_b_hingefloor_pick10a.tdb",
       "ai_agent": MCP / "rerun/step4c_b_hingefloor_pick10a.tdb"}
T = pd4.TT
PROV = []


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p, role):
    PROV.append({"path": paths.tilde(p), "sha256": sha(p), "role": role})
    return Path(p)


def J(p, role):
    return json.loads(read(p, role).read_text())


def ref_from(tdb):
    """pd4.ref_grid computed from this TDB (all VV = 0), cached outside the campaign (key = sha256 of the non-VV lines)."""
    body = "\n".join(l for l in Path(tdb).read_text().splitlines() if "VV00" not in l and not l.startswith("$"))
    key = hashlib.sha256(body.encode()).hexdigest()[:16]
    c = CACHE / f"crni_fig_ref_{key}_{len(T)}_{pd4.NX}.npy"
    if c.exists():
        return np.load(c), key
    from pycalphad import Database, calculate
    db = Database(str(tdb))
    pars = {f"VV{i:04d}": 0.0 for i in range(14)}
    pts = np.stack([1 - pd4.X, pd4.X], axis=1)
    out = np.empty((4, len(T), len(pd4.X)))
    for k, ph in enumerate(pd4.PH):
        r = calculate(db, ["CR", "NI", "VA"], ph, T=T, P=101325, N=1, points=pts, parameters=pars)
        out[k] = np.asarray(r.GM.squeeze()).reshape(len(T), len(pd4.X))
    r = calculate(db, ["CR", "NI", "VA"], "CRNI2", T=T, P=101325, N=1, parameters=pars)
    out[3] = np.asarray(r.GM.squeeze()).reshape(len(T), -1)[:, :1]
    np.save(c, out)
    return out, key


def tracks(di):
    """Two-phase field edges {key: [[T, x], ...]} with key 'P1+P2#k:side'; CrNi2 line points."""
    tr, c2 = {}, []
    for t, segs in zip(T, di):
        seen = {}
        for kind, phs, xl, xr in segs:
            if kind == 1 and phs == ("CRNI2",):
                c2.append([float(t), float(xl)])
            if kind != 2 or (xr - xl) <= 2.5 / (pd4.NX - 1):
                continue
            pair = "+".join(phs)
            k = seen.get(pair, 0); seen[pair] = k + 1
            for side, xv in (("l", xl), ("r", xr)):
                if pd4.X[0] < xv < pd4.X[-1]:
                    tr.setdefault(f"{pair}#{k}:{side}", []).append([float(t), float(xv)])
    return tr, c2


def invariant_line(di, t_target, must):
    i = int(np.argmin(np.abs(T - t_target)))
    xs = [(xl, xr) for kind, phs, xl, xr in di[i] if kind == 2 and (set(phs) & must) and (xr - xl) > 2.5 / (pd4.NX - 1)]
    return [float(min(a for a, _ in xs)), float(max(b for _, b in xs))] if xs else None


ROLE = {"original": "final fit as recorded (pick s4, Mac Studio)",
        "dgx_spark": "scripted rerun on a DGX Spark (specific protocol 1.0.3, same science as 1.0.4)",
        "ai_agent": "AI-agent rerun through the ORCHID-SAGE MCP server on the Mac Studio (specific protocol 1.0.4)"}
out = {"T_grid": [float(T[0]), float(T[-1]), float(T[1] - T[0])], "nx": int(pd4.NX), "diagrams": {}}
for name, p in TDB.items():
    read(p, f"TDB, {ROLE[name]}")
    ref, key = ref_from(p)
    th = model.read_theta(p)
    di = pd4.diagram(th, T, ref)
    tr, c2 = tracks(di)
    topo = pd4.topology(th, T, ref)
    out["diagrams"][name] = {"tdb_sha256": sha(p), "ref_key": key, "theta": th.tolist(), "tracks": tr, "crni2": c2,
                             "T_liquid_min": topo["T_liquid_min"], "T_CrNi2_max": topo["T_CrNi2_max"],
                             "liquid_min_line": invariant_line(di, topo["T_liquid_min"], {"LIQUID"}),
                             "crni2_top_line": invariant_line(di, topo["T_CrNi2_max"], {"CRNI2"})}
    print(name, sha(p)[:12], "T_eut", topo["T_liquid_min"], "T_CrNi2", topo["T_CrNi2_max"])
assert out["diagrams"]["original"]["tdb_sha256"] == PICK_SHA, "original TDB differs from the recorded pick"

# largest boundary difference of each rerun from the original on the common grid (same track keys and temperatures)
o = out["diagrams"]["original"]["tracks"]
for name in ("dgx_spark", "ai_agent"):
    r = out["diagrams"][name]["tracks"]
    dmax, unmatched = 0.0, sorted(set(o) ^ set(r))
    for k in set(o) & set(r):
        a = {t: x for t, x in o[k]}; b = {t: x for t, x in r[k]}
        dmax = max([dmax] + [abs(a[t] - b[t]) for t in set(a) & set(b)])
        if set(a) != set(b):
            unmatched.append(k + " (T range)")
    out["diagrams"][name]["vs_original"] = {"max_abs_dx": dmax, "grid_dx": float(pd4.X[2] - pd4.X[1]), "unmatched": unmatched}
    print(name, "max |dx| vs original", dmax, "unmatched", unmatched)

# ---- the 13 compared checks of each rerun, as recorded
SR = J(SPARK / "reproduce_report.json", "DGX Spark rerun: reproduce report (13 checks)")
MC = J(MCP / "comparison.json", "AI-agent rerun: comparison (13 checks)")
MP = J(MCP / "plan_compare.json", "AI-agent rerun: plan comparison (kinds, host class)")
ST = J(SPARK / "rerun/thermo_compare.json", "DGX Spark rerun: thermochemistry comparison")
MT = J(MCP / "rerun/thermo_compare.json", "AI-agent rerun: thermochemistry comparison")
SPK = J(SPARK / "rerun/pick10a_rerun.json", "DGX Spark rerun: 10a pick")
MPK = J(MCP / "rerun/pick10a_rerun.json", "AI-agent rerun: 10a pick")
assert SR["pass"] is True and MC["pass"] is True and MP["pass"] is True and not MC["not_run"]
kind = {it["id"]: it["kind"] for it in MP["items"]}
assert kind == {it["id"]: it["kind"] for it in SR["items"]}


def rows(checks, thermo):
    """[label, kind, |diff|/tol (None when compared for equality), pass] in a fixed order; checks = [{item, ...}]."""
    by = {}
    for c in checks:
        by.setdefault(c["item"], []).append(c)
    t = lambda c: abs(float(c["diff"])) / float(c["abs_tol"])
    c10, g = by["check10a"], by["global_10c"]
    out_ = [("states evaluated", "deterministic", None, by["evaluate_states"][0]["pass"]),
            ("phase sequence", "deterministic", None, by["phase_sequence"][0]["pass"]),
            ("pure elements (3)", "deterministic", None, all(c["pass"] for c in by["pure_elements"])),
            ("objective", "numerical", t(c10[0]), c10[0]["pass"]),
            ("pick eligible", "numerical", None, c10[1]["pass"]),
            ("eutectic T", "numerical", t(c10[2]), c10[2]["pass"]),
            ("CrNi$_2$ top T", "numerical", t(c10[3]), c10[3]["pass"]),
            ("basin hopping", "numerical", t(g[0]), g[0]["pass"]),
            ("annealing", "numerical", t(g[1]), g[1]["pass"]),
            ("thermochemistry", "numerical", thermo["max_abs_diff_rms_z"] / thermo["tol_z"], thermo["within_tol"]),
            ("Laplace weight", "numerical", t(by["laplace_weights"][0]), by["laplace_weights"][0]["pass"])]
    return out_, sum(len(v) for v in by.values())


s_checks = [dict(c, item=it["id"]) for it in SR["items"] for c in it.get("checks", [])]
m_checks = [c for c in MC["checks"] if "rule" in c]
s_rows, s_n = rows(s_checks, ST)
m_rows, m_n = rows(m_checks, MT)
assert s_n == m_n == MC["compared"] == 13, (s_n, m_n, MC["compared"])
out["checks"] = {
    "dgx_spark": {"protocol": SR["specific_protocol"], "machine": paths.machine(SR["host"]).rstrip(" 0123456789"),
                  "arch": SR["machine"], "pass": SR["pass"], "n": s_n, "rows": s_rows, "pick": SPK["pick"],
                  "T_liquid_min": float(SPK["T_liquid_min"]), "T_CrNi2_max": float(SPK["T_CrNi2_max"])},
    "ai_agent": {"protocol": MC["protocol"], "machine": paths.machine(MP["host"]), "arch": MP["machine"], "pass": MC["pass"],
                 "n": m_n, "rows": m_rows, "pick": MPK["pick"],
                 "T_liquid_min": float(MPK["T_liquid_min"]), "T_CrNi2_max": float(MPK["T_CrNi2_max"])}}
for name in ("dgx_spark", "ai_agent"):     # the record's invariants equal the ones computed here from its TDB
    assert out["checks"][name]["T_liquid_min"] == out["diagrams"][name]["T_liquid_min"]
    assert out["checks"][name]["T_CrNi2_max"] == out["diagrams"][name]["T_CrNi2_max"]
out["provenance"] = {"script": "scripts/export_hero_repro_crni.py", "python": sys.version.split()[0],
                     "pycalphad": __import__("pycalphad").__version__, "files": PROV,
                     "campaign_code_read_only": {m: {"path": paths.tilde(Path(mod.__file__)), "sha256": sha(mod.__file__)}
                                                 for m, mod in (("pd4", pd4), ("model", model))}}
(ROOT / "data/hero_repro_crni.json").write_text(json.dumps(out))
print("written data/hero_repro_crni.json;", {k: (v["machine"], v["protocol"], v["pick"]) for k, v in out["checks"].items()})
