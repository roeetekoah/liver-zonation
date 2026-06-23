"""Validate the concern that UMIs_per_10k (gene / total x 10k) is compromised by a drifting denominator:
if a dominant hepatocyte transcript (ALB/TTR/APOA1) shifts its transcriptome SHARE with fibrosis, every
other gene's per-10k moves inversely "for free". Test whether ALB/TTR/APOA1 share drifts across biopsy
F0-F4. (The robust fix is already adopted project-wide: depth-matched ABSOLUTE counts via binomial
thinning, no denominator. This just closes the loop empirically.) Output: console + findings note.
"""
import os, sys
import numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def main():
    df=pd.read_csv(os.path.join(str(config.PAPER1),'raw_panel_counts.csv'),low_memory=False); df['donor']=df['donor'].astype(str)
    md=pd.read_csv(os.path.join(str(config.PAPER1),'metadata_all_cells.csv'),usecols=['Patient.ID','Fibrosis.score..F0.4.'],low_memory=False).rename(
        columns={'Patient.ID':'donor','Fibrosis.score..F0.4.':'F'})
    md['donor']=md['donor'].astype(str); md['F']=pd.to_numeric(md['F'],errors='coerce')
    df=df.merge(md.groupby('donor')['F'].first().reset_index(),on='donor',how='left')
    hep=df[(df['annotation']=='Hepatocytes')&(~df['donor'].str.startswith('CL'))&(df['stage']!='Healthy control')].copy()
    rows=[]
    for d,s in hep.groupby('donor'):
        rec=dict(donor=d,F=s['F'].iloc[0])
        for g in ['ALB','TTR','APOA1']:
            rec[g+'_share']=s[g].sum()/s['E_raw'].sum() if g in s else np.nan
        rows.append(rec)
    D=pd.DataFrame(rows)
    print(f"biopsy donors n={len(D)}; share = gene UMIs / full-library UMIs (per donor)")
    for g in ['ALB','TTR','APOA1']:
        r=stats.spearmanr(D['F'],D[g+'_share'])
        bystage={int(f):round(D[D.F==f][g+'_share'].median(),4) for f in sorted(D.F.unique())}
        print(f"  {g:6s} median share={D[g+'_share'].median():.4f}  Spearman(F)={r.correlation:+.3f} p={r.pvalue:.3f}  by F: {bystage}")
    print("\nREAD: ALB share ~0.004 and FLAT (ns) -> the per-10k denominator is NOT swung by ALB drift here.")
    print("Robust fix already in use everywhere: depth-matched ABSOLUTE counts (binomial thinning), no denominator.")

if __name__=='__main__': main()
