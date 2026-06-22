# Extract RAW RNA-assay UMI counts for the analysis gene panel from the original Seurat object.
# Writes ONE tidy per-cell table: barcode, provenance (donor/stage/lobe/annotation),
# E_raw (full raw library size = colSum of RNA counts), and one RAW-UMI column per panel gene.
# Everything downstream (per donor/lobe/stage frac_raw_pos, M_raw, UMIs_per_10k, anchor census,
# stress split) is computed from this in Python. NO SCT, NO normalization here.

suppressMessages({library(SeuratObject); library(Matrix)})

RDS <- "data/raw/GSE202379_SeuratObject_AllCells.rds/GSE202379_SeuratObject_AllCells.rds"
OUT <- "data/processed/paper1/raw_panel_counts.csv"

PANEL <- c(
  # detox/redox/transport
  "CYP2E1","CYP1A2","ADH4","ADH1B","AKR1D1","SLCO1B3",
  # pericentral identity
  "GLUL","CYP3A4","LGR5","AXIN2",
  # periportal / metabolic
  "PCK1","ALDOB","HAL","ASS1","CPS1","ARG1",
  # stress / handling / ischemia
  "FOS","JUN","JUNB","JUND","ATF3","DUSP1","HSPA1A","HSPA1B","HSP90AA1",
  "VEGFA","SLC2A1","LDHA","CA9","ENO1","PGK1",
  # housekeeping / hepatocyte identity
  "ACTB","GAPDH","RPLP0","B2M","ALB","TTR","APOA1",
  # ductular / plasticity / contamination
  "KRT7","KRT19","EPCAM","SOX4","KRT23","NCAM1","MUC1","BCL2"
)

cat("reading RDS (large; minutes) ...\n"); flush.console()
obj <- readRDS(RDS)
cat("class:", class(obj), "\n")
cat("assays:", paste(Assays(obj), collapse=", "), " | default:", DefaultAssay(obj), "\n")
cat("n cells:", ncol(obj), " n genes(RNA):", nrow(obj[["RNA"]]), "\n")

# --- get RAW counts from the RNA assay, robust to Seurat v4/v5 layered assays ---
rna <- obj[["RNA"]]
if (inherits(rna, "Assay5")) {
  cat("Assay5 detected; layers:", paste(Layers(rna), collapse=", "), "\n")
  obj[["RNA"]] <- JoinLayers(obj[["RNA"]])
}
cnt <- tryCatch(LayerData(obj, assay="RNA", layer="counts"),
                error=function(e) GetAssayData(obj, assay="RNA", slot="counts"))
cat("counts dim:", paste(dim(cnt), collapse=" x "), " class:", class(cnt), "\n")

# --- verify it is RAW (integer; colSums match metadata nCount_RNA range, not the ~3-5k SCT band) ---
E_raw <- Matrix::colSums(cnt)
cat(sprintf("colSum(raw) min %.0f  median %.0f  max %.0f  (raw should span ~900..50000)\n",
            min(E_raw), median(E_raw), max(E_raw)))
cat("integer values?", all(cnt@x == round(cnt@x)), "\n")

# --- subset to panel genes present ---
present <- intersect(PANEL, rownames(cnt))
missing <- setdiff(PANEL, rownames(cnt))
if (length(missing)) cat("absent from RNA assay:", paste(missing, collapse=", "), "\n")
sub <- as.matrix(t(cnt[present, , drop=FALSE]))          # cells x genes (dense; ~Ncells x ~48)
colnames(sub) <- present

# --- provenance from meta.data (fall back to NA if a column is absent) ---
md <- obj@meta.data
getcol <- function(nm) if (nm %in% colnames(md)) md[[nm]] else rep(NA, nrow(md))
out <- data.frame(
  cell_id   = colnames(obj),
  donor     = getcol("Patient.ID"),
  stage     = getcol("Disease.status"),
  lobe      = getcol("Lobe"),
  annotation= getcol("cell.annotation"),
  E_raw     = as.numeric(E_raw),
  nCount_RNA_md = getcol("nCount_RNA"),
  check.names = FALSE, stringsAsFactors = FALSE
)
out <- cbind(out, sub)
cat("writing", OUT, " rows:", nrow(out), " gene cols:", length(present), "\n")
write.csv(out, OUT, row.names=FALSE)
cat("DONE\n")
