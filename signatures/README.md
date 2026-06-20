# signatures/

Pericentral (PC) and periportal (PP) hepatocyte zonation gene sets. One gene symbol per
line, no header. **The primary signature is `full` — the transcriptome-wide zonation
program** — matching the project's core motivation: read each cell's position from the
*whole* program, not from a handful of markers by eye.

| File | What it is | Size (PC / PP) | Role |
|---|---|---|---|
| `*_full.txt` | **Transcriptome-wide program** — every significantly-zonated hepatocyte gene from Paper 2 (q<0.05, well-expressed), present in Paper 1 | **1273 / 364** | **PRIMARY (default)** |
| `*_expanded.txt` | landmark ∪ core ∪ top-ranked | 102 / 91 | mid-size robustness |
| `*_core.txt` | curated, biology-informed anchors | 13 / 8 | interpretable anchor set |
| `*_paper2_landmark.txt` | the EXACT Paper 2 landmark set (verbatim) | 20 / 20 | sanity baseline |
| `periportal_sensitivity.txt` | core PP minus inflammation gene (HAMP) | – / 7 | acute-phase robustness |
| `plasticity.txt` | cholangiocyte / biphenotypic markers (KRT7, KRT19, SOX9…) | 6 | **different axis** (H3, not zonation) |

## The default is the full program (this is the point of the project)
`config.py` sets `DEFAULT_SET = "full"`, so the pipeline scores the coordinate — and trains
the classifier — on the **~1,637-gene transcriptome-wide zonation program**, not on 20
markers. This is the whole motivation ("transcriptome-wide, via an external healthy
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

## Decision: report BOTH as a comparison
The analysis runs every result **both ways** — with the exact Paper 2 `paper2_landmark` set
(faithful to the original landmark/marker-based plan) **and** the `full` transcriptome-wide set —
and presents them side by side (`config.SETS_TO_COMPARE = ["paper2_landmark", "full"]`). Agreement
between the faithful baseline and the transcriptome-wide program is itself evidence the de-zonation
signal is robust, not an artefact of how many genes we chose.

## Using the different sets (what the analysis should report)
- **Primary results** use `full`.
- **Robustness:** re-run H1/H2 with `expanded` and `core` and show the collapse is not an
  artefact of the gene set; run H1 with `periportal_sensitivity.txt` to rule out an
  acute-phase confound.
- **Baseline:** `paper2_landmark` reproduces the analysis on exactly Paper 2's anchors.
- The classifier (Step 4b) uses the **same `full` feature genes**; `paper2_train.npz`
  currently stores only the 40 landmark features and must be rebuilt with the full feature
  set for the transcriptome-wide classifier (see `src/prep/02_convert_paper2_mat.py`).
- **H2 circularity / held-out genes:** because the coordinate is built from these genes, the
  H2 "driver" test must use a **random held-out split** of the gene set, **repeated K≈20–50
  times**, reporting the distribution of the result across splits (a robust signal holds
  across most splits). With the full ~1,640-gene set this is meaningful; it would not be with
  20 landmarks. See `src/IMPLEMENTATION_PLAN` Step 7.

## Human-specific note
`PCK2` is **pericentral in humans** (Paper 2); urea-cycle `ASL/OTC/NAGS` are pericentrally
shifted while `ASS1` stays periportal — handled by the data-driven `full`/`expanded` sets and
by the curated `core`.
