"""EXACT per-donor, per-stress-gene numbers (no medians) — for the stress leg's integrative analysis.
All-lobe hepatocytes (keeps all 4 healthy donors incl. the 2 with no recorded lobe). Metrics per
(donor, gene): raw_mean = mean raw UMIs/nucleus; dm_mean = depth-matched mean (thin to B, 4-draw MC);
det1 = frac UMI>=1; det2 = AMBIENT-ROBUST frac UMI>=2. Stress module = sum of 8 IEG+HSP genes.
Output: findings/stress_and_panel_by_stage/stress_per_donor_alllobe.csv
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
B=1500; NDRAW=4
STRESS=['FOS','JUN','JUNB','JUND','ATF3','DUSP1','HSPA1A','HSPA1B']
ORDER=['Healthy control','NAFLD','NASH w/o cirrhosis','NASH with cirrhosis','end stage']

def met(vals,E):
    raw=vals.mean(); d1=(vals>=1).mean(); d2=(vals>=2).mean(); m=E>=B
    if m.sum()>0:
        rng=np.random.RandomState(0); p=B/E[m]; acc=np.zeros(m.sum())
        for _ in range(NDRAW): acc+=rng.binomial(vals[m].astype(int),p)
        dm=(acc/NDRAW).mean()
    else: dm=np.nan
    return raw,dm,d1,d2

def main():
    df=pd.read_csv(os.path.join(str(config.PAPER1),'raw_panel_counts.csv'),low_memory=False); df['donor']=df['donor'].astype(str)
    md=pd.read_csv(os.path.join(str(config.PAPER1),'metadata_all_cells.csv'),usecols=['cell_id','Disease.status'],low_memory=False)
    df=df.merge(md,on='cell_id',how='left')
    hep=df[df['annotation']=='Hepatocytes'].copy(); hep['stress_mod']=hep[STRESS].sum(axis=1)
    hep['src']=np.where(hep['donor'].str.startswith('CL'),'explant',np.where(hep['Disease.status']=='Healthy control','healthy(deceased-donor)','needle_biopsy'))
    rows=[]
    for (donor,stage),s in hep.groupby(['donor','Disease.status']):
        E=s['E_raw'].values
        for g in STRESS+['stress_mod']:
            raw,dm,d1,d2=met(s[g].values.astype(float),E)
            rows.append(dict(donor=donor,stage=stage,source=s['src'].iloc[0],gene=g,nCells=len(s),
                raw_mean=round(raw,4),dm_mean=round(dm,4),det1=round(d1,4),det2=round(d2,4)))
    PD=pd.DataFrame(rows)
    outd=os.path.join('findings','stress_and_panel_by_stage'); os.makedirs(outd,exist_ok=True)
    PD.to_csv(os.path.join(outd,'stress_per_donor_alllobe.csv'),index=False)
    mod=PD[PD.gene=='stress_mod'].copy()
    mod['__o']=mod['stage'].map({s:i for i,s in enumerate(ORDER)}); mod=mod.sort_values(['__o','donor'])
    print("=== STRESS MODULE, EXACT per donor (all-lobe) — raw & depth-matched mean UMIs/nucleus, ambient-robust det2 ===")
    print(mod[['donor','stage','source','nCells','raw_mean','dm_mean','det2']].to_string(index=False))
    print("\n=== per-source summary (mean across donors; NOT median) ===")
    print(mod.groupby('source').agg(nDonors=('donor','nunique'),raw_mean=('raw_mean','mean'),
        dm_mean=('dm_mean','mean'),det2=('det2','mean')).round(4).to_string())
    print(f"\nwrote {outd}/stress_per_donor_alllobe.csv")

if __name__=='__main__': main()
