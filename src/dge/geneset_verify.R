# ADVERSARIAL VERIFICATION of the pericentral-detox "dimming" gene-set finding.
# The concern: camera/GSEA-prerank are COMPETITIVE tests on CPM pseudobulk. CPM is
# compositional -- if biliary/EMT/IFN genes RISE with fibrosis they eat library budget and
# every other gene's CPM mechanically falls, so the detox set could read "Down" with no true
# per-hepatocyte dimming. Three composition controls here (R); Test 4 (within-PC depth-matched
# burden) is in geneset_verify_test4.py.
#
# TEST 1  CPM vs edgeR-TMM camera (TMM is robust to composition)
# TEST 2  limma::mroast  (SELF-CONTAINED rotation test -- absolute, not relative to transcriptome)
# TEST 3  contaminant removal: drop up-with-fibrosis genes (biliary/EMT/IFN set members + any gene
#         rho_F>0 & fdr_trend<0.05 in dge_genomewide.csv), renormalize (TMM), re-test detox sets.
#
# donor-level, biopsy-only F0-F4, exclude CL*/Healthy.  Output:
#   results/tables/analysis/geneset_verify_camera_cpm_vs_tmm.csv
#   results/tables/analysis/geneset_verify_roast.csv
#   results/tables/analysis/geneset_verify_decontam.csv
suppressMessages({library(limma); library(edgeR)})

root <- getwd()
P1  <- file.path(root, "data", "processed", "paper1")
SIG <- file.path(root, "data", "signatures")
OUTD<- file.path(root, "results", "tables", "analysis")

pb <- read.csv(file.path(P1, "pseudobulk_hep_by_donor.csv"), check.names=FALSE)
rownames(pb) <- pb$gene; pb$gene <- NULL
dm <- read.csv(file.path(P1, "donor_meta.csv"), check.names=FALSE); dm$donor <- as.character(dm$donor)
md <- read.csv(file.path(P1, "metadata_all_cells.csv"), check.names=FALSE)
Fcol <- "Fibrosis.score..F0.4."; md$donor <- as.character(md$Patient.ID)
Fmap <- tapply(suppressWarnings(as.numeric(md[[Fcol]])), md$donor, function(x) x[!is.na(x)][1])

src <- setNames(dm$stage, dm$donor)
donors <- colnames(pb)
keep <- sapply(donors, function(d)
  !startsWith(d, "CL") && (is.na(src[d]) || src[d] != "Healthy control") && !is.na(Fmap[d]))
donors <- donors[keep]
F <- as.numeric(Fmap[donors])
pb <- as.matrix(pb[, donors])
cat(sprintf("biopsy donors: %d  F dist (F0/F1/F2/F3/F4): %s\n", length(donors),
            paste(sapply(0:4, function(k) sum(F==k)), collapse="/")))

# expression filter (matches dge_genomewide.py / geneset_camera.R): CPM>=1 in >= half donors
lib0 <- colSums(pb); cpm0 <- t(t(pb)/lib0)*1e6
expr_ok <- rowSums(cpm0 >= 1) >= (length(donors) %/% 2)
pb <- pb[expr_ok, ]
cat(sprintf("genes tested (CPM>=1 in >= half donors): %d\n", nrow(pb)))

design <- model.matrix(~ F)

readset <- function(f) { x <- readLines(file.path(SIG, f)); x <- trimws(x); x[x!="" & !startsWith(x,"#")] }
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

# -------- log-expression matrices: CPM (as in original) and TMM --------------------------
logcpm <- log2(cpm0[expr_ok, ] + 1)                 # exactly the original metric
dge <- DGEList(counts = pb)
dge <- calcNormFactors(dge, method = "TMM")         # composition-robust norm factors
logtmm <- cpm(dge, log = TRUE, prior.count = 1)     # log2 CPM on TMM-effective library sizes
cat(sprintf("TMM norm factors range: %.3f - %.3f\n", min(dge$samples$norm.factors), max(dge$samples$norm.factors)))

idx <- ids2indices(sets, rownames(logcpm))

# ============================ TEST 1: camera CPM vs TMM ===================================
cam_cpm <- camera(logcpm, idx, design, contrast="F")
cam_tmm <- camera(logtmm, idx, design, contrast="F")
cam_cpm$gene_set <- rownames(cam_cpm); cam_tmm$gene_set <- rownames(cam_tmm)
m <- merge(cam_cpm[, c("gene_set","NGenes","Direction","PValue","FDR")],
           cam_tmm[, c("gene_set","Direction","PValue","FDR")],
           by="gene_set", suffixes=c("_CPM","_TMM"))
m <- m[order(m$FDR_TMM), ]
write.csv(m, file.path(OUTD, "geneset_verify_camera_cpm_vs_tmm.csv"), row.names=FALSE)
cat("\n=== TEST 1: camera CPM vs edgeR-TMM (donor-level fibrosis trend) ===\n")
print(m, row.names=FALSE, digits=3)

# ============================ TEST 2: mroast (self-contained) =============================
set.seed(0)
roast_res <- mroast(logtmm, idx, design, contrast="F", nrot=9999, set.statistic="mean")
roast_res$gene_set <- rownames(roast_res)
keepc <- intersect(c("gene_set","NGenes","PropDown","PropUp","Direction","PValue","FDR"), colnames(roast_res))
roast_out <- roast_res[, keepc]
roast_out <- roast_out[order(roast_out$PValue), ]
write.csv(roast_out, file.path(OUTD, "geneset_verify_roast.csv"), row.names=FALSE)
cat("\n=== TEST 2: mroast SELF-CONTAINED rotation test (TMM, absolute direction) ===\n")
print(roast_out, row.names=FALSE, digits=3)

# ============================ TEST 3: contaminant removal ================================
# up-with-fibrosis "budget eaters": members of biliary/EMT/IFN sets, PLUS genome-wide
# genes with rho_F>0 & fdr_trend<0.05.
gw <- read.csv(file.path(OUTD, "dge_genomewide.csv"), check.names=FALSE)
gw_up <- gw$gene[!is.na(gw$rho_F) & !is.na(gw$fdr_trend) & gw$rho_F > 0 & gw$fdr_trend < 0.05]
contam_sets <- unique(c(sets$cholangiocyte_ductular, sets$CTRL_EMT, sets$CTRL_interferon))
contam <- unique(c(contam_sets, gw_up))
drop_rows <- rownames(pb) %in% contam
cat(sprintf("\nTEST 3 contaminants dropped: %d (set members present + gw rho>0&FDR<0.05; gw_up=%d)\n",
            sum(drop_rows), length(intersect(gw_up, rownames(pb)))))

pb2 <- pb[!drop_rows, ]
dge2 <- calcNormFactors(DGEList(counts=pb2), method="TMM")   # renormalize AFTER removing eaters
logtmm2 <- cpm(dge2, log=TRUE, prior.count=1)
# also a plain renormalized-CPM version (no TMM) so we separate "remove eaters" from "use TMM"
lib2 <- colSums(pb2); logcpm2 <- log2(t(t(pb2)/lib2)*1e6 + 1)

detox_sets <- list(pericentral_anchors=sets$pericentral_anchors,
                   periportal_anchors =sets$periportal_anchors,
                   xenobiotic_CYP     =sets$xenobiotic_CYP,
                   detox_phase2       =sets$detox_phase2,
                   urea_cycle         =sets$urea_cycle)
idx2t <- ids2indices(detox_sets, rownames(logtmm2))
idx2c <- ids2indices(detox_sets, rownames(logcpm2))
cam_decontam_tmm <- camera(logtmm2, idx2t, design, contrast="F")
cam_decontam_cpm <- camera(logcpm2, idx2c, design, contrast="F")
cam_decontam_tmm$gene_set <- rownames(cam_decontam_tmm)
cam_decontam_cpm$gene_set <- rownames(cam_decontam_cpm)
d <- merge(cam_decontam_cpm[, c("gene_set","NGenes","Direction","PValue","FDR")],
           cam_decontam_tmm[, c("gene_set","Direction","PValue","FDR")],
           by="gene_set", suffixes=c("_decontamCPM","_decontamTMM"))
d <- d[order(d$PValue_decontamTMM), ]
write.csv(d, file.path(OUTD, "geneset_verify_decontam.csv"), row.names=FALSE)
cat("\n=== TEST 3: camera AFTER dropping up-with-fibrosis budget-eaters + renorm ===\n")
print(d, row.names=FALSE, digits=3)

cat("\nwrote 3 CSVs to results/tables/analysis/\n")
