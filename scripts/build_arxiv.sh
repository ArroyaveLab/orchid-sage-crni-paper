#!/usr/bin/env bash
# Build the arXiv package of the paper (prepared, NOT submitted).
#
#   scripts/build_arxiv.sh            # from the repository root
#
# Output:
#   arxiv/                 flattened main.tex (no comments), class, figures, main.bbl
#   arxiv.tar.gz           the same files, ready for upload to arXiv
#   arxiv-build/           scratch builds (bibtex run, standalone test), logs
#   arxiv-build/REPORT.txt page count, undefined references and citations
#
# Steps:
#   1. scripts/arxiv_flatten.py writes arxiv/ and checks it for local paths,
#      hostnames, '%%' and internal notes (fails the build if any is found).
#   2. With main.bib next to it (outside the package), the package is compiled
#      with pdflatex + bibtex (the class loads natbib with unsrtnat, so BibTeX,
#      not biber) to produce main.bbl, which is copied into arxiv/.
#   3. The package alone (no .bib, no .aux) is compiled with pdflatex three
#      times, as arXiv does, and the warnings are counted.
#
# Without pdflatex on the PATH (e.g. this Mac) only step 1 runs.
# The script never deletes anything: existing outputs are moved aside with a
# timestamp suffix.

set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=$(pwd)
NAME=main
STAMP=$(date +%Y%m%d-%H%M%S)

for d in arxiv arxiv-build arxiv.tar.gz; do
  if [[ -e "$d" ]]; then
    mkdir -p .arxiv-old
    mv "$d" ".arxiv-old/$d.$STAMP"
  fi
done

python3 scripts/arxiv_flatten.py --root "$ROOT" --out arxiv --name "$NAME"

if ! command -v pdflatex >/dev/null 2>&1; then
  echo "build_arxiv: pdflatex not found; package sources written to arxiv/ without main.bbl."
  echo "build_arxiv: compile in CI (.github/workflows/arxiv.yml)."
  exit 0
fi

PDFLATEX=(pdflatex -interaction=nonstopmode -file-line-error)

# Step 2: bibliography
mkdir -p arxiv-build/bib
cp -R arxiv/. arxiv-build/bib/
cp main.bib arxiv-build/bib/
(
  cd arxiv-build/bib
  "${PDFLATEX[@]}" "$NAME.tex" >/dev/null || true
  bibtex "$NAME" | tee bibtex.out || true
  "${PDFLATEX[@]}" "$NAME.tex" >/dev/null || true
)
if [[ ! -s "arxiv-build/bib/$NAME.bbl" ]]; then
  echo "build_arxiv: bibtex produced no $NAME.bbl" >&2
  exit 1
fi
cp "arxiv-build/bib/$NAME.bbl" arxiv/

# Re-check, now that the .bbl is in the package
python3 scripts/arxiv_flatten.py --out arxiv --check-only

# Step 3: standalone compile of the package, as arXiv does
mkdir -p arxiv-build/standalone
cp -R arxiv/. arxiv-build/standalone/
(
  cd arxiv-build/standalone
  for i in 1 2 3; do
    "${PDFLATEX[@]}" "$NAME.tex" > "pass$i.out" || true
  done
)
LOG="arxiv-build/standalone/$NAME.log"
PDF="arxiv-build/standalone/$NAME.pdf"
if [[ ! -s "$PDF" ]]; then
  echo "build_arxiv: the standalone package did not produce a PDF; see $LOG" >&2
  tail -40 "$LOG" >&2 || true
  exit 1
fi

pages=$(grep -a -o 'Output written on .* (\([0-9]*\) page' "$LOG" | grep -o '([0-9]*' | tr -d '(' | tail -1)
undef_refs=$(grep -a -c "LaTeX Warning: Reference .* undefined" "$LOG" || true)
undef_cites=$(grep -a -c "Citation .* undefined" "$LOG" || true)
errors=$(grep -a -c '^!\|:[0-9]*: ' "$LOG" || true)
{
  echo "arXiv package standalone build ($(date -u +%Y-%m-%dT%H:%MZ))"
  echo "pdflatex: $(pdflatex --version | head -1)"
  echo "pages: ${pages:-unknown}"
  echo "LaTeX errors (file-line-error lines): $errors"
  echo "undefined reference warnings (last pass): $undef_refs"
  grep -a -o "Reference \`[^']*'" "$LOG" | sort | uniq -c || true
  echo "undefined citation warnings (last pass): $undef_cites"
  grep -a -o "Citation \`[^']*'" "$LOG" | sort | uniq -c || true
  echo "other LaTeX warnings:"
  grep -a "LaTeX Warning\|Package .* Warning" "$LOG" | grep -v "undefined" | sort | uniq -c || true
  echo "overfull boxes: $(grep -a -c 'Overfull' "$LOG" || true)"
  echo "package files:"
  (cd arxiv && find . -type f | sort)
} > arxiv-build/REPORT.txt
cat arxiv-build/REPORT.txt

cp "$PDF" arxiv-build/main_arxiv.pdf
tar -czf arxiv.tar.gz -C arxiv .
echo "build_arxiv: wrote arxiv.tar.gz and arxiv-build/main_arxiv.pdf"
