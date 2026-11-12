#!/usr/bin/env python3
"""Export the computed data of Figs. 4 and 6 of the Cr-Ni paper from the frozen fit crni-paper-fit-step4c-b@1.0.0.

Nothing is typed by hand: every number comes from the files listed in `provenance` of the output, each with its sha256.

Diagrams (Fig. 4, Fig. 6a): the campaign's own diagram method, pd4.py of <campaigns>/crni-paper-fit-20261106/scripts
(imported read-only): G_ref + ideal of BCC_A2, FCC_A1, LIQUID and CRNI2 by pycalphad `calculate` from EACH TDB with every
VV = 0, then the lower convex hull at every temperature (600-2200 K, 2 K; 1201 compositions). pd4.ref_grid is never called
(it writes a cache into the campaign directory); the grid is cached here in $FIG_CACHE.
  step 1 one-shot : tdb/step1_oneshot_pick.tdb
  step 2 liquidus : tdb/step2_liquidus_pick.tdb
  step 3b thermo  : tdb/step3b_thermo_crni2free_pick.tdb
  step 4c-b final : tdb/step4c_b_hingefloor_pick.tdb (sha256 must be 36922433...)
Evidence: the 695 states of the evidence bundle 1.1.0 of crni-paper-fit-step4c-b (states@1.1.0.json; pinned by @1.0.2; bundle 1.0.0
placed the 130 ZPF states given in x(CR) at x(NI) = x(CR)), with the group each
enters the fit in (liq_c = liquid ZPF from step 2, solid_c = solid ZPF from step 4, hinge = exclusions from step 4).
Physics (Fig. 6a): metastable BCC_A2 alone at the pick - chemical spinodal (d2G/dx2 = 0, physics.d2), Cahn coherent spinodal
(d2G/dx2 + 2k = 0 with k of cr-ni-coherent-20261105/results.json, cases base/low/high, as physics.py), and the binodal from
the lower hull of G_BCC alone (as physics.binodal), on the same grids.
Scalars (Fig. 6b-e) are copied from results/physics_step4c_b.json, results/uq/laplace_step4c_b.json and
results/uq/classified_mixture_draws_step4c_b.json, and the draws' T_eut / T_CrNi2 values from the latter.

Run with the fit interpreter (ESPEI gradient PR 9039ea2 + pycalphad) (the fit environment of the specific protocol). Writes data/crni_paper_fit_figs.json.
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
SPEC = SAGE / "protocols/specific/crni-paper-fit-step4c-b@1.0.0.yaml"
BUNDLE = SAGE / "assessments/crni-paper-fit-step4c-b/evidence"
DASH = SAGE / "protocols/dashboards/crni-paper-fit-step4c-b-1.0.0/dashboard_data.json"
COH = paths.loc("runs_root") / "cr-ni-coherent-20261105/results.json"
ROOT = Path(__file__).resolve().parents[1]
CACHE = Path(os.environ.get("FIG_CACHE", "/tmp"))
PICK_SHA = "3692243331691fd6f48921a805f77ef136a280be8e23a0e454685eb4853f7b78"

sys.path.insert(0, str(RUN / "scripts"))
import model  # noqa: E402  (read_theta only)
import pd4  # noqa: E402  (diagram / topology / excess / _lower_hull on a supplied ref grid)
import physics  # noqa: E402  (d2 only)

TDB = {"step1": RUN / "tdb/step1_oneshot_pick.tdb",
       "step2": RUN / "tdb/step2_liquidus_pick.tdb",
       "step3b": RUN / "tdb/step3b_thermo_crni2free_pick.tdb",
       "step4c_b": RUN / "tdb/step4c_b_hingefloor_pick.tdb"}
T = pd4.TT
PROV = []


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p, role):
    PROV.append({"path": paths.tilde(p), "sha256": sha(p), "role": role})
    return Path(p)


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
    """Two-phase field edges {key: [[T, x], ...]} with key 'P1+P2#k:side'; CrNi2 line points; invariant lines."""
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
    """[x_left, x_right] spanned at T = t_target by the two-phase fields that contain a phase in `must`."""
    i = int(np.argmin(np.abs(T - t_target)))
    xs = [(xl, xr) for kind, phs, xl, xr in di[i] if kind == 2 and (set(phs) & must) and (xr - xl) > 2.5 / (pd4.NX - 1)]
    if not xs:
        return None
    return [float(min(a for a, _ in xs)), float(max(b for _, b in xs))]


out = {"T_grid": [float(T[0]), float(T[-1]), float(T[1] - T[0])], "nx": int(pd4.NX), "steps": {}}
read(SPEC, "specific protocol crni-paper-fit-step4c-b@1.0.0")
for name, p in TDB.items():
    read(p, f"TDB {name}")
    ref, key = ref_from(p)
    th = model.read_theta(p)
    di = pd4.diagram(th, T, ref)
    tr, c2 = tracks(di)
    topo = pd4.topology(th, T, ref)
    eut = invariant_line(di, topo["T_liquid_min"], {"LIQUID"}) if np.isfinite(topo["T_liquid_min"]) else None
    c2l = invariant_line(di, topo["T_CrNi2_max"], {"CRNI2"}) if np.isfinite(topo["T_CrNi2_max"]) else None
    out["steps"][name] = {"tdb": paths.tilde(p), "sha256": sha(p), "ref_key": key, "theta": th.tolist(),
                          "tracks": tr, "crni2": c2, "T_liquid_min": topo["T_liquid_min"], "T_CrNi2_max": topo["T_CrNi2_max"],
                          "liquid_min_line": eut, "crni2_top_line": c2l, "topology_ok": topo["ok"], "n_bad": topo["n_bad"],
                          "bad_T_range": topo["bad_T_range"], "spurious_severity": topo["spurious_severity"]}
    print(name, sha(p)[:12], "T_liq_min", topo["T_liquid_min"], "T_CrNi2", topo["T_CrNi2_max"], "ok", topo["ok"], "bad", topo["bad_T_range"])
assert out["steps"]["step4c_b"]["sha256"] == PICK_SHA, "pick TDB hash differs from the frozen protocol"

# ---- evidence: the bundle's states, with the fit group each enters
stf = read(BUNDLE / "states@1.1.0.json", "evidence bundle states (695), bundle 1.1.0")
read(BUNDLE / "MANIFEST@1.1.0.json", "evidence bundle manifest 1.1.0")
S = json.loads(stf.read_text())
pts = []
for s in S["states"]:
    if s.get("x") is None or s.get("T_K") is None:
        continue
    x = s["x"] if s.get("element", "NI") == "NI" else 1 - s["x"]
    grp = "hinge" if s["source"] == "hinge" else s["source_file"].split("/")[0]
    pts.append({"x": float(x), "T": float(s["T_K"]), "kind": s["kind"], "group": grp, "evidence_class": s["evidence_class"],
                "orchid_ids": s.get("orchid_ids") or [], "state_ids": s.get("state_ids") or [],
                "vertices": s.get("vertices") or [], "excluded": s.get("excluded") or []})
out["evidence"] = {"n_states": S["n_states"], "points": pts, "release": sorted({s.get("orchid_release") for s in S["states"]})}

# ---- invariants as recorded in the dashboard (ORCHID observed values) and the steps' objectives
D = json.loads(read(DASH, "dashboard data crni-paper-fit-step4c-b-1.0.0").read_text())
out["invariants"] = D["invariants"]
out["dashboard_steps"] = [{k: (paths.public_text(s[k]) if isinstance(s[k], str) else s[k]) for k in ("step", "pick", "objective", "starts", "modes", "key_results", "role")}
                         for s in D["steps"]]   # record text with host names as machine labels
out["orchid_release"] = D["orchid_release"]

# ---- physics at the pick: metastable bcc gap curves
th = np.asarray(out["steps"]["step4c_b"]["theta"])
ref, _ = ref_from(TDB["step4c_b"])
coh = json.loads(read(COH, "Cahn coherent-strain inputs k (cases)").read_text())["cases"]
pb = (th[4], th[5], th[6], th[7])
xg = np.linspace(1e-4, 1 - 1e-4, 4001)
TS = np.arange(200.0, 2001.0, 1.0)


def spinodal_curve(shift):
    rows = []
    for t in TS:
        v = physics.d2(*pb, t, xg) + shift
        neg = np.where(v < 0)[0]
        if len(neg):
            rows.append([float(t), float(xg[neg[0]]), float(xg[neg[-1]])])
    return rows


gap = {"chemical_spinodal": spinodal_curve(0.0),
       "coherent_spinodal": {k: spinodal_curve(2 * c["k_J"]) for k, c in coh.items()},
       "coherent_k_J": {k: c["k_J"] for k, c in coh.items()}}
ex, _ = pd4.excess(th, T)
bino = []
for i, t in enumerate(T):
    g = ref[0, i] + ex[0, i]
    h = pd4._lower_hull(pd4.X, g)
    best = None
    for a, b in zip(h[:-1], h[1:]):
        if b - a > 3 and (best is None or pd4.X[b] - pd4.X[a] > best[1] - best[0]):
            best = (float(pd4.X[a]), float(pd4.X[b]))
    if best:
        bino.append([float(t), best[0], best[1]])
gap["binodal"] = bino
gap["chemical_spinodal_top_K"] = gap["chemical_spinodal"][-1][0] if gap["chemical_spinodal"] else None
gap["coherent_spinodal_top_K"] = {k: (v[-1][0] if v else None) for k, v in gap["coherent_spinodal"].items()}
gap["binodal_top_K"] = bino[-1][0] if bino else None
out["bcc_gap"] = gap
print("bcc: chem top", gap["chemical_spinodal_top_K"], "coh", gap["coherent_spinodal_top_K"], "binodal top", gap["binodal_top_K"])

P = json.loads(read(RUN / "results/physics_step4c_b.json", "physics checks of the pick").read_text())
assert P["source"].endswith("step4c_b_hingefloor_pick.tdb")
out["physics_file"] = {"bcc": {k: P["bcc"][k] for k in ("chemical_spinodal_top_K", "at_x_Ni", "coherent_spinodal_top_K",
                                                         "coherent_k_J", "metastable_binodal", "H_mix_0.5_fit_J", "S_ex_0.5_fit",
                                                         "incoherent_estimates")},
                       "fcc_chemical_spinodal_top_K": P["fcc"]["chemical_spinodal_top_K"],
                       "liquid_convex_600_2200": P["liquid_convexity"]["convex_everywhere_600_2200"]}
out["design_point"] = {"x_Ni": 0.52, "T_K": 1473.0, "phase_at_pick": pd4.phase_at(th, 1473.0, 0.52, ref[:, [int(np.argmin(np.abs(T - 1473.0)))]])}

# ---- UQ
L = json.loads(read(RUN / "results/uq/laplace_step4c_b.json", "Laplace mixture (modes, weights, mixture and independent summaries)").read_text())
C = json.loads(read(RUN / "results/uq/classified_mixture_draws_step4c_b.json", "1000 classified mixture draws").read_text())
out["uq"] = {"weights": L["weights"], "mode_classes": L["mode_classes"], "mixture": L["mixture"],
             "independent_marginals": L["independent_marginals"], "draw_component_counts": L["draw_component_counts"],
             "modes": [{k: m[k] for k in ("name", "logpost", "log_evidence", "grad_norm_q")} for m in L["modes"]],
             "classified": {k: v for k, v in C.items() if k != "draws"},
             "draws": [[d["T_eut"], d["T_CrNi2"], bool(d["ok_no_crni2_window"]), int(d["n_bad"])] for d in C["draws"]]}
out["provenance"] = {"script": "scripts/export_crni_paper_fit.py", "python": sys.version.split()[0],
                     "pycalphad": __import__("pycalphad").__version__, "files": PROV,
                     "campaign_code_read_only": {m: {"path": paths.tilde(Path(mod.__file__)), "sha256": sha(mod.__file__)}
                                                 for m, mod in (("pd4", pd4), ("model", model), ("physics", physics))}}
(ROOT / "data/crni_paper_fit_figs.json").write_text(json.dumps(out))
print("written data/crni_paper_fit_figs.json;", len(pts), "states")
