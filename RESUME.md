# RESUME — where we are, how to continue

_Last updated: 2026-06-22._

## State (done)
H1/H2/H3 complete and committed. One unified entry point: `python src/run_everything.py`
(builds candidate sets → learned coords → 17-ruler battery → summary → reports).
- **H1** zonation collapse: robust across valid rulers (landmark, expanded_curated, unsupervised
  dense/P2/combined); Spearman **and** Jonckheere–Terpstra agree (e.g. expanded spread JT z=−3.07).
  Non-monotonic only at Healthy→NAFLD (small-n noise, direction flips across rulers); real decline
  is NASH→end-stage.
- **H2** slope-loss: H2a held-out (96/100 weaken), H2b program-level on the *valid* ruler
  (Wnt q=8.5e-6, CYP q=5e-5, urea q=3e-3, lipid q=0.014; acute-phase spared), H2c transcriptome-wide
  (67% weaken, 8/30k survive FDR → broad-but-structured).
- **H3** de-zonation↔plasticity: weak, marginal, ruler-dependent (marker rulers Wilcoxon p≈1e-4 but
  AUC≈0.505; unsupervised null).
- Frozen primary ruler (healthy-metrics selection, not disease): **expanded_curated**.

## Read these first (portable context — all in the repo)
`CLAUDE.md` (auto-loaded), `GROUND_TRUTH.md` (verified facts from both papers),
`RULERS_EXPLAINED.md` (every ruler + method), `PRIMER_COMPLIANCE.md` (specified-vs-done audit),
`results/Zonation_Narrative_Report.pdf` + `Zonation_Ruler_Report.pdf`.

## Left to do
1. Explicit H2 coord×stage interaction OLS (`expr~coord+stage+coord:stage` per gene) — proxy exists.
2. Step 9 bonus (Paper 3 inherited-risk hypergeometric) — needs Paper 3 SI gene list (see data_urls.md).
3. External replication on the spatial-MASLD cohort (data not yet fetched; see data_urls.md).

## To run on another machine
`git clone` gets all code + the context docs above. Data is git-ignored — either re-download via
`data/data_urls.md` or copy `data/processed/` (≈3 GB, REQUIRED) and `data/raw/` (≈7.8 GB, needed only
to regenerate learned coords / prep) from a USB. Then `python src/run_everything.py`.
