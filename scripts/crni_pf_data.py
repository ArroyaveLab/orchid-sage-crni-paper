"""Shared loaders for the Cr-Ni PhaseForge one-shot figures (fig_entropy, fig_energetics, fig_oneshot).

Reads only computed result files of the run crni-phaseforge-20261105/results/ (campaign directory) and ORCHID records from the local
ORCHID data release (an orchid-data checkout, records with their ids). Nothing is typed in by hand.
"""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402  (locations outside the repository: env or local/config.json)

RUN = paths.loc("runs_root") / "crni-phaseforge-20261105"
RES = RUN / "results"
ORCHID = paths.loc("orchid_data")
MODELS = {"GRACE-2L-SMAX-OMAT-large": "GRACE-2L-SMAX-OMAT-large", "GRACE-2L-OMAT": "GRACE-2L-OMAT"}
MAIN = "GRACE-2L-SMAX-OMAT-large"


def res(name):
    return json.loads((RES / name).read_text())


def solids(model=MAIN):
    p = RES / f"solids_{model}.json"
    return json.loads(p.read_text()) if p.exists() else None


def orchid_records():
    """ORCHID Cr-Ni literature records (accepted), as stored in the release."""
    d = json.loads((ORCHID / "literature/systems/CR-NI.json").read_text())
    return [r for r in d["records"] if r.get("flags", {}).get("extraction_accepted", True)]


def orchid_release():
    d = json.loads((ORCHID / "literature/systems/CR-NI.json").read_text())
    return d.get("release")


def label_of(r):
    ph = r.get("phases") or []
    return ph[0].get("label", "") if ph else ""


def x_ni(r):
    return (r.get("overall_composition") or {}).get("NI")


def orchid_mixing(lattice):
    """HM_MIX records of one lattice with BOTH references on that lattice (the convention of the SQS mixing enthalpies).
    lattice: 'BCC_A2' (labels A2) or 'FCC_A1' (labels gamma / fcc, disordered)."""
    out = []
    for r in orchid_records():
        if r.get("property") != "HM_MIX":
            continue
        ref = r.get("reference_state") or {}
        if not (ref.get("CR", {}).get("phase") == lattice and ref.get("NI", {}).get("phase") == lattice):
            continue
        lab = label_of(r)
        dis = (lab in ("A2",)) if lattice == "BCC_A2" else (lab in ("γ", "fcc"))
        if dis and x_ni(r) is not None:
            out.append({"id": r["id"], "x_Ni": x_ni(r), "value": r["value"], "evidence_class": r["evidence_class"],
                        "sigma": r.get("uncertainty_budget", {}).get("quantities", {}).get("value", {}).get("sigma_effective"),
                        "citation": r.get("source", {}).get("citation") or r.get("paper"), "label": lab})
    return out


def orchid_ordered_fcc():
    """Ordered fcc (L12 gamma') HM_FORM / HM_MIX records referenced to fcc Cr and fcc Ni, de-duplicated by (x, value)."""
    seen, out = set(), []
    for r in orchid_records():
        if r.get("property") not in ("HM_FORM", "HM_MIX"):
            continue
        ref = r.get("reference_state") or {}
        if not (ref.get("CR", {}).get("phase") == "FCC_A1" and ref.get("NI", {}).get("phase") == "FCC_A1"):
            continue
        lab = label_of(r)
        if "γ'" not in lab and "γ’" not in lab and "L12" not in lab:
            continue
        key = (x_ni(r), r["value"])
        if key in seen:
            out[[k for k, q in enumerate(out) if (q["x_Ni"], q["value"]) == key][0]]["duplicate_ids"].append(r["id"]); continue
        seen.add(key)
        out.append({"id": r["id"], "duplicate_ids": [], "x_Ni": x_ni(r), "value": r["value"], "evidence_class": r["evidence_class"],
                    "label": lab, "citation": r.get("source", {}).get("citation") or r.get("paper")})
    return out


def orchid_temperatures():
    """Invariant and transition temperatures (K) with phases and class."""
    out = []
    for r in orchid_records():
        if r.get("property") in ("INVARIANT_TEMPERATURE", "TRANSITION_TEMPERATURE") and r.get("unit") == "K":
            out.append({"id": r["id"], "property": r["property"], "T": r["value"], "evidence_class": r["evidence_class"],
                        "phases": [p.get("label", "") for p in (r.get("phases") or [])],
                        "reaction": (r.get("reaction") or {}).get("printed") if isinstance(r.get("reaction"), dict) else r.get("reaction_printed"),
                        "source_system": r.get("source_system", "CR-NI"), "citation": r.get("source", {}).get("citation")})
    return out


def orchid_assessed():
    d = json.loads((ORCHID / "assessed-phase-assemblages/espei-zpf/CR-NI-p329.json").read_text())
    pts = []
    for T, reg, rid in zip(d["conditions"]["T"], d["values"], d["orchid"]["record_ids"]):
        if len(reg) == 1:
            pts.append({"id": rid, "T": T, "x_Ni": reg[0][2][0], "kind": "single", "phases": [reg[0][0]]})
        else:
            hp = [q for q in reg if q[0] == "__HYPERPLANE__"][0]
            pts.append({"id": rid, "T": T, "x_Ni": hp[2][0], "kind": "two_phase", "phases": [q[0] for q in reg if q[0] != "__HYPERPLANE__"]})
    return pts, d["reference"]
