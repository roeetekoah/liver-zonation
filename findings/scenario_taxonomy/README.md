# F9 — Scenario taxonomy, every row grounded (the de-zonation mechanism coverage)

**Status: LIVE.** The systematic test: enumerate every way zonation could collapse, map each to a
count-based signature, and test it on **down-thinned to B=1,500** counts (binomial thinning to B=1500, MC-averaged;
cells below B dropped; donor = unit). Each row below states its **signature, script, metric+scale, the
numbers, and the conclusion** — so no "flat" is asserted without grounding.

| # | scenario | count signature | script | metric (scale) | biopsy F0→F4 numbers | conclusion |
|---|---|---|---|---|---|---|
| 1 | **Depletion** | PC-anchor fraction ↓ | `load_bearing.py` | fraction of down-thinned to B=1,500 nuclei that are PC-anchor (donor-median) | 36 / 19 / 23 / 22 / 21 % | flat / non-monotone → **no depletion** |
| 2 | **Dimming** | within-PC detox burden ↓ | (was `mde.py`/§4) | down-thinned to B=1,500 UMIs/nuc in PC cells | 12.7→8.9 (F1→F4) | **DROPPED (D2)** — confounded, not genome-wide robust; not a finding |
| 3 | **Co-expression** | dual (PC⁺PP⁺) fraction ↑ | `review_checks.py` | fraction dual at threshold k (k=2 = ambient-robust) | k=1: .071/.097/.080/.096 → **k≥2: .002/.006/.003/.005** | k=1 was **ambient soup**; real co-expression ~0, no trend → **no de-zonation** |
| 4 | **Gradient compression** | per-cell PC/(PC+PP) distribution → middle | `make_gradient_figure.py` | density of donor-balanced per-cell balance; mid-mass = frac in [0.4,0.6) | mid 0.21/0.22/0.24/**0.28**/0.26 ; poles 0.47/0.41/0.39/0.32/0.38 | **mild, non-monotone** middle-drift peaking at F3, reverts F4; poles stay dominant → **gradient present, not collapsed** (explant = spike at PP-pole, mid 0.18/poles 0.58) |
| 5 | **Turn-off** | null (double-negative) fraction ↑ | `load_bearing.py` | fraction null (donor-median) | 34 / 44 / 36 / 39 / 39 % | flat → **no turn-off** |
| 6 | **Composition shift** | PP:PC anchor ratio | `load_bearing.py` | ratio of fractions (donor-median) | 0.62 / 1.16 / 1.01 / 1.10 / 1.18 | ~flat / non-monotone → **no shift** |
| 7 | **Induction** | program burden ↑ | `panel_by_stage.py` | det2 by stage (ambient-robust) | PP genes flat across biopsy; rise only end-stage (PCK1 .15→.58 cirr→end) | **induction is explant-only** |
| 8 | **Preserved** | all stable | — | — | rows 1,3,4,5,6 above | **= the null (D3)** |

## The gradient figure (row 4) — done right
[`results/figures/h2/gradient_polarization_dist.png`]. Binomial down-thinning to **B=1,500 UMIs/nucleus,
8-draw MC** (definition: `findings/downsampling_method/`); **donor-balanced** (≤300 informative nuclei/donor
— so one donor, e.g. F4 #22 at ~59%, can't dominate a stage's histogram; defuses pseudoreplication; for
visualization only — inference is donor-level); **density-normalized** (y = fraction of cells per bin, bars
sum to 1; NOT raw cell count — the old raw-count y-axis was wrong). x = per-cell PC/(PC+PP) program-count
balance (0 = all periportal, 1 = all pericentral). Biopsy panels keep mass at both poles; only the explant
collapses to a single (PP) pole. The mid-mass numbers in row 4 are MC-stable (≈unchanged 4- vs 8-draw).
Coverage of the gradient scenario (the old open GAP) is now closed.

## Honest notes
- Row 4 shows a **real but mild, non-monotone** middle-ward drift (F1→F3) that partially reverts at F4 — do
  not call row 4 a perfect "flat"; call it "gradient present, not collapsed; mild non-monotone drift."
- Depth-matching B-robust where tested (e.g. co-expression slope across B∈{1000,1500,3000}, `review_checks.py`).
- Inference is **donor-level** throughout (n donors, not cells) — the per-cell histograms are visualization only.
