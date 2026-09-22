#!/usr/bin/env bash
# Download all raw inputs into the configured data root. Run from the repo root:
#   bash scripts/download_data.sh
#
# The raw directory is git-ignored. Never commit these multi-gigabyte source files.
# URLs come from the papers' data-availability sections. See data/data_urls.md for
# the annotated manifest.
set -euo pipefail

DATA_ROOT="${LIVER_ZONATION_DATA_ROOT:-data}"
RAW="$DATA_ROOT/raw"
mkdir -p "$RAW"
cd "$RAW"

dl () {
  # dl <url> <output-filename>
  if [ -f "$2" ]; then
    echo "== have $2 (skip)"
    return
  fi
  echo ">> downloading $2"
  curl -L --fail --retry 3 -o "$2" "$1"
}

# Paper 1 — Gribben et al. (GEO GSE202379), disease snRNA cohort.
dl "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE202nnn/GSE202379/suppl/GSE202379_SeuratObject_AllCells.rds.gz" \
   "GSE202379_SeuratObject_AllCells.rds.gz"

if [ -f "GSE202379_SeuratObject_AllCells.rds.gz" ] && \
   [ ! -f "GSE202379_SeuratObject_AllCells.rds/GSE202379_SeuratObject_AllCells.rds" ]; then
  mkdir -p "GSE202379_SeuratObject_AllCells.rds"
  gzip -dc "GSE202379_SeuratObject_AllCells.rds.gz" > \
    "GSE202379_SeuratObject_AllCells.rds/GSE202379_SeuratObject_AllCells.rds"
  echo "== extracted GSE202379 Seurat object"
fi

# Paper 2 — Yakubovsky et al. (Zenodo 17735587), atlas and ruler.
dl "https://zenodo.org/records/17735587/files/combined_scRNAseq_atlas_M5M6M7M8.mat?download=1" \
   "combined_scRNAseq_atlas_M5M6M7M8.mat"
dl "https://zenodo.org/records/17735587/files/zon_struct_all_full.mat?download=1" \
   "zon_struct_all_full.mat"

# Paper 2 — code and landmark CSVs.
dl "https://github.com/OranYak/Human-liver/archive/refs/heads/main.zip" \
   "Human-liver-main.zip"
if [ -f "Human-liver-main.zip" ] && [ ! -d "Human-liver" ]; then
  unzip -q "Human-liver-main.zip"
  mv "Human-liver-main" "Human-liver"
  echo "== unpacked Human-liver/"
fi

# Paper 2 supplementary tables, including supplementary_table_8.xlsx, come
# from the Nature article supplementary archive:
# https://www.nature.com/articles/s41586-026-10377-y

echo
echo "Done. Next:"
echo "  Rscript src/prep/01_extract_paper1_hepatocytes.R"
echo "  Rscript src/prep/05_extract_raw_panel.R"
echo "  Rscript src/prep/09_extract_full_and_union.R"
echo "  python  src/prep/00_mtx_to_npz.py"
echo "  python  src/prep/06_sanity_raw.py"
