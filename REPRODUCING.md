# Reproducing LiZARD

The repository supports two levels of review:

1. **Inspect the committed evidence.** The small donor-level and per-gene tables in `results/tables/analysis/` are versioned with the code.
2. **Rerun the bounded headline route.** Prepare the large inputs locally, then use `scripts/run_verified.py` to build into a new output directory with logs and a hash manifest.

## Tested environment

- Python 3.13.12 with the versions pinned in `requirements.txt`.
- R 4.4.3 with the versions recorded in `R-packages.txt`.
- The verified route uses SeuratObject, Matrix, edgeR and limma. `celda` is needed only for the optional decontX rerun.

Install Python dependencies in an isolated environment:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Install the listed R/Bioconductor packages using the package managers appropriate to your R installation.

## Prepare the data

Run from the repository root:

```bash
bash scripts/download_data.sh
Rscript src/prep/01_extract_paper1_hepatocytes.R
Rscript src/prep/05_extract_raw_panel.R
Rscript src/prep/09_extract_full_and_union.R
python src/prep/00_mtx_to_npz.py
python src/prep/06_sanity_raw.py
```

The extraction scripts explicitly select the Seurat `RNA` assay. The historical default-assay extraction produced an SCT matrix and remains useful only for the explicit RNA-versus-SCT sanity check.

Large data can live outside the checkout. Set `LIVER_ZONATION_DATA_ROOT` to a directory containing `raw/` and `processed/`, or pass that directory to the verified runner.

## Run into a fresh output directory

```bash
python scripts/run_verified.py \
  --data-root /path/to/liver-zonation-data \
  --output-root /path/to/new-empty-output
```

The output directory must be empty. This prevents an old figure or table from surviving a partial run. The runner executes:

1. raw-count validation;
2. batch/source inventory;
3. deterministic eight-draw donor metrics;
4. confidence intervals and fixed-margin equivalence checks;
5. minimum-detectable-effect summaries;
6. genome-wide trend and Plan A F4-versus-F1 models;
7. CAMERA and mROAST gene-set checks;
8. the independent within-PC detox measure.

Every command writes a log. `run-manifest.json` records the Git revision, dirty-state flag, input SHA-256 hashes, commands, exit codes and output hashes.

## What the verified route does not run

- `src/dge/decontX_replan_a.R` is optional and computationally heavier. It re-estimates ambient RNA and reruns per-gene Plan A; it does not test the CYP gene set.
- Presentation and report builds are release tasks, separate from analysis verification.
- Historical SCT-based and exploratory routes are not prerequisites for the current claims.

## Determinism

`src/thinning.py` assigns each gene an independent pseudo-random stream derived from the draw number and gene name. The same gene therefore receives the same draw regardless of Python hash order or which other genes a script requests. Headline donor metrics average eight fixed draws.
