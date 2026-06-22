# RESUME — start here

_Last updated 2026-06-22. This is the single orientation doc: read it top to bottom and you are
caught up. It points to deeper docs only where you need detail._

**If you are a new Claude session resuming this project:** read this whole file first, then
**`PLAN.md`** (the active "show the real biology" work plan from the professor meeting — A/B/C/D
deliverables, emerging findings, what's ticked off). Then, only if you need depth: `GROUND_TRUTH.md`
(verified facts from both papers), `RULERS_EXPLAINED.md` (how every ruler/method works),
`PRIMER_COMPLIANCE.md` (which primer-specified tests are done). `CLAUDE.md` is auto-loaded and holds
the conventions + the "treat narrative docs as unverified" rule.

**Repo layout (reorganized):** `src/` root holds only `config.py` + `run_everything.py` (entry point).
Subpackages: `src/steps/` (pipeline steps), `src/battery/` (ruler-battery orchestration:
build_candidate_sets, summarize, h2_program/transcriptome, unsupervised_axis_eval, make_panel_figure),
`src/reports/` (PDF generators: make_latex/narrative/methods/report), `src/plotting/` (battery plots),
`src/analysis/` (biology deep-dive A/B/C/D; shared loaders in `analysis/common.py`, run via
`python src/analysis/run_analysis.py`), `src/prep/` (data conversions). Outputs: `results/reports/`
(PDFs), `results/figures/{h1,h2,confounders,staging}/` (analysis) + battery figures in
`results/figures/` root, `results/tables/analysis/` (per-donor summaries). _(Legacy pipeline.py /
classifier.py / run_all.py / run_p2_validation.py and the archive/*.html primers were removed.)_

---

## 1. The project in a paragraph
Healthy human liver is spatially **zonated** (pericentral ↔ periportal hepatocytes run opposite
metabolic programs). Paper 1 (Gribben/Vallier 2024, GSE202379) profiled ~69k hepatocytes across
47 donors spanning MASLD stages by **single-nucleus RNA-seq — but spatially blind**. Paper 2
(Yakubovsky/Itzkovitz 2026) is a **healthy spatial atlas** that defines a zonation reference. We use
Paper 2's program as a **ruler** to assign each Paper-1 cell a pseudo-zonation coordinate, then ask,
**at the donor level** (never the cell):
- **H1** — does zonation collapse across disease stage?
- **H2** — which gene programs lose their zonal slope, and fastest?
- **H3** — are de-zonated cells also more plastic (hepatocyte↔cholangiocyte)?

## 2. The governing rule (do not break it)
**Unit of inference = donor (~47), never the cell.** Rulers are selected on **healthy-atlas quality
only** (8-marker sign gate + healthy PC–PP anti-correlation + split-half reproducibility); the best
healthy rulers are **frozen, then** applied to disease. Disease H1/H2/H3 are the *test* — never used to
choose a ruler (that would be leakage/cherry-picking). **Eligibility for the frozen slot is by
LEAKAGE, not publishability:** a ruler may compete iff its axis was *not* fit on Paper-1 cells.
`unsupervised`/`unsupervised_combined` are PCA-fit on Paper-1 *healthy* cells, so their healthy
metrics are in-sample-inflated → shown as `control (Paper1-fit)`, kept as H1 robustness (their Paper-1
*disease* cells are never fit), but **ineligible**. Everything else (published lists + Paper-2-trained
axes `unsupervised_p2`/`supervised`/`lasso`/`elasticnet`) is leakage-clean and eligible. Effect size
beside every p; BH-FDR for many tests; rank-based tests by default.

## 3. What's done — results
- **Two co-primary rulers** (frozen on healthy metrics; leakage-clean eligibility, "do both"):
  **`expanded_curated`** (26+23 published genes — interpretable anchor; healthy score 1.149) and
  **`unsupervised_p2`** (label-free PCA on the external Paper-2 atlas, zero Paper-1 cells — healthy
  score 1.162, the *highest* eligible). The two are within the 0.02 tie band, so we report both and
  the headline rests on their **agreement** (curated signature + marker-free axis → same coordinate,
  same collapse). `expanded_curated` still drives H2b/H2c (it has named gene programs).
  *(History: an earlier cut restricted the competition to published sets only; that conflated
  publishability with leakage and is fixed — `unsupervised_combined` looked best on the raw table only
  because it's PCA-fit on the same Paper-1 healthy cells the metric scores.)*
- **H1 — collapse confirmed, robust.** Per-donor coord-spread falls and PC–PP anticorr rises toward 0
  with stage. Spearman **and** Jonckheere–Terpstra agree (expanded: spread ρ=−0.43 p=0.002, JT z=−3.1;
  anticorr ρ=+0.61 p=6e-6). Holds on the landmark ruler (ρ=−0.38) and a label-free PCA ruler (−0.51 to
  −0.56). Non-monotonic only Healthy→NAFLD (small-n noise, flips across rulers); real decline is
  **NASH→end-stage**.
- **H2 — slope-loss, broad but structured.** H2a held-out split: ~96/100 ruler genes weaken
  (non-circular). H2c transcriptome-wide: 67% of ~30k genes lean to weakening but only 8 survive
  per-gene FDR (n=47 underpowered per gene → diffuse). H2b program-level (on the valid ruler, Mann–
  Whitney vs genome background): **Wnt/pericentral-identity q=8.5e-6 (rank-biserial −0.82), CYP q=5e-5,
  urea q=3e-3, lipid q=0.014; acute-phase/bile-acid spared.** → pericentral Wnt identity de-zonates first.
  **H2d explicit interaction OLS** (primer's `expr ~ coord + stage + coord:stage`, fit donor-level on
  per-donor coord-bin pseudobulk with cluster-robust SE by donor; aligned coord:stage<0 = slope-loss):
  34/49 signature genes weaken (sign-test p=9e-3), concordant with the held-out proxy (Pearson r=+0.85,
  80% sign-agree) and reproduces the program split independently — PC 24/26 weaken (median beta=-0.011;
  GLUL/CYPs/SLCO1B3 lead), PP acute-phase spared/strengthen (10/23, median beta~0).
- **H3 — weak, marginal, ruler-dependent.** Marker rulers: Wilcoxon signed-rank p≈1e-4 but tiny effect
  (AUC≈0.505, mean ρ≈0.025); the unsupervised ruler is null. Honest: H1/H2 robust, H3 marginal.
- **Leakage control:** an unsupervised PCA axis trained **entirely on the external Paper-2 atlas**
  (zero Paper-1 cells) still collapses (ρ=−0.50, p=3e-4) → not leakage, not a variance artefact.
- **Dilution result:** unweighted full sets (`paper2_full`, `unsupervised_full`) **break** (healthy
  PC–PP correlation flips positive) → weighting/selection matters; full is a documented negative control.
- **Classifier (auxiliary):** calibrated multinomial LR, landmarks excluded, held-out Paper-2 accuracy
  0.755 vs 0.333 chance; entropy is an auxiliary layer (labels are η-over-landmark, signature-derived).

## 4. Where everything lives
**Run it all:** `python src/run_everything.py` (one entry point: build candidate sets → learned
coords → 17-ruler battery → summary → panel → H2b/H2c → both PDF reports).

**Code (`src/`):**
- `run_everything.py` — unified orchestrator (explicit ruler registry; no hidden config).
- `steps/` — the pipeline, single source of truth: `step2_load_qc`, `step4_score`, `step4b_classifier`,
  `step5_validate` (gate), `step5b_ruler_diagnostics`, `step6_collapse` (H1, +JT), `step7_de`
  (H2 held-out slope-loss + explicit interaction OLS + pseudobulk DE), `step8_plasticity` (H3,
  +Wilcoxon/AUC), `common.py`
  (helpers incl. `jonckheere_terpstra`, `bh`, `set_dir`), `step4c_learned_coords` (PCA / regularized /
  supervised rulers).
- `build_candidate_sets.py`, `run_explicit_signature_battery.py`, `summarize_signature_battery.py`
  (ranking + auto-select), `h2_program_analysis.py` (H2b), `h2_transcriptome_wide.py` (H2c),
  `unsupervised_axis_eval.py`, `make_panel_figure.py`, `make_latex_report.py`, `make_narrative_report.py`,
  `plotting/artefacts.py` (the single plotting layer).
- `prep/` — one-time data conversions (`00`–`04`).

**Outputs (`results/`):**
- `tables/<set>/` per ruler: `validation.csv`, `ruler_diagnostics.csv`, `collapse_per_donor.csv`,
  `collapse_trends.csv` (incl. `jt_z`,`jt_perm_p`), `per_donor_plasticity.csv`, `h3_summary.csv`,
  `h2_slope_loss[_summary].csv`, `h2_interaction_ols[_summary,_by_program].csv` (explicit interaction
  OLS), `h2_program_summary.csv`/`h2_transcriptome_wide.csv` (expanded only),
  `coordinates.csv` (git-ignored, big).
- `tables/` globals: `signature_battery_summary.csv` (the ranking), `candidate_set_build_report.csv`,
  `selected_set_decision.txt`, `classifier_{eval,confusion_matrix,entropy}.csv`.
- `Zonation_Narrative_Report.pdf` (analysis writeup), `Zonation_Ruler_Report.pdf` (per-set dossier),
  `figures/`.

## 5. What's left (open items)
1. ~~**H2 explicit interaction OLS**~~ — DONE (`h2_interaction_ols` in `step7_de.py`; the exact
   primer model `expr ~ coord + stage + coord:stage`, donor-level via per-donor coord-bin pseudobulk +
   cluster-robust SE by donor). Writes `h2_interaction_ols{,_summary,_by_program}.csv` + a figure per
   ruler; agrees with the held-out proxy (r=+0.85) and the H2b program split. See §3 (H2d).
2. **Step 9 bonus** — Paper 3 (Zhu 2026) inherited-risk hypergeometric enrichment. Needs the risk→target
   gene supplementary `.xlsx` (paywalled; see `data/data_urls.md`). `step9_bonus_enrichment.py` is a stub.
3. **External replication** — apply the frozen ruler to the spatial-MASLD cohort (Nat Genet 2025; scRNA
   + Visium) to replicate H1 *and* validate the coordinate against real disease spatial positions. Data
   located but not fetched (portal `db.genomics.cn/stomics/hmsma`; see `data/data_urls.md`).

## 6. Running on another machine
`git clone` brings all code + the context docs above. Data is git-ignored — either re-download via
`data/data_urls.md` or copy from USB: **`data/processed/` (~3 GB, REQUIRED)** and **`data/raw/`
(~7.8 GB, needed only to regenerate learned coords / prep / build candidate sets)**. Then
`python src/run_everything.py`. (Note: the local `~/.claude` memory does not transfer between machines
— this repo's docs are the portable context.)
