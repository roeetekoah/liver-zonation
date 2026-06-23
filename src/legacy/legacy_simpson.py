"""Does the legacy 'de-zonation collapse' have the structure of Simpson's paradox?
We reconstruct the legacy-style zonation metrics (PC-PP module anti-correlation; z-coordinate spread)
and test whether the apparent collapse across the 'stage' axis is an AGGREGATION artifact: present
when samples are POOLED across the lurking variable (sampling mode = needle biopsy vs deceased-donor
organ cube), absent/reversed WITHIN the acquisition-matched biopsy subgroup.

Metric (legacy spirit, on log-normalized counts, hepatocytes):
  PCmod = mean log1p(CP10k) over canonical pericentral genes; PPmod = same over periportal.
  anti-corr  = Pearson(PCmod, PPmod) across cells (zonation => negative; collapse => toward 0/positive).
  spread     = IQR of z(PCmod) - z(PPmod) within group (zonation => wide; collapse => narrow).
Reported per group, per donor, and as a 'naive stage trend' pooled vs biopsy-only.  No depth-matching
here on purpose: this reproduces what the legacy pooled analysis actually did.
"""
import os, sys
import numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
P1=str(config.PAPER1)
PC=['GLUL','CYP3A4','CYP2E1','CYP1A2','ADH4','AKR1D1','SLCO1B3']
PP=['CPS1','ASS1','ALDOB','PCK1','HAL','ARG1']

def main():
    df=pd.read_csv(os.path.join(P1,'raw_panel_counts.csv'),low_memory=False); df['donor']=df['donor'].astype(str)
    md=pd.read_csv(os.path.join(P1,'metadata_all_cells.csv'),usecols=['Patient.ID','Fibrosis.score..F0.4.'],low_memory=False).rename(
        columns={'Patient.ID':'donor','Fibrosis.score..F0.4.':'F'})
    md['donor']=md['donor'].astype(str); md['F']=pd.to_numeric(md['F'],errors='coerce')
    df=df.merge(md.groupby('donor')['F'].first().reset_index(),on='donor',how='left')
    df=df[df['annotation']=='Hepatocytes'].copy()
    df['source']=np.where(df['donor'].str.startswith('CL'),'end-stage',
                  np.where(df['stage']=='Healthy control','healthy','biopsy'))
    E=df['E_raw'].values
    def mod(genes):
        g=[x for x in genes if x in df.columns]
        cp=df[g].values/E[:,None]*1e4
        return np.log1p(cp).mean(axis=1)
    df['PCmod']=mod(PC); df['PPmod']=mod(PP)
    def anti(s):  # pearson across cells
        if len(s)<30: return np.nan
        return stats.pearsonr(s['PCmod'],s['PPmod'])[0]
    def spread(s):
        if len(s)<30: return np.nan
        z=lambda x:(x-x.mean())/x.std() if x.std()>0 else x*0
        c=z(s['PCmod'])-z(s['PPmod']); return np.subtract(*np.percentile(c,[75,25]))

    # ---- per-group (pooled cells) ----
    print("=== legacy metric per group (POOLED cells) ===")
    print(f"{'group':16s}{'nCells':>8}{'anti-corr':>11}{'z-coord IQR':>13}")
    order=[('healthy',df[df.source=='healthy']),
           ('biopsy F0',df[(df.source=='biopsy')&(df.F==0)]),
           ('biopsy F1',df[(df.source=='biopsy')&(df.F==1)]),
           ('biopsy F2',df[(df.source=='biopsy')&(df.F==2)]),
           ('biopsy F3',df[(df.source=='biopsy')&(df.F==3)]),
           ('biopsy F4',df[(df.source=='biopsy')&(df.F==4)]),
           ('end-stage',df[df.source=='end-stage'])]
    for name,s in order:
        print(f"{name:16s}{len(s):>8}{anti(s):>11.3f}{spread(s):>13.3f}")

    # ---- per-donor anti-corr (the within-donor truth) ----
    print("\n=== per-donor anti-corr (median across donors in group) ===")
    for name,grp in [('healthy','healthy'),('biopsy','biopsy'),('end-stage','end-stage')]:
        sub=df[df.source==grp]; rs=[anti(s) for _,s in sub.groupby('donor') if len(s)>=30]
        rs=[r for r in rs if not np.isnan(r)]
        print(f"  {name:10s}: median {np.median(rs):+.3f}   range [{min(rs):+.3f},{max(rs):+.3f}]  (nDonors={len(rs)})")

    # ---- THE SIMPSON TEST: naive 'stage trend' pooled vs biopsy-only ----
    print("\n=== SIMPSON TEST: anti-corr magnitude vs a naive stage axis ===")
    # per-donor anti-corr + a naive stage index (healthy=0, F1..F4=1..4, end-stage=5)
    rows=[]
    for d,s in df.groupby('donor'):
        if len(s)<30: continue
        r=anti(s)
        if np.isnan(r): continue
        src=s['source'].iloc[0]; F=s['F'].iloc[0]
        # naive ordinal stage axis: healthy=0, biopsy F0..F4 = 1..5, end-stage=6 (no collision)
        idx = 0 if src=='healthy' else (6 if src=='end-stage' else (F+1 if not np.isnan(F) else np.nan))
        rows.append(dict(donor=d,source=src,stage_idx=idx,F=F,anti=r))
    D=pd.DataFrame(rows).dropna(subset=['stage_idx'])
    # pooled (incl healthy + end-stage)
    sp_all=stats.spearmanr(D['stage_idx'],D['anti'])
    bi=D[D.source=='biopsy']
    sp_bi=stats.spearmanr(bi['F'],bi['anti'])
    print(f"  POOLED  (healthy+F0-F4+end-stage, n={len(D)}):  Spearman(stage, anti-corr) = {sp_all.correlation:+.3f}  (p={sp_all.pvalue:.3f})")
    print(f"  BIOPSY-ONLY (F0-F4 needle, n={len(bi)}):         Spearman(F,     anti-corr) = {sp_bi.correlation:+.3f}  (p={sp_bi.pvalue:.3f})")
    print(f"\n  per-donor anti-corr by stage-idx (donor-median):")
    for i in [0,1,2,3,4,5,6]:
        s=D[D.stage_idx==i]
        if len(s): print(f"    idx{i} ({s.source.iloc[0]:9s} F={s.F.iloc[0] if not np.isnan(s.F.iloc[0]) else '-'}): {s['anti'].median():+.3f}  (nD={len(s)})")
    D.to_csv(os.path.join(str(config.ANALYSIS_TABLES),'legacy_simpson.csv'),index=False)
    print("\nwrote legacy_simpson.csv")
    print("Simpson structure holds IF pooled trend is strongly negative (collapse) but biopsy-only is ~0.")

if __name__=='__main__': main()
