# F17 — Sequencing batch is NOT randomized (confounded with stage/source)

**Status: LIVE — data-quality finding.** Reproducible: `src/confound/batch_qc.py` →
`results/tables/analysis/batch_qc.csv`.

## Where the batch data comes from (provenance — exact)
The only batch/run information in the deposited data is the **`orig.ident`** column of
`data/processed/paper1/metadata_all_cells.csv` (one value per cell, e.g. `SLX-21151-SITTB7`). "SLX" is the
sequencing facility's run identifier; we parse the **run prefix** `SLX-#####` (regex `SLX-\d+`) as the batch,
and the trailing token (e.g. `SITTB7`) is the per-sample 10x index within that run. There is **no separate
batch/date/lane column**; `manuscript.expt` exists but = `CG` for all 47 donors (a single experiment label,
useless for separation). So the SLX run is the finest batch unit available. **13 distinct runs over 47 donors.**
This is the right field to test "are sequencing batches randomized vs disease stage?" (it is the actual machine
run grouping); the donor-coloured MDS plot is only a secondary "did batch leak into expression" picture.

## Result
- **Run predicts tissue source almost perfectly: Cramér's V(run, source) = 0.84.** **9 of 13 runs carry only
  ONE disease stage**; the organ-cube groups are largely on dedicated runs (healthy-only SLX-21151; end-stage-
  only SLX-19940/21153/21155). → samples were sequenced in **stage/source-clustered batches, not randomized**.
  This is another layer of the same confound (tissue-source + procurement + **now sequencing batch**, all
  collinear with stage). It is *uncorrectable* for the healthy/end-stage groups — but those are already
  excluded from the disease axis.
- **Within the 38 biopsy donors it is weaker and partly crossed: Cramér's V(run, F) = 0.40.** The **4 F4 biopsy
  donors are on 2 runs (SLX-20270, SLX-20290), and BOTH runs also carry F0/F1/F2/F3 donors** (MIXED) → the
  **F1-vs-F4 fibrosis effect is estimable within-batch, NOT collinear with run.** So the biopsy DGE is not a
  pure batch artifact.

## Run × fibrosis (biopsy donors)
| run | F0 | F1 | F2 | F3 | F4 |
|---|---|---|---|---|---|
| SLX-20270 | 1 | 0 | 3 | 3 | **2** |
| SLX-20290 | 1 | 3 | 3 | 0 | **2** |
| SLX-20793 | 0 | 1 | 2 | 5 | 0 |
| SLX-20289 | 0 | 1 | 2 | 1 | 0 |
| (5 small runs, 1–2 donors each) | | | | | |

## How the DGE handles it (pin #2, now answered)
Cannot model 13-level run as a fixed factor at n=38 (over-parameterized). Instead:
1. **MDS / PCA colored by run** as pre-flight — does run drive the dominant variance, or stage?
2. **Per-hit within-run sensitivity:** for any F1/early-vs-F4 hit, confirm the effect is present **within
   SLX-20270 and SLX-20290** (the two runs that contain F4 alongside earlier stages). A hit that only appears
   between runs, not within, is batch.
3. **Leave-one-donor-out** (already planned) — also catches a single-run-driven hit.
4. Optionally include a coarse **2–3-level batch covariate** (the biggest runs vs rest) if the n permits.

This does not rescue end-stage (Plan C stays descriptive); it bounds the biopsy DGE honestly.
