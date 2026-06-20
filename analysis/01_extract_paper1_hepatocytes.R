#!/usr/bin/env Rscript
# Robust extraction of Paper 1 hepatocytes + metadata for the Python pipeline.
# Auto-detects the cell-type and stage columns (no manual editing).
# Run from the Hackathon folder:   Rscript analysis/01_extract_paper1_hepatocytes.R
suppressMessages({ library(Seurat); library(Matrix) })

# find the actual .rds FILE (the .gz may have extracted into a same-named folder)
rdsf <- list.files(c(".", ".."), pattern = "GSE202379.*\\.rds$", recursive = TRUE, full.names = TRUE)
rdsf <- rdsf[!dir.exists(rdsf)]                       # keep files, drop the directory
if (length(rdsf) == 0) stop("No GSE202379*.rds FILE found (only a folder?). Check the extraction.")
rds  <- rdsf[which.max(file.info(rdsf)$size)]         # the real object is the biggest one
cat("Reading", rds, "...\n"); obj <- readRDS(rds)
cat("class:", class(obj)[1], "| cells:", ncol(obj), "| genes:", nrow(obj), "\n")

md <- obj@meta.data
md$.ident <- as.character(Idents(obj))                 # identity as an extra candidate
low <- function(x) tolower(as.character(x))

dir.create("analysis/paper1", recursive = TRUE, showWarnings = FALSE)

# ---- preview every categorical column so we can always see the structure ----
sink("analysis/meta_preview.txt")
cat("== meta.data columns ==\n"); print(colnames(md))
for (c in colnames(md)) {
  v <- md[[c]]
  if (is.factor(v) || is.character(v)) {
    u <- sort(table(as.character(v)), decreasing = TRUE)
    if (length(u) <= 40) { cat("\n[", c, "]\n"); print(u) }
  }
}
sink()

# ---- auto-detect the cell-type column (one whose values include 'hepato...') ----
ct_col <- NA
for (c in colnames(md)) if (any(grepl("hepato", low(md[[c]])))) { ct_col <- c; break }
if (is.na(ct_col)) stop("No column has a 'hepato...' label; inspect analysis/meta_preview.txt and tell Claude.")
labs <- unique(as.character(md[[ct_col]]))
hep_labels <- labs[grepl("hepato", low(labs))]

# ---- auto-detect the stage column (most matches to known stage tokens) ----
tokens <- c("healthy","control","normal","nafld","masld","nash","mash",
            "steato","cirrho","fibro","end")
sc <- sapply(colnames(md), function(c){ u <- unique(low(md[[c]]))
        sum(sapply(tokens, function(tk) any(grepl(tk, u)))) })
stage_col <- names(which.max(sc))
cat("cell-type column:", ct_col, "| hepatocyte labels:", paste(hep_labels, collapse=", "), "\n")
cat("stage column    :", stage_col, "(", max(sc), "stage tokens matched )\n")

# ---- subset hepatocytes + export ----
keep <- rownames(md)[ as.character(md[[ct_col]]) %in% hep_labels ]
hep  <- subset(obj, cells = keep)
cat("hepatocytes kept:", ncol(hep), "(paper reports ~69,426)\n")

da <- DefaultAssay(hep)
counts <- tryCatch(GetAssayData(hep, assay = da, slot  = "counts"),
                   error = function(e) GetAssayData(hep, assay = da, layer = "counts"))
Matrix::writeMM(counts, "analysis/paper1/counts.mtx")
writeLines(rownames(counts), "analysis/paper1/genes.txt")
writeLines(colnames(counts), "analysis/paper1/barcodes.txt")

hm <- hep@meta.data
out <- data.frame(cell_id = rownames(hm),
                  cell_type = as.character(hm[[ct_col]]),
                  stage = as.character(hm[[stage_col]]))
write.csv(out, "analysis/paper1/cell_metadata.csv", row.names = FALSE)
write.csv(cbind(cell_id = rownames(md), md), "analysis/paper1/metadata_all_cells.csv", row.names = FALSE)
cat("\nWrote analysis/paper1/{counts.mtx, genes.txt, barcodes.txt, cell_metadata.csv, metadata_all_cells.csv}\n")
cat("Check analysis/meta_preview.txt to confirm the auto-detected columns look right.\n")
