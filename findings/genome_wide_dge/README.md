# F15 — Genome-wide differential expression: explicit method + result

**Status: LIVE.** Script: `src/dge/dge_genomewide.py`; input `pseudobulk_hep_by_donor.csv` (from
`src/prep/09_extract_full_and_union.R`); compositional audit `dge_compositional.py` (+ `prep/10`).

## Method — written out explicitly (no hand-waving)
- **Unit = donor.** Pseudobulk = **sum of raw RNA-assay UMIs over each donor's hepatocyte nuclei** (NOT
  per-cell; avoids pseudoreplication).
- **Genes:** the **full transcriptome = 31,257 genes** (the entire RNA assay), donors × genes matrix.
- **Cohort:** restricted to **38 acquisition-matched biopsy donors** (non-CL, non-Healthy, with a fibrosis
  score). F-distribution F0–F4 = 2/8/12/12/4.
- **Normalization:** library-size **CPM** = (gene pseudobulk count) ÷ (donor's total pseudobulk) × 10⁶,
  then **log2(CPM + 1)**. (No SCT; no per-cell normalization — pseudobulk + CPM is the standard donor-level
  DE normalization.)
- **Expression filter:** keep genes with **CPM ≥ 1 in ≥ 19 of 38 donors** → **17,572 genes tested** (of 31,257).
- **Tests:** (a) trend — **Spearman(fibrosis stage, log2-CPM)** per gene, **Benjamini–Hochberg FDR**;
  (b) contrast — **Mann–Whitney** F1 vs F4 on log2-CPM. Output `dge_genomewide.csv`.

## Result
- **Zonation + xenobiotic genes are flat transcriptome-wide:** CYP2E1 FDR 0.98, CYP1A2 0.91, ADH4 0.97,
  SLCO1B3 0.80, CYP3A4 0.97, GLUL 0.85; all periportal genes FDR > 0.79 — none significant. → the null holds
  **beyond our curated panel** (strengthens the primary result).
- **23 genes trend at FDR < 0.05** — a fibrosis-associated program (A2M CPM 219→718, ESRRG, DTNA, GUCY1A1,
  ADAMTS9 up; DOK6, ENPP3 down). Compositional audit (`dge_compositional.py`, all 99,809 nuclei): **15/23 are
  ≥3× higher in a non-hepatocyte lineage** (stellate/cholangiocyte/endothelial/immune) → mostly **ambient**;
  the non-hep fraction does not rise with fibrosis (ρ=−0.07), so it's per-nucleus ambient, not a composition
  shift. The one clear hepatocyte-intrinsic signal is **A2M** (acute-phase) — a modest injury response.
- **Retires the §4 "only internal change is detox dimming"** (Item 1b FALSIFIED, D2): the within-PC detox dip
  does NOT survive this pseudobulk multiple-testing (those genes FDR 0.80–0.98).

## Why it matters
This is the panel-free check. It (i) **strengthens** "gene-expression zonation preserved" (D3) genome-wide,
and (ii) **kills** the detox sub-story (D2). The only biopsy-internal hepatocyte signal is a small
acute-phase response (A2M), not de-zonation.
