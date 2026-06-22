# RESUME — start here

_Last updated 2026-06-22. This is the single orientation doc: read it top to bottom and you are
caught up. It points to deeper docs only where you need detail._

**If you are a new Claude session resuming this project:** read this whole file first. Then, only if
you need depth: `GROUND_TRUTH.md` (verified facts from both papers), `RULERS_EXPLAINED.md` (how every
ruler/method works), `PRIMER_COMPLIANCE.md` (which primer-specified tests are done). `CLAUDE.md` is
auto-loaded and holds the conventions + the "treat narrative docs as unverified" rule.

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
healthy ruler is **frozen, then** applied to disease. Disease H1/H2/H3 are the *test* — never used to
choose a ruler (that would be leakage/cherry-picking). Effect size beside every p; BH-FDR for many
tests; rank-based tests by default.

## 3. What's done — results
- **Frozen primary ruler: `expanded_curated`** (26+23 published genes; chosen by healthy metrics).
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
  (H2 held-out slope-loss + pseudobulk DE), `step8_plasticity` (H3, +Wilcoxon/AUC), `common.py`
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
  `h2_slope_loss[_summary].csv`, `h2_program_summary.csv`/`h2_transcriptome_wide.csv` (expanded only),
  `coordinates.csv` (git-ignored, big).
- `tables/` globals: `signature_battery_summary.csv` (the ranking), `candidate_set_build_report.csv`,
  `selected_set_decision.txt`, `classifier_{eval,confusion_matrix,entropy}.csv`.
- `Zonation_Narrative_Report.pdf` (analysis writeup), `Zonation_Ruler_Report.pdf` (per-set dossier),
  `figures/`.

## 5. What's left (open items)
1. **H2 explicit interaction OLS** — `expr ~ coord + stage + coord:stage` per gene (we have the
   per-donor-slope proxy + held-out + H2b/H2c; the exact model isn't fit yet).
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
