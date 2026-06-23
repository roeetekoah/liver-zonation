# signatures/

Pericentral (PC) and periportal (PP) hepatocyte zonation gene sets. One gene symbol per
line, no header. **The primary signature is `full` — the transcriptome-wide zonation
program** — matching the project's core motivation: read each cell's position from the
*whole* program, not from a handful of markers by eye.

| File | What it is | Size (PC / PP) | Role |
|---|---|---|---|
| `*_full.txt` | **Transcriptome-wide program** — every significantly-zonated hepatocyte gene from Paper 2 (q<0.05, well-expressed), present in Paper 1 | **1273 / 364** | **PRIMARY (default)** |
| `*_expanded.txt` | landmark ∪ core ∪ top-ranked | 102 / 91 | mid-size robustness |
| `*_core.txt` | curated, biology-informed anchors (hand-picked) | 13 / 8 | interpretable anchor set |
| `*_paper2_landmark.txt` | the **EXACT** Paper 2 hepatocyte landmark genes, verbatim from `Hepatocyte-{PC,PP}-LM.csv` (the genes Paper 2 uses to assign snRNA zonation) | 20 / 20 | audit baseline |
| `periportal_sensitivity.txt` | core PP minus inflammation gene (HAMP) | – / 7 | acute-phase robustness |
| `plasticity.txt` | cholangiocyte / biphenotypic markers (KRT7, KRT19, SOX9…) | 6 | **different axis** (H3, not zonation) |

## The default is the full program (this is the point of the project)
`config.py` sets `DEFAULT_SET = "full"`, so the pipeline scores the coordinate — and trains
the classifier — on the **~1,637-gene transcriptome-wide zonation program**, not on a
handful of markers. This is the whole motivation ("transcriptome-wide, via an external healthy
reference, not 2–3 markers by eye", primer §3.4). Switch sets in one place:
```python
import config
pc, pp = config.signature_files("full")        # default; or "expanded" / "core" / "paper2_landmark"
```

> **Honest note on the earlier confusion.** When you asked to keep "the EXACT set Paper 2
> used" as a baseline, I over-applied it and made the 20-gene landmark set the *default* —
> which silently contradicted the transcriptome-wide motivation. That is corrected here: the
> **full program is the default/primary**; the landmark set is retained only as a small
> *sanity baseline* to report alongside.

## How `*_full.txt` was built
From `data/raw/2025-01-01424E-s1/supplementary_table_8.xlsx`, sheet **`Hepatocyte`** (Paper 2's
single-nucleus, hepatocyte-specific zonation table — same platform as Paper 1). Keep genes with
**`qValue < 0.05`** and `Max_expression ≥ 90th percentile` (drops snRNA dropout noise), present in
Paper 1; assign each to a side by its **`Center_of_Mass`** along zones 1–8 (zone 1 = pericentral →
low COM; zone 8 = periportal → high COM, verified via CYP2E1/GLUL low vs ASS1/HAL high); sort by
zonation strength. Rebuild: `python src/prep/03_build_signatures.py`. (Table 2, the Visium Fig-2
table, has the same columns — `pValue/qValue/Center_of_Mass` — and can be used instead; we use the
snRNA Table 8 for platform match to Paper 1.)

## Decision: `full` is the result, `paper2_landmark` is the audit
We report **both**, but they are not equal partners — they do different jobs.

**`full` is the primary instrument** (the headline result) for three reasons:
1. *It is the contribution.* The novelty over "look at 3 markers" is reading position from the
   whole program via an external healthy reference. Demoting that loses the point.
2. *It is the more robust ruler in disease.* The coordinate is a **mean** of z-scored genes per
   side, so disease-corruption of any single marker is diluted. A 20-ish-gene ruler is acutely
   exposed: `CYP2E1` (canonical pericentral) is genuinely induced in NASH for oxidative-stress
   reasons unrelated to position, and as 1-of-13 it could swing the axis; as 1-of-~1,600 it cannot.
3. *H2 needs it.* "Which programs collapse?" is unanswerable with ~20 genes, and the circularity
   guard (build the coordinate on a random half of the genes, test collapse on the held-out half,
   repeat K≈20–50×) is only meaningful with hundreds of genes.

**`paper2_landmark` is the credibility control, not a competing answer.** The obvious objection to
a 1,600-gene result is "did you engineer it with enough genes?" The landmark run is the rebuttal:
if a canonical, biologically-named, Paper-2-faithful 13+8 ruler shows the *same* collapse, the
signal is not a gene-set artefact. If the two *disagree*, that is itself a finding (and a warning
the ruler may be disease-sensitive). It is also faithful to Paper 2 and fully interpretable.

So: `config.SETS_TO_COMPARE = ["paper2_landmark", "full"]`, **lead with `full`**, present landmark
alongside. `expanded`/`core` are an optional robustness gradient (the result isn't a knife-edge of
gene count).

**Per hypothesis:** H1 (collapse) + ruler/classifier → `full` primary, `landmark` control;
H2 (which programs) → `full` with the held-out repeated split; H3 (plasticity) → de-zonation
score from `full`.

**Why the original plan said "landmark."** Marker/landmark reconstruction is the field-standard,
validated method — it is exactly what Paper 2 and the foundational liver-zonation work
(Halpern et al. 2017) did. Landmark was the conservative, known-good starting point; `full` is the
deliberate upgrade, not a correction of a mistake.

## The PC/PP imbalance (1273 vs 364) does not bias the coordinate
The `full` set is ~3.5:1 pericentral-heavy. This is a **feature**-set asymmetry, *not* ML "class
imbalance" (which is about label counts, e.g. the classifier's zone terciles). It does **not** tilt
the coordinate, because

```
coord = mean(z of PC genes)  −  mean(z of PP genes)     # each arm is a MEAN, not a sum
```

a mean of 1273 z-scores and a mean of 364 z-scores live on the same per-gene scale, so the count
ratio creates no magnitude bias (the prep script uses `np.mean`). What the imbalance *does* create
is a **precision asymmetry**: the PP arm averages fewer genes, so it is noisier and the periportal
end of the axis is estimated less reliably. Mitigations:
- **Per-arm standardization** — z-score each arm (PC-mean, PP-mean) to unit variance across cells
  *before* subtracting; equalizes the two arms regardless of count. (Cheap; recommended.)
- **Size-matched robustness run** — take the top-364 strongest-zonated PC genes to match the 364 PP
  and confirm the collapse is unchanged.
- **Strength-weighting** — weight each gene by Paper 2 zonation strength (center-of-mass / effect
  size); naturally shrinks the imbalance by down-weighting the long tail of weak PC genes.

The imbalance itself is part real biology (hepatocyte zonation skews pericentral here) and part the
selection thresholds (q<0.05 + p90 expression + center-of-mass split).

## Using the different sets (what the analysis should report)
- **Primary results** use `full`.
- **Robustness:** re-run H1/H2 with `expanded` and `core` and show the collapse is not an
  artefact of the gene set; run H1 with `periportal_sensitivity.txt` to rule out an
  acute-phase confound.
- **Baseline:** `paper2_landmark` reproduces the analysis on exactly Paper 2's anchors.
- The classifier (Step 4b) uses the **same `full` feature genes**. `src/prep/02_convert_paper2_mat.py`
  now caches the **union of all tiers** (~1,700 genes) in `paper2_train.npz`, so any set can be
  sliced from it by gene name — re-run that script once if the cache predates this change.
- **H2 circularity / held-out genes:** because the coordinate is built from these genes, the
  H2 "driver" test must use a **random held-out split** of the gene set, **repeated K≈20–50
  times**, reporting the distribution of the result across splits (a robust signal holds
  across most splits). With the full ~1,640-gene set this is meaningful; it would not be with
  ~20 landmarks. See `src/IMPLEMENTATION_PLAN` Step 7.

## Human-specific note
`PCK2` is **pericentral in humans** (Paper 2); urea-cycle `ASL/OTC/NAGS` are pericentrally
shifted while `ASS1` stays periportal — handled by the data-driven `full`/`expanded` sets and
by the curated `core`.
