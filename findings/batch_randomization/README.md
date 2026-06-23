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
- **Within the 38 biopsy donors it is weaker and partly crossed: Cramér's V(run, F) = 0.40.** The 4 cirrhotic-F4
  biopsy donors sit on 2 runs — SLX-20270 (donors 12, 22) and SLX-20290 (donors 68, 75). **CORRECTION (caught by
  methodological review 2026-06-23):** an earlier draft said "BOTH runs also carry F0/F1/F2/F3 (MIXED) → F1-vs-F4
  estimable within-batch." That is **wrong** and contradicts our own table below: **SLX-20270 carries F0/F2/F3/F4
  but NO F1 donor.** Only **SLX-20290 contains both an F1 and an F4** donor. So two of the four F4 donors (12, 22)
  have **no within-run F1 comparator** — for them the raw F1-vs-F4 contrast is partly aliased with run. The old
  `batch_qc.py` "MIXED" flag was too weak: it tested "≥2 fibrosis levels on the run," not "both endpoints (F1 AND
  F4) present." We therefore ran the sensitivity test the section below had only *promised* — see "Batch
  sensitivity (executed)."

## Run × fibrosis (biopsy donors)
| run | F0 | F1 | F2 | F3 | F4 |
|---|---|---|---|---|---|
| SLX-20270 | 1 | 0 | 3 | 3 | **2** |
| SLX-20290 | 1 | 3 | 3 | 0 | **2** |
| SLX-20793 | 0 | 1 | 2 | 5 | 0 |
| SLX-20289 | 0 | 1 | 2 | 1 | 0 |
| (5 small runs, 1–2 donors each) | | | | | |

## Batch sensitivity (executed) — `src/dge/plan_a_batch_sensitivity.R`
We re-tested the F4-vs-F1 biliary hits two ways that remove the run confound:
- **(A) Run as a blocking covariate**, restricted to the 2 F4-bearing runs (18 donors), model `~ run + fibrosis`,
  contrast F4−F1: the biliary genes keep **large positive log2 fold-changes** (B3GNT3 +3.3, GRHL2 +3.1, SOX4 +3.0,
  EPCAM +2.5, CXCL10 +6.6, SPINT2 +3.1) — i.e. controlling for run does **not** shrink the effect — but with the
  smaller donor set only B3GNT3 clears FDR<0.05 (B3GNT3 0.011; SPINT2 0.083, EPCAM 0.095, CXCL10 0.103, GRHL2/SOX4
  0.21–0.26). What batch adjustment costs is **significance (sample size), not effect size.**
- **(B) Within a single run** (SLX-20290 only, the one run with both endpoints; 2 F4 vs 3 F1, zero batch confound):
  the **same genes top the list with the same large fold-changes** (B3GNT3 +3.2, CXCL10 +7.0, SOX4 +3.3, GRHL2 +2.9,
  EPCAM +2.2); none reach FDR<0.05 at this tiny n, but the program is plainly present **inside one batch.**

**Conclusion:** the biliary rise is **not created by sequencing batch** — its direction and magnitude reproduce
both under run-adjustment and within a single run; only statistical significance attenuates with the reduced n.
(This is the test F17 originally only promised. The MDS pre-flight and a formal leave-one-donor-out remain as
optional extra checks; full 13-level run cannot be modelled as a fixed factor at n=38.) **Caveat:** this rescues
the *direction*, not power — and it does not change the deeper point that these genes are **cholangiocyte-ambient
by the cross-lineage burden audit (F18)** regardless of batch. Batch was a candidate *inflator* of the hits; it
is not the source. End-stage (Plan C) stays descriptive.
