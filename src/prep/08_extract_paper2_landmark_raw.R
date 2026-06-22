# Extract RAW RNA-assay UMI counts for Paper 2's EXACT hepatocyte landmark genes
# (Hepatocyte-{PC,PP}-LM.csv, 20+20), so the marker-set robustness check can run the
# count-based census on Paper 2's own ruler genes — NOT their fitted relative coordinate.
# Writes one tidy per-cell table keyed by cell_id (join to raw_panel_counts.csv on cell_id).
# NO SCT, NO normalization here. Mirrors prep/05.

suppressMessages({library(SeuratObject); library(Matrix)})

RDS  <- "data/raw/GSE202379_SeuratObject_AllCells.rds/GSE202379_SeuratObject_AllCells.rds"
LMPC <- "signatures/pericentral_paper2_landmark.txt"
LMPP <- "signatures/periportal_paper2_landmark.txt"
OUT  <- "data/processed/paper1/paper2_landmark_raw_counts.csv"

rd <- function(p) trimws(readLines(p)); rd <- function(p) { x <- readLines(p); trimws(x[nchar(trimws(x))>0]) }
pc <- rd(LMPC); pp <- rd(LMPP)
GENES <- unique(c(pc, pp))
cat("Paper-2 landmark genes requested:", length(pc), "PC +", length(pp), "PP =", length(GENES), "\n")

cat("reading RDS (large; minutes) ...\n"); flush.console()
obj <- readRDS(RDS)
rna <- obj[["RNA"]]
if (inherits(rna, "Assay5")) { obj[["RNA"]] <- JoinLayers(obj[["RNA"]]) }
cnt <- tryCatch(LayerData(obj, assay="RNA", layer="counts"),
                error=function(e) GetAssayData(obj, assay="RNA", slot="counts"))
cat("counts dim:", paste(dim(cnt), collapse=" x "), "\n")

E_raw <- Matrix::colSums(cnt)
cat("integer values?", all(cnt@x == round(cnt@x)), "  colSum raw range:",
    sprintf("%.0f..%.0f", min(E_raw), max(E_raw)), "\n")

present <- intersect(GENES, rownames(cnt))
missing <- setdiff(GENES, rownames(cnt))
cat("present in RNA assay:", length(present), "/", length(GENES),
    " | absent:", if (length(missing)) paste(missing, collapse=", ") else "none", "\n")
cat("PC-LM present:", sum(pc %in% present), "/", length(pc),
    " | PP-LM present:", sum(pp %in% present), "/", length(pp), "\n")

sub <- as.matrix(t(cnt[present, , drop=FALSE])); colnames(sub) <- present
md <- obj@meta.data
getcol <- function(nm) if (nm %in% colnames(md)) md[[nm]] else rep(NA, nrow(md))
out <- data.frame(cell_id = colnames(obj),
                  E_raw = as.numeric(E_raw),
                  check.names = FALSE, stringsAsFactors = FALSE)
out <- cbind(out, sub)
write.csv(out, OUT, row.names=FALSE)
cat("wrote", OUT, " rows:", nrow(out), " gene cols:", length(present), "\nDONE\n")
