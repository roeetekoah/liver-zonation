# Extract RAW RNA counts for the Plan-A F4-vs-F1 hit genes (signatures/_planA_hits.txt) across ALL cells
# + cell.annotation, so the compositional audit can ask whether the F1->F4 biliary/transdiff program
# (EPCAM/SOX4/SOX9/GRHL2...) is hepatocyte-INTRINSIC or ambient from expanding cholangiocytes. Mirrors prep/10.
suppressMessages({library(SeuratObject); library(Matrix)})
RDS <- "data/raw/GSE202379_SeuratObject_AllCells.rds/GSE202379_SeuratObject_AllCells.rds"
G   <- trimws(readLines("signatures/_planA_hits.txt")); G <- G[nchar(G)>0]
OUT <- "data/processed/paper1/planA_hits_allcells.csv"
cat("genes:", length(G), "\n  reading RDS (minutes)...\n"); flush.console()
obj <- readRDS(RDS)
if (inherits(obj[["RNA"]], "Assay5")) obj[["RNA"]] <- JoinLayers(obj[["RNA"]])
cnt <- tryCatch(LayerData(obj, assay="RNA", layer="counts"),
                error=function(e) GetAssayData(obj, assay="RNA", slot="counts"))
present <- intersect(G, rownames(cnt)); cat("present:", length(present), "/", length(G),
    if(length(setdiff(G,present))) paste("| absent:",paste(setdiff(G,present),collapse=",")) else "", "\n")
sub <- as.matrix(t(cnt[present, , drop=FALSE])); colnames(sub) <- present
md <- obj@meta.data; getc <- function(n) if(n %in% colnames(md)) md[[n]] else rep(NA,nrow(md))
out <- data.frame(cell_id=colnames(obj), donor=as.character(getc("Patient.ID")),
                  annotation=as.character(getc("cell.annotation")),
                  E_raw=as.numeric(Matrix::colSums(cnt)), check.names=FALSE, stringsAsFactors=FALSE)
out <- cbind(out, sub); write.csv(out, OUT, row.names=FALSE)
cat("wrote", OUT, "rows:", nrow(out), "gene cols:", length(present), "\nDONE\n")
