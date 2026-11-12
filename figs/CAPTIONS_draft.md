# Caption drafts: Cr–Ni PhaseForge one-shot figures (6 Nov 2026, for PI review; not committed)

Protocol: the 5 Nov campaign with the PI decisions of 6 Nov: full composition range, disordered FCC_A1 (L1₂, L1₀ and D0₂₂ computed
but not used; Pt₂Mo-type CrNi₂ kept as a stoichiometric compound), alphabetical L(CR,NI;k), and SGTE for every end-member.
All values come from `<campaigns>/crni-phaseforge-20261105/results/` and the local ORCHID release (orchid-literature
2026-10-23). Scripts: `scripts/fig_entropy.py`, `scripts/fig_energetics.py`, `scripts/fig_oneshot.py` (loaders in
`scripts/crni_pf_data.py`). Main potential: GRACE-2L-SMAX-OMAT-large; GRACE-2L-OMAT is a cross-check.

## fig_crni_entropy

**Excess entropy of the Cr–Ni liquid from MLIP molecular dynamics and the corrected Hong–Liu estimator.** Entropies are in J K⁻¹ mol⁻¹ per mole of atoms.

(a) Total excess entropy, S_ex = S_vib,ex + S_chem,ex, against x_Ni at 2200 K (circles) and 1900 K (squares).
- Each alloy is referenced to pure Cr and pure Ni liquids at the same temperature.
- Each state: 108 atoms, 100 ps NVT production at the NPT density for 1 atm.
- Error bars: the standard error of five 20 ps blocks and the spread over four neighbour cut-offs, in quadrature. Potential and method errors are not included; excess electronic entropy assumed zero (metallic liquid; PI, 6 Nov).
- The pure-Cr reference at 1900 K crystallized after 82 ps; it is evaluated over its first 80 ps.

(b) Ideal-mixing check. With species labels permuted at random on the MD neighbour graphs, the pair (quasi-chemical) chemical
term returns the ideal mixing entropy (grey curve). The inset shows S_chem,ex for the permuted labels, at most 0.004 J K⁻¹
(mol of atoms)⁻¹ in magnitude.

(c) Components: vibrational excess (filled; from the velocity autocorrelation function, VACF) and pair-corrected chemical
excess (open), at 2200 K (black) and 1900 K (grey).

(d) Finite-size check at Cr₅₀Ni₅₀ and 2200 K, 108 against 864 atoms with matched settings. Points show the vibrational entropy with block standard errors: 86.96 for 108 atoms and 87.35 for 864 atoms. The grey band is ±5 % of the 864-atom value. The difference is 0.45 %, within the < 5 % acceptance, so 108 atoms is accepted for the campaign. The inset shows the chemical excess term: −0.002 for 108 atoms and −0.0001 for 864 atoms.

| T | x_Ni = 0.25 | 0.50 | 0.75 |
|---|---|---|---|
| 2200 K | −0.14 ± 0.21 | −0.26 ± 0.22 | −0.68 ± 0.24 |
| 1900 K | −0.84 ± 0.22 | −0.98 ± 0.29 | −1.00 ± 0.29 |

Values in J K⁻¹ (mol of atoms)⁻¹. They are provisional: the correction to Hong and Liu's Eqs. 15–16 is ours and awaits human
review.

## fig_crni_energetics

**PhaseForge energetics of Cr–Ni from GRACE MLIPs, with ORCHID DFT records.**

(a) Mixing enthalpies of 128-atom m_scraps SQS on bcc (A2, squares) and fcc (A1, circles), over the whole composition range.
- Two seeds per composition. Black: GRACE-2L-SMAX-OMAT-large; grey: GRACE-2L-OMAT.
- Relative to the pure elements on the same lattice from the same MLIP.
- Points: the volume + ions relaxed value with the cell shape fixed (the protocol value).
- Error bars: the staged interval from fully relaxed to unrelaxed, used as the uncertainty (σ = half-width).
- Orange curves: the Redlich–Kister parameters of the one-shot TDB, a weighted fit to the points.
  - bcc: L0 = +22.5, L1 = +38.2 kJ (mol of atoms)⁻¹
  - fcc: L0 = −40.5, L1 = −8.3 kJ (mol of atoms)⁻¹
- Pink: ORCHID DFT records in the same reference convention, numbered D1–D7 (table below). ORCHID holds no experimental Cr–Ni mixing
  enthalpies.

| label | ORCHID id | phase | x_Ni | ΔH_mix (kJ (mol of atoms)⁻¹) | source DOI |
|---|---|---|---|---|---|
| D1 | ORC-ECXY5ARLCL | bcc (A2) | 0.25 | 10.02 | 10.1016/j.calphad.2015.12.007 |
| D2 | ORC-4AVGOLDRYY.862ddc | bcc (A2) | 0.5 | 9.15 | 10.1016/j.calphad.2015.12.007 |
| D3 | ORC-NNQH4SF765 | bcc (A2) | 0.75 | 4.98 | 10.1016/j.calphad.2015.12.007 |
| D4 | ORC-BJCC23KTCK.7c92d8 | fcc (γ) | 0.25 | -12.69 | 10.1016/j.calphad.2015.12.007 |
| D5 | ORC-XYCE5GPHM6 | fcc (γ) | 0.5 | -9.03 | 10.1016/j.calphad.2015.12.007 |
| D6 | ORC-CG6B7EHP2R.127230 | fcc (γ) | 0.75 | -5.79 | 10.1016/j.calphad.2015.12.007 |
| D7 | ORC-NYY5VGMVQQ.0cb658 | fcc (fcc) | 0.5 | -9.719 | 10.1007/s11669-021-00922-9 |


Several cells leave their parent lattice even with the shape fixed: Cr-rich fcc (x_Ni ≤ 0.31) and Ni-rich bcc (x_Ni ≥ 0.5). Their
intervals are therefore wide. Fcc at x_Ni 0.0625 runs from −31.8 (fully relaxed) to −2.1 kJ (mol of atoms)⁻¹ (unrelaxed).

(b) Liquid mixing enthalpy from 100 ps MLIP MD at 2200 K (circles) and 1900 K (squares), with block standard errors. The orange
curve is the L0 = −19.1 kJ (mol of atoms)⁻¹ of the one-shot TDB, fitted to the 2200 K data.

(c) Pt₂Mo-type CrNi₂ (Immm, 108 atoms) against the disordered fcc SQS and their lower convex hull. Relative to fcc Cr and fcc Ni,
the formation enthalpy is −14.50 ± 0.28 kJ (mol of atoms)⁻¹ (volume + ions value; ± half the staged interval). The compound lies
6.3 kJ (mol of atoms)⁻¹ below the disordered fcc at x_Ni = 2/3. In the TDB it is a stoichiometric compound on SGTE fcc
references: G = GFCCCR + 2 GHSERNI + 3 H_f. L1₂, L1₀ and D0₂₂ were computed but are not used (PI, 6 Nov).

## fig_crni_oneshot

**PhaseForge one-shot Cr–Ni phase diagram, computed with pycalphad.**
- Phases: LIQUID, BCC_A2 and FCC_A1 (Redlich–Kister terms as in fig_crni_energetics), plus the stoichiometric CRNI2.
- SGTE91 unaries for every pure-element end-member.

Black solid lines: the one-shot with the corrected Hong–Liu liquid excess entropy, b0 = −1.53 J K⁻¹ (mol of atoms)⁻¹ from S_ex at
2200 K. Black dashed lines: the same model without the liquid excess entropy. Light grey: CrNi-92Lee-LB (SGTE binary, Lee 1992),
for reference. All boundaries are pycalphad mapping lines (binplot).

Orange markers: ORCHID assessed-diagram assemblages (Nash 1991 / Okamoto 1997, class assessed_phase_diagram). Circles are
single-phase fields; diamonds are two-phase fields at the tie-line composition.

| label | id | phases | x_Ni | T (K) |
|---|---|---|---|---|
| A1 | aspa-2e53a5a5989683f8 | bcc | 0.104 | 1577 |
| A2 | aspa-353b9ffbb8dbf6a9 | bcc + fcc | 0.317 | 819 |
| A3 | aspa-7b92add114110a2f | fcc | 0.790 | 1253 |
| A4 | aspa-1a191ce9edb5af77 | bcc + fcc | 0.334 | 1168 |
| A5 | aspa-0e8055991642b840 | fcc + liquid | 0.682 | 1663 |
| A6 | aspa-4fa6130e0abf4ba7 | bcc + liquid | 0.221 | 1822 |
| A7 | aspa-a3d958dbc5188cab | liquid | 0.580 | 1945 |

Ticks at the right edge: ORCHID printed transition and invariant temperatures (blue = experimental, orange-red = model). Labels are
staggered and joined to their ticks by leader lines. No composition is assumed for them. Records naming Al–Cr–Ni phases are excluded.

| label | id | class | T (K) | phases printed |
|---|---|---|---|---|
| T1 | ORC-42HR6B6LUU.3bf076 | model | 2180 | liquid |
| T2 | ORC-XBIQHO5JWX | experimental | 2180 | liquid |
| T3 | ORC-42HR6B6LUU.0028e2 | model | 2136 | liquid |
| T4 | ORC-UWNYLPUNSF | experimental | 2136 | liquid |
| T5 | ORC-O24YICU5WD | model | 2136 | bcc, liquid |
| T6 | ORC-2M4FWURZF3 | experimental | 1873 | bcc, liquid |
| T7 | ORC-SV7H3CNRYS | experimental | 1618 | liquid, bcc, fcc |
| T8 | ORC-FWWPHXWR5Z | model | 863 | CrNi2 |
| T9 | ORC-FWFLDARLZM.cef5da | model | 820 | CrNi2 |
| T10 | ORC-FWFLDARLZM.fbcce2 | model | 807 | CrNi2 |
| T11 | ORC-XJ6BSXJZ4T | experimental | 633 | fcc |
| T12 | ORC-AJ4EQOMP2O | model | 611 | CrNi2 |

Reading of the diagrams:
- SGTE fcc Cr (7.3 kJ above bcc) sits under an fcc mixing energy referenced to the MLIP's fcc Cr (about 38 kJ above bcc). As a
  result, Cr-rich fcc is over-stabilised: the fcc field reaches x_Ni ≈ 0.26 at 1600 K and melts congruently near 2100 K.
- bcc dissolves almost no Ni.
- The bcc + liquid + fcc eutectic lies at about x_Ni 0.14 and 1900 K without S_ex, and about x_Ni 0.13 and 1930 K with S_ex (read from
  the computed lines; ORCHID T7: 1618 K).
- CrNi₂ is stable up to about 1150 K (ORCHID T8: 863 K, model).
These are the starting point for the liquidus-first fit.

---

# Caption drafts: main Figs. 2, 4, 5 and 6 (6 Nov 2026, from the frozen fit crni-paper-fit-step4c-b@1.0.0; for PI review)

Source of truth: specific protocol `crni-paper-fit-step4c-b@1.0.0` (orchid-sage 5bede65), pick TDB
`<campaigns>/crni-paper-fit-20261106/tdb/step4c_b_hingefloor_pick.tdb` (sha256 36922433…), evidence bundle 1.0.0 (695 states),
dashboard `crni-paper-fit-step4c-b-1.0.0`. Scripts: `scripts/export_crni_paper_fit.py` (writes `data/crni_paper_fit_figs.json` with the
path and sha256 of every file read), `scripts/fig_standard.py`, `scripts/fig_sequence.py`, `scripts/fig_dashboard.py`,
`scripts/fig_physics_uq.py` (shared helpers in `scripts/crni_fig_common.py`). Environment: the fit environment (ESPEI gradient PR 9039ea2 + pycalphad) (pycalphad
0.11.3.dev35+g9a6939dd2), the fit environment of the protocol. Badge "ORCHID provisional": the records are not yet in a release.

## Fig. 2 — fig_crni_standard (schematic)

**The ORCHID-SAGE standard, shown for the Cr–Ni assessment.** The general protocol `orchid-calphad-fit@2.0.0` has 7 sections and
44 steps (23 deterministic, 12 numerical, 9 judgement; one glyph per step). The specific protocol `crni-paper-fit-step4c-b@1.0.0`
instantiates it for one TDB: 28 input files with their sha256, 16 runs in sequence (13 with run cards), 16 overrides of the general
defaults, and 17 decisions (10 by the PI, 7 by the agent, each with who, why and source). Each run card records host, interpreter,
package lock, seeds, threads, data-file hashes and the trajectory. The package holds the TDB with its header, the dashboard and the
RO-Crate (Workflow Run Crate and Process Run Crate profiles). Grey arrows are the provenance links written in the crate: each run
`prov:hadPlan` a general-protocol step (16 runs), has the specific protocol as `instrument`, uses its inputs (`object`, among them the
evidence bundle of 695 ORCHID states) and `prov:wasDerivedFrom` the run before it; the TDB `prov:wasGeneratedBy` the run. Bottom: an
agent reads the protocol through the ORCHID-SAGE MCP and executes it step by step (`get_step`, `run_step`, `compare_outputs`), writing
run cards; at judgement steps a person decides and `record_decision` returns the decision to the decisions log. An MCP-driven rerun of
this fit has been briefed but not yet run. Counts are read from the protocol, crate and bundle files (`figs/fig_crni_standard_sources.json`).

## Fig. 4 — fig_crni_sequence

**The Cr–Ni fit sequence from the PhaseForge one-shot to the pick.** Computed diagrams (lower convex hull of the pycalphad Gibbs
energies of each TDB, 600–2200 K in 2 K steps, 1201 compositions). (a) One-shot (step 1, orange): the lowest liquid is at 1730 K and
CrNi₂ is stable to 1156 K; Cr-rich fcc is too stable. (b) Step 2, liquid ZPF data, the ORCHID eutectic, the liquid excess entropy and
the one-shot anchors: lowest liquid 1616 K, CrNi₂ (not yet free) stable to 1664 K. (c) Step 3b, + activities, mixing and formation
enthalpies (not drawn) with CrNi₂ free: lowest liquid 1626 K, CrNi₂ to 1074 K. (d) Step 4c-b, the pick: + solid ZPF data and excluded
phases at every observed state. The eutectic is at 1614 K (ORCHID 1618 K, ORC-SV7H3CNRYS) and the CrNi₂ top at 860 K (ORCHID 863 K,
ORC-X3KVP7D3PO, single reader). Purple: ORCHID-SAGE fits; dashed grey: the previous step. Markers: the 695 states of the evidence bundle
crni-paper-fit-step4c-b@1.0.0, all experimental, in blue where the step's objective contains them and in grey where it does not yet;
open circles are single-phase states, filled circles phase-boundary states, crosses states of non-ZPF (mostly thermochemical) records
that enter only through their excluded phases, the triangle the eutectic record and the square the CrNi₂ ordering record. States with
excluded phases at the same (x, T) as a ZPF record are drawn once. The strict topology check of the pick fails at one grid temperature
only (a BCC_A2 + LIQUID sliver at 2176 K). 78 of the 695 states carry an ORC id; the others are pending intake. ORC ids of the plotted
records: ESI Table {n} (`figs/fig_crni_sequence_orchid_ids.json`).

## Fig. 5 — fig_crni_dashboard

**Fit trajectory and model space, from the assessment dashboard of crni-paper-fit-step4c-b@1.0.0.** (a) −log posterior at the end of
every start of steps 2, 3 (failed: CrNi₂ fixed, stable above the liquidus), 3b and 4c-b; filled purple: the start picked at each step.
Data are added at each step, so the values of different steps are not comparable. (b) Step 4c-b, every evaluation of the 8 starts;
the pick s4 ends at log posterior −5657.29. Topology is classified every 10 evaluations (dots accepted, crosses wrong). (c) The 14
parameters along the lineage one-shot → step 2 s7 → step 3b s1 → step 4c-b s4, as (θ − θ_one-shot) divided by the prior sd (50 kJ mol⁻¹
for a terms, 30 J mol⁻¹ K⁻¹ for b terms); solid a terms, dashed b terms; steps 2 and 3b record start and end only. (d) The dashboard's
fixed PCA basis of 1906 parameter vectors (PC 1 66 %, PC 2 15 % of the variance): the lineage path with its topology class, the other
starts, the 1000 Laplace-mixture draws (purple) and the two mode centres (weights 0.766 and 0.234). Seven failed step-3 ends lie at PC 1
≈ −2.4, outside the plotted range. The objective is computed over the evidence bundle of Fig. 4; this figure plots no ORCHID records.

## Fig. 6 — fig_crni_physics_uq

**Physics and uncertainty of the pick.** (a) Stable diagram (purple) with the metastable BCC_A2 miscibility gap computed from the pick:
binodal (lower hull of the bcc Gibbs energy alone), chemical spinodal (top 1385 K at x_Ni 0.22) and Cahn coherent spinodal with the
coherency strain energy k of the base case (top 1338 K; grey band: low and high cases, 1352 and 1275 K). The gap lies inside the stable
bcc + fcc and bcc + CrNi₂ fields. Star: the design point x_Ni 0.52, 1473 K, single-phase fcc in the pick. (b) Estimates of the
incoherent T_c of the bcc gap from Ω = 4 H_mix(0.5): regular solution (MF), with the short-range-order factor 0.79 (SRO), and with the
excess vibrational entropy 2.69 ± 0.98 J mol⁻¹ K⁻¹ (SRO + vib; thick bar from the entropy uncertainty, thin bar from σ_Ω = 4 × 9.7 kJ),
from the MLIP one-shot, the Liu 2016 DFT and the fit (fit: 1188, 939, 570 K). Vertical lines: the chemical and coherent spinodal tops
of the fit. (c) Laplace-mixture weights of the two modes of one basin, A_s4 0.766 and A2_s5_flat 0.234 (778 and 222 of 1000 draws;
99.2 % and 97.7 % with the accepted topology). (d) Probabilities from the 1000 mixture draws (purple) and from independent marginals
(grey, columns permuted): accepted topology 0.989 vs 0.044; eutectic in 1560–1680 K 1.000 vs 0.661; CrNi₂ top in 800–930 K 0.992 vs
0.130; single-phase fcc at the design point 1.000 vs 0.469. Bars: binomial standard errors. (e) Eutectic and CrNi₂-top temperatures
of the draws (5 K grid, jittered by ±1.2 K for display); 5/50/95 % 1610/1615/1620 K and 830/860/885 K; P(|T_CrNi₂ − 863 K| ≤ 25 K) =
0.871. Blue lines: the ORCHID records (eutectic 1618 K; CrNi₂ 863 K with the ±25 K band); diamond: the pick. One draw without CrNi₂
is not shown. ORC ids of the plotted records: ESI Table {n} (`figs/fig_crni_physics_uq_orchid_ids.json`).

Notes for the PI (not caption text):
- REPORT.md's "Physics checks" and first "UQ" sections describe the superseded step-4 s1 pick (bcc chemical spinodal 1329 K, coherent
  1278/1293/1210 K, fit T_c 603/993 K, weights 0.901/0.099, P(fcc) 0.941). The figures use the step-4c-b pick:
  `results/physics_step4c_b.json` and `results/uq/laplace_step4c_b.json`.
- The eutectic of the pick is 1614 K on the 2 K grid of the diagram and 1615 K on the 5 K grid of the UQ classification.

---

# 7 Nov 2026: Methods 2.1-2.2 figures (drafts for the PI; numbers from figs/*_sources.json)

## fig_crni_standard (regenerated for orchid-calphad-fit@2.1.0 and crni-paper-fit-step4c-b@1.0.1)

**The ORCHID-SAGE standard applied to Cr–Ni.** The general protocol orchid-calphad-fit@2.1.0 (7 sections, 45 steps: 23 deterministic, 13 numerical, 9 judgement) is instantiated by the specific protocol crni-paper-fit-step4c-b@1.0.1 (28 hashed input files, 16 runs of which 13 have run cards, 17 overrides of which 15 conform, 25 decisions: 12 PI, 13 agent), which uses an evidence bundle of 695 ORCHID states. Run cards record each execution; the package holds the TDB with its header, the dashboard and the Workflow Run RO-Crate. PROV terms as recorded in the crate. Schematic; no badge.

## fig_orchid_evidence (panels 2 and 4 new)

**Evidence used in this work.** (1) Sources found and read by AI agents. (2) A state record and its identifiers: the record id of the Cr–Ni eutectic (ORC-SV7H3CNRYS) is computed from the locator of the value in its source, the state id (S-5e711ae309) from the canonical description of the state; data not yet released carry a provisional local:<ORCID>/<dataset-uuid> id, linked to the released id by an alias record. (3) The uncertainty of each record sets its weight. (4) Excluded phases: the hinge scale of each of the 878 exclusions of the fit against its certainty tier (10, 50 or 100 J/mol-atom); σ = max(tier, the state's T and x uncertainty converted to energy), which raises 868 of the 878 scales above their tier. (5) The 165 Cr–Ni phase-boundary points, by phase. (6) The consistency check on the 65 activities of Cr measured by Pugliese and Fitterer; the circled value is flagged, not changed. ORC ids: ESI (figs/fig_orchid_evidence_orchid_ids.json).

## fig_verification (new)

**Verifying a protocol and a rerun.** (a) The validator checks that every document conforms to the schema, that every referenced file exists with its recorded SHA-256 (102 references in crni-paper-fit-step4c-b@1.0.1) and that no step uses an input before it is produced (119 supply links in 45 steps). (b) The independent rerun of crni-paper-fit-step4c-b@1.0.1 on a second machine (a DGX Spark, aarch64), compared by step kind: deterministic outputs are byte-identical (408 staged files; the 695 evaluated states; the phase sequence on heating at 99 compositions); numerical results are shown as |rerun − recorded| / tolerance, all far below 1; judgement steps are reproduced by their rule and the person who set it. Parameters are compared only as a note (grey). (c) The fitted parameters have a flat direction: the two recorded minima of the basin, A and A2, are 5.9 tolerances apart in the bcc and fcc L¹ terms (±50 J/mol boxes) and differ by 0.0045 in log posterior; the converged starts of both machines fall into one or the other (Studio 7:1, DGX Spark 5:3). (d) Their predictions do not differ: the eutectic (1614 K) and the CrNi₂ top (860 K) are the same at every start, within the ±2 K tolerance (grey), shown against the ORCHID records (1618 K, ORC-SV7H3CNRYS; 863 K, ORC-X3KVP7D3PO, single reader). ORC ids: ESI (figs/fig_verification_orchid_ids.json).

## fig_gates_ranking (new; schematic)

**Gates and ranking.** (a) The nine gates of orchid-calphad-fit@2.1.0 and the steps that check them; they concern the integrity of the process and the record, and an assessment that fails one is incomplete. (b) Candidate fits are not passed or failed on a figure of merit; they are ranked by plausible energies (R1, 10 kJ/mol-atom of the one-shot/MLIP values), then topology (R2), then quantitative agreement (R3, invariants within 25 K, then thermochemical RMSE by dataset), and the most reasonable fit is picked. Schematic: no R1–R3 ranking across candidate fits is recorded for Cr–Ni.

Notes for the PI (not caption text):
- The evidence bundle's own tier counts (states@1.0.0.json: 526 / 343 / 9) differ from the tiers in the hinge input the fit read (673 / 186 / 19, data/hinge/step4c_hinge_floor.json); tile 4 uses the fit's input. Same 878 pairs.
- validate.py (7 Nov) reports 0 errors for 2.1.0 and 1.0.1, and 1 error elsewhere: orchid-calphad-fit@2.0.0 pins a fit_protocol.md hash that has since changed (2.1.0 re-pins it).
- The RO-Crate exists for 1.0.0 only; 1.0.1 has no crate yet.

---

## 2026-11-07: one-column figures, minimal text (PI: "Too much text")

Details removed from the one-column figures, to be carried by the captions. These are draft notes of content, not final
caption prose (the final wording still goes through the voice check).

### fig_crni_standard_1col (89 x 80 mm)
- General protocol orchid-calphad-fit@2.1.0: 7 sections (preflight, evidence, one-shot, fit sequence, checks/pick, UQ,
  package), 45 steps; one glyph per step, grouped by section: square deterministic (23), circle numerical (13), diamond
  judgement (9).
- Specific protocol crni-paper-fit-step4c-b@1.0.1: 28 input files (sha256 each), 16 runs in sequence (13 with run cards),
  17 overrides of the general defaults (15 conform), 25 decisions (12 PI, 13 agent; each with who, why and source).
- Evidence bundle: 695 ORCHID states (states@1.0.0).
- Run cards record host, interpreter, packages and lock sha256, seeds and threads, data-file sha256, trajectory and pick.
- Package: TDB with header (sha256 36922433...), dashboard (trajectory, checks, UQ), Workflow Run RO-Crate (the crate exists
  for 1.0.0 only).
- Arrows (PROV, as recorded in the crate): specific -> general = instantiates; run cards -> specific = instrument; run cards
  -> general steps (right margin) = prov:hadPlan, 16 runs; run cards -> evidence = object (used); TDB -> run cards =
  prov:wasGeneratedBy; loop on the cards = prov:wasDerivedFrom (run -> run).
- People decide at the 9 judgement steps; decisions return to the record through record_decision. An agent runs the
  specific protocol through the ORCHID-SAGE MCP (get_step -> run_step -> compare_outputs); run_step writes the run cards.

### fig_gates_ranking_1col (89 x 86 mm)
- (a) The nine gates of orchid-calphad-fit@2.1.0 concern the integrity of the process and the record; any gate failed and
  the assessment is incomplete, however well it fits. Steps that check each gate: G1 verify_build; G2 oneshot_diagram,
  pick_liquidus, physics_checks; G3 data_consistency; G4 exclusions_every_state; G5 record_trajectory; G6 and G7
  specific_protocol; G8 dashboard; G9 independent_rerun. Boxes are drawn empty: no gate pass/fail status is recorded for
  Cr-Ni.
- (b) Candidate fits (all starts of a step, after polishing) are ranked, not gated: R1 plausible energies (compounds within
  ~10 kJ/mol-atom of the one-shot/MLIP values), R2 topology (right reaction types, right fields, no spurious phases), R3
  quantitative (invariant temperatures within 25 K of the observed values, then thermochemical RMSE by dataset). The most
  reasonable fit is picked; misses are reported as notes, not rejections. Applied at pick_liquidus, pick_thermo, pick_solid,
  final_pick. PI decision 2026-10-31: "rank fits and pick the most reasonable one; no pass/fail gates on fits".
- Schematic: no R1 -> R2 -> R3 ranking of candidate fits is recorded for Cr-Ni.

### fig_verification_1col_1 (89 x 88 mm)
- (a) validate.py (orchid-sage protocols/tools, run read-only 7 Nov 2026) on orchid-calphad-fit@2.1.0 and
  crni-paper-fit-step4c-b@1.0.1: 0 errors. Schema: every document conforms to orchid-assessment-schema (1.0.0-draft.2).
  File hashes: 102 file references in the specific protocol, each file exists and its sha256 matches. Step order: 119
  supply links over 45 steps, no input used before it is produced.
- (b) Two independent reruns of crni-paper-fit-step4c-b@1.0.1: scripted rerun on a DGX Spark (aarch64, 7 Nov 2026) and an
  AI agent using only the orchid-sage MCP tools on the Studio (arm64, 7 Nov 2026). 13 of 13 checks pass in each.
  Deterministic (5 checks: evaluated states, phase sequence, pure elements x3) byte-identical; states evaluated (695)
  sha256 b610e5ec... in both, equal to the recorded file; phase sequence on heating 0 of 99 compositions differ in both;
  inputs staged by sha256 (408 files on a DGX Spark, 409 in the MCP run). Numerical (8 checks): |rerun - recorded| / declared
  tolerance on a log axis, 0 drawn left of the break; rows = objective of the 10a pick, best of basin-hopping and of dual
  annealing (10c), eutectic and CrNi2-top temperatures (+-2 K), thermochemistry (22 datasets, |delta rms_z| <= 0.1),
  Laplace weight of mode A. Grey band = notes, not verdict: parameters of the rerun pick vs the recorded mode A (DGX Spark
  0.039, MCP 1.5e-5 x tolerance) and the recorded mode A2 vs A (5.9 x tolerance). Judgement: the pick rule (eligible
  starts first, then the objective, never a start label; fit_protocol 10a, PI 2026-11-06); picks Studio s4, DGX Spark s1,
  MCP s4, all in mode A; verdict by predictions only (PI 2026-11-06).

### fig_verification_1col_2 (89 x 88 mm)
- (a) The two recorded minima of the basin, A (A_s4, Laplace weight 0.77) and A2 (A2_s5_flat), 5.9 x tolerance apart with
  delta log posterior 0.0045, in the plane of the two parameters that differ most (L1 bcc a, L1 fcc a); dashed boxes =
  10b tolerance +-50 J/mol. Converged starts: Studio 7 in A, 1 in A2; DGX Spark 5 in A, 3 in A2.
- (b) Eutectic and CrNi2-top temperature at every start (filled = mode A, open = A2); grey band = +-2 K around the recorded
  pick (1614 K, 860 K); dashed blue = ORCHID records ORC-SV7H3CNRYS (1618 K) and ORC-X3KVP7D3PO (863 K, single reader, not
  yet released). Badge: ORCHID provisional.

## 2026-11-07 caption notes: fig_crni_entropy_1col (89 x 90 mm)
Moved out of the figure (minimal text inside; numbers from figs/fig_crni_entropy_sources.json):
- Units: all entropies in J K^-1 (mol of atoms)^-1. Liquid at x_Ni = 0.25, 0.5, 0.75; pure-liquid references at the same T.
- Markers (all panels): circles 2200 K, squares 1900 K; small x offsets separate the two temperatures.
- (a) S_ex = S_vib,ex + S_chem,ex; 2200 K black, 1900 K dark grey; dotted lines join the points to 0 at the pure
  elements (guide only). Error bars = block SE and cut-off spread in quadrature (potential and method error not
  included). Filled = all three trajectories liquid (all are); open would mark a non-liquid state.
- (b) Ideal-limit check: species labels permuted at random on the MD neighbour graphs; pair (quasi-chemical) estimator
  (open markers) vs the ideal mixing entropy -R sum x ln x (grey curve). Inset: S_chem,ex of the permuted labels in
  units of 10^-3 J K^-1 mol^-1 (about -0.002 to -0.003; block SE bars); criterion |S_chem,ex| < 0.05, passed.
- (c) Vibrational (VACF; filled) and pair-corrected chemical (open) excess terms; 2200 K black circles, 1900 K light-grey
  squares. Chemical term within 0.024 of zero at every state; the excess entropy is vibrational.
- (d) Finite-size check, Cr50Ni50 at 2200 K: total vibrational entropy S_vib for 108 and 864 atoms (86.96 and 87.35,
  block SE bars); grey band = +-5 % of the 864-atom value; difference 0.45 % (acceptance < 5 %). S_chem,ex -0.0022 (108)
  and -0.0001 (864) (inset of the two-column version, dropped here). No 864-atom pure references, so S_vib,ex is not
  formed at 864 atoms.
- Computed figure (MLIP MD), no ORCHID records, no badge. Status: correction ours, pending human review.

## 2026-11-07 caption notes: Results figures in the hero style (cards; text moved out of the figures)
Every panel now sits in a rounded card with the letter and a short orchid heading; legends sit below the axes. The text
below was removed from the figures and belongs in the captions. No plotted number changed.

### fig_crni_sequence (183 x 150 mm) and fig_crni_sequence_1col (89 x 97 mm)
- Objective of each step (formerly sub-lines): (a) one-shot, PhaseForge MLIP + SGTE, no fit; (b) step 2: liquid ZPF, eutectic,
  liquid S_ex, one-shot anchors; (c) step 3b: + activities, H_mix, H_form (not drawn), CrNi2 free; (d) step 4c-b (the pick):
  + solid ZPF, excluded phases at every state.
- Lowest liquid / CrNi2 stable to: one-shot 1730 / 1156 K; step 2 1616 / 1664 K; step 3b 1626 / 1074 K; step 4c-b 1614 / 860 K
  (ORCHID eutectic 1618 K, CrNi2 ordering 863 K). The 1col version omits the one-line notes of a-c and the field labels and
  invariant labels of d (liquid, fcc, bcc, bcc + fcc, bcc + CrNi2; 1614 K vs 1618 K; 860 K vs 863 K).
- Key: blue = experimental states in the step's objective (open circle single-phase, dot phase boundary, + state of a
  non-ZPF record that carries exclusions only); light grey = states not yet in the objective; triangle / square = ORCHID
  eutectic and CrNi2-ordering records; orange = one-shot TDB (model); orchid = this step's fit; dashed grey = previous step.
- Badge: ORCHID provisional. ORC ids: figs/fig_crni_sequence_orchid_ids.json.

### fig_crni_physics_uq (183 x 124 mm)
- (a) Design point x_Ni 0.52, 1473 K (fcc at the pick); chemical-spinodal top 1385 K. Legend: stable diagram of the pick,
  metastable bcc binodal, chemical spinodal, Cahn coherent spinodal (k base) and its low-high strain band.
- (b) Incoherent T_c estimates of the bcc gap per source (MLIP one-shot, DFT Liu 2016, this fit) and estimator (circle MF,
  square SRO, diamond SRO + vib; thick bar = SRO + vib range, thin = sigma_Omega range); vertical lines = chemical and
  coherent spinodal tops of the fit. MLIP estimates now drawn in neutral ink (the Materials Project green is reserved for MP DFT).
- (c) Laplace-mixture weights 0.766 (A = A_s4) and 0.234 (A2 = A2_s5_flat): 778 and 222 draws, 99.2 % and 97.7 % with the
  accepted topology; two modes of one basin, log posterior -5657.289 / -5657.293.
- (d) Probabilities from the 1000 mixture draws (orchid) and from independent marginals (grey, columns permuted).
- (e) Draw quantiles (5/50/95 %): T_eut 1610/1615/1620 K, T_CrNi2 830/860/885 K; P(|T_CrNi2 - 863| <= 25 K) = 0.871; 1 draw
  without CrNi2 not shown; draws sit on a 5 K grid (jitter for display only); blue band = 863 +- 25 K.
- Badge: ORCHID provisional (ORCHID records in e only; ids in figs/fig_crni_physics_uq_orchid_ids.json).

### fig_crni_dashboard (183 x 118 mm)
- No ORCHID records are plotted (objective, parameters and draws only), so the badge was removed (orchid-brand figures.md:
  badge only where ORCHID records are plotted). PI to confirm, since dashboards always keep the ORCHID style.
- (a) -log posterior at the end of every start per step; data are added at each step, so steps differ in scale; step 3 failed.
- (b) Every evaluation of the 8 step-4c-b starts; pick s4 ends at log posterior -5657.3.
- (c) Delta theta = (theta - theta_one-shot) / prior sd along the lineage one-shot -> step 2 s7 -> step 3b s1 -> step 4c-b s4
  (steps 2 and 3b: start and end only).
- (d) Fixed PCA basis of the dashboard (PC 1 66 %, PC 2 15 % of variance); mode centres A 0.766 / A2 0.234; 7 failed step-3
  ends lie off scale at PC 1 about -2.4.

### fig_crni_energetics (183 x 80 mm) and fig_crni_energetics_1col (89 x 96 mm)
- Legend labels shortened: "bcc / fcc SQS" = GRACE-2L-SMAX-OMAT-large; "second MLIP" = GRACE-2L-OMAT (grey); "one-shot TDB"
  curves: bcc L0 +22.5, L1 +38.2; fcc L0 -40.5, L1 -8.3; liquid L0 -19.1 kJ (mol of atoms)^-1 (2200 K data). Units on the
  axes: kJ mol^-1 = kJ (mol of atoms)^-1. D1-D7 labels now 5 pt (were 4.5 pt); D5 sits left of its point.
- Badge added: ORCHID v2026.10 (the D1-D7 DFT records; ids in figs/fig_crni_energetics_orchid_ids.json, unchanged).

### fig_crni_oneshot (89 x 90 mm) and fig_crni_oneshot_2col (183 x 96 mm, new)
- 1col: one card, one-shot + liquid S_ex (solid) and without (dashed). 2col: (a) one-shot without S_ex, (b) with S_ex, a
  dashed for comparison. A1-A7 and T1-T12 labels now 5 pt (were 4.5 / 4.2 pt); ids in figs/fig_crni_oneshot_overlay_ids.json
  (unchanged). Badge added: ORCHID v2026.10. T axis now 600-2400 K (legend moved below).
- Lines are cached in data/crni_oneshot_lines.json (pycalphad 0.11.2, TDB sha256 checked at plot time). pycalphad
  0.11.3.dev in the fit environment maps the fcc + liquid boundaries only to x_Ni about 0.86 (1900 K), not to pure Ni.

## 2026-11-07 caption notes: fig_pair_entropy (Appendix A, pair entropy of chemical mixing in the liquid)
183 x 72 mm (fig_pair_entropy) and 89 x 92 mm (fig_pair_entropy_1col). Methods figure, computed benchmarks only: no ORCHID
records, no badge, neutral inks. Numbers from figs/fig_pair_entropy_sources.json (inputs with sha256). Units J K^-1 mol^-1
(per mole of atoms).
- (a) Cartoon of a liquid neighbour graph, two species (white / dark grey), one bond i-j highlighted (layout is schematic,
  not data). x_i site fraction, y_ij bond fraction, w_i bond-end fraction, zbar mean number of neighbours; the pair
  (quasi-chemical, Bethe) estimator S_chem/R = -sum_i x_i ln x_i - (zbar/2) sum_ij y_ij ln[y_ij/(w_i w_j)].
- (b) Random labels, z = 12 lattice, thermodynamic limit (benchmark_random.json, case thermodynamic_limit, lattice z=12):
  grey line ideal -R sum x ln x (closed with 0 at the end points), open circles pair estimator (every other composition
  drawn); max |pair - ideal| over the plotted rows 1.1e-14, over all lattices and the
  Cu50Zr50 liquid graph 1.2e-14 (finite samples
  0.0035). Line styles: original Hong-Liu chemical-mixing term (Eqs. 15-16) in its
  four readings: species-blind (dotted), same-species (dashed), cross-species (dash-dot), heavy-first (thin solid). At
  x_B = 0.5: ideal 5.76; species-blind 0.00, same-species 8.18,
  cross-species 16.36, heavy-first 12.27. 1col: direct labels blind / same / cross / heavy.
- (c) Bethe lattice z = 12, x_B = 0.5 (benchmark_ordered.json, case bethe_lattice_quasichemical_analytic): excess chemical
  entropy vs Warren-Cowley alpha (ordering alpha < 0, clustering alpha > 0); grey line exact, circles pair estimator
  (max |pair - exact| over all Bethe rows, z = 4, 8, 12: 0.0e+00); original term
  drawn as its change from the random-label value, same line styles as b. At alpha = +0.6: exact
  -9.62; original term species-blind 0.00, same-species -1.03,
  cross-species -2.06, heavy-first -1.54.
- Data caveats: (i) the benchmark has alpha = -0.6, -0.3, -0.1, +0.1, +0.3, +0.6 only (no alpha = 0 row), so c draws straight segments between those
  rows, the two branches separately; at x_B = 0.5 the values are symmetric in alpha. (ii) The species-blind reading is
  identically zero on a regular lattice (every site has z neighbours); on the MD liquid graphs it is not (Cr-Ni permuted
  labels, liquid_ideal_mixing_check.json: 6.27-6.70), so b shows only the lattice behaviour of that reading.
  (iii) The Bethe "exact" values are the analytic quasi-chemical tree entropy, on which the pair estimator is exact by
  construction; the non-tree checks (1D chain, 2D Ising/Onsager, finite samples) are in benchmark_ordered.json and are not
  drawn. Status: correction ours, derivation pending human review (PI, 5 Nov).
- Recolour 2026-11-07 (PI: "more color within the orchid palette"), ORCHID brand tokens only: pair estimator = filled
  brand-orchid circles; ideal (b) and exact Bethe (c) = brand-ink line; original-term readings keep their line styles,
  coloured species-blind ink 50 % (dotted), same-species orchid 75 % = sepal tint (dashed), cross-species muted grey
  (dash-dot), heavy-first ink 75 % (thin solid); (a) species in brand-orchid and brand-petal, highlighted bond orchid,
  formula in an ORCHID box (fill-orchid, 0.75 pt orchid frame). brand-sage not used (token usage: logo contours only,
  2.15:1 on white); light orchid #C79AE6 not used for lines (2.28:1). All line/marker colours >= 3.3:1 on white.
