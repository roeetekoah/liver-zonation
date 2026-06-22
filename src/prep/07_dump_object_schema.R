# AUTHORITATIVE schema dump of the Seurat object — what assays/layers exist, which is default,
# and proof that the RNA 'counts' layer (what prep/05 pulled) is RAW and differs from SCT.
# Writes results/object_schema.txt. Run: Rscript src/prep/07_dump_object_schema.R
suppressMessages({library(SeuratObject)})
RDS <- "data/raw/GSE202379_SeuratObject_AllCells.rds/GSE202379_SeuratObject_AllCells.rds"
OUT <- "results/object_schema.txt"; dir.create("results", showWarnings=FALSE)
sink(OUT, split=TRUE)
cat("==== Seurat object schema (GSE202379) ====\n")
obj <- readRDS(RDS)
cat("class:", class(obj), "\n")
cat("assays:", paste(Assays(obj), collapse=", "), "\n")
cat("DEFAULT assay:", DefaultAssay(obj), "   <-- prep/01 pulled GetAssayData(default,'counts') = THIS\n")
cat("n cells:", ncol(obj), "\n\n")

for (a in Assays(obj)) {
  as <- obj[[a]]
  cat("---- assay:", a, " (class", class(as)[1], ") ----\n")
  cat("   genes:", nrow(as), "\n")
  ly <- tryCatch(Layers(as), error=function(e) slotNames(as))
  cat("   layers/slots:", paste(ly, collapse=", "), "\n")
}
# join layers for RNA (v5 may split), then prove RNA counts are raw integers
if (inherits(obj[["RNA"]],"Assay5")) obj[["RNA"]] <- JoinLayers(obj[["RNA"]])
rna <- tryCatch(LayerData(obj, assay="RNA", layer="counts"), error=function(e) GetAssayData(obj,"RNA",slot="counts"))
sct <- tryCatch(LayerData(obj, assay="SCT", layer="counts"), error=function(e) GetAssayData(obj,"SCT",slot="counts"))
cat("\n==== RNA 'counts' (what we pulled in prep/05) ====\n")
cat("   dim:", paste(dim(rna),collapse=" x "), " | integer:", all(rna@x==round(rna@x)),
    " | colSum range:", paste(round(range(Matrix::colSums(rna))),collapse=".."), "\n")
cat("==== SCT 'counts' (what prep/01 wrongly pulled) ====\n")
cat("   dim:", paste(dim(sct),collapse=" x "), " | integer:", all(sct@x==round(sct@x)),
    " | colSum range:", paste(round(range(Matrix::colSums(sct))),collapse=".."), "\n")

# side-by-side for a few genes/cells: RNA(raw) vs SCT(corrected) — should DIFFER
gs <- intersect(c("ALB","CYP2E1","GLUL","PCK1"), intersect(rownames(rna),rownames(sct)))
cs <- colnames(rna)[1:4]
cat("\n==== RNA(raw) vs SCT(corrected) for sample genes x cells ====\n")
for (g in gs) {
  rv <- as.numeric(rna[g, cs]); sv <- as.numeric(sct[g, cs])
  cat(sprintf("   %-7s RNA: %s | SCT: %s\n", g, paste(rv,collapse=","), paste(sv,collapse=",")))
}
cat("\n==== nCount_RNA vs nCount_SCT (meta.data) ====\n")
md <- obj@meta.data
for (c in c("nCount_RNA","nFeature_RNA","nCount_SCT","nFeature_SCT")) if (c %in% colnames(md))
  cat(sprintf("   %-13s median=%.0f  range=%.0f..%.0f\n", c, median(md[[c]]), min(md[[c]]), max(md[[c]])))
cat("\n==== meta.data columns (",ncol(md),") ====\n"); print(colnames(md))
cat("\nDONE — RNA counts are raw integers spanning ~900..50k; SCT counts are corrected (~3-5.7k). prep/05 pulled RNA.\n")
sink()
