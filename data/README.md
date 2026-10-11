# LiZARD data provenance and reuse

Local data store. **Nothing in `raw/` or `processed/` is committed** (multi-GB and
copyrighted) — each machine downloads `raw/` and regenerates `processed/` locally.

```
data/
├── raw/          # original downloads, never edited by our code (read-only inputs)
└── processed/    # derived, Python-native files our pipeline actually consumes
```

## raw/  (original inputs)

| file | what it is |
|------|------------|
| `GSE202379_SeuratObject_AllCells.rds(.gz)` | Paper 1 Seurat object (disease cohort) |
| `combined_scRNAseq_atlas_M5M6M7M8.mat` | Paper 2 snRNA atlas (MATLAB v7.3 / HDF5) → classifier training |
| `zon_struct_all_full.mat` | Paper 2 zonation reconstruction (positive control) |
| `41586_2026_10377_MOESM1_ESM.zip`, `2025-01-01424E-s1/` | Paper 2 supplementary tables (zonation tables) |
| `Human-liver/` | Paper 2 GitHub repo (MATLAB scripts, landmark CSVs) |

---

## Getting the data on a fresh machine (e.g. the HUJI computers)

`data/raw/` and `data/processed/` are git-ignored, so a clone has **no large inputs**. The tracked
signature definitions remain in `data/signatures/`. The recommended route is documented in
[`../REPRODUCING.md`](../REPRODUCING.md).

**Step 1 — download into `data/raw/`:**

| source | what to download | into |
|---|---|---|
| **GEO `GSE202379`** (ncbi.nlm.nih.gov/geo) | `GSE202379_SeuratObject_AllCells.rds.gz` (~2.6 GB) | `data/raw/` |
| **Zenodo `17735587`** (and `17735506`, `17735558`) | `combined_scRNAseq_atlas_M5M6M7M8.mat`, `zon_struct_all_full.mat` | `data/raw/` |
| **Nature paper SI** (doi 10.1038/s41586-026-10377-y) | supplementary tables zip → unzip to `2025-01-01424E-s1/` | `data/raw/` |
| **GitHub `OranYak/Human-liver`** | `git clone https://github.com/OranYak/Human-liver data/raw/Human-liver` | `data/raw/` |

`scripts/download_data.sh` downloads the public sources it can obtain automatically and extracts the
GSE202379 `.rds.gz` into the path expected by the extraction scripts. Paper 2 supplementary inputs may
still require manual download from the publisher.

**Step 2 — regenerate the Paper 1 inputs used by the verified route:**

```bash
Rscript src/prep/01_extract_paper1_hepatocytes.R
Rscript src/prep/05_extract_raw_panel.R
Rscript src/prep/09_extract_full_and_union.R
python  src/prep/00_mtx_to_npz.py
python  src/prep/06_sanity_raw.py
```

All current Paper 1 extraction scripts explicitly select the Seurat `RNA` assay. The signature files are
committed and do not need to be regenerated for the selected route. Paper 2 conversion scripts support
historical and optional marker-set analyses.

---

## processed/  (derived — what the pipeline actually reads)

`counts.mtx` and `raw_panel_counts.csv` contain integer RNA-assay UMIs. Normalization or thinning is
performed inside the analysis that needs it. `src/prep/06_sanity_raw.py` explicitly checks RNA-versus-SCT
separation, library sizes, integer counts, panel completeness and the expected hepatocyte count.

### `paper1/`  (produced by `src/prep/01_extract_paper1_hepatocytes.R`)

| file | schema | how to load |
|---|---|---|
| `counts.mtx` | MatrixMarket, **integer**, 30117 genes (rows) × 69426 hepatocytes (cols), raw UMI counts. Row *i* ↔ `genes.txt` line *i*; col *j* ↔ `barcodes.txt` line *j*. | `scipy.io.mmread("counts.mtx").tocsc()` |
| `genes.txt` | 30117 gene symbols, one per line (= mtx row order) | `[l.strip() for l in open(...)]` |
| `barcodes.txt` | 69426 cell IDs, one per line (= mtx col order) | same |
| `cell_metadata.csv` | columns: `cell_id`, `cell_type` (all `Hepatocytes`), `stage` ∈ {Healthy control, NAFLD, NASH w/o cirrhosis, NASH with cirrhosis, end stage} | `pandas.read_csv(...)` |
| `metadata_all_cells.csv` | full per-cell metadata; key columns: `cell_id`, **`Patient.ID`** (= donor, used for donor-level stats), `nCount_RNA` (library size), `nFeature_RNA`, `Disease.status`, clinical scores | `pandas.read_csv(...)` |

```python
import scipy.io, pandas as pd, numpy as np
M     = scipy.io.mmread("data/processed/paper1/counts.mtx").tocsc()   # 30117 x 69426 raw counts
genes = [l.strip() for l in open("data/processed/paper1/genes.txt")]
bars  = [l.strip() for l in open("data/processed/paper1/barcodes.txt")]
meta  = pd.read_csv("data/processed/paper1/cell_metadata.csv")        # cell_id, cell_type, stage
allm  = pd.read_csv("data/processed/paper1/metadata_all_cells.csv")   # + Patient.ID (donor), nCount_RNA
```

### `paper2_train.npz`  (produced by `src/prep/02_convert_paper2_mat.py`)

Zone-labelled Paper 2 **snRNA** hepatocytes — the classifier training set.

`X` spans the **union of all signature tiers** (full ∪ expanded ∪ core ∪ paper2_landmark,
restricted to genes shared with Paper 1) — ~1,700 genes, not just the 40 landmarks. One
cache serves every set: downstream, pick a tier by slicing the columns of `feats` whose
gene symbol is in that tier's list. Zone labels are derived from the **`full`** coordinate.

| key | shape | dtype | meaning |
|---|---|---|---|
| `X` | (≈50979, ≈1700) | float32 | CP-normalized expression over the union of all signature-tier genes, column order = `feats` |
| `feats` | (≈1700,) | str | gene symbols (the X column order); slice per tier by membership |
| `zone_label` | (50979,) | int64 | zone class per nucleus (0 / 1 / 2 = portal / mid / central tercile) |
| `donor` | (50979,) | str | donor ID (`M5`…`M8`) |

```python
import numpy as np
z = np.load("data/processed/paper2_train.npz", allow_pickle=True)
X, feats, y, donor = z["X"], z["feats"], z["zone_label"], z["donor"]   # train: X -> y
```

All paths are centralised in `src/config.py` (`DATA_RAW, DATA_PROC, PAPER1, PAPER2_TRAIN,
SIGNATURES, RESULTS`). Import those rather than hard-coding paths.
