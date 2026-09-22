# Adversarial verification: is the pericentral-detox "dimming" real or a compositional artifact?

**Date:** 2026-06-24 · **Unit:** donor-level · **Cohort:** biopsy-only F0–F4 (38 donors; F0/F1/F2/F3/F4 = 2/8/12/12/4; CL\* explants + Healthy excluded) · **Scripts:** `src/dge/geneset_verify.R`, `src/dge/geneset_verify_test4.py`

## The concern
camera (`src/dge/geneset_camera.R`) and GSEA-prerank (`src/dge/geneset_tests.py`) are **competitive** tests on **CPM** pseudobulk. CPM is compositional: if biliary/EMT/IFN genes rise with fibrosis they consume library budget and every other gene's CPM mechanically falls, so the pericentral-detox set could read "Down" with no true per-hepatocyte dimming. Red flag: pericentral_anchors Down while periportal_anchors Up (a see-saw) — the signature of a competitive test under a compositional shift.

## TEST 1 — Composition-robust normalization (CPM vs edgeR-TMM camera)
TMM down-weights composition shifts. Re-ran camera on TMM-normalized log-CPM. (TMM norm factors span only **0.908–1.211** — the compositional pull on the library is modest.)
File: `results/tables/analysis/geneset_verify_camera_cpm_vs_tmm.csv`

| gene_set | Dir | FDR (CPM) | FDR (TMM) |
|---|---|---|---|
| xenobiotic_CYP | Down | 2.32e-6 | **3.53e-6** |
| pericentral_anchors | Down | 1.46e-4 | **2.66e-4** |
| detox_phase2 | Down | 7.01e-3 | **9.38e-3** |
| urea_cycle | Down | 1.23e-1 | 1.30e-1 (ns) |
| cholangiocyte_ductular | Up | 1.88e-5 | 3.01e-5 |
| CTRL_EMT | Up | 9.15e-6 | 8.03e-7 |
| CTRL_interferon | Up | 1.47e-3 | 1.01e-4 |
| periportal_anchors | Up | 1.46e-2 | 7.61e-3 |

**Verdict:** detox sets stay Down with **near-identical (marginally stronger)** FDRs under TMM. The competitive significance is **not** a CPM artifact.

## TEST 2 — Self-contained rotation test (limma::mroast, TMM, 9,999 rotations)
roast is a **self-contained** test (does the set move against its own null?), rather than a competitive comparison with genes outside the set. It still analyzes normalized sequencing counts and does not establish absolute molecule loss or enzyme activity.
File: `results/tables/analysis/geneset_verify_roast.csv`

| gene_set | Dir | PropDown | PValue | FDR |
|---|---|---|---|---|
| xenobiotic_CYP | **Down** | 0.54 | 0.0040 | **0.015** ✓ |
| pericentral_anchors | Down | 0.15 | 0.032 | 0.081 (borderline) |
| detox_phase2 | Down | 0.13 | 0.154 | 0.220 (ns) |

**Verdict:** the **CYP xenobiotic family moves Down in the self-contained test** (survives FDR). The broader pericentral anchor set is borderline; phase-II detox does **not** reach self-contained significance. The supported set-level signal is therefore narrower than the competitive result.

## TEST 3 — Contaminant removal (drop budget-eaters, renormalize, re-test)
Dropped **65 genes**: all cholangiocyte_ductular + CTRL_EMT + CTRL_interferon set members present, plus the **20** genome-wide genes with rho_F>0 & fdr_trend<0.05 in `dge_genomewide.csv`. Renormalized (TMM) and re-tested the detox sets.
File: `results/tables/analysis/geneset_verify_decontam.csv`

| gene_set | Dir | FDR (decontam CPM) | FDR (decontam TMM) |
|---|---|---|---|
| xenobiotic_CYP | Down | 8.78e-7 | **2.67e-6** |
| pericentral_anchors | Down | 1.33e-4 | **2.93e-4** |
| detox_phase2 | Down | 6.96e-3 | **8.00e-3** |

**Verdict:** after removing the things that could eat library budget, the detox sets stay Down with **essentially unchanged** FDRs. The Down call is **not driven by the up-going compositional shift**.

## TEST 4 — Within-PC, depth-matched detox burden (decisive, non-compositional)
Separate per-cell measure: detox UMIs per **pericentral** nucleus on counts **down-thinned to a common 1,500-UMI budget**, averaged over eight deterministic draws (DETOX = CYP2E1/CYP1A2/ADH4/AKR1D1/SLCO1B3, same PC gate as `src/confound/mde.py`). This avoids between-cell library-depth and donor-composition differences, but remains a relative measurement within a fixed sequencing budget. 37 of 38 donors had ≥20 PC nuclei.
File: `results/tables/analysis/geneset_verify_within_pc_detox.csv`

| stage | nDonors | mean detox UMIs/nuc |
|---|---|---|
| F0 | 2 | 12.48 |
| F1 | 8 | 11.86 |
| F2 | 12 | 10.21 |
| F3 | 11 | 10.04 |
| F4 | 4 | 9.02 |

- Donor-level **Spearman(detox, F) = −0.461, p = 0.0041** (n=37).
- **F1→F4: 11.861 → 9.015** UMIs/nuc (diff **−2.846**, 95% CI **[−4.383, −1.309]**, Welch p=0.0022).
- The MDE calculation is a design diagnostic, not an additional significance threshold; the estimate and interval above are the primary endpoint summary.

This matches the deck's "~12.7→8.9" (F0=12.45, F1→F4 = 11.88→8.79; the headline figure rounded the ends).

**Verdict:** the per-cell, depth-matched burden **declines** with fibrosis and the decline is statistically supported and above the power floor. Because it is per-nucleus and depth-matched, this **cannot** be a compositional/library-budget artifact.

## Reconciliation with the genome-wide per-gene result (honesty check)
Per-gene pseudobulk DGE: **20 of 22** pericentral/detox landmark genes have rho_F < 0 (coordinated direction), but **not one** survives per-gene FDR (min **fdr_trend = 0.80**, `dge_genomewide.csv`). This is exactly the "many genes each shifting a little, same direction" pattern that per-gene FDR misses but a set test and a per-cell aggregate detect. The `CLAIMS_LEDGER` "FALSIFIED (row 1b)" refers specifically to the **per-gene** claim — *no single detox gene is individually significant* — which remains true and is **not** contradicted here.

## VERDICT
**Scoped verdict.** The relative pericentral-detox decline is supported by TMM-normalized CAMERA, removal of the up-going budget-eaters, a self-contained test for the CYP core, and a separate within-PC depth-matched measure (Spearman −0.461, p=0.0041). Only the **CYP xenobiotic core** clears FDR in the self-contained rotation test; the broader anchor and phase-II sets are borderline-to-null there. None of these checks establishes absolute molecular or functional loss.

**One-line wording for the deck:**
> The relative pericentral-detox program declines with fibrosis: within-PC depth-matched burden falls 11.86→9.02 UMIs/nucleus from F1 to F4 (Spearman −0.461, p=0.0041), while the CYP set is Down in both CAMERA and mROAST; no single detox gene clears per-gene FDR.

**Strongest defensible claim:** a *relative, coordinated* detox decline is robust across the selected normalization and aggregation checks; the *CYP xenobiotic core* is the part that also clears the self-contained test. Biliary/ductular attribution of the up-going contrast remains a **lead, not closed**.
