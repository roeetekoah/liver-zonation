# decontX ambient-removal -> re-pseudobulk biopsy hepatocytes -> re-run Plan A (F4-vs-F1).
# THE test of ambient-vs-real for the biliary/transdiff program (F18). decontX uses the cell-type labels
# to estimate, per cell, how much of its counts are contamination from OTHER lineages (e.g. cholangiocyte
# EPCAM appearing inside a hepatocyte nucleus), and subtracts it. If EPCAM/SOX4/SOX9/GRHL2 VANISH from the
# F4-vs-F1 result after decontamination -> ambient. If they SURVIVE -> likely real hepatocyte signal.
suppressMessages({library(SeuratObject); library(Matrix); library(decontX); library(edgeR)})
RDS<-"data/raw/GSE202379_SeuratObject_AllCells.rds/GSE202379_SeuratObject_AllCells.rds"
P1<-"data/processed/paper1"; OUT<-"results/tables/analysis"
cat("reading RDS...\n"); flush.console()
obj<-readRDS(RDS); if(inherits(obj[["RNA"]],"Assay5")) obj[["RNA"]]<-JoinLayers(obj[["RNA"]])
cnt<-tryCatch(LayerData(obj,assay="RNA",layer="counts"),error=function(e) GetAssayData(obj,assay="RNA",slot="counts"))
md<-obj@meta.data
z<-as.character(md$cell.annotation); z[is.na(z)|z==""]<-"unknown"
donor<-as.character(md$Patient.ID); stage<-as.character(md$Disease.status)
cat("decontX on",ncol(cnt),"cells x",nrow(cnt),"genes (uses cell-type labels)...\n"); flush.console()
set.seed(0); dx<-decontX(cnt, z=z)
dec<-if(!is.null(dx$decontXcounts)) dx$decontXcounts else decontXcounts(dx)
contam<-if(!is.null(dx$contamination)) dx$contamination else dx$estimates
cat("mean per-cell contamination est:",round(mean(contam),3),
    " | hepatocytes:",round(mean(contam[z=="Hepatocytes"]),3),"\n")

# pseudobulk biopsy hepatocyte DECONTAMINATED counts per donor
hep<- z=="Hepatocytes" & !startsWith(donor,"CL") & stage!="Healthy control"
hd<-donor[hep]; dech<-dec[,hep]; donors<-sort(unique(hd))
pb<-sapply(donors,function(d) Matrix::rowSums(dech[,hd==d,drop=FALSE])); rownames(pb)<-rownames(dec)
pb<-round(pb)
write.csv(data.frame(gene=rownames(pb),pb,check.names=FALSE), file.path(P1,"pseudobulk_hep_decontx.csv"), row.names=FALSE)

# edgeR Plan A F4 vs F1 on decontaminated pseudobulk
bq<-read.csv(file.path(OUT,"batch_qc.csv")); bq$donor<-as.character(bq$donor)
dm<-read.csv(file.path(P1,"donor_meta.csv")); dm$donor<-as.character(dm$donor)
meta<-merge(bq,dm[,c("donor","n_hep")],by="donor"); meta<-meta[meta$donor %in% colnames(pb),]
bi<-meta[meta$source=="biopsy"&!is.na(meta$F)&meta$n_hep>=50,]
cols<-as.character(bi$donor); bi<-bi[match(cols,bi$donor),]
Ff<-factor(paste0("F",bi$F)); design<-model.matrix(~0+Ff); colnames(design)<-levels(Ff)
y<-DGEList(counts=pb[,cols]); keep<-filterByExpr(y,design=design); y<-y[keep,,keep.lib.sizes=FALSE]
y<-calcNormFactors(y); y<-estimateDisp(y,design,robust=TRUE); fit<-glmQLFit(y,design,robust=TRUE)
tt<-topTags(glmQLFTest(fit,contrast=makeContrasts(F4-F1,levels=design)),n=Inf)$table
write.csv(tt,file.path(OUT,"dge_planA_decontx_F4vsF1.csv"))
bil<-c("EPCAM","SOX4","SOX9","GRHL2","SPINT2","B3GNT3","CXCL10")
zon<-c("GLUL","CYP3A4","CYP2E1","CYP1A2","ADH4","AKR1D1","SLCO1B3","CPS1","ASS1","ALDOB","PCK1","HAL","ARG1")
cat("\n======== Plan A F4-vs-F1 AFTER decontX ========\n")
cat("genes tested:",nrow(tt)," | FDR<0.05:",sum(tt$FDR<0.05)," (was 64 before decontX)\n")
cat("\nBILIARY genes after decontX (were FDR ~1e-3 to 1e-6, logFC +2.3 to +3.1 before):\n")
print(tt[rownames(tt)%in%bil, c("logFC","PValue","FDR")])
cat("\nzonation genes after decontX (n FDR<0.05):",sum(tt[rownames(tt)%in%zon,"FDR"]<0.05),"of",sum(rownames(tt)%in%zon),"\n")
cat("\ntop 15 surviving hits:\n"); print(head(tt[order(tt$FDR),c("logFC","FDR")],15))
cat("\nDONE\n")
