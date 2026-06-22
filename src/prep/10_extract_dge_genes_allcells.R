# Extract RAW RNA-assay counts for the genome-wide DGE hit genes (signatures/_dge_sig.txt) across
# ALL cells + cell.annotation, so the compositional check can ask whether each fibrosis-trending
# gene is hepatocyte-intrinsic or a non-parenchymal (stromal/immune) transcript. Mirrors prep/08.
suppressMessages({library(SeuratObject); library(Matrix)})
RDS <- "data/raw/GSE202379_SeuratObject_AllCells.rds/GSE202379_SeuratObject_AllCells.rds"
G   <- trimws(readLines("signatures/_dge_sig.txt")); G <- G[nchar(G)>0]
OUT <- "data/processed/paper1/dge_genes_allcells.csv"
cat("genes:", length(G), "\n"); cat("reading RDS (minutes) ...\n"); flush.console()
obj <- readRDS(RDS)
if (inherits(obj[["RNA"]], "Assay5")) obj[["RNA"]] <- JoinLayers(obj[["RNA"]])
cnt <- tryCatch(LayerData(obj, assay="RNA", layer="counts"),
                error=function(e) GetAssayData(obj, assay="RNA", slot="counts"))
present <- intersect(G, rownames(cnt)); cat("present:", length(present), "/", length(G), "\n")
sub <- as.matrix(t(cnt[present, , drop=FALSE])); colnames(sub) <- present
md <- obj@meta.data
getcol <- function(nm) if (nm %in% colnames(md)) md[[nm]] else rep(NA, nrow(md))
out <- data.frame(cell_id=colnames(obj), donor=as.character(getcol("Patient.ID")),
                  annotation=as.character(getcol("cell.annotation")),
                  E_raw=as.numeric(Matrix::colSums(cnt)), check.names=FALSE, stringsAsFactors=FALSE)
out <- cbind(out, sub)
write.csv(out, OUT, row.names=FALSE)
cat("wrote", OUT, "rows:", nrow(out), "gene cols:", length(present), "\nDONE\n")
