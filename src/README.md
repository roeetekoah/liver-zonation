# src/ — code, grouped by analysis leg

All current analysis code. Scripts are grouped into subfolders that map onto the project's **findings**
(see [`../findings/README.md`](../findings/README.md), audited in [`../CLAIMS_LEDGER.md`](../CLAIMS_LEDGER.md)).
Paths are centralised in **`config.py`** — import it, don't hard-code.

> The pre-reanalysis exploration code (the flat `analysis/` figure family, the Step 2–9 `steps/` z-ruler
> pipeline, the signature `battery/`, the `reports/` PDF generators, and `run_everything.py`) is **legacy**
> and has been moved to [`../archive/legacy_src/`](../archive/legacy_src/). A full point-in-time copy of the
> earlier flat `src/` is at `../archive/src_backup_2026-06-23/`. Nothing here imports the archived code.

## The import contract
Every script puts `src/` on `sys.path` and imports `config`:
```python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # -> src/
import config
```
This only resolves to `src/` when a script sits **exactly two levels deep** (`src/<group>/script.py`).
Don't nest deeper/shallower without fixing that line. `plotting/` is an import package (`from plotting import
artefacts`); the rest are script collections run directly (`python src/<group>/<script>.py`).

## Layout
```
src/
├── config.py     central paths (data/, signatures/, results/)
├── prep/         one-time raw -> processed extraction, schema & sanity            [F11]
├── confound/     provenance & confound leg (source/lobe/stress/batch/power/equiv) [F1,F2,F3,F5,F6,F16,F17]
├── census/       count-based anchor classification & scenario taxonomy            [F7,F8,F9,F13,F14]
├── dge/          genome-wide + compositional differential expression              [F15,F18,F20,F21]
├── legacy/       relative-ruler post-mortem (Simpson's-paradox check)             [F12]
└── plotting/     shared plotting machinery + standalone figures                   (figures: F9,F12)
```

## Script → finding map

### `prep/` — extraction, schema, sanity → **F11**
`00_mtx_to_npz.py`, `01_extract_paper1_hepatocytes.R`, `02_convert_paper2_mat.py`, `03_build_signatures.py`,
`04_extract_spatial_reference.py`, `05_extract_raw_panel.R` (raw RNA-assay UMIs for the panel),
`06_sanity_raw.py` (9 sanity checks, **F11**), `07_dump_object_schema.R` (proves RNA counts = RAW ≠ SCT),
`08_extract_paper2_landmark_raw.R`, `09_extract_full_and_union.R`, `10_extract_dge_genes_allcells.R`,
`11_extract_planA_hits_allcells.R` (Plan A hit genes across all cells, for **F18/F21**), `audit_data.py`.

### `confound/` — provenance & confound leg → **F1, F2, F3, F5, F6, F16, F17**
| script | finding | does |
|---|---|---|
| `raw_counts.py` | **F1**, Item 5 | RAW-count donor tables; builds the right-lobe-only primary result |
| `lobe_invariance.py` | **F1** | zonation detection is lobe-invariant (R/C/L) within explants |
| `panel_by_stage.py` | **F2/F3** | right-lobe per-gene × per-stage panel (det2 + depth-matched) |
| `stress_exact.py` | **F2** | exact per-donor per-stress-gene numbers |
| `stress_celltype_segmented.py` | **F5** | cross-lineage stress segmented IEG/HSP/HIF |
| `nas_components_detox.py` | **F6 (QUARANTINED)** | NAS-component ↔ detox test |
| `umi10k_validation.py` | Item 9 | the UMIs/10k denominator worry is empirically minor |
| `mde.py` | F9 power footnote | minimum-detectable-effect table |
| `equivalence_bound.py` | **F16** | affirmative TOST equivalence bound on the PC-anchor fraction |
| `batch_qc.py` | **F17** | sequencing run × stage cross-tab + Cramér's V (batch not randomized) |

### `census/` — anchor classification & scenario taxonomy → **F7, F8, F9, F13, F14**
`census.py` / `census_v2.py` (**F7/F8**, PC/PP/dual/null anchor classification, depth-matched + sensitivity grid),
`census_2d.py` (**F13**, 2D pole-collapse visual), `gapfill.py` (**F9**, scenario coverage),
`load_bearing.py` (**F7/F14**, integrated donor-level table), `all_sets_census.py` (**F8/F9**, marker-set ladder),
`markerset_robustness.py` (**F8**), `review_checks.py` (**F8/F14**, B-sweep), `supplementary_checks.py` (**F5/F8**).

### `dge/` — differential expression → **F15, F18, F20, F21**
| script | finding | does |
|---|---|---|
| `dge_genomewide.py` | **F15** | first genome-wide donor-level DE (pseudobulk, Spearman+BH) |
| `dge_compositional.py` | **F15** | are the F15 trending genes hepatocyte-intrinsic vs compositional |
| `plan_a_genomewide.R` | **F18** | Plan A genome-wide DGE (edgeR pseudobulk, TMM + NB-QL), F4-vs-F1 |
| `plan_a_interior.R` | **F18** | F1→F3 interior contrasts (the well-populated, no-F4 look) |
| `plan_a_batch_sensitivity.R` | **F17/F18** | biliary hits under a run covariate + within a single run |
| `dge_planA_compositional.py` | **F18** | cross-lineage burden audit of the Plan A hits |
| `decontX_replan_a.R` | **F18** | decontX ambient removal, re-pseudobulk, re-test |
| `plan_b_within_class.R` | **F20** | within-zone DGE (PC/PP/null/dual), subordinate robustness check |
| `doublet_chase.py` | **F21** | source-attribution doublet probe (exploratory lead) |

### `legacy/` — relative-ruler post-mortem → **F12**
`legacy_simpson.py` — does the legacy "collapse" have Simpson's-paradox structure (aggregation artefact).

### `plotting/` — shared machinery + standalone figures
`artefacts.py` (plotting helpers), `make_gradient_figure.py` (**F9** gradient-compression figure),
`make_simpson_figure.py` (**F12** Simpson reveal).

## Requirements
```
pip install numpy scipy pandas scikit-learn statsmodels matplotlib h5py openpyxl
```
R side: `Seurat`, `Matrix`, `edgeR`, `celda` (decontX). Each count/DGE script is standalone — run it directly;
it reads the raw panel / pseudobulk via `config`.
