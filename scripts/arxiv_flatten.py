#!/usr/bin/env python3
"""Build the source tree of the arXiv package from main.tex.

The package is a single flattened .tex file, the class file, the figures that
are actually included, and (added later by build_arxiv.sh) the compiled .bbl.

What this script does:
  * inlines every \\input / \\include of main.tex, recursively;
  * strips ALL comments, from every .tex and .cls file in the package: a line
    that is only a comment is dropped, and an inline comment is cut back to a
    bare '%', which keeps TeX's end-of-line behaviour unchanged;
  * drops optional cross-document \\externaldocument directives and \\usepackage{lipsum}
    when nothing uses \\lipsum;
  * copies only the figures named in \\includegraphics (PDF preferred);
  * checks the package for internal notes and local information.

Usage: python3 scripts/arxiv_flatten.py [--root .] [--out arxiv] [--name main]
       python3 scripts/arxiv_flatten.py --check-only --out arxiv

Exit status 1 when a forbidden pattern is found in the package.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

INPUT_RE = re.compile(r"\\(input|include)\s*\{([^}]+)\}")
GRAPHICS_RE = re.compile(r"\\includegraphics\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}")
GRAPHICSPATH_RE = re.compile(r"\\graphicspath\s*\{((?:\{[^}]*\})+)\}")
FIG_EXTS = (".pdf", ".png", ".jpg", ".jpeg", ".eps")

# Strings that must never appear in a public package. Text files are checked
# case-sensitively for these; PDFs are checked as raw bytes for the first group.
# Generic forms here; this machine's host and user names come from local/config.json
# (scripts/paths.py; absent in CI, where scripts/check_public.py covers the repository).
FORBIDDEN_ANYWHERE = ["/Users/", "/home/", "/private/tmp", "/tmp/claude-"]
FORBIDDEN_TEXT_RE = [re.compile(r"(?<![A-Za-z0-9+/=])(?:spark-|dgx-)?b\d{3}(?![A-Za-z0-9+/=])"),   # DGX node names
                     re.compile(r"\bclaude-\d{3,}\b")]
try:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import paths as _paths
    _cfg = _paths.config()
    FORBIDDEN_ANYWHERE += [h for h in (_cfg.get("hosts") or {}).values() if h] + list((_cfg.get("private") or {}).get("usernames", []))
except Exception:  # noqa: BLE001  (the check must run without a local config)
    pass
FORBIDDEN_TEXT_ONLY = ["%%", "TODO", "CITE:", "CHECK:", "PENDING:", "OLD-P", "%%OLD"]


def first_comment(line: str) -> int:
    """Index of the first unescaped % in a line, or -1."""
    i = 0
    while True:
        i = line.find("%", i)
        if i < 0:
            return -1
        backslashes = 0
        j = i - 1
        while j >= 0 and line[j] == "\\":
            backslashes += 1
            j -= 1
        if backslashes % 2 == 0:
            return i
        i += 1


def strip_comments(text: str) -> str:
    out: list[str] = []
    for line in text.splitlines():
        k = first_comment(line)
        if k < 0:
            out.append(line.rstrip())
        elif line[:k].strip() == "":
            continue  # a comment-only line contributes nothing to the output
        else:
            out.append(line[:k] + "%")
    result = "\n".join(out) + "\n"
    return re.sub(r"\n{3,}", "\n\n", result)


def resolve_tex(root: Path, name: str) -> Path:
    p = root / name
    if p.suffix != ".tex":
        p = p.with_name(p.name + ".tex")
    if not p.is_file():
        raise SystemExit(f"arxiv_flatten: cannot find input file {name!r} ({p})")
    return p


def flatten(path: Path, root: Path, depth: int = 0) -> str:
    if depth > 20:
        raise SystemExit("arxiv_flatten: \\input nesting too deep")
    text = strip_comments(path.read_text(encoding="utf-8"))

    def repl(m: re.Match) -> str:
        child = resolve_tex(root, m.group(2).strip())
        body = flatten(child, root, depth + 1).rstrip("\n")
        if m.group(1) == "include":
            return "\\clearpage\n" + body + "\n\\clearpage"
        return body

    return INPUT_RE.sub(repl, text)


def arxiv_driver(text: str) -> str:
    """Remove optional cross-document directives and unused template filler."""
    text = re.sub(r"^\\externaldocument.*\n", "", text, flags=re.M)
    if "\\lipsum" not in text:
        text = re.sub(r"^\\usepackage\{lipsum\}\s*\n", "", text, flags=re.M)
    return re.sub(r"\n{3,}", "\n\n", text)


def graphics_dirs(text: str) -> list[str]:
    m = GRAPHICSPATH_RE.search(text)
    if not m:
        return [""]
    return [d for d in re.findall(r"\{([^}]*)\}", m.group(1))] + [""]


def find_figure(root: Path, dirs: list[str], name: str) -> tuple[Path, str]:
    stem = Path(name)
    candidates = [stem] if stem.suffix.lower() in FIG_EXTS else [stem.with_name(stem.name + e) for e in FIG_EXTS]
    for d in dirs:
        for c in candidates:
            p = root / d / c
            if p.is_file():
                return p, str(Path(d) / c)
    raise SystemExit(f"arxiv_flatten: figure {name!r} not found in {dirs}")


def check_package(out: Path) -> list[str]:
    problems: list[str] = []
    for p in sorted(out.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(out)
        data = p.read_bytes()
        is_text = p.suffix.lower() in {".tex", ".cls", ".sty", ".bbl", ".bst", ".txt", ".md"}
        pats = FORBIDDEN_ANYWHERE + (FORBIDDEN_TEXT_ONLY if is_text else [])
        for pat in pats:
            if pat.encode() in data:
                if is_text:
                    for n, line in enumerate(data.decode("utf-8", "replace").splitlines(), 1):
                        if pat in line:
                            problems.append(f"{rel}:{n}: contains {pat!r}: {line.strip()[:120]}")
                else:
                    problems.append(f"{rel}: binary contains {pat!r}")
        if is_text:
            for n, line in enumerate(data.decode("utf-8", "replace").splitlines(), 1):
                for rx in FORBIDDEN_TEXT_RE:
                    m = rx.search(line)
                    if m:
                        problems.append(f"{rel}:{n}: contains {m.group(0)!r}: {line.strip()[:120]}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="arxiv")
    ap.add_argument("--name", default="main", help="base name of the .tex in the package")
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args()
    root = Path(a.root).resolve()
    out = Path(a.out).resolve()

    if not a.check_only:
        if out.exists():
            raise SystemExit(f"arxiv_flatten: {out} exists; move it aside first (no deletion here)")
        out.mkdir(parents=True)
        tex = arxiv_driver(flatten(root / "main.tex", root))
        dirs = graphics_dirs(tex)
        figures = []
        for name in GRAPHICS_RE.findall(tex):
            src, rel = find_figure(root, dirs, name.strip())
            dst = out / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            figures.append(rel)
        m = re.search(r"\\documentclass(?:\[[^\]]*\])?\{([^}]+)\}", tex)
        cls = root / f"{m.group(1)}.cls" if m else None
        if cls and cls.is_file():
            (out / cls.name).write_text(strip_comments(cls.read_text(encoding="utf-8")), encoding="utf-8")
        (out / f"{a.name}.tex").write_text(tex, encoding="utf-8")
        print(f"arxiv_flatten: wrote {out / (a.name + '.tex')}; class {cls.name if cls else '(TeX Live)'}; "
              f"{len(figures)} figures: {', '.join(figures)}")

    problems = check_package(out)
    if problems:
        print("arxiv_flatten: FORBIDDEN CONTENT in the package:")
        for p in problems:
            print("  " + p)
        return 1
    print("arxiv_flatten: package check passed (no local paths, hostnames, '%%' or internal notes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
