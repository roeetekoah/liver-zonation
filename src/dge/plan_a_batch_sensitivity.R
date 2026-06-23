# PLAN A batch sensitivity (answers methodological-review Objection 1, finding F17).
# The F1-vs-F4 contrast is partly confounded with sequencing run: the 4 cirrhotic-F4 biopsy
# donors sit on SLX-20270 (12,22) and SLX-20290 (68,75), but ONLY SLX-20290 also carries an
# F1 donor. So we test whether the 64 biliary hits survive once run is controlled:
#   (A) batch-adjusted: restrict to the 2 F4-bearing runs, fit ~run + fibrosis, contrast F4-F1.
#   (B) pure within-run: SLX-20290 only (the one run with BOTH F1 and F4), contrast F4-F1.
# Plus the omnibus count and a monotonicity read (is each hit a graded trend or only an F4 jump?).
suppressMessages(library(edgeR))
P1 <- "data/processed/paper1"; OUT <- "results/tables/analysis"
pb <- as.matrix(read.csv(file.path(P1,"pseudobulk_hep_by_donor.csv"), row.names=1, check.names=FALSE))
bq <- read.csv(file.path(OUT,"batch_qc.csv"), stringsAsFactors=FALSE); bq$donor <- as.character(bq$donor)
dm <- read.csv(file.path(P1,"donor_meta.csv"), stringsAsFactors=FALSE); dm$donor <- as.character(dm$donor)
meta <- merge(bq, dm[,c("donor","n_hep")], by="donor")
bi <- meta[meta$source=="biopsy" & !is.na(meta$F) & meta$n_hep>=50, ]
bi <- bi[as.character(bi$donor) %in% colnames(pb), ]
HEAD <- c("EPCAM","GRHL2","SPINT2","SOX9","SOX4","B3GNT3","CXCL10","KCNJ16")

run_edger <- function(sub, design, contrast, label){
  cols <- as.character(sub$donor)
  y <- DGEList(counts=pb[, cols]); keep <- filterByExpr(y, design=design)
  y <- y[keep,,keep.lib.sizes=FALSE]; y <- calcNormFactors(y)
  y <- estimateDisp(y, design, robust=TRUE); fit <- glmQLFit(y, design, robust=TRUE)
  tt <- topTags(glmQLFTest(fit, contrast=contrast), n=Inf)$table
  cat("\n================", label, "================\n")
  cat("donors:", nrow(sub), " genes kept:", sum(keep), " common BCV:", round(sqrt(y$common.dispersion),3),
      " | total FDR<0.05:", sum(tt$FDR<0.05), "\n")
  h <- tt[rownames(tt) %in% HEAD, c("logFC","PValue","FDR")]
  print(h[order(h$FDR), ])
  invisible(tt)
}

# (A) batch-adjusted across the two F4-bearing runs --------------------------------
ab <- bi[bi$run %in% c("SLX-20270","SLX-20290"), ]
cat("(A) runs SLX-20270 + SLX-20290 — fibrosis x run table:\n")
print(table(F=factor(ab$F,levels=0:4), run=ab$run))
batch <- factor(ab$run); Ff <- factor(paste0("F", ab$F))
dA <- model.matrix(~ batch + Ff);
conA <- numeric(ncol(dA)); names(conA) <- colnames(dA); conA["FfF4"] <- 1; conA["FfF1"] <- -1
run_edger(ab, dA, conA, "(A) BATCH-ADJUSTED  F4-vs-F1  (~run + fibrosis, 2 F4-bearing runs)")

# (B) pure within-run: SLX-20290 only (carries both F1 and F4) ---------------------
b9 <- bi[bi$run=="SLX-20290", ]
cat("\n(B) SLX-20290 only — fibrosis counts:", paste(table(factor(b9$F,levels=0:4)),collapse="/"),"(F0..F4)\n")
Ff9 <- factor(paste0("F", b9$F)); d9 <- model.matrix(~0+Ff9); colnames(d9) <- levels(Ff9)
con9 <- makeContrasts(F4-F1, levels=d9)
run_edger(b9, d9, con9, "(B) WITHIN-RUN SLX-20290  F4-vs-F1  (2 F4 vs 3 F1, same run)")

# omnibus + monotonicity from already-saved tables ---------------------------------
om <- read.csv(file.path(OUT,"dge_planA_omnibus.csv"), row.names=1)
cat("\n=== omnibus across F0-F4 (already saved): genes FDR<0.05 =", sum(om$FDR<0.05), "===\n")
f2 <- read.csv(file.path(OUT,"dge_planA_F2vsF1.csv"), row.names=1)
f3 <- read.csv(file.path(OUT,"dge_planA_F3vsF1.csv"), row.names=1)
f4 <- read.csv(file.path(OUT,"dge_planA_F4vsF1.csv"), row.names=1)
cat("\n=== monotonicity: headline-gene logFC at each step vs F1 (is it graded or an F4-only jump?) ===\n")
mono <- data.frame(F2vF1=f2[HEAD,"logFC"], F3vF1=f3[HEAD,"logFC"], F4vF1=f4[HEAD,"logFC"],
                   F4_FDR=f4[HEAD,"FDR"], row.names=HEAD)
print(round(mono,3))
