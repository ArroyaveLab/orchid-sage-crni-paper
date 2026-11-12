# ORCHID-SAGE: Fully Reproducible CALPHAD Assessment from Evidence to Phase Diagram

Source of the paper by R. Arróyave, with the scripts and data behind every figure.

- **Paper:** `main.tex` and its sections (`01_introduction.tex` … `07_appendix.tex`), `main.bib`; compiled copy `main.pdf`.
- **Figures:** `figs/` (PDF and PNG), produced by the scripts in `scripts/` from the data in `data/`. Each figure has a `*_sources.json` file listing the ORCHID records and assessment files it was drawn from.
- **Assessment record:** the Cr–Ni assessment itself (specific protocol `crni-paper-fit-step4c-b@1.0.4`, run cards, evidence bundle, TDB and dashboard) is archived as a Workflow Run RO-Crate, [doi:10.5281/zenodo.24045965](https://doi.org/10.5281/zenodo.24045965). The standard and its tools are in [orchid-calphad/orchid-sage](https://github.com/orchid-calphad/orchid-sage) ([doi:10.5281/zenodo.24045967](https://doi.org/10.5281/zenodo.24045967)).

## Building

```sh
latexmk -pdf main.tex
```

`latexmk` reruns pdfLaTeX and BibTeX until the references settle. `scripts/build_arxiv.sh` produces the arXiv package.

## Regenerating the figures

The figure scripts read the assessment files from sibling checkouts (`../orchid-sage`, `../orchid-data`, …) or from the locations given in `local/config.json`; `local.example/config.json` documents every key. `python3 scripts/check_public.py` checks that no machine-specific information is committed.

## Licence

Scripts and the LaTeX class: MIT (`LICENSE`; the class comes from the latex-paper-template by D. Sarıtürk). Paper text and figures: © the author; the licence of the published article applies to its final version. Data files in `data/` are derived from the ORCHID release v2026.10 (CC BY 4.0, [doi:10.5281/zenodo.23736065](https://doi.org/10.5281/zenodo.23736065)) and from the assessment record above; cite the original sources listed in each record.
