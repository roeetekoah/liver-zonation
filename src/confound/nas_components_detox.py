"""THE SHARP, FREE TEST of the pathologist's mechanism hypothesis (cytokine CYP-suppression):
within needle biopsies, does the INFLAMMATION sub-score predict hepatocyte detox loss? If end-stage
detox loss is cytokine-driven (IL-6/TNF -> down HNF4A/PXR/CAR), inflammation (orthogonal to fibrosis)
should track detox WITHIN the biopsy spectrum. Uses NAS COMPONENTS separately (Steatosis/Ballooning/
Inflammation), not summed NAS. Donor-level, biopsy-only (NaN-NAS explants/HL excluded automatically).

Detox module = CYP2E1, CYP1A2, ADH4, AKR1D1, SLCO1B3 (xenobiotic drug-metabolism; excludes CYP3A4 which
is PC-identity). Per-donor metric = mean DEPTH-MATCHED UMIs/cell over hepatocytes (binomial thinning to
B=1500, 4-draw MC). Stats: Spearman(detox, each component) + partial(detox, inflammation | fibrosis).
Output: findings/nas_components_detox/nas_components_detox.csv
"""
import os, sys
import numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
B=1500; NDRAW=4
DETOX=['CYP2E1','CYP1A2','ADH4','AKR1D1','SLCO1B3']

def partial_spearman(x,y,z):
    # partial corr of x,y given z via rank residuals
    rx,ry,rz=[stats.rankdata(v) for v in (x,y,z)]
    def resid(a,b):
        b1=np.c_[np.ones_like(b),b]; beta,_,_,_=np.linalg.lstsq(b1,a,rcond=None); return a-b1@beta
    ex,ey=resid(rx,rz),resid(ry,rz)
    return stats.pearsonr(ex,ey)[0]

def main():
    df=pd.read_csv(os.path.join(str(config.PAPER1),'raw_panel_counts.csv'),low_memory=False); df['donor']=df['donor'].astype(str)
    md=pd.read_csv(os.path.join(str(config.PAPER1),'metadata_all_cells.csv'),
        usecols=['Patient.ID','Steatosis','Ballooning','Inflammation','Fibrosis.score..F0.4.'],low_memory=False).rename(
        columns={'Patient.ID':'donor','Fibrosis.score..F0.4.':'F'})
    md['donor']=md['donor'].astype(str)
    for c in ['Steatosis','Ballooning','Inflammation','F']: md[c]=pd.to_numeric(md[c],errors='coerce')
    cl=md.groupby('donor').first()
    hep=df[(df['annotation']=='Hepatocytes')&(~df['donor'].str.startswith('CL'))&(df['stage']!='Healthy control')].copy()
    hep['detox']=hep[DETOX].sum(axis=1)
    rows=[]
    for d,s in hep.groupby('donor'):
        E=s['E_raw'].values; m=E>=B
        if m.sum()<20: continue
        rng=np.random.RandomState(0); p=B/E[m]; acc=np.zeros(m.sum())
        for _ in range(NDRAW): acc+=rng.binomial(s['detox'].values[m].astype(int),p)
        rows.append(dict(donor=d, detox_dm=acc.mean()/NDRAW,
            Steatosis=cl.loc[d,'Steatosis'],Ballooning=cl.loc[d,'Ballooning'],
            Inflammation=cl.loc[d,'Inflammation'],F=cl.loc[d,'F']))
    D=pd.DataFrame(rows).dropna()
    D.to_csv(os.path.join('findings','nas_components_detox','nas_components_detox.csv'),index=False) if os.path.isdir(os.path.join('findings','nas_components_detox')) else (os.makedirs(os.path.join('findings','nas_components_detox')),D.to_csv(os.path.join('findings','nas_components_detox','nas_components_detox.csv'),index=False))
    print(f"biopsy donors with NAS components + detox: n={len(D)}")
    print(f"detox_dm (depth-matched detox UMIs/cell) range {D.detox_dm.min():.2f}-{D.detox_dm.max():.2f}\n")
    print(f"{'predictor':14s}{'Spearman rho':>14}{'p':>9}")
    for c in ['Inflammation','Ballooning','Steatosis','F']:
        r=stats.spearmanr(D[c],D['detox_dm']); print(f"{c:14s}{r.correlation:>14.3f}{r.pvalue:>9.3f}")
    pr=partial_spearman(D['detox_dm'].values, D['Inflammation'].values, D['F'].values)
    print(f"\npartial(detox, Inflammation | Fibrosis) = {pr:+.3f}")
    print("\nREAD: cytokine-CYP-suppression predicts a NEGATIVE detox~inflammation correlation within biopsies.")
    print("If ~0, the mechanism (if real) is not detectable in biopsy tissue -> an end-stage-only phenomenon.")
    print("wrote findings/nas_components_detox/nas_components_detox.csv")

if __name__=='__main__': main()
