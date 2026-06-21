# PREP_LOG — advance prep for the 2-day hackathon

Scope of this log: **environment + data caching + a RUN-only smoke test**, done ahead of the
hackathon so day 1 isn't lost to downloads/parsing/deps. **No analysis, no result numbers.**
The science (validation gate, classifier+entropy, H1/H2/H3, plotting, interpretation) is the
live work. Date of prep run: 2026-06-21.

## Environment

**OS:** Windows 11 Pro (10.0.26200). Shells: PowerShell + Git-Bash.

**Python:** 3.13.13 (`C:\Python313\python`)

| package | version |
|---|---|
| numpy | 2.4.4 |
| scipy | 1.17.1 |
| pandas | 3.0.2 |
| scikit-learn | 1.8.0 |
| statsmodels | 0.14.6 |
| matplotlib | 3.10.9 |
| h5py | 3.16.0 |
| openpyxl | 3.1.5 |
| psutil | 7.2.2 |

> `openpyxl` was the only missing package — installed via `pip` (pulled `et-xmlfile 2.0.0`).
> `psutil` used only for peak-memory measurement in the smoke test.

**R:** 4.4.3 (`C:\Program Files\R\R-4.4.3\bin\x64\Rscript`)

| package | version |
|---|---|
| Seurat | 5.5.0 |
| Matrix | 1.7.2 |

**Import check:** `cd src && python -c "import pipeline"` → OK.

## Data caches (all present in `data/processed/`)

| artifact | status | notes |
|---|---|---|
| `paper1/{counts.mtx, genes.txt, barcodes.txt, cell_metadata.csv, metadata_all_cells.csv}` | present | from `01_extract_paper1_hepatocytes.R` (already run); 30117 genes × 69426 hepatocytes |
| `paper1/counts.npz` | **built this prep** | `00_mtx_to_npz.py`; shape (30117, 69426), nnz 169,877,876; **347 MB; built in 58 s** |
| `paper2_train.npz` | present + verified | `02_convert_paper2_mat.py` (already run). Verified: **X = (50979, 1721)** features (~1,700 ✓, the union — not just the 40 landmarks), zone classes balanced **{0:16993, 1:16993, 2:16993}**, donors `M5 M6 M7 M8`. No rebuild needed. |

## Subset smoke test — "does it RUN", not "what does it find"

Ran `pipeline.py` end-to-end via a throwaway harness on a **20-donor subset** (18,301 / 69,426
cells), for **both** sets in `config.SETS_TO_COMPARE` (`paper2_landmark`, `full`), into a
temp output dir.

- **Result:** executed start→finish for both sets; wrote `coordinates_<set>.csv`,
  `collapse_per_donor_<set>.csv`, `collapse_<set>.png`, and (full set only) `de_portal.csv` /
  `de_central.csv`. No crashes, no shape errors, no OOM.
- **Peak working set (OS, psutil):** **1.97 GB**
- **Runtime:** **57.3 s** (subset; dominated by loading the full `counts.npz` before subsetting)
- **Outputs deleted afterward** — no subset numbers kept or committed. `results/tables/` left
  clean (only `.gitkeep`). The harness script (`src/_smoke_test.py`) was removed.

### Crash fixed
- **`UnicodeEncodeError` (cp1252) in `pipeline.py`'s `log()`** — log strings contain non-ASCII
  characters (`→`, em-dashes); the Windows console's default cp1252 codec can't encode `→`,
  killing the run mid-pipeline (would also hit the HUJI Windows boxes). **Fix:** force UTF-8 on
  `sys.stdout`/`sys.stderr` at the top of `pipeline.py`. This is the only code change; it is a
  crash fix, not analysis.

### Non-fatal warnings (left as-is; not crashes)
- `DtypeWarning: mixed types` reading `metadata_all_cells.csv` — cosmetic.
- `ConstantInputWarning` from `spearmanr` inside the donor bootstrap — expected on a tiny
  subset where a bootstrap resample can be constant; harmless on the full data.

## Explicitly NOT done (deferred to the live hackathon)
Validation/go-no-go gate, Step 5b ruler battery, classifier + entropy, H1/H2/H3, the held-out
DE splits, plotting, and all interpretation. No result numbers produced or committed.
