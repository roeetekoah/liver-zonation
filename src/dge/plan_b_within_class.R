# PLAN B — within-class discovery DGE. Classify each biopsy hepatocyte nucleus PC / PP / null / dual by
# ambient-robust (>=2 UMI) anchor detection, then pseudobulk the FULL transcriptome per donor WITHIN each
# class and run edgeR F4-vs-F1 within each class. Question (v3 rationale): given preserved zonation, does the
# gene program shift INSIDE a stable zonal population? Classifier genes excluded from the DE (no circularity).
# Read alongside class COUNTS (a flat within-class result + shifted counts != "no change").
suppressMessages({library(SeuratObject); library(Matrix); library(edgeR)})
RDS<-"data/raw/GSE202379_SeuratObject_AllCells.rds/GSE202379_SeuratObject_AllCells.rds"
P1<-"data/processed/paper1"; OUT<-"results/tables/analysis"
cat("reading RDS...\n"); flush.console()
obj<-readRDS(RDS); if(inherits(obj[["RNA"]],"Assay5")) obj[["RNA"]]<-JoinLayers(obj[["RNA"]])
cnt<-tryCatch(LayerData(obj,assay="RNA",layer="counts"),error=function(e) GetAssayData(obj,assay="RNA",slot="counts"))
md<-obj@meta.data; donor<-as.character(md$Patient.ID); stage<-as.character(md$Disease.status); annot<-as.character(md$cell.annotation)
hepbi<- annot=="Hepatocytes" & !startsWith(donor,"CL") & stage!="Healthy control"
cat("biopsy hepatocyte nuclei:",sum(hepbi),"\n")
PCg<-c("GLUL","CYP3A4"); PPg<-c("ASS1","PCK1","HAL","ALDOB")
PCd<- Matrix::colSums(cnt[PCg,]>=2)>=1            # any PC anchor at >=2 UMI (ambient-robust)
PPd<- Matrix::colSums(cnt[PPg,]>=2)>=2            # >=2 PP anchors at >=2 UMI
cls<- ifelse(PCd&!PPd,"PC", ifelse(PPd&!PCd,"PP", ifelse(PCd&PPd,"dual","null")))
cls[!hepbi]<-NA
cat("class counts (biopsy hep):",paste(names(table(cls)),table(cls),sep="=",collapse="  "),"\n")
bq<-read.csv(file.path(OUT,"batch_qc.csv")); bq$donor<-as.character(bq$donor)
dm<-read.csv(file.path(P1,"donor_meta.csv")); dm$donor<-as.character(dm$donor)
meta<-merge(bq,dm[,c("donor","n_hep")],by="donor")
zon<-c("GLUL","CYP3A4","CYP2E1","CYP1A2","ADH4","AKR1D1","SLCO1B3","CPS1","ASS1","ALDOB","PCK1","HAL","ARG1")
excl<-c(PCg,PPg)
for(K in c("PC","PP","null","dual")){
  inK<- which(cls==K)
  dK<-donor[inK]; tab<-table(dK); keepd<-names(tab)[tab>=30]   # >=30 nuclei/donor-class
  keepd<-intersect(keepd, meta$donor[meta$source=="biopsy" & !is.na(meta$F)])
  cat("\n==== class",K,": donors with >=30 nuclei:",length(keepd),"====\n")
  if(length(keepd)<6){cat("  too few donors, skipping\n"); next}
  pb<-sapply(keepd,function(d) Matrix::rowSums(cnt[,inK[dK==d],drop=FALSE])); rownames(pb)<-rownames(cnt)
  bi<-meta[match(keepd,meta$donor),]
  Fdist<-table(factor(bi$F,levels=0:4)); cat("  F dist:",paste(Fdist,collapse="/"),"(F0..F4)\n")
  if(sum(bi$F==4)<2 | sum(bi$F==1)<2){cat("  not enough F1/F4 donors for contrast, skipping\n"); next}
  Ff<-factor(paste0("F",bi$F)); design<-model.matrix(~0+Ff); colnames(design)<-levels(Ff)
  y<-DGEList(counts=pb[!rownames(pb)%in%excl, keepd]); k<-filterByExpr(y,design=design); y<-y[k,,keep.lib.sizes=FALSE]
  y<-calcNormFactors(y); y<-estimateDisp(y,design,robust=TRUE); fit<-glmQLFit(y,design,robust=TRUE)
  if(!all(c("F1","F4")%in%colnames(design))){cat("  F1/F4 not both present, skipping contrast\n"); next}
  tt<-topTags(glmQLFTest(fit,contrast=makeContrasts(F4-F1,levels=design)),n=Inf)$table
  write.csv(tt,file.path(OUT,paste0("dge_planB_",K,"_F4vsF1.csv")))
  cat("  genes FDR<0.05:",sum(tt$FDR<0.05)," | zonation genes FDR<0.05:",sum(tt[rownames(tt)%in%zon,"FDR"]<0.05,na.rm=TRUE),"\n")
  cat("  top 6:\n"); print(head(tt[order(tt$FDR),c("logFC","FDR")],6))
}
cat("\nDONE\n")
