# PLAN — "show the real biology" deep dive

_Tracked work plan from the professor meeting (2026-06-22). Principle: **summary statistics are
indicators, not results.** Every claim must be backed by a look at the actual cell-level data and an
explicit confounder check. Tick items as they land. Companion: [RESUME.md](RESUME.md) (project state),
methods in `results/reports/Zonation_Methods_Explainer.pdf`._

**Primary disease axes (decided):** run everything on BOTH the 5 coarse stages AND fibrosis F0–F4
(the stronger biology). NAS (activity 0–8) as a secondary axis. All staging is already in
`data/processed/paper1/metadata_all_cells.csv` (`Fibrosis.score..F0.4.`, `Steatosis`/`Ballooning`/
`Inflammation` → NAS, `SAF.Score`) — **no download needed.**

**Scatter scope (decided):** all 47 donors as a contact sheet + a curated depth-matched representative
panel (never cherry-picked single donors).

---


> **UPDATE (review 4): C confounder controls DROPPED** (code+report) — they validated the secondary indicators (spread/IQR/anti-corr), not the dominant turn-off signal. Parked in CONFOUNDERS_PLAN.md (recenter on pericentral LEVEL + stronger checks: neg-control genes, purity, covariate regression). The old Biology Findings PDF was rejected (unreadable shrunk figures, offset auto-circles) and REPLACED by `results/reports/Zonation_Story.pdf` (`src/reports/make_zonation_story.py`): arc-driven (indicators->biology), one readable figure per page, full 47-donor panels, no auto-circles, fibrosis re-staging shown, de-zonation called WEAK honestly (pattern-view z-scoring artifact explained).

## Emerging findings (from A1–A4, B1–B4 — first pass, expanded_curated ruler)
A coherent, mechanism-specific picture (real biology), CONVERGENT across 7 independent views:
- **Dominant signal = pericentral program TURN-OFF (level collapse), strongest End-stage/F4.**
  B4: raw PC level −34–37% by End-stage (all sets agree). A3: CYP1A2/CYP2E1/SLCO1B3/GLUL drop. B2: PC
  program loses level *in the PC zone* (1.25→0.74). B3: PC level 0.92→0.73. B1 (raw + z-scored): the
  pericentral rows go uniformly low (turn-off), not merely un-patterned.
- **Secondary signal = DE-ZONATION is MODEST and mostly LATE.** B1 PATTERN view (each stage z-scored
  within itself): the left→right gradient diagonal **largely persists** through NAFLD/NASH/Cirrhosis
  and degrades clearly only at End-stage/F4. B3 agrees (PC slope only +0.126→+0.102). So the spatial
  PATTERN mostly survives — the dominant change is LEVEL (turn-off), not pattern loss. (The old
  z-vs-healthy heatmap conflated level & pattern and looked like "a flip"; now split into separate
  PATTERN / LEVEL / deviation views — `b1_heatmap_{pattern,level,vs_healthy}_*`.)
- **The bipolar axis dissolves** (A1): intact anti-diagonal Healthy(r=−0.48)/NAFLD/NASH → positive
  blob by Cirrhosis(+0.26)/End-stage(+0.22). Likely **downstream of the pericentral turn-off** (silent
  PC genes → pc score becomes noise → anti-corr breaks), i.e. A4's "noise" may not be independent.
- **The 1D coordinate distribution is a weak readout** (A2): broad unimodal humps; "spread by stage"
  is an indicator, not the result.
- **End-stage is HETEROGENEOUS** (B2): the across-donor boxes WIDEN markedly at end-stage — this is
  genuine donor-to-donor variability (some end-stage donors retain pericentral expression, others lose
  it) compounded by small n (5 donors), NOT per-cell measurement noise. The widening is itself biology;
  it's also why n-labelling + the C controls gate confidence.
- **H1 SURVIVES the confounder controls (C — now run, the decisive step):** the collapse trend
  Spearman(strength, stage) = −0.612 is unmoved by equalizing **cell count** (common-N=200 → −0.586)
  and by equalizing **sequencing depth** (all cells thinned to a common depth, re-scored → −0.617).
  Within-donor depth-response confirms depth *does* causally degrade the measurement (donor 6:
  −0.55→−0.33 when thinned) — but depth isn't differentially distributed across stages, so it can't
  manufacture the trend. End-stage blob is NOT a depth artifact: high-UMI cells are *more* positive
  (+0.33), not more anti-correlated. **So H1 is robust, not an artifact.**
- **Honest caveats:** only 4 healthy donors, 2 low-depth & weak; per-donor metrics noisy at low n;
  contact sheet (all 47) is the full view, representatives are best-powered (outcome-independent).
  Caveat on C: the counts matrix used for thinning has per-cell totals ~3–5k (gene-subset), below the
  full clinical nCount, so depth targets are on that scale — the *relative* depth effect + trend
  survival are valid; absolute UMI numbers are not the raw sequencing depth.

## Decisions / conventions (from review 2)
- **Representatives are NOT cherry-picked — document this prominently (in F):** cross-sectional design
  (each donor = one stage, so per-stage panels are necessarily different donors); selection is
  OUTCOME-INDEPENDENT (best-powered = highest depth, never by anti-corr/the result); the 47-donor
  contact sheet is the honest full view, representatives are just clean well-measured examples.
- **Number of sets:** MAIN story figures use 1–2 rulers (the co-primaries expanded_curated +
  unsupervised_p2) for clarity; the broad multi-set figure (B4) is kept as a labelled ROBUSTNESS
  panel (all sets agree on direction), not the headline.
- **A4 mechanism CLASSIFICATION is deprecated** (heuristic z-argmax → unreliable, per review). KEEP the
  per-donor metric trajectories (anticorr / prog_raw / coord_range vs stage — real measurements);
  DROP the "dominant mechanism" call. The mechanism story is carried by B1–B4, which measure level vs
  pattern directly.
- **The currently-committed `Zonation_Narrative_Report` is STALE** — superseded by deliverable F once
  the controls (C) land. Narrative depth is increasing; F is the new authoritative writeup.

## A — H1: is zonation intact at the start, and HOW does it collapse?
The question behind H1: when "spread" shrinks, is it (a) **expression turn-off** (genes go silent →
cloud collapses to the origin), (b) **noise** (anti-correlation dissolves → round blob), or (c) **true
de-zonation** (cells pile at the axis center, keep anti-correlation sign, lose the extremes)? The
PC-arm vs PP-arm scatter discriminates these.

- [x] **A1** Per-donor **PC vs PP scatter** — full 47-donor contact sheet (by stage AND fibrosis) +
  best-powered representative panel vs healthy envelope; colored by coordinate.
  `src/analysis/a1_scatter.py` → `results/figures/h1/a1_*`.
- [x] **A2** Per-donor **coordinate distribution** along the zonation axis. `src/analysis/
  a2_distributions.py` → `results/figures/h1/a2_*`. _(TODO: extend to fibrosis axis + contact sheet.)_
- [x] **A3** **Marker zonation profiles** (`src/analysis/a3_marker_profiles.py` → results/figures/h1/a3_*) — — mean expression of canonical markers (GLUL, CYP2E1 / ASS1,
  ALDOB) vs coordinate-bin, per stage/fibrosis: does the gradient flatten while expression persists
  (de-zonation) or drop to zero (turn-off)?
- [x] **A4** **Per-donor mechanism quantification** — anti-corr (noise) / raw program level (turn-off)
  / coordinate range (de-zonation); classify + plot across stage/fibrosis. `src/analysis/
  a4_mechanism.py` → `results/figures/h1/a4_*`, `results/tables/analysis/mechanism_by_donor.csv`.
- [ ] **A1b** **Anti-cherry-pick hardening:** representative panel shows 2–3 best-powered donors per
  stage with the (outcome-independent) selection rule printed on the figure; PLUS a clean **cross-ruler
  story figure** — PC/PP collapse for the two co-primary rulers (expanded_curated + unsupervised_p2)
  side by side, to show the collapse is ruler-independent, not a hand-picked view.

## B — H2: which programs lose zonation, shown as patterns
- [x] **B1** **Gene × cell heatmap** (`src/analysis/b1_heatmap.py` → results/figures/h2/b1_*) — — cells (cols) ordered by coordinate, genes (rows) ordered by
  their **healthy** slope (fixed order across stages). Render BOTH per-gene z-scored (pattern /
  de-zonation) and library-normalized log (level / turn-off). Bin cells ~50/stage for tractability.
- [x] **B2** **Zone × program boxplots** (`src/analysis/b2_zone_boxplots.py` → results/figures/h2/b2_*) — — terciles PC/mid/PP on x, program expression on y, faceted by
  stage/fibrosis: does the pericentral program lose expression *in the pericentral zone*?
- [x] **B3** **Program score vs coordinate** (`src/analysis/b3_program_vs_coord.py` → results/figures/h2/b3_*) — per cell, colored by stage — the gradient directly.
- [x] **B4** **Per-set expression level** — x = stage & fibrosis, y = mean per-DONOR raw expression of
  each set's PC and PP arms, one line per set. `src/analysis/b4_set_levels.py` →
  `results/figures/h2/b4_*`, `results/tables/analysis/set_expression_levels.csv`.

## C — Confounders (first-class, not footnotes)  — `src/analysis/c_confounders.py` → results/figures/confounders/
> **CRITICAL METHODS NOTE (found 2026-06-22):** the count matrix the whole pipeline scores on
> (`counts.npz`) is the **SCT-corrected (SCTransform) assay**, not raw counts — `corr(matrix_total,
> nCount_SCT) = 1.000` exactly (per-cell totals ~3–5.7k), whereas raw `nCount_RNA` spans 935–49,854.
> Implication: **depth is already largely regularized at the source**, so the main result is not built
> on raw-depth-confounded data. The C2 "depth" intervention thins these SCT-corrected counts (so the
> targets are on the SCT scale, not raw UMI) — a valid sensitivity test on the corrected scale. This
> belongs prominently in F (methods).
- [x] **C1** **Cell count**: strength-vs-n_cells (confounded by stage); **common-N=200 intervention** →
  H1 trend −0.612 → **−0.586** (survives). `c1_cellcount_vs_strength.png`, `c1_commonN_h1.png`.
- [x] **C2** **Sequencing depth** (the key control — DONE as an INTERVENTION, not a correlation):
  thin all cells to a common depth + re-score → H1 trend −0.612 → **−0.617 (survives)**; within-donor
  depth-response curve shows depth causally attenuates anti-corr (donor 6: −0.55→−0.33). The earlier
  correlation was only an indicator; the intervention is the proof. `c2_depth_paired.png`,
  `c2_depth_response.png`, `c2_depth_control.csv`.
- [x] **C3** **Level vs slope (confounder genes)** (`c3_level_vs_slope.py`): pericentral genes cluster in TURN-OFF (14/26 lost level+slope, CYP2E1 dLevel -1.21); periportal 22/23 stable -> turn-off primary, de-zonation secondary.: per H2 gene, report mean-expression-change beside
  slope-change. Slope lost + mean kept = real de-zonation; both lost = turn-off. _(still TODO)_
- [x] **C4** **UMI-colored scatter**: end-stage PC/PP colored by per-cell UMI — high-UMI tercile
  anticorr +0.33 vs low-UMI +0.24, i.e. best-sequenced cells are NOT more anti-correlated → the blob
  is real biology, not a depth artifact. `c4_endstage_umi_scatter.png`.

## D — Higher-resolution staging
- [x] **D1** (`d_staging.py`) zonation strength declines with fibrosis F0->F4 (rho=-0.49, p=4.4e-4), tracks FIBROSIS specifically (partial -0.40 vs NAS -0.12); within-NASH F1-F3 flat. Re-run H1/H2 along **fibrosis F0-F4** and **NAS 0-8**; split "NASH no-cirrhosis"
  (27 donors) into F1/F2/F3. Ask: does zonation track fibrosis specifically, activity, or both?
  (cell-count caveat front and center, given finer strata).

## E — Interpret the LEARNED (PCA) ruler  [added per professor Q]
What did the PCA actually pick, and does it mean biology?
- [x] **E** (`e_pca_interpretation.py`): PC1 IS zonation (|corr|=0.76 curated coord, 0.54 markers, 5.8% var); loadings real (PP: CRP/SAA1/SAA2/FGL1; PC: ADH4/AKR1D1); depth on PC2 not PC1 -> learned ruler is genuine biology.
- [x] **E1** Variance explained per PC (scree); which PC was selected as the zonation axis and how
  strongly it aligns with the marker axis (|corr|).
- [ ] **E2** Top +/− loading genes on the zonation PC — do they read as real pericentral (GLUL, CYPs,
  SLCO1B3…) vs periportal (ASS1, ALDOB, fibrinogens…) biology? Tabulate.
- [ ] **E3** What the OTHER top PCs capture: correlate PC1/PC2/PC3 scores with total UMI/depth,
  n_genes, %mito — is the leading axis zonation or a technical/quality factor? PC1–PC2 map colored by
  zonation coordinate AND by depth.
  (Reconstruct on Paper-1 healthy hepatocytes via HVG PCA — self-contained with `counts.npz`. Mirrors
  the `unsupervised` ruler; the atlas-fit `unsupervised_p2` follows the same logic in step4c.)

## F — Biology Findings report (PDF)  [added per professor Q]
- [x] **F1** DONE: `src/reports/make_biology_findings.py` -> `results/reports/Zonation_Biology_Findings.pdf` (9 pages, every figure-citing claim shows the figure with the key region CIRCLED; exact numbers; honest-caveats section). A dedicated "Biology Findings" PDF: the H1/H2 mechanism story with **exact numbers**
  (n donors/cells per stage & fibrosis, how many plots, how each was analyzed), the representative
  figures embedded, the confounder controls (C) stated, and honest caveats. Build AFTER C lands so the
  numbers are control-checked, not provisional.

---

## Infrastructure / organization
- [x] Organized result dirs in `config.py`: `results/reports/` (PDFs), `results/figures/{h1,h2,
  confounders,staging}/`, `results/tables/analysis/`.
- [x] Moved PDFs → `results/reports/`; report generators point there (config.REPORTS; absolute figure
  paths fixed for the new cwd).
- [x] `src/analysis/` package: `common.py` (coordinates, clinical metadata, raw program expression,
  per-donor summary, representative selection, staging axes), modules `a1_scatter`/`a2_distributions`/
  `a4_mechanism`/`b4_set_levels`, `run_analysis.py` orchestrator (`python src/analysis/run_analysis.py`).

## Repo map (target)
```
src/
  steps/        pipeline (load→score→validate→collapse→DE→plasticity)   [unchanged]
  plotting/     shared battery plotting                                 [unchanged]
  prep/         one-time data conversions                               [unchanged]
  analysis/     NEW biology deep-dive (A/B/C/D); imports analysis/common.py
  make_*.py, summarize_*, build_candidate_sets, ...  battery orchestration + reports
results/
  reports/      PDFs (Narrative, Ruler dossier, Methods explainer, ...)
  figures/      battery figures (root) + h1/ h2/ confounders/ staging/  (analysis)
  tables/       per-set battery tables + analysis/  (per-donor summaries, mechanism calls)
```

## Done earlier this session (context)
- [x] H2 explicit interaction OLS (`expr ~ coord + stage + coord:stage`, donor cluster-robust).
- [x] Leakage-clean eligibility + two co-primary rulers (`expanded_curated` + `unsupervised_p2`).
- [x] Methods companion PDF (normalization, PCA, validation, quality score, spread/IQR, coherence,
  ρ, perm-p, slope-loss held-out).
