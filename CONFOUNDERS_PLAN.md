# Confounder strategy — DEFERRED (parked, not in the report/code)

_Why this is parked (2026-06-22): the confounder controls we built (C1 cell-count, C2 depth, C4 UMI)
all asked "does the **zonation-strength / spread / IQR / anti-correlation** trend survive
equalization?" — but A and B showed those are the **weak, secondary** indicators. The dominant
signal is **pericentral program TURN-OFF (expression level)**. So the controls were validating the
wrong (secondary) thing. We removed them rather than ship a mismatched story._

## If/when we revisit — recenter on the DOMINANT signal
Validate the **pericentral expression LEVEL** (the turn-off), not spread/IQR/anti-corr:
- Quick check already run: per-donor pericentral level vs stage ρ=−0.49, and it **survives depth
  equalization** (−0.486 → −0.476 thinning all cells to a common SCT-count depth). So the dominant
  signal does hold — a recentered C would lead with this, with spread/anti-corr demoted to "downstream
  consequence of the turn-off."

## Better ways to spot confounders than "demote + re-measure spread/IQR/anti-corr"
Brainstorm of stronger / orthogonal checks (think before building):
1. **Negative-control genes.** Housekeeping / depth-insensitive genes (e.g. ACTB, GAPDH, B2M) should
   show NO stage trend in level or zonation. If they do, the "turn-off" is a technical/normalization
   artifact, not biology. This is a much sharper test than re-measuring the same indicators.
2. **Positive-control stable genes.** A gene known to be uniformly expressed across zones should stay
   flat — a sanity anchor.
3. **Technical covariate regression.** Regress per-cell/per-donor level on nFeature, %mito, ambient-RNA
   fraction, lobe, processing batch BEFORE the stage test; does the turn-off survive adjustment?
4. **Cell-purity / contamination.** In disease, "hepatocyte" clusters may be contaminated by immune
   infiltrate, cholangiocytes, doublets — which could dilute pericentral signal and mimic turn-off.
   Check marker purity (ALB high, PTPRC/EPCAM low) per stage; re-test on high-purity cells only.
5. **Permutation / label-shuffle null.** Shuffle donor→stage labels many times; the observed turn-off
   effect should sit far in the tail. (We did permutation p for H1; do it for the LEVEL.)
6. **SCT vs raw RNA assay.** The scored matrix is SCT-corrected. Re-extract the raw RNA assay and check
   the turn-off is present there too (not created or hidden by SCT). The honest "true-depth" control.
7. **Within-donor split-half stability** (reliability, not confound): split a donor's cells; both halves
   should give the same level — separates real signal from sampling noise at low n.
8. **Ambient/empty-droplet model** for the low-count end-stage cells specifically.

## What we KEPT (it is mechanism, not a spread/IQR control)
`c3_level_vs_slope.py` — per-gene LEVEL change vs SLOPE change (turn-off vs de-zonation). This is
turn-off EVIDENCE (14/26 pericentral genes lose level+slope), not a confounder control, so it stays.
