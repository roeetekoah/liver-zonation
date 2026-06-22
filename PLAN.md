# PLAN — mechanism-first, confounder-first reset

_Created 2026-06-22 after the professor consultation. Supersedes the previous plans, now archived in
`archive/plans/` (`PLAN_2026-06-22_show-real-biology.md`, `CONFOUNDERS_PLAN_2026-06-22.md`). Read those
only for history — do not act on them._

---

## 0. Why this plan exists (the critique, taken seriously)

The previous phase **improved the summary statistics but kept the wrong working method**: pick a metric
reflexively, plot many graphs on inconsistent axes, then look for "something." The professor's session
exposed that this is not science. Concretely:

1. **Metrics/scales were chosen by default, not by argument.** Heatmaps z-score (who says z is the
   interpretable scale?); the "raw" view uses **mean expression** instead of a **fold-change scale**
   (`log2(x) − median(log2 x)` or comparable). Result: phantom uniformly-coloured rows we cannot
   attribute to signal vs scaling. _(Confirmed in code: `b1_heatmap.py` z-scores each gene against its
   own within-panel SD — a silenced gene divided by a tiny SD becomes flat-0 or amplified noise; and the
   "LEVEL" view is raw mean log1p-CP10k on an arbitrary 1–99 pct magma scale with no biological zero.)_
2. **"Zonation kept" (B2 boxplots) was asserted, not stressed.** Class imbalance and **cell counts** are
   never shown, yet medians/means over cells are taken and a caption already declares the spread is
   "genuine heterogeneity, NOT noise." _(Confirmed: `b2_zone_boxplots.py` uses global terciles, no
   per-donor-zone cell-count floor, counts never reported.)_
3. **We never interrogated the cohort.** How does Paper 1 define each stage / "end-stage"? Is staging
   **confounded with batch / run-order / tissue source** (explant vs biopsy)? If the paper is silent, the
   raw metadata must answer it.
4. **Staging rulers are incomplete.** NAS components are in the metadata but NAS is not used as an axis
   alongside coarse stage and fibrosis F0–F4.
5. **Views are redundant/confusing.** B1's "level vs raw vs vs-healthy" trichotomy teaches nothing
   crisp — three encodings of overlapping content.

**The governing principle for everything below:** _a summary statistic is an indicator; a deliberately
chosen metric on confounder-controlled data, with N shown, is evidence._ We do **fewer** analyses, each
**pre-committed**: question → metric (+ justification) → confounder it kills → falsification rule. No new
figure ships without all four.

**Non-negotiables carried forward (unchanged):** unit of inference = **donor (~47)**, never the cell. The
scored matrix is **SCT-corrected** (`counts.npz` == `nCount_SCT`); raw `nCount_RNA`/`nFeature_RNA`/
`%mt` ARE in `data/processed/paper1/metadata_all_cells.csv` (verified) and are usable for the quality
check even though the raw RNA *count matrix* was not extracted.

---

## The current scientific claim (what we are testing, sharply)

> In MASLD progression, the **pericentral hepatocyte program is transcriptionally silenced (level
> turn-off)**, strongest at fibrosis **F4 / end-stage**; the **periportal program holds its level**; the
> **zonation gradient (spatial pattern) is largely retained until late**; and the "collapse" indicators
> (spread / IQR / anti-correlation) are **downstream consequences** of the turn-off, not the result.

Three mechanisms compete for "zonation weakens," and they are **distinguishable per gene** by a 2-D
readout — change in **LEVEL** vs change in **SLOPE** (vs the healthy reference):

| mechanism            | ΔLevel (vs healthy) | ΔSlope (zonal gradient) |
|----------------------|---------------------|-------------------------|
| **turn-off**         | strongly negative   | toward 0 (numerator gone) |
| **de-zonation**      | ~0 (level retained) | toward 0                |
| **noise / dropout**  | ~0 or down          | sign unstable, scatter ↑ |

This ΔLevel×ΔSlope plane is the **discriminator** and becomes the centerpiece (M4). Everything else
either feeds it a trustworthy metric (M0, M3), removes a confound from it (M1, M2, M5), or asks what it
tracks (M6).

---

## M0 — Metric charter (DO THIS FIRST; it gates all figures)

Write `src/analysis/metrics.py` + a one-page `METRICS.md` fixing the canonical choices, with the
argument for each. No headline figure may deviate without recording why.

- **Expression unit = donor pseudobulk.** Per (donor, gene): mean CP10k across that donor's cells, then
  `log2(mean_CP10k + 1)`. Donors weighted equally downstream (never cells).
- **Headline scale = log2 fold-change vs healthy reference**, anchored at 0:
  `Δlevel(g, donor) = log2pb(g, donor) − median_over_healthy_donors[ log2pb(g, ·) ]`.
  0 = healthy level, negative = turn-off. This is the professor's fold-change scale; it makes a "phantom
  uniform row" interpretable (a gene flat at Δ≈0 = unchanged; flat at Δ≪0 = turned off — no ambiguity).
- **Zonation slope = OLS of per-cell expression on the zonation coordinate, within donor** (or per-donor
  coord-bin pseudobulk to de-weight dense bins). `Δslope = slope_disease − slope_healthy`. Report the
  slope value, never a within-panel z.
- **Z-scoring is banned from headline figures.** If a "shape only" view is ever needed, it is secondary,
  explicitly labelled, and **applied only to genes above a level floor** so silenced genes are masked/
  greyed, not phantom-coloured.
- **Every estimate carries its N** (donors; and cells-per-donor-per-stratum). Figures print N; tables
  have an `n_cells`/`n_donors` column.
- **Falsification stance per analysis is written before running it.**

Deliverable: `METRICS.md`, `metrics.py`. _Output of M0 is a contract, not a plot._

---

## M1 — Interrogate the cohort & kill the batch/quality confound (#3)

The most dangerous alternative explanation for "global pericentral turn-off at end-stage" is that
end-stage tissue is simply **lower quality / a different batch / a different tissue source** (cirrhotic
explants vs needle biopsies). Settle this before believing the biology.

- **M1a — Read Paper 1's methods for the staging definition.** What is "end-stage"? Explant vs biopsy?
  How were donors assigned to stages? Capture verbatim into `COHORT_NOTES.md`. If the paper is silent on
  randomization/order, the metadata must answer it (next).
- **M1b — Provenance cross-tabs.** From metadata: stage × `manuscript.expt`, stage × `orig.ident`,
  stage × `Lobe`, stage × `Gender`/`Age`/`BMI`/diabetes. Is any stage confined to one experiment/lobe?
  Is `orig.ident` ordering correlated with stage (run-order confound)? Table + heatmap of the cross-tabs.
- **M1c — Quality-by-stage.** Per-donor distributions of raw `nCount_RNA`, `nFeature_RNA`, `%mt.RNA`,
  `%rp.RNA` vs stage and fibrosis. Does end-stage have systematically fewer genes / higher mito? Quantify
  (this is the raw-depth/quality check the SCT scale hides).
- **Falsification:** if stage is fully confounded with experiment, or end-stage quality collapses, the
  turn-off claim is *unproven* until M5c (covariate adjustment) and the negative-control genes (M5a)
  clear it. Report honestly either way.

Deliverable: `COHORT_NOTES.md` + `src/analysis/m1_cohort_provenance.py` →
`results/figures/cohort/` + `results/tables/analysis/cohort_provenance.csv`. **Verdict line** stating
whether batch/order/quality is or is not confounded with stage.

---

## M2 — Cell-count audit; rebuild the zone story on it (#2)

Make cell counts a first-class object, then decide whether the B2 "zonation kept" claim survives.

- **M2a — Count tables.** Cells per donor; per donor × stage; per donor × zone (terciles); per donor ×
  fibrosis. Show the imbalance explicitly (bar/strip with the numbers). Healthy has 4 donors; end-stage 5
  — surface every such floor.
- **M2b — Does the zone estimate depend on N?** For B2's per-donor-zone means: plot the estimate vs the
  number of cells behind it; impose a **min-cells-per-zone floor** (e.g. ≥20) and re-issue; add a
  **downsample-to-common-N** sensitivity (equal cells per donor-zone). If the "PC zone holds in early
  stages / widens at end-stage" pattern changes when N is floored/matched, the original was a count
  artifact.
- **M2c — Weighting.** Confirm donor-equal weighting (mean of donor means), not cell-pooled. State it.
- **Replace B2's asserted caption** ("widening = genuine heterogeneity, NOT noise") with the *result* of
  M2b — show it, don't claim it.

Deliverable: `src/analysis/m2_cell_counts.py` → `results/figures/counts/`,
`results/tables/analysis/cell_counts.csv`; a revised B2 that prints N per box and includes the
floored/common-N sensitivity panel.

---

## M3 — Fix B1: one honest metric, no phantom rows (#1, #5)

Retire the level/raw/vs-healthy trichotomy. Two panels, each with a stated claim:

- **LEVEL panel — turn-off.** Per gene (rows, fixed healthy-slope order) × stage/fibrosis (panels):
  **Δlevel = log2FC vs healthy** (M0), diverging colormap centered at 0 (blue below, red above). A
  pericentral row going uniformly blue = unambiguous turn-off; a uniform row near 0 = unchanged. No
  arbitrary magma zero.
- **PATTERN panel — de-zonation.** Per gene × stage: the **zonal slope value** (M0), diverging at 0,
  **with a level floor**: genes whose Δlevel is below the turn-off threshold are greyed out (slope of a
  silenced gene is meaningless — this is what produced the phantom rows). The viewer sees de-zonation
  only where there is still expression to be zonated.
- Drop the z-vs-healthy panel entirely (it conflates level and pattern — the thing we are separating).
- Keep the cell-level binning for the *picture*, but annotate cells-per-bin and mask bins below floor.

Deliverable: rewrite `src/analysis/b1_heatmap.py` (or `m3_zonation_heatmaps.py`) →
`results/figures/h2/`. Each figure title states exactly what it proves and what would refute it.

---

## M4 — Centerpiece: the ΔLevel × ΔSlope plane, confounder-clean (mechanism)

Promote `c3_level_vs_slope.py` from a footnote to **the** mechanism figure, on the M0 metric.

- Per signature gene: scatter **Δslope (x) vs Δlevel (y)** vs healthy, faceted/animated across stage and
  fibrosis. Quadrants are pre-labelled with the mechanism table above. Pericentral vs periportal genes
  coloured distinctly.
- **Overlay negative-control housekeeping genes (M5a) on the same axes** — they must sit at the origin.
  This embeds the technical control *inside* the mechanism plot.
- **Decision rule (pre-registered):** the claim "turn-off dominant, de-zonation secondary" holds iff
  pericentral genes move predominantly into the **down-level / slope-toward-0** quadrant while periportal
  genes stay near the origin, *and* housekeeping genes stay at the origin.

Deliverable: `src/analysis/m4_level_slope_plane.py` → `results/figures/h2/`, a per-gene table with
Δlevel, Δslope, quadrant, N.

---

## M5 — Confounder kill-shots (orthogonal, each decisive)

Only controls that test the **dominant (level) signal** — not spread/IQR/anti-corr (those were the prior
plan's mistake). Each is a single sharp test.

- **M5a — Negative & positive control genes.** Housekeeping (ACTB, GAPDH, B2M, …) and known
  zone-invariant genes on the **same Δlevel metric**: they must show **no** stage trend. If they turn off
  too → the effect is normalization/quality, not biology. **This is the decisive technical-vs-biology
  test.** (Also overlaid in M4.)
- **M5b — Purity / contamination.** In disease, "hepatocyte" nuclei may be diluted by immune/cholangiocyte/
  doublet contamination, mimicking turn-off. Check per-stage marker purity (ALB high; PTPRC/EPCAM low);
  re-run the Δlevel test on high-purity cells only. Does turn-off survive?
- **M5c — Technical-covariate adjustment.** Regress per-donor pericentral Δlevel on `nFeature_RNA`,
  `%mt`, (and M1's batch) **before** the stage test. Does the stage effect survive adjustment?
- **M5d — Permutation null on LEVEL.** Shuffle donor→stage labels (≥1000×); the observed pericentral
  Δlevel trend should sit far in the tail. (We did this for H1 spread; do it for level.)

Deliverable: `src/analysis/m5_confounders.py` → `results/figures/confounders/`,
`results/tables/analysis/confounder_controls.csv`. A verdict line per control.

---

## M6 — Staging rulers done right (#4)

Run the **single core metric** (pericentral Δlevel, and Δslope) against **all** disease axes, to ask what
the turn-off tracks.

- Axes: coarse **stage**, **fibrosis F0–F4**, **NAS 0–8** (= Steatosis + Ballooning + Inflammation, all
  in metadata), and **SAF**.
- **Partial correlations**: turn-off vs fibrosis controlling for NAS, and vs NAS controlling for fibrosis
  — is it fibrosis-specific, activity-driven, or both? (Earlier hint: fibrosis-specific, partial −0.40 vs
  NAS −0.12 — re-confirm on the clean metric.)
- Cell-count caveat (M2) printed per stratum, especially the finer NAS/fibrosis bins.

Deliverable: `src/analysis/m6_staging_axes.py` → `results/figures/staging/`,
`results/tables/analysis/staging_axes.csv`.

---

## M7 — Integrate into ONE narrative (the deliverable)

Not "tons of graphs" — a **minimal, ordered figure set**, each panel: a named question, the justified
metric, N shown, the confounder it survived. Rebuild `Zonation_Story.pdf` from M1–M6 only after the
controls land, so every number is control-checked. Arc:

1. Cohort is sound (or: here is the confound and how we adjusted) — M1.
2. Counts are imbalanced; here is how we handle it — M2.
3. Turn-off, on a fold-change scale, with N — M3 LEVEL + M4.
4. It is biology, not technical — M5 (controls), housekeeping at origin.
5. Pattern (de-zonation) is weak/late where measurable — M3 PATTERN.
6. It tracks fibrosis specifically — M6.
7. Honest caveats — small healthy n, end-stage heterogeneity, SCT scale.

---

## Sequencing & gates

```
M0 (metric charter) ─┬─> M1 (cohort/batch)  ─┐
                     ├─> M2 (cell counts)    ─┤
                     └─> M3 (B1 fix) ─> M4 (level×slope) ─> M5 (controls) ─┬─> M7
                                                            M6 (staging) ──┘
```

- **M0 is a hard gate** — nothing plots until the metric charter exists.
- **M1 + M2 gate belief**: if either finds an unhandled confound, M4's claim is provisional until M5
  clears it; say so in M7.
- **M4 is the centerpiece**; M5a (housekeeping) overlaid inside it.
- Ship M7 last, never provisional.

## What we explicitly will NOT do
- No new z-scored headline figures. No mean-expression-on-arbitrary-scale figures.
- No re-litigating spread / IQR / anti-correlation as the result (they are downstream; keep only as
  labelled "downstream indicator").
- No per-stage figure without cell counts on it.
- No claim ("heterogeneity not noise", "zonation kept") stated in a caption that the figure does not show.

## Pointers
- Archived prior plans: `archive/plans/`. Orientation: `HANDOFF.md`, `RESUME.md` (note: their results
  sections predate this reset — machinery valid, headline is turn-off).
- Verified data facts: NAS components, raw QC fields, batch fields all in
  `data/processed/paper1/metadata_all_cells.csv`.
