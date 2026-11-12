"""Locations of the inputs that live outside this repository (standard library only).

No machine-specific path, host or user name is written in the scripts. Each location comes from an environment variable,
else from local/config.json (gitignored; template local.example/config.json), else from a default: the sibling
checkouts next to this repository (../orchid-sage, ../orchid-data, ../orchid-brand, ../open-tdb, ../PhaseForgePlus) and
data/runs/ inside it for the campaign directories.

  loc(key)        a location (Path)
  host(label)     the host name of a machine label (spark1, spark2, studio) in this machine's records; the label otherwise
  machine(name)   the machine class shown in figures and data ("DGX Spark 1", "Mac Studio") for a host name or label
  expand(p)       a path as written in a record ('<orchid-sage>/...' -> loc('orchid_sage'), other '<home>/...' -> the
                  record home; a '~' a user gives -> that user's home)
  tilde(p)        the inverse, for writing records

The records name machine-specific locations by placeholder only, as the public ORCHID-SAGE copy does: <orchid-sage> for
the ORCHID-SAGE checkout (ORCHID_SAGE_REPO or config 'orchid_sage'), <home> for the home directory of the machine that
wrote the record (CRNI_RECORD_HOME or config 'record_home', else this user's home).
"""
import json
import os
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SETTINGS = {  # key -> (environment variable, default relative to the repository root)
    "runs_root": ("CRNI_RUNS_ROOT", "data/runs"),               # campaign directories
    "mcp_runs_root": ("CRNI_MCP_RUNS_ROOT", "data/runs"),       # fresh run roots of the MCP reruns
    "orchid_sage": ("ORCHID_SAGE_REPO", "../orchid-sage"),
    "orchid_data": ("ORCHID_DATA_DIR", "../orchid-data"),
    "orchid_brand": ("ORCHID_BRAND_REPO", "../orchid-brand"),
    "open_tdb": ("OPEN_TDB_REPO", "../open-tdb"),
    "phaseforgeplus": ("PHASEFORGEPLUS_REPO", "../PhaseForgePlus"),
}
ALIASES = {"<orchid-sage>": "orchid_sage"}                    # how the records name the orchid-sage checkout (loc('orchid_sage'))
RECORD_HOME = "<home>"                                         # how the records name the home directory
MACHINES = {"studio": "Mac Studio", "spark1": "DGX Spark 1", "spark2": "DGX Spark 2", "spark3": "DGX Spark 3", "spark4": "DGX Spark 4"}
_cfg = None


def config():
    global _cfg
    if _cfg is None:
        p = Path(os.environ.get("CRNI_PAPER_CONFIG") or REPO / "local" / "config.json")
        _cfg = json.loads(p.read_text()) if p.is_file() else {}
    return _cfg


def _path(v):
    q = Path(os.path.expanduser(str(v)))       # '~' in a config value or environment variable: this user's home
    return q if q.is_absolute() else (REPO / q).resolve()


def loc(key):
    env, dflt = SETTINGS[key]
    return _path(os.environ.get(env) or config().get(key) or dflt)


def host(label):
    return (config().get("hosts") or {}).get(label, label)


def machine(name):
    hs = {v: k for k, v in (config().get("hosts") or {}).items()}
    lab = hs.get(name) or hs.get(str(name).replace("spark-", "", 1)) or str(name).replace("spark-", "", 1)
    return MACHINES.get(lab, MACHINES.get(name, str(name)))


def record_home():
    v = os.environ.get("CRNI_RECORD_HOME") or config().get("record_home")
    return Path(os.path.expanduser(v or "~"))   # the home directory that <home> stands for in records


def expand(p):
    s = str(p)
    for a, key in ALIASES.items():
        if s == a or s.startswith(a + "/"):
            return loc(key) / s[len(a) + 1:]
    if s == RECORD_HOME or s.startswith(RECORD_HOME + "/"):
        return record_home() / s[len(RECORD_HOME) + 1:]
    q = Path(os.path.expanduser(s))                         # a path a user gives ('~' = that user's home)
    return q if q.is_absolute() else REPO / q               # a file of this repository


def public_text(s):
    """Host names in a copied record text written as their machine labels (spark1, mac-studio)."""
    for lab, name in (config().get("hosts") or {}).items():
        if name and name != lab:
            s = re.sub(r"(?<![A-Za-z0-9])(?:spark-|dgx-)?" + re.escape(name) + r"(?![A-Za-z0-9])", "mac-studio" if lab == "studio" else lab, s)
    return s


def tilde(p):
    """A path as the records of this repository write it: its own files relative to its root, the ORCHID-SAGE checkout
    as <orchid-sage>, the home directory as <home>, host names in directory and file names as their machine labels
    (spark1, mac-studio), i.e. the names of the public orchid-sage copy."""
    s = str(p); h = str(record_home()); r = str(loc("orchid_sage"))
    if s.startswith(str(REPO) + os.sep):                     # a file of this repository: relative to its root
        return s[len(str(REPO)) + 1:]
    if s == r or s.startswith(r + os.sep):
        return public_text("<orchid-sage>" + s[len(r):])
    return public_text(RECORD_HOME + s[len(h):] if s.startswith(h) else s)
