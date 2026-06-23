"""Are the 23 genome-wide fibrosis-trending genes (dge_genomewide.csv, FDR<0.05) hepatocyte-INTRINSIC
or COMPOSITIONAL/ambient (stromal/immune transcripts leaking into hepatocyte nuclei as fibrosis
expands the non-parenchymal compartment)? Two donor-level diagnostics on RAW counts:
  (1) CROSS-LINEAGE burden: depth-normalized UMIs/10k of each gene per cell lineage (all 99,809 cells,
      src/prep/10). A gene whose burden is far higher in a non-hep lineage than in hepatocytes is
      ambient-prone (its apparent rise in hep nuclei tracks how much of that lineage the donor has).
  (2) AMBIENT-TRACKING: across biopsy donors, Spearman(hepatocyte-pseudobulk CPM, donor non-hep
      nuclei fraction). Stromal fraction rises with fibrosis; if a gene's hep-CPM tracks it, the
      "fibrosis trend" is compositional, not hepatocyte-intrinsic.
Output: dge_compositional.csv + per-gene verdict (intrinsic / compositional / mixed).
"""
import os, sys
import numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
P1=str(config.PAPER1)

def main():
    de=pd.read_csv(os.path.join(str(config.ANALYSIS_TABLES),'dge_genomewide.csv'))
    sig=de[de.fdr_trend<0.05]['gene'].tolist()
    ac=pd.read_csv(os.path.join(P1,'dge_genes_allcells.csv'),low_memory=False)
    ac['donor']=ac['donor'].astype(str)
    gpresent=[g for g in sig if g in ac.columns]
    print(f"testing {len(gpresent)} FDR<0.05 trend genes (present in extraction) for composition\n")
    # ---- (1) cross-lineage burden = UMIs/10k within each lineage ----
    lin=ac.groupby('annotation')
    Etot=lin['E_raw'].sum()
    burden={}  # gene -> {lineage: umis/10k}
    for g in gpresent:
        gsum=lin[g].sum()
        burden[g]={L: 1e4*gsum[L]/Etot[L] for L in Etot.index if Etot[L]>0}
    # ---- per-donor non-hep fraction (all cells) + biopsy hep-pseudobulk CPM ----
    md=pd.read_csv(os.path.join(P1,'metadata_all_cells.csv'),usecols=['Patient.ID','cell.annotation','Fibrosis.score..F0.4.'],low_memory=False).rename(
        columns={'Patient.ID':'donor','Fibrosis.score..F0.4.':'F'})
    md['donor']=md['donor'].astype(str); md['F']=pd.to_numeric(md['F'],errors='coerce')
    Fd=md.groupby('donor')['F'].first()
    tot=md.groupby('donor').size(); nonhep=md[md['cell.annotation']!='Hepatocytes'].groupby('donor').size()
    nhf=(nonhep/tot).fillna(0)
    pb=pd.read_csv(os.path.join(P1,'pseudobulk_hep_by_donor.csv')).set_index('gene'); pb.columns=pb.columns.astype(str)
    bdonors=[d for d in pb.columns if not d.startswith('CL') and d in Fd.index and not np.isnan(Fd.get(d,np.nan))]
    lib=pb[bdonors].sum(axis=0); cpm=pb[bdonors]/lib*1e6
    nhf_b=np.array([nhf.get(d,np.nan) for d in bdonors]); fst=np.array([Fd[d] for d in bdonors])
    print(f"non-hep nuclei fraction vs fibrosis across {len(bdonors)} biopsy donors: "
          f"Spearman rho={stats.spearmanr(fst,nhf_b).correlation:+.2f} (stroma rises with fibrosis if +); "
          f"non-hep frac median {np.nanmedian(nhf_b):.2f}\n")
    rows=[]
    for g in gpresent:
        b=burden[g]; hepb=b.get('Hepatocytes',0.0)
        nonh={L:v for L,v in b.items() if L not in ('Hepatocytes','unknown','NA')}
        topL=max(nonh,key=nonh.get); topv=nonh[topL]
        ratio=topv/max(hepb,1e-9)
        r_amb=stats.spearmanr(nhf_b, cpm.loc[g].values).correlation if g in cpm.index else np.nan
        verdict=('compositional' if (ratio>=3 or (r_amb is not None and r_amb>0.5)) else
                 'intrinsic' if (ratio<1.5 and (r_amb is None or r_amb<0.3)) else 'mixed')
        rows.append(dict(gene=g,hep_burden=round(hepb,2),top_nonhep_lineage=topL,top_nonhep_burden=round(topv,2),
            nonhep_over_hep=round(ratio,2),corr_hepCPM_vs_nonhepFrac=round(r_amb,2),verdict=verdict))
    R=pd.DataFrame(rows).sort_values('nonhep_over_hep',ascending=False)
    R.to_csv(os.path.join(str(config.ANALYSIS_TABLES),'dge_compositional.csv'),index=False)
    vc=dict(R['verdict'].value_counts())
    print("per-gene verdict counts:", vc, "\n")
    print(f"{'gene':12s}{'hepBurd':>8}{'topNonHep':>13}{'tnhBurd':>9}{'nh/hep':>8}{'corrAmb':>8}  verdict")
    for _,r in R.iterrows():
        print(f"{r.gene:12s}{r.hep_burden:>8.2f}{str(r.top_nonhep_lineage):>13}{r.top_nonhep_burden:>9.2f}{r.nonhep_over_hep:>8.2f}{r.corr_hepCPM_vs_nonhepFrac:>8.2f}  {r.verdict}")
    print("\nwrote dge_compositional.csv")
    print("Read: compositional = burden >=3x higher in a non-hep lineage OR hep-CPM tracks stromal fraction")
    print("(rho>0.5). intrinsic = hepatocyte-dominant and independent of stromal load.")

if __name__=='__main__': main()
