"""Cross-lineage stress, SEGMENTED by program (IEG / heat-shock / HIF) and per gene — robust rebuild of
the old cross-lineage stress table (which used deprecated UMIs/10k donor-medians). Stress is defined per
the project's stress definition (see memory): two acute classes folded into the stress module, plus a
SEPARATE hypoxia/HIF panel kept apart on purpose (chronic low-O2 != acute handling).

Programs:
  IEG  = FOS, JUN, JUNB, JUND, ATF3, DUSP1      (immediate-early; dissociation/handling artifact)
  HSP  = HSPA1A, HSPA1B                          (heat-shock / proteotoxic-ischemic)
  HIF  = VEGFA, SLC2A1, LDHA, CA9, ENO1, PGK1, HSP90AA1  (hypoxia; NOT part of the stress module)
Metric per (cell_type, source, donor, program): mean DEPTH-MATCHED UMIs/cell = binomial down-thinning of
each cell's module-sum to budget B=1500 (cells below B dropped), Monte-Carlo averaged over 4 draws; plus
det2 = fraction with raw module-sum >= 2 (ambient-robust). Unit = donor. Output:
findings/stress_celltype_segmented/{per_donor,by_lineage}.csv
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
B=1500; NDRAW=4
PROG={'IEG':['FOS','JUN','JUNB','JUND','ATF3','DUSP1'],'HSP':['HSPA1A','HSPA1B'],
      'HIF':['VEGFA','SLC2A1','LDHA','CA9','ENO1','PGK1','HSP90AA1']}
LINS=['Hepatocytes','Endothelial','Stellate','Macrophages','Cholangiocytes','Lymphocytes']

def dm_mean(vals,E):
    m=E>=B
    if m.sum()==0: return np.nan
    rng=np.random.RandomState(0); p=B/E[m]; acc=np.zeros(m.sum())
    for _ in range(NDRAW): acc+=rng.binomial(vals[m].astype(int),p)
    return (acc/NDRAW).mean()

def main():
    df=pd.read_csv(os.path.join(str(config.PAPER1),'raw_panel_counts.csv'),low_memory=False)
    df['donor']=df['donor'].astype(str)
    df['source']=np.where(df['donor'].str.startswith('CL'),'explant',
                  np.where(df['stage']=='Healthy control','healthy','biopsy'))
    for prog,genes in PROG.items():
        g=[x for x in genes if x in df.columns]; df[prog]=df[g].sum(axis=1)
    rows=[]
    for (lin,src,donor),s in df[df['annotation'].isin(LINS)].groupby(['annotation','source','donor']):
        E=s['E_raw'].values
        for prog in PROG:
            v=s[prog].values.astype(float)
            rows.append(dict(cell_type=lin,source=src,donor=donor,program=prog,nCells=len(s),
                dm_mean=round(dm_mean(v,E),4), det2=round((v>=2).mean(),4)))
    PD=pd.DataFrame(rows)
    outd=os.path.join('findings','stress_celltype_segmented'); os.makedirs(outd,exist_ok=True)
    PD.to_csv(os.path.join(outd,'per_donor.csv'),index=False)
    # by lineage x source x program: mean across donors
    G=PD.groupby(['cell_type','source','program']).agg(nDonors=('donor','nunique'),
        dm_mean=('dm_mean','mean'),det2=('det2','mean')).reset_index().round(4)
    G.to_csv(os.path.join(outd,'by_lineage.csv'),index=False)
    # console: depth-matched mean per program, biopsy vs healthy vs explant, by lineage
    for prog in PROG:
        print(f"\n=== {prog} module — depth-matched mean UMIs/cell (mean across donors) ===")
        print(f"{'cell_type':14s}{'biopsy':>9}{'healthy':>9}{'explant':>9}{'ex/bx':>8}")
        for lin in LINS:
            g=G[(G.cell_type==lin)&(G.program==prog)]
            def val(sr):
                r=g[g.source==sr]['dm_mean']; return r.iloc[0] if len(r) else np.nan
            b,h,e=val('biopsy'),val('healthy'),val('explant')
            fold=e/b if (b and b>0) else np.nan
            print(f"{lin:14s}{b:>9.3f}{h:>9.3f}{e:>9.3f}{fold:>7.1f}x")
    print(f"\nwrote {outd}/per_donor.csv and by_lineage.csv  (also see per-gene via stress_exact.py for hepatocytes)")

if __name__=='__main__': main()
