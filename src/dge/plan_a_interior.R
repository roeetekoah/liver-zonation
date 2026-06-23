# Plan A, INTERIOR contrasts: F3-vs-F1 and F2-vs-F1 (pre-cirrhotic) — does anything change BEFORE the
# cirrhotic ductular-reaction ambient floods in at F4? Same edgeR model as plan_a_genomewide.R.
suppressMessages(library(edgeR))
P1<-"data/processed/paper1"; OUT<-"results/tables/analysis"
pb<-as.matrix(read.csv(file.path(P1,"pseudobulk_hep_by_donor.csv"),row.names=1,check.names=FALSE))
bq<-read.csv(file.path(OUT,"batch_qc.csv")); bq$donor<-as.character(bq$donor)
dm<-read.csv(file.path(P1,"donor_meta.csv")); dm$donor<-as.character(dm$donor)
meta<-merge(bq,dm[,c("donor","n_hep")],by="donor")
bi<-meta[meta$source=="biopsy"&!is.na(meta$F)&meta$n_hep>=50,]; bi<-bi[as.character(bi$donor)%in%colnames(pb),]
cols<-as.character(bi$donor); bi<-bi[match(cols,bi$donor),]
Ff<-factor(paste0("F",bi$F)); design<-model.matrix(~0+Ff); colnames(design)<-levels(Ff)
y<-DGEList(counts=pb[,cols]); keep<-filterByExpr(y,design=design); y<-y[keep,,keep.lib.sizes=FALSE]
y<-calcNormFactors(y); y<-estimateDisp(y,design,robust=TRUE); fit<-glmQLFit(y,design,robust=TRUE)
zon<-c("GLUL","CYP3A4","CYP2E1","CYP1A2","ADH4","AKR1D1","SLCO1B3","CPS1","ASS1","ALDOB","PCK1","HAL","ARG1")
bil<-c("EPCAM","SOX4","SOX9","GRHL2","SPINT2","CXCL10")
for(cn in c("F3-F1","F2-F1")){
  con<-makeContrasts(contrasts=cn,levels=design)
  tt<-topTags(glmQLFTest(fit,contrast=con),n=Inf)$table
  write.csv(tt,file.path(OUT,paste0("dge_planA_",gsub("-","vs",cn),".csv")))
  cat("\n================",cn,"================\n")
  cat("genes FDR<0.05:",sum(tt$FDR<0.05)," | FDR<0.10:",sum(tt$FDR<0.10),"\n")
  cat("top 8:\n"); print(head(tt[order(tt$FDR),c("logFC","FDR")],8))
  cat("biliary genes:\n"); print(tt[rownames(tt)%in%bil,c("logFC","FDR")])
  cat("zonation genes (n FDR<0.05):",sum(tt[rownames(tt)%in%zon,"FDR"]<0.05),"of",sum(rownames(tt)%in%zon),"\n")
}
cat("\nDONE\n")
