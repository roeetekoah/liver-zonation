"""Supplementary committed checks: (1) cross-lineage procurement-stress + HIF ratios (the §1 spine —
donor-median estimator, explicit); (2) recorded-covariate test (Age/Sex/T2D) against the §4 detox
attenuation, since these ARE in the metadata and Age tracks fibrosis. Raw counts, donor-level.
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
STRESS=['FOS','JUN','JUNB','JUND','ATF3','DUSP1','HSPA1A','HSPA1B']
HIF=['VEGFA','SLC2A1','LDHA','CA9','ENO1','PGK1']
DETOX=['CYP2E1','CYP1A2','ADH4','AKR1D1','SLCO1B3']

def main():
    df=pd.read_csv(os.path.join(str(config.PAPER1),'raw_panel_counts.csv'),low_memory=False); df['donor']=df['donor'].astype(str)
    md=pd.read_csv(os.path.join(str(config.PAPER1),'metadata_all_cells.csv'),
        usecols=['Patient.ID','Fibrosis.score..F0.4.','Age','Gender','Diabetes.type.2','BMI'],low_memory=False).rename(
        columns={'Patient.ID':'donor','Fibrosis.score..F0.4.':'F'})
    md['donor']=md['donor'].astype(str)
    for c in ['F','Age','BMI']: md[c]=pd.to_numeric(md[c],errors='coerce')
    mdd=md.groupby('donor').first().reset_index()
    df=df.merge(mdd,on='donor',how='left')
    df['source']=np.where(df['donor'].str.startswith('CL'),'explant',np.where(df['stage']=='Healthy control','healthy','biopsy'))

    # ---------- (1) cross-lineage stress + HIF, donor-median ratios ----------
    df['stress']=df[STRESS].sum(axis=1); df['hif']=df[HIF].sum(axis=1)
    def lineage_ratio(col):
        g=df.groupby(['source','annotation','donor']).apply(lambda s:1e4*s[col].sum()/s['E_raw'].sum(),include_groups=False).reset_index(name='v')
        pv=g.groupby(['annotation','source'])['v'].median().unstack('source')
        return pv
    print("="*64+"\n(1) cross-lineage STRESS & HIF — donor-median UMIs/10k, explant/biopsy ratio\n"+"="*64)
    order=['Hepatocytes','Endothelial','Stellate','Macrophages','Cholangiocytes','Lymphocytes']
    s=lineage_ratio('stress'); h=lineage_ratio('hif')
    print(f"{'lineage':14s}{'stress bx':>10}{'stress ex':>10}{'ratio':>7}   {'HIF bx':>7}{'HIF ex':>7}{'ratio':>7}")
    for a in order:
        if a not in s.index: continue
        print(f"{a:14s}{s.loc[a,'biopsy']:10.2f}{s.loc[a,'explant']:10.2f}{s.loc[a,'explant']/s.loc[a,'biopsy']:7.1f}   "
              f"{h.loc[a,'biopsy']:7.2f}{h.loc[a,'explant']:7.2f}{h.loc[a,'explant']/h.loc[a,'biopsy']:7.1f}")
    print("  (estimator = median across donors; pooled-sum gives lower ratios because high-depth explants dominate)")

    # ---------- (2) recorded covariates vs §4 detox attenuation (biopsy donors) ----------
    print("\n"+"="*64+"\n(2) recorded covariates vs detox attenuation (biopsy, donor-level)\n"+"="*64)
    bi=df[df.source=='biopsy']
    rows=[]
    for d,g in bi.groupby('donor'):
        rows.append(dict(donor=d, F=g['F'].iloc[0], Age=g['Age'].iloc[0], Gender=g['Gender'].iloc[0],
                         T2D=g['Diabetes.type.2'].iloc[0], detox=1e4*g[DETOX].values.sum()/g['E_raw'].sum()))
    D=pd.DataFrame(rows).dropna(subset=['F','Age','detox'])
    print(f"  n donors with Age+F+detox: {len(D)}")
    def sp(a,b):
        from scipy.stats import spearmanr; return spearmanr(D[a],D[b])
    for a,b in [('detox','F'),('detox','Age'),('Age','F'),('detox','BMI') if 'BMI' in D else ('detox','Age')]:
        if a in D and b in D:
            r,p=sp(a,b); print(f"  Spearman({a},{b}) = {r:+.2f}  (p={p:.3f})")
    # partial corr detox~F controlling Age (rank, via residuals)
    from numpy.polynomial import polynomial as P
    def resid(y,x):
        x=np.asarray(x,float); y=np.asarray(y,float); b=np.polyfit(x,y,1); return y-np.polyval(b,x)
    rF=resid(D['detox'],D['Age']); rA=resid(D['F'],D['Age'])
    pc=np.corrcoef(rF,rA)[0,1]
    print(f"  partial corr(detox, F | Age) (Pearson on residuals) = {pc:+.2f}")
    print(f"  detox by fibrosis (median UMIs/10k): " + " ".join(f"F{int(f)}={D[D.F==f]['detox'].median():.0f}" for f in sorted(D.F.unique())))
    print(f"  Gender split n: {D['Gender'].value_counts().to_dict()}")

if __name__=='__main__': main()
