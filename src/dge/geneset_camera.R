# Independent cross-check of geneset_tests.py using limma::camera.
# camera is a COMPETITIVE gene-set test that adjusts the variance-inflation for INTER-GENE
# CORRELATION within the set -- the standard guard against GSEA-permutation anticonservatism.
# Self-contained: rebuilds the donor-level log2-CPM pseudobulk exactly as dge_genomewide.py,
# fits a fibrosis-stage (continuous F) design at DONOR level, and runs camera per pre-specified set.
# Output: results/tables/analysis/geneset_camera.csv
suppressMessages({library(limma)})

# run from repo root: Rscript src/dge/geneset_camera.R
root <- getwd()
P1  <- file.path(root, "data", "processed", "paper1")
SIG <- file.path(root, "data", "signatures")
OUT <- file.path(root, "results", "tables", "analysis", "geneset_camera.csv")

pb <- read.csv(file.path(P1, "pseudobulk_hep_by_donor.csv"), check.names=FALSE)
rownames(pb) <- pb$gene; pb$gene <- NULL
dm <- read.csv(file.path(P1, "donor_meta.csv"), check.names=FALSE)
dm$donor <- as.character(dm$donor)
md <- read.csv(file.path(P1, "metadata_all_cells.csv"), check.names=FALSE)
Fcol <- "Fibrosis.score..F0.4."
md$donor <- as.character(md$Patient.ID)
Fmap <- tapply(suppressWarnings(as.numeric(md[[Fcol]])), md$donor, function(x) x[!is.na(x)][1])

src <- setNames(dm$stage, dm$donor)
donors <- colnames(pb)
keep <- sapply(donors, function(d)
  !startsWith(d, "CL") && (is.na(src[d]) || src[d] != "Healthy control") &&
  !is.na(Fmap[d]))
donors <- donors[keep]
F <- as.numeric(Fmap[donors])
pb <- as.matrix(pb[, donors])
cat(sprintf("biopsy donors: %d  F dist: %s\n", length(donors),
            paste(sapply(0:4, function(k) sum(F==k)), collapse="/")))

# CPM -> log2(CPM+1), expression filter CPM>=1 in >= half donors (matches dge_genomewide.py)
lib <- colSums(pb); cpm <- t(t(pb)/lib)*1e6; logcpm <- log2(cpm+1)
expr_ok <- rowSums(cpm >= 1) >= (length(donors) %/% 2)
logcpm <- logcpm[expr_ok, ]; cpm <- cpm[expr_ok, ]
cat(sprintf("genes tested: %d\n", nrow(logcpm)))

design <- model.matrix(~ F)   # donor-level continuous fibrosis trend

readset <- function(f) {
  x <- readLines(file.path(SIG, f)); x <- trimws(x); x[x!="" & !startsWith(x,"#")]
}
pc_lm <- readset("pericentral_paper2_landmark.txt")
pp_lm <- readset("periportal_paper2_landmark.txt")
plast <- readset("plasticity.txt")
sets <- list(
  pericentral_anchors = pc_lm,
  periportal_anchors  = pp_lm,
  xenobiotic_CYP = c("CYP2E1","CYP1A2","CYP3A4","CYP3A5","CYP3A43","CYP2C8","CYP2C9","CYP2C19","CYP2B6","CYP1A1","CYP2A6","CYP2D6","CYP4F12"),
  detox_phase2 = c("UGT1A1","UGT2B4","UGT2B7","GSTA1","GSTA2","SULT2A1","SULT1A1","AKR1D1","AKR1C1","ADH1A","ADH1B","ADH4","ALDH1L1","FMO3","AOX1","AMACR"),
  urea_cycle = c("CPS1","OTC","ASS1","ASL","ARG1","NAGS","SLC25A13","GLS2","GLUL"),
  bile_acid_lipid = c("SLCO1B3","SLCO1B1","BAAT","CYP7A1","CYP8B1","CYP27A1","SLC10A1","ABCB11","ABCC2","NR1H4","APOA1","APOA5","APOB","APOC3","FABP1","SREBF1","FASN","MLXIPL","GPAM","PLIN1"),
  cholangiocyte_ductular = c(plast, "KRT7","KRT19","KRT23","EPCAM","CFTR","HNF1B","SPP1","ANXA4","DEFB1","PKHD1","CLDN4","TACSTD2","MMP7"),
  CTRL_interferon = c("STAT1","IRF1","ISG15","IFI6","IFI27","IFI44","IFIT1","IFIT3","MX1","MX2","OAS1","OAS2","OAS3","IFITM3","B2M","GBP1","GBP2","RSAD2","XAF1","BST2"),
  CTRL_EMT = c("FN1","VIM","COL1A1","COL1A2","COL3A1","COL5A2","TIMP1","TIMP3","SPARC","TAGLN","ACTA2","BGN","LUM","DCN","THBS1","POSTN","FBN1","MMP2","LOX","TPM1"),
  CTRL_ER_stress = c("HSPA5","DDIT3","ATF4","XBP1","HERPUD1","DNAJB9","EDEM1","SEC61B","PDIA4","PDIA6","HYOU1","MANF","CALR","HSP90B1","SDF2L1","DNAJC3","ERN1","ATF6","SEL1L","SYVN1")
)
idx <- ids2indices(sets, rownames(logcpm))   # map symbols -> row indices
res <- camera(logcpm, idx, design, contrast="F")  # competitive, inter-gene-correlation adjusted
res$gene_set <- rownames(res)
res$n_in_set <- sapply(sets[res$gene_set], length)
res <- res[, c("gene_set","NGenes","n_in_set","Direction","PValue","FDR")]
res <- res[order(res$PValue), ]
write.csv(res, OUT, row.names=FALSE)
cat("\n=== camera (limma) competitive set test, donor-level fibrosis trend ===\n")
print(res, row.names=FALSE)
cat(sprintf("\nwrote %s\n", OUT))
