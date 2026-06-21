# Raw data — download manifest

All raw inputs live in `data/raw/` (git-ignored — **never commit these**; multi-GB + copyrighted).
Recreate them on any machine with `bash scripts/download_data.sh`, or grab individual files below.

> URLs compiled from the two papers' data-availability sections + the Paper 2 GitHub/Zenodo.
> Not independently re-verified here — if a Zenodo link 404s it may need the access token printed in
> the paper / the `OranYak/Human-liver` README (records can be embargoed).

## Minimal set (everything the project actually needs)

| File | Source | URL |
|---|---|---|
| `GSE202379_SeuratObject_AllCells.rds.gz` | Paper 1 (GEO GSE202379) processed Seurat object | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE202nnn/GSE202379/suppl/GSE202379_SeuratObject_AllCells.rds.gz |
| `combined_scRNAseq_atlas_M5M6M7M8.mat` | Paper 2 snRNA atlas (Zenodo 17735587) | https://zenodo.org/records/17735587/files/combined_scRNAseq_atlas_M5M6M7M8.mat?download=1 |
| `zon_struct_all_full.mat` | Paper 2 zonation ruler (Zenodo 17735587) | https://zenodo.org/records/17735587/files/zon_struct_all_full.mat?download=1 |
| `Human-liver/` (repo) | Paper 2 code + landmark CSVs (`Matlab_scripts/Hepatocyte-{PC,PP}-LM.csv`) | https://github.com/OranYak/Human-liver/archive/refs/heads/main.zip |
| Paper 2 supplementary tables (incl. `supplementary_table_8.xlsx`) | Nature article SI (`41586_2026_10377_MOESM1_ESM.zip`) | https://www.nature.com/articles/s41586-026-10377-y → Supplementary information |

That set supports: Paper 1 hepatocytes + donor/stage metadata; Paper 2 PC/PP signatures (Table 8 +
the `-LM.csv` landmark genes); the Paper 2 snRNA reference + zonation ruler for the classifier.

## Optional extras (only to reproduce the papers, not needed for the project)

| File | Source | URL |
|---|---|---|
| `snRNAseq.zip` | Paper 2 raw snRNA (Zenodo 17735506) | https://zenodo.org/records/17735506/files/snRNAseq.zip?download=1 |
| `human_samples_metadata.xlsx` | Paper 2 sample metadata (small, useful) | https://zenodo.org/records/17735506/files/human_samples_metadata.xlsx?download=1 |
| `Visium.zip` / `VisiumHD.zip` / `MERFISH.zip` | Paper 2 spatial (Zenodo 17735506) | https://zenodo.org/records/17735506/files/Visium.zip?download=1 (etc.) |
| `v.mat` | Paper 2 processed spatial object (Zenodo 17735587) | https://zenodo.org/records/17735587/files/v.mat?download=1 |
| `PhenoCyclerLiverPanel.zip` | Paper 2 protein imaging (Zenodo 17735558) | https://zenodo.org/records/17735558/files/PhenoCyclerLiverPanel.zip?download=1 |
| `GSE202379_RAW.tar` / SRA FASTQs | Paper 1 raw (GEO / PRJNA835824) | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE202nnn/GSE202379/suppl/GSE202379_RAW.tar |

## Extension data (Days 3-4 — replication, inherited-risk bonus)

> Recon June 2026. Paper 4 (Martin/Alatrakchi, Nat Immunol 2025) is **immune-cell-focused**
> (liver+blood fine-needle aspirates) and is **NOT a good hepatocyte-zonation replication** — no
> public GEO surfaced. Use a hepatocyte-bearing MASLD cohort instead (below).

| Purpose | Dataset | Source / URL | Notes |
|---|---|---|---|
| **Replication + spatial validation (recommended)** | Spatially resolved multi-omics of human MASLD (Nat Genet 2025) | atlas portal https://db.genomics.cn/stomics/hmsma/ ; article https://www.nature.com/articles/s41588-025-02407-8 ; open text PMC12695644 | 540k scRNA cells (incl. hepatocytes) **+ 47,864 Visium spots** across control/MASLD/MASH. scRNA → replicate H1 collapse; Visium → validate the reconstructed coordinate vs **real disease spatial position** (the gap the primer flags). |
| Replication (alt, spatial, open) | Spatial transcriptomics of healthy & fibrotic human liver (Nat Commun 2024) | https://www.nature.com/articles/s41467-024-55325-4 | open-access; GEO in its data-availability |
| Replication (alt, snRNA) | MASLD scRNA cohort | GEO GSE159977 (healthy + MASLD) | dissociated; hepatocyte content to verify |
| **Inherited-risk bonus (Step 9, Paper 3)** | Zhu et al., Nat Genet 2026 — risk→target genes | https://www.nature.com/articles/s41588-026-02617-8 (SI) ; preprint Research Square rs-6984670 ; PMC12633503 | target genes in **Suppl. Tables S2 (365 DAVs, HepG2), S6 (20 CRISPRi metabolic target genes), S7 (114 LD-indep DAVs)**. SI is paywalled on Nature — grab the `*_MOESM*_ESM.xlsx` manually or from the preprint. Known examples: SLC22A3, APOA5, ANGPTL3, LPL. |

**Fetch status (June 2026):** landing pages/accessions located; the Nature SI (Paper 3 target genes)
is **paywalled** (manual download of the supplementary xlsx needed), and the spatial-MASLD atlas is a
**large portal download** (run from `db.genomics.cn/stomics/hmsma`). Neither auto-downloads here.

## Landing pages / browse

- Paper 1 GEO: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE202379
- Paper 2 article: https://www.nature.com/articles/s41586-026-10377-y
- Paper 2 Zenodo (MATLAB-ready): https://zenodo.org/records/17735587
- Paper 2 Zenodo (main data): https://zenodo.org/records/17735506
- Paper 2 GitHub: https://github.com/OranYak/Human-liver
- Paper 2 zonation web app: https://shalevapps.weizmann.ac.il/liver_app/

## Caveat carried from GEO
GEO notes samples `GSM6112262` / `GSM6112263` had **swapped metadata**, corrected 2025-06-06 — make
sure your download/conversion reflects the corrected metadata.

## After downloading
Build the processed files the pipeline reads:
```
Rscript src/prep/01_extract_paper1_hepatocytes.R   # rds  -> data/processed/paper1/
python  src/prep/00_mtx_to_npz.py                  # mtx  -> counts.npz
python  src/prep/03_build_signatures.py            # table+LM csv -> signatures/
python  src/prep/02_convert_paper2_mat.py          # mat  -> paper2_train.npz
python  src/prep/audit_data.py                     # sanity check
```
