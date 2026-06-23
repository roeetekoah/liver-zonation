# src/ — code, grouped by analysis leg

All analysis code. Scripts are grouped into subfolders that map onto the project's
**findings** (F1–F15 in [`../findings/README.md`](../findings/README.md), audited in
[`../CLAIMS_LEDGER.md`](../CLAIMS_LEDGER.md)). Paths are centralised in **`config.py`** —
import it, don't hard-code.

> Reorganised 2026-06-23. A verified full copy of the previous flat layout is at
> `../archive/src_backup_2026-06-23/`. The reorg **moved/regrouped files only** — no
> analysis logic changed. See "Reorg notes" at the bottom for exactly what moved and why.

## The import contract (read before moving anything)

Every script puts `src/` on `sys.path` with:

```python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # -> src/
import config
```

This `dirname(dirname(__file__))` only resolves to `src/` when the script sits **exactly two
levels deep**: `src/<group>/script.py`. **Do not nest scripts deeper** (e.g.
`src/census/sub/x.py`) or shallower without fixing that line — `import config` will break.

Three folders are **import packages** whose names are load-bearing — other modules do
`from analysis import common`, `from steps.<step> import ...`, `from plotting import artefacts`.
**Do not rename `analysis/`, `steps/`, or `plotting/`, and do not move `analysis/common.py`
out of `analysis/`.** (`run_everything.py` is the one top-level driver and uses a single
`dirname` because it already lives in `src/`.)

## Layout

```
src/
├── config.py              central paths (data/, signatures/, results/)
│
├── prep/                  one-time raw -> processed extraction, schema & sanity   [F11]
├── confound/              provenance & confound leg (source/lobe/stress/NAS/power) [F1,F2,F3,F5,F6,F9]
├── census/                count-based structural census & scenario taxonomy        [F7,F8,F9,F13,F14]
├── dge/                   genome-wide & compositional differential expression       [F15]
├── legacy/                relative-ruler post-mortem (Simpson's-paradox check)      [F12]
│
├── analysis/              figure/exploration family (a*/b*/c*/d*/e*) + common.py    (figures; F3,F8,F9 visuals)
├── plotting/              shared plotting machinery + standalone deck figures       (figures)
├── reports/               report / PDF / methods-explainer generators              (writeups)
│
├── steps/                 modular Step 2-9 pipeline (the legacy z-ruler pipeline)   [feeds F10/F12 context]
├── battery/               signature-set battery + H1/H2 transcriptome-wide eval     [method validation]
└── run_everything.py      top-level driver for the steps/ pipeline
```

`prep/`, `confound/`, `census/`, `dge/`, `legacy/` are **script collections** run directly
(`python src/<group>/<script>.py`); they are not imported, so they carry no `__init__.py`.
`analysis/`, `plotting/`, `steps/`, `battery/` are **packages** (have `__init__.py`) because
their members import each other.

---

## Script -> finding map

### `prep/` — extraction, schema, sanity  → **F11**
| script | does | output |
|---|---|---|
| `00_mtx_to_npz.py` | `counts.mtx` -> `counts.npz` (fast/low-mem load) | `data/processed/.../counts.npz` |
| `01_extract_paper1_hepatocytes.R` | Seurat `.rds` -> Paper 1 hepatocytes + metadata | `data/processed/paper1/` |
| `02_convert_paper2_mat.py` | Paper 2 `.mat` -> train npz (union of tiers) | `data/processed/paper2_train.npz` |
| `03_build_signatures.py` | Paper 2 supp table -> signature gene sets | `signatures/*_full.txt, *_expanded.txt` |
| `04_extract_spatial_reference.py` | extract Paper 2 spatial reference | `data/processed/paper2/` |
| `05_extract_raw_panel.R` | RAW RNA-assay UMIs for the analysis gene panel (per-cell tidy table) | `data/.../raw_panel_counts.csv` |
| `06_sanity_raw.py` | 9 falsifiable sanity checks on the raw extraction | console / sanity log (**F11**) |
| `07_dump_object_schema.R` | authoritative Seurat schema dump; proves RNA counts = RAW (≠ SCT) | schema dump |
| `08_extract_paper2_landmark_raw.R` | RAW UMIs for Paper 2's exact PC/PP landmark genes | landmark raw csv |
| `09_extract_full_and_union.R` | full-transcriptome donor pseudobulk + union panel | pseudobulk / union csv |
| `10_extract_dge_genes_allcells.R` | RAW counts for genome-wide DGE hit genes, all cell types | dge-genes all-cells csv |
| `audit_data.py` | data-foundation audit helper | console |

### `confound/` — provenance & confound leg  → **F1, F2, F3, F5, F6, F9(power)**
| script | finding | does | output (`results/tables/...`) |
|---|---|---|---|
| `raw_counts.py` | **F1**, ledger Item 5 | RAW-count donor-level tables; builds right-lobe-only primary result | `rawA_*.csv`, `rawF_qc_source.csv` |
| `lobe_invariance.py` | **F1** | zonation pattern is lobe-invariant (R/C/L) within explants | `lobe_invariance.csv` |
| `panel_by_stage.py` | **F2/F3** | right-lobe per-gene × per-stage panel (robust det2 + depth-matched rebuild) | `per_group.csv` etc. |
| `stress_exact.py` | **F2** | exact per-donor per-stress-gene numbers (no medians) | `stress_per_donor_alllobe.csv` |
| `stress_celltype_segmented.py` | **F5** | cross-lineage stress segmented IEG/HSP/HIF per gene | `per_donor.csv`, `by_lineage.csv` |
| `nas_components_detox.py` | **F6 (QUARANTINED)** | NAS-component ↔ detox cytokine-suppression test | nas/detox csv |
| `umi10k_validation.py` | ledger Item 9 | shows the UMIs/10k denominator worry is empirically minor | console / csv |
| `mde.py` | **F9 power footnote** | minimum-detectable-effect table (the power bound) | mde csv |

### `census/` — count-based structural census & scenario taxonomy  → **F7, F8, F9, F13, F14**
| script | finding | does |
|---|---|---|
| `census.py` | **F7/F8** | PC/PP/dual/null anchor census on RAW counts, depth-matched + sensitivity grid |
| `census_2d.py` | **F13** | 2D joint distribution of PC-program vs PP-program (pole-collapse visual) |
| `census_v2.py` | **F8** | hardened census/polarization (multi-draw depth-matching) |
| `gapfill.py` | **F9** | gap-fillers for complete H1 scenario coverage (count-based, donor=unit) |
| `load_bearing.py` | **F7, F14**, ledger Item 8 | load-bearing donor-level absolute-count census (the integrated table) |
| `all_sets_census.py` | **F8/F9** | is the F0–F4 biopsy null invariant across the whole curated marker breadth |
| `markerset_robustness.py` | **F8** | is the null invariant to which zonation gene set is used |
| `review_checks.py` | **F8/F14**, ledger N2 | post-review count checks; B-sweep {1000,1500,3000} for co-expression |
| `supplementary_checks.py` | **F5/F8** | supplementary committed checks (cross-lineage stress + HIF ratios, etc.) |

### `dge/` — differential expression  → **F15**
| script | finding | does |
|---|---|---|
| `dge_genomewide.py` | **F15** | genome-wide donor-level DE across biopsy F0–F4 (pseudobulk, Spearman+BH-FDR) |
| `dge_compositional.py` | **F15** | are the genome-wide fibrosis-trending genes hepatocyte-intrinsic vs compositional |

### `legacy/` — relative-ruler post-mortem  → **F12**
| script | finding | does |
|---|---|---|
| `legacy_simpson.py` | **F12** | does the legacy "de-zonation collapse" have Simpson's-paradox structure (aggregation artefact) |

### `analysis/` — figure / exploration family (kept together; depends on `analysis/common.py`)
Run via `analysis/run_analysis.py [signature_set]`, which launches each as a subprocess.
These read precomputed coordinate tables under `results/tables/<signature_set>/` (produced by
the `steps/`/battery track) — they need that upstream run to exist before they plot.
| script | does | artefact |
|---|---|---|
| `common.py` | shared loaders/helpers for the figure family (imported as `analysis.common`) | — |
| `a1_scatter.py` | PC/PP scatter (contact sheet + reps) | A1 |
| `a2_distributions.py` | per-patient coordinate distributions | A2 |
| `a3_marker_profiles.py` | marker zonation profiles | A3 |
| `a4_mechanism.py` | per-donor mechanism quantification | A4 |
| `b1_heatmap.py` | gene × cell heatmap (centerpiece) | B1 |
| `b2_zone_boxplots.py` | zone × program boxplots | B2 |
| `b3_program_vs_coord.py` | program-arm expression vs coordinate | B3 |
| `b4_set_levels.py` | per-set expression level vs stage/fibrosis | B4 |
| `c3_level_vs_slope.py` | level vs slope per gene | C3 |
| `d_staging.py` | fibrosis / NAS higher-resolution staging | D |
| `e_pca_interpretation.py` | interpret the learned PCA ruler | E |
| `run_analysis.py` | driver: runs the above as subprocesses | all A/B/C/D/E figures |

### `plotting/` — shared plotting machinery + standalone deck figures
| script | does |
|---|---|
| `artefacts.py` | premade plotting functions (imported by `steps/` as `plotting.artefacts`) |
| `make_gradient_figure.py` | per-cell zonal-balance distribution by stage (gradient-compression test, **F9**) |
| `make_simpson_figure.py` | Simpson-paradox reveal figure (**F12** visual) |

### `reports/` — report / PDF generators (writeups, not new science)
`make_zonation_story.py` (arc-driven professor report), `make_methods_explainer.py`
(stand-alone methods companion PDF), `make_narrative_report.py`, `make_latex_report.py`,
`make_report_pdf.py`.

### `steps/` + `battery/` + `run_everything.py` — the legacy z-ruler pipeline & method battery
The modular **Step 2–9** pipeline (load/QC → harmonize → score → classify → validate → ruler
diagnostics → collapse → DE → plasticity) and the signature-set **battery** (H1 spread / H2
slope-loss / transcriptome-wide eval, unsupervised-axis agreement). This is the **relative
z-ruler** track that the count census later replaced (see **F12**); it also supplies the
learned-coordinate tables the `analysis/` figures consume, and the method-validation context
behind **F10**. `run_everything.py` is its top-level driver; `battery/run_explicit_signature_battery.py`
runs the frozen battery.

---

## Run order (unchanged by the reorg)

```bash
# Step 1 (prep) — once per machine, needs raw data:
Rscript src/prep/01_extract_paper1_hepatocytes.R
python  src/prep/00_mtx_to_npz.py
python  src/prep/02_convert_paper2_mat.py
python  src/prep/03_build_signatures.py
Rscript src/prep/05_extract_raw_panel.R        # raw panel for the count analyses
python  src/prep/06_sanity_raw.py              # 9/9 sanity checks (F11)

# the count-based findings (each is standalone, reads the raw panel via config):
python  src/confound/raw_counts.py
python  src/census/census.py
python  src/dge/dge_genomewide.py
python  src/legacy/legacy_simpson.py
# ...and the rest of confound/ census/ dge/ as needed.

# the legacy z-ruler pipeline + figures:
python  src/run_everything.py                  # steps 2-9 -> results/tables/<set>/
python  src/analysis/run_analysis.py           # A/B/C/D/E figures (needs the run above)
```

## Requirements
```
pip install numpy scipy pandas scikit-learn statsmodels matplotlib h5py openpyxl
```
R side: `Seurat`, `Matrix`.

---

## Reorg notes (2026-06-23) — what moved, what didn't

**Moved** (out of the old flat `analysis/`, into themed sibling folders, all still 2 levels
deep so `import config` is unaffected — verified by running them):
- → `confound/`: raw_counts, lobe_invariance, panel_by_stage, stress_exact,
  stress_celltype_segmented, nas_components_detox, umi10k_validation, mde
- → `census/`: census, census_2d, census_v2, gapfill, load_bearing, all_sets_census,
  markerset_robustness, review_checks, supplementary_checks
- → `dge/`: dge_genomewide, dge_compositional
- → `legacy/`: legacy_simpson

**Left in place on purpose:**
- `analysis/` keeps the **figure family** (`a*/b*/c*/d*/e*`, `run_analysis.py`) and
  `common.py`, because those scripts do `from analysis import common` — the package name and
  `common.py`'s location are load-bearing.
- `prep/`, `plotting/`, `steps/`, `battery/`, `reports/`, `run_everything.py` were already
  cleanly grouped and/or are import packages; left untouched.

**No import-path edits were needed:** because every script was moved to another 2-levels-deep
location, the existing `dirname(dirname(__file__))` line keeps resolving to `src/`, and the
package imports (`from analysis import common`, `from steps.* import`, `from plotting import
artefacts`) resolve against `src/` on `sys.path` regardless of the importer's own folder. This
was verified empirically before and after the move.
