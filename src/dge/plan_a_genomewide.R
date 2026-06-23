# PLAN A — genome-wide discovery DGE across biopsy fibrosis (v3 plan, writeup/DGE.md).
# Question: given preserved zonation, what ELSE changes with fibrosis? Discovery, data-driven.
# Method: pseudobulk per donor (raw UMIs, hepatocytes) -> edgeR TMM + QLF (robust). Biopsy-only.
# Primary = F4-vs-F1 contrast; secondary = omnibus across F0-F4. Controls: housekeeping (must be flat),
# zonation genes (expected flat = preserved), MDS by run vs by fibrosis (batch pre-flight, F17).
suppressMessages(library(edgeR))
P1 <- "data/processed/paper1"; OUT <- "results/tables/analysis"; FIG <- "results/figures/h2"
pb <- as.matrix(read.csv(file.path(P1,"pseudobulk_hep_by_donor.csv"), row.names=1, check.names=FALSE))
bq <- read.csv(file.path(OUT,"batch_qc.csv"), stringsAsFactors=FALSE); bq$donor <- as.character(bq$donor)
dm <- read.csv(file.path(P1,"donor_meta.csv"), stringsAsFactors=FALSE); dm$donor <- as.character(dm$donor)
meta <- merge(bq, dm[,c("donor","n_hep")], by="donor")

# biopsy donors, fibrosis known, >=50 nuclei (locked min-nuclei filter)
bi <- meta[meta$source=="biopsy" & !is.na(meta$F) & meta$n_hep>=50, ]
bi <- bi[as.character(bi$donor) %in% colnames(pb), ]
cat("biopsy donors total:", sum(meta$source=="biopsy" & !is.na(meta$F)),
    " | kept (n_hep>=50):", nrow(bi), "\n")
cat("F distribution after filter:", paste(table(factor(bi$F,levels=0:4)), collapse="/"), "(F0..F4)\n")
cat("min/median nuclei/donor:", min(bi$n_hep), "/", median(bi$n_hep), "\n\n")

cols <- as.character(bi$donor); bi <- bi[match(cols, bi$donor), ]
Ff <- factor(paste0("F", bi$F)); design <- model.matrix(~0+Ff); colnames(design) <- levels(Ff)
y <- DGEList(counts=pb[, cols])
keep <- filterByExpr(y, design=design); cat("genes kept (filterByExpr):", sum(keep), "of", nrow(y), "\n")
y <- y[keep,, keep.lib.sizes=FALSE]
y <- calcNormFactors(y)                       # TMM
y <- estimateDisp(y, design, robust=TRUE)
cat("common BCV:", round(sqrt(y$common.dispersion),3), "\n")
fit <- glmQLFit(y, design, robust=TRUE)

# --- PRIMARY: F4 vs F1 ---
con <- makeContrasts(F4-F1, levels=design)
tt <- topTags(glmQLFTest(fit, contrast=con), n=Inf)$table
write.csv(tt, file.path(OUT,"dge_planA_F4vsF1.csv"))
cat("\n================ PLAN A primary: F4 vs F1 ================\n")
cat("genes FDR<0.05:", sum(tt$FDR<0.05), "\n")
print(head(tt[order(tt$FDR), c("logFC","logCPM","PValue","FDR")], 20))

# --- SECONDARY: omnibus across F0-F4 ---
om <- topTags(glmQLFTest(fit, contrast=makeContrasts(F1-F0,F2-F0,F3-F0,F4-F0, levels=design)), n=Inf)$table
write.csv(om, file.path(OUT,"dge_planA_omnibus.csv"))
cat("\n=== omnibus (secondary screen, across F0-F4): genes FDR<0.05:", sum(om$FDR<0.05), "===\n")

# --- CONTROLS ---
hk  <- c("ACTB","GAPDH","B2M","MALAT1","ACTG1","PPIA","TBP")
zon <- c("GLUL","CYP3A4","CYP2E1","CYP1A2","ADH4","AKR1D1","SLCO1B3","CPS1","ASS1","ALDOB","PCK1","HAL","ARG1")
cat("\n=== CONTROL — housekeeping (MUST be flat) F4vsF1 ===\n")
print(tt[rownames(tt) %in% hk, c("logFC","PValue","FDR")])
cat("\n=== zonation genes (expected flat = preserved) F4vsF1 ===\n")
print(tt[rownames(tt) %in% zon, c("logFC","PValue","FDR")])

# --- MDS pre-flight: run vs fibrosis ---
png(file.path(FIG,"dge_mds.png"), width=1500, height=720, res=150); par(mfrow=c(1,2))
plotMDS(y, col=as.integer(factor(bi$run)), pch=16, main="MDS — colour = SLX run (batch)")
plotMDS(y, col=as.integer(factor(bi$F))+1, pch=16, main="MDS — colour = fibrosis F")
dev.off()
cat("\nwrote dge_planA_F4vsF1.csv, dge_planA_omnibus.csv, dge_mds.png\n")
