"""GENOME-WIDE donor-level differential expression across biopsy fibrosis F0-F4.
Purpose: test the manuscript claim that the xenobiotic/detox attenuation is the ONLY biopsy-internal
change. We did NOT do this before (panel only) — this is transcriptome-wide.

Unit = donor (pseudobulk = sum of RAW UMIs over each donor's hepatocyte nuclei; src/prep/09).
Restrict to acquisition-matched biopsy donors (non-CL, non-Healthy). Two count-based readouts:
  (a) TREND: Spearman rho of log2-CPM vs fibrosis stage F across donors  (BH-FDR)
  (b) CONTRAST: F1-group vs F4 Mann-Whitney on log2-CPM + median log2FC
Genes filtered to those expressed (CPM>=1) in >= half the biopsy donors. Report: # significant,
top up/down, and exactly where the detox panel genes rank.  Output: dge_genomewide.csv
"""
import os, sys
import numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
P1=str(config.PAPER1)
DETOX=['CYP2E1','CYP1A2','ADH4','AKR1D1','SLCO1B3']; PCID=['GLUL','CYP3A4']
PANEL=DETOX+PCID+['ASS1','CPS1','PCK1','HAL','ALDOB','ARG1']

def main():
    pb=pd.read_csv(os.path.join(P1,'pseudobulk_hep_by_donor.csv'),low_memory=False).set_index('gene')
    dm=pd.read_csv(os.path.join(P1,'donor_meta.csv'),low_memory=False); dm['donor']=dm['donor'].astype(str)
    md=pd.read_csv(os.path.join(P1,'metadata_all_cells.csv'),
        usecols=['Patient.ID','Fibrosis.score..F0.4.'],low_memory=False).rename(
        columns={'Patient.ID':'donor','Fibrosis.score..F0.4.':'F'})
    md['donor']=md['donor'].astype(str); md['F']=pd.to_numeric(md['F'],errors='coerce')
    F=md.groupby('donor')['F'].first()
    pb.columns=pb.columns.astype(str)
    # biopsy donors only: non-CL, non-Healthy, with a fibrosis score
    src=dm.set_index('donor')['stage']
    donors=[d for d in pb.columns if not d.startswith('CL') and str(src.get(d,''))!='Healthy control'
            and d in F.index and not np.isnan(F.get(d,np.nan))]
    pb=pb[donors]; f=np.array([F[d] for d in donors]); n_hep=dm.set_index('donor')['n_hep'].reindex(donors).values
    print(f"biopsy hepatocyte donors: {len(donors)}  (F dist: {[int((f==k).sum()) for k in [0,1,2,3,4]]})")
    print(f"min nuclei/donor in pseudobulk: {int(np.nanmin(n_hep))}, median {int(np.nanmedian(n_hep))}")
    # CPM
    lib=pb.sum(axis=0).values; cpm=pb.values/lib[None,:]*1e6; logcpm=np.log2(cpm+1)
    # expression filter: CPM>=1 in >= half the donors
    keep=(cpm>=1).sum(axis=1) >= (len(donors)//2)
    genes=pb.index.values[keep]; L=logcpm[keep]; C=cpm[keep]
    print(f"genes tested (expressed CPM>=1 in >= {len(donors)//2} donors): {len(genes)} of {pb.shape[0]}")
    # (a) trend across F
    rho=np.array([stats.spearmanr(f, L[i]).correlation for i in range(len(genes))])
    pt=np.array([stats.spearmanr(f, L[i]).pvalue for i in range(len(genes))])
    # (b) F1 vs F4 contrast
    i1=np.where(f==1)[0]; i4=np.where(f==4)[0]
    def mw(row):
        try: return stats.mannwhitneyu(row[i1],row[i4],alternative='two-sided').pvalue
        except Exception: return np.nan
    pc=np.array([mw(L[i]) for i in range(len(genes))])
    med1=np.median(C[:,i1],axis=1); med4=np.median(C[:,i4],axis=1)
    lfc=np.log2((med4+1)/(med1+1))
    # BH-FDR on the trend test
    order=np.argsort(pt); ranks=np.empty_like(order); ranks[order]=np.arange(1,len(pt)+1)
    fdr=pt*len(pt)/ranks; fdr=np.minimum.accumulate(fdr[order][::-1])[::-1]; q=np.empty_like(fdr); q[order]=fdr
    out=pd.DataFrame(dict(gene=genes,rho_F=np.round(rho,3),p_trend=pt,fdr_trend=np.round(q,4),
        med_cpm_F1=np.round(med1,1),med_cpm_F4=np.round(med4,1),log2FC_F4_F1=np.round(lfc,2),p_F1vF4=np.round(pc,4)))
    out=out.sort_values('p_trend')
    out.to_csv(os.path.join(str(config.ANALYSIS_TABLES),'dge_genomewide.csv'),index=False)
    sig=out[out.fdr_trend<0.05]
    print(f"\n=== genome-wide trend (Spearman vs F, BH-FDR<0.05): {len(sig)} genes ===")
    print("  top 25 by trend p-value (rho<0 = decreases with fibrosis):")
    for _,r in out.head(25).iterrows():
        tag=' <DETOX>' if r.gene in DETOX else (' <PCID>' if r.gene in PCID else '')
        print(f"    {r.gene:12s} rho={r.rho_F:+.2f}  fdr={r.fdr_trend:.3f}  CPM {r.med_cpm_F1:.0f}->{r.med_cpm_F4:.0f}  log2FC={r.log2FC_F4_F1:+.2f}{tag}")
    print("\n  where do the detox/identity panel genes rank (of %d tested)?" % len(genes))
    out=out.reset_index(drop=True)
    for g in PANEL:
        row=out[out.gene==g]
        if len(row): r=row.iloc[0]; print(f"    {g:10s} rank {row.index[0]+1:5d}  rho={r.rho_F:+.2f} fdr={r.fdr_trend:.3f} log2FC={r.log2FC_F4_F1:+.2f}")
        else: print(f"    {g:10s} (filtered out: low expression)")
    print("\nwrote dge_genomewide.csv")

if __name__=='__main__': main()
