# One RDS pass -> two deliverables, both from RAW RNA-assay counts:
#  (1) FULL-transcriptome donor pseudobulk (genes x donors), summed over each donor's hepatocyte
#      nuclei -> for genome-wide donor-level differential expression ("is the detox dip the ONLY
#      biopsy-internal change?").  Output: pseudobulk_hep_by_donor.csv  + donor_meta.csv
#  (2) Per-cell RAW counts for the 1,646 curated zonation-set union genes (the breadth ladder:
#      core/expanded/full/paper2_landmark/sensitivity/plasticity + anchors/program) as a sparse
#      .mtx -> for the all-marker-sets census.  Output: raw_curated_union.{mtx,genes.txt} + cells.csv
# NO SCT, NO normalization here.

suppressMessages({library(SeuratObject); library(Matrix)})
RDS   <- "data/raw/GSE202379_SeuratObject_AllCells.rds/GSE202379_SeuratObject_AllCells.rds"
UNION <- "signatures/_curated_union.txt"
OUTD  <- "data/processed/paper1"

union_genes <- trimws(readLines(UNION)); union_genes <- union_genes[nchar(union_genes)>0]
cat("curated union genes requested:", length(union_genes), "\n")

cat("reading RDS (large; minutes) ...\n"); flush.console()
obj <- readRDS(RDS)
if (inherits(obj[["RNA"]], "Assay5")) obj[["RNA"]] <- JoinLayers(obj[["RNA"]])
cnt <- tryCatch(LayerData(obj, assay="RNA", layer="counts"),
                error=function(e) GetAssayData(obj, assay="RNA", slot="counts"))
cat("counts dim:", paste(dim(cnt), collapse=" x "), " integer:", all(cnt@x==round(cnt@x)), "\n")

md <- obj@meta.data
getcol <- function(nm) if (nm %in% colnames(md)) md[[nm]] else rep(NA, nrow(md))
donor <- as.character(getcol("Patient.ID"))
stage <- as.character(getcol("Disease.status"))
annot <- as.character(getcol("cell.annotation"))
E_raw <- Matrix::colSums(cnt)
is_hep <- annot == "Hepatocytes"
cat("hepatocyte nuclei:", sum(is_hep, na.rm=TRUE), " of", length(annot), "\n")

# ---- (1) FULL-transcriptome donor pseudobulk over hepatocytes ----
donors <- sort(unique(donor[is_hep & !is.na(donor)]))
pb <- matrix(0, nrow=nrow(cnt), ncol=length(donors), dimnames=list(rownames(cnt), donors))
nhep <- integer(length(donors)); names(nhep) <- donors
for (i in seq_along(donors)) {
  cols <- which(is_hep & donor==donors[i])
  nhep[i] <- length(cols)
  if (length(cols)) pb[, i] <- Matrix::rowSums(cnt[, cols, drop=FALSE])
}
write.csv(data.frame(gene=rownames(pb), pb, check.names=FALSE),
          file.path(OUTD,"pseudobulk_hep_by_donor.csv"), row.names=FALSE)
dm <- data.frame(donor=donors,
                 stage=sapply(donors, function(d) stage[which(donor==d)][1]),
                 n_hep=as.integer(nhep),
                 lib_pb=as.numeric(colSums(pb)))
write.csv(dm, file.path(OUTD,"donor_meta.csv"), row.names=FALSE)
cat("(1) wrote pseudobulk_hep_by_donor.csv  genes x donors =", nrow(pb), "x", ncol(pb), "\n")

# ---- (2) per-cell RAW counts for the curated-union genes (ALL cells) ----
present <- intersect(union_genes, rownames(cnt))
cat("(2) union genes present in RNA:", length(present), "/", length(union_genes), "\n")
sub <- cnt[present, , drop=FALSE]                       # genes x cells, sparse
Matrix::writeMM(sub, file.path(OUTD,"raw_curated_union.mtx"))
writeLines(present, file.path(OUTD,"raw_curated_union.genes.txt"))
cells <- data.frame(cell_id=colnames(cnt), donor=donor, stage=stage,
                    annotation=annot, E_raw=as.numeric(E_raw),
                    check.names=FALSE, stringsAsFactors=FALSE)
write.csv(cells, file.path(OUTD,"raw_curated_union.cells.csv"), row.names=FALSE)
cat("(2) wrote raw_curated_union.mtx  genes x cells =", nrow(sub), "x", ncol(sub), "\nDONE\n")
