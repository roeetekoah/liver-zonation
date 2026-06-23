"""Compositional audit of the Plan-A F4-vs-F1 hits (64 genes): are they hepatocyte-INTRINSIC or AMBIENT
(transcripts from another lineage — esp. cholangiocytes in the cirrhotic ductular reaction — leaking into
hepatocyte nuclei)? Two diagnostics on RAW counts (all 99,809 cells, src/prep/11):
 (1) CROSS-LINEAGE burden: depth-normalized UMIs/10k of each gene per lineage. A gene >=3x higher in a
     non-hepatocyte lineage than in hepatocytes is ambient-prone.
 (2) AMBIENT-TRACKING: across biopsy donors, Spearman(hepatocyte-pseudobulk CPM, donor cholangiocyte frac).
Output: results/tables/analysis/dge_planA_compositional.csv
"""
import os, sys
import numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
P1=str(config.PAPER1)

def main():
    ac=pd.read_csv(os.path.join(P1,'planA_hits_allcells.csv'),low_memory=False); ac['donor']=ac['donor'].astype(str)
    genes=[c for c in ac.columns if c not in ('cell_id','donor','annotation','E_raw')]
    tt=pd.read_csv(os.path.join(str(config.ANALYSIS_TABLES),'dge_planA_F4vsF1.csv'),index_col=0)
    lin=ac.groupby('annotation'); Etot=lin['E_raw'].sum()
    # per-donor cholangiocyte fraction + biopsy hep-pseudobulk CPM
    md=pd.read_csv(os.path.join(P1,'metadata_all_cells.csv'),usecols=['Patient.ID','Fibrosis.score..F0.4.','cell.annotation'],low_memory=False)
    md['donor']=md['Patient.ID'].astype(str); md['F']=pd.to_numeric(md['Fibrosis.score..F0.4.'],errors='coerce')
    bi=md[(~md['donor'].str.startswith('CL'))&(md['F'].notna())]
    tot=bi.groupby('donor').size(); chol=bi[bi['cell.annotation']=='Cholangiocytes'].groupby('donor').size()
    cfrac=(chol/tot).reindex(tot.index).fillna(0)
    pb=pd.read_csv(os.path.join(P1,'pseudobulk_hep_by_donor.csv')).set_index('gene'); pb.columns=pb.columns.astype(str)
    bd=[d for d in pb.columns if d in cfrac.index]; lib=pb[bd].sum(axis=0); cpm=pb[bd]/lib*1e6
    cf=np.array([cfrac[d] for d in bd])
    rows=[]
    for g in genes:
        gsum=lin[g].sum(); burden={L:1e4*gsum[L]/Etot[L] for L in Etot.index if Etot[L]>0}
        hep=burden.get('Hepatocytes',0.0)
        nonh={L:v for L,v in burden.items() if L not in ('Hepatocytes','unknown')}
        topL=max(nonh,key=nonh.get); ratio=nonh[topL]/max(hep,1e-9)
        chb=burden.get('Cholangiocytes',0.0)
        r_amb=stats.spearmanr(cf,cpm.loc[g].values).correlation if g in cpm.index else np.nan
        verdict=('ambient' if (ratio>=3 or (r_amb==r_amb and r_amb>0.5)) else
                 'intrinsic' if (ratio<1.5 and (r_amb!=r_amb or r_amb<0.3)) else 'mixed')
        rows.append(dict(gene=g,logFC=round(tt.loc[g,'logFC'],2) if g in tt.index else np.nan,
            hep_burden=round(hep,2),top_nonhep=topL,top_nonhep_burden=round(nonh[topL],2),
            chol_burden=round(chb,2),nonhep_over_hep=round(ratio,2),
            corr_hepCPM_vs_cholFrac=round(r_amb,2),verdict=verdict))
    R=pd.DataFrame(rows).sort_values('nonhep_over_hep',ascending=False)
    R.to_csv(os.path.join(str(config.ANALYSIS_TABLES),'dge_planA_compositional.csv'),index=False)
    vc=dict(R['verdict'].value_counts()); print("verdicts:",vc,"\n")
    focus=['EPCAM','SOX4','SOX9','GRHL2','SPINT2','B3GNT3','CXCL10','KRT7','KRT19','A2M','ESRRG']
    print(f"{'gene':10s}{'logFC':>7}{'hepBurd':>8}{'topNonHep':>14}{'tnhBurd':>8}{'nh/hep':>7}{'corrChol':>9}  verdict")
    for _,r in R[R.gene.isin(focus)].iterrows():
        print(f"{r.gene:10s}{r.logFC:>7.1f}{r.hep_burden:>8.2f}{str(r.top_nonhep)[:13]:>14}{r.top_nonhep_burden:>8.2f}{r.nonhep_over_hep:>7.1f}{r.corr_hepCPM_vs_cholFrac:>9.2f}  {r.verdict}")
    print(f"\nOf {len(R)} Plan-A hits: {vc.get('ambient',0)} ambient, {vc.get('mixed',0)} mixed, {vc.get('intrinsic',0)} intrinsic.")
    print("wrote dge_planA_compositional.csv")

if __name__=='__main__': main()
