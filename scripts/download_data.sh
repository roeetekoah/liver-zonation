#!/usr/bin/env bash
# Download all raw inputs into data/raw/. Run from the repo root:  bash scripts/download_data.sh
#
# data/raw/ is git-ignored — NEVER commit these files (multi-GB + copyrighted).
# URLs are from the papers' data-availability sections; if a Zenodo link fails it may need the
# access token printed in the paper / the OranYak/Human-liver README (records can be embargoed).
# See data/data_urls.md for the full annotated manifest.
set -u
RAW="data/raw"
mkdir -p "$RAW"
cd "$RAW"

dl () {  # dl <url> <output-filename>
  if [ -f "$2" ]; then echo "== have $2 (skip)"; return; fi
  echo ">> downloading $2"
  curl -L --fail --retry 3 -o "$2" "$1" || echo "!! FAILED: $2  <$1>"
}

# ---------- Paper 1 — Gribben et al. (GEO GSE202379), disease snRNA cohort ----------
dl "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE202nnn/GSE202379/suppl/GSE202379_SeuratObject_AllCells.rds.gz" \
   "GSE202379_SeuratObject_AllCells.rds.gz"

# ---------- Paper 2 — Yakubovsky et al. (Zenodo 17735587), MATLAB-ready atlas + ruler ----------
dl "https://zenodo.org/records/17735587/files/combined_scRNAseq_atlas_M5M6M7M8.mat?download=1" \
   "combined_scRNAseq_atlas_M5M6M7M8.mat"
dl "https://zenodo.org/records/17735587/files/zon_struct_all_full.mat?download=1" \
   "zon_struct_all_full.mat"

# ---------- Paper 2 — code + landmark CSVs (GitHub) ----------
dl "https://github.com/OranYak/Human-liver/archive/refs/heads/main.zip" "Human-liver-main.zip"
if [ -f "Human-liver-main.zip" ] && [ ! -d "Human-liver" ]; then
  unzip -q Human-liver-main.zip && mv Human-liver-main Human-liver && echo "== unpacked Human-liver/"
fi

# ---------- OPTIONAL extras (uncomment if you need them) ----------
# dl "https://zenodo.org/records/17735506/files/snRNAseq.zip?download=1"            "snRNAseq.zip"
# dl "https://zenodo.org/records/17735506/files/human_samples_metadata.xlsx?download=1" "human_samples_metadata.xlsx"
# dl "https://zenodo.org/records/17735587/files/v.mat?download=1"                   "v.mat"
# dl "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE202nnn/GSE202379/suppl/GSE202379_RAW.tar" "GSE202379_RAW.tar"

# NOTE: Paper 2 supplementary tables (incl. supplementary_table_8.xlsx, needed by 03_build_signatures)
# come from the Nature article SI: https://www.nature.com/articles/s41586-026-10377-y
# Download "41586_2026_10377_MOESM1_ESM.zip" there and unzip into data/raw/ manually.

echo
echo "Done. Next: build processed files —"
echo "  Rscript src/prep/01_extract_paper1_hepatocytes.R"
echo "  python  src/prep/00_mtx_to_npz.py"
echo "  python  src/prep/03_build_signatures.py"
echo "  python  src/prep/02_convert_paper2_mat.py"
echo "  python  src/prep/audit_data.py"
