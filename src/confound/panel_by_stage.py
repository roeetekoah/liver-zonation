"""Right-lobe-only, donor-level per-gene x per-stage panel — ROBUST rebuild of the old "fraction
expressing" / stress-by-stage tables, with every metric labeled by scale. Replaces raw-gaze / UMIs_per_10k
/ medians-as-final (see memory working-method-documentation-and-metrics).

Metrics, per (donor, stage, gene), Right-lobe hepatocytes (end-stage uses its Right-lobe cells too):
  raw_mean   : mean raw UMIs / nucleus            [DEPRECATED for conclusions; provenance only]
  det1       : fraction of nuclei with UMI >= 1   [detection, PRE-ROBUST]
  det2       : fraction of nuclei with UMI >= 2   [AMBIENT-ROBUST detection]
  dm_mean    : mean depth-matched UMIs/nucleus    [binomial thinning to B, MC avg over 4 draws; ROBUST]
  dm_det1    : fraction with depth-matched UMI>=1  [ROBUST detection]
Aggregated per (stage,gene) = mean across donors (+ min,max, nDonors). Unit = donor.
Stress MODULE = sum of 8 IEG+HSP genes/nucleus, same metrics. Output: findings/panel_by_stage/{per_donor,per_group}.csv
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
B=1500; NDRAW=4
STRESS=['FOS','JUN','JUNB','JUND','ATF3','DUSP1','HSPA1A','HSPA1B']
PC=['GLUL','CYP3A4','CYP2E1','CYP1A2','ADH4','AKR1D1','SLCO1B3']
PP=['ASS1','CPS1','PCK1','ALDOB','HAL','ARG1']; HOUSE=['ALB','ACTB','GAPDH']
GENES=STRESS+PC+PP+HOUSE
ORDER=['Healthy control','NAFLD','NASH w/o cirrhosis','NASH with cirrhosis','end stage']
SHORT={'Healthy control':'Healthy','NAFLD':'NAFLD','NASH w/o cirrhosis':'NASH','NASH with cirrhosis':'Cirrhosis','end stage':'End-stage'}

def metrics(vals, E):
    """vals: raw UMIs per cell (1 gene or module sum); E: per-cell library. Returns dict of metrics."""
    raw_mean=vals.mean(); det1=(vals>=1).mean(); det2=(vals>=2).mean()
    m=E>=B
    if m.sum()>0:
        rng=np.random.RandomState(0); p=B/E[m]; acc=np.zeros(m.sum())
        for _ in range(NDRAW): acc+=rng.binomial(vals[m].astype(int),p)
        thin=acc/NDRAW; dm_mean=thin.mean(); dm_det1=(thin>=1).mean()
    else: dm_mean=dm_det1=np.nan
    return dict(raw_mean=raw_mean,det1=det1,det2=det2,dm_mean=dm_mean,dm_det1=dm_det1)

def main():
    df=pd.read_csv(os.path.join(str(config.PAPER1),'raw_panel_counts.csv'),low_memory=False)
    df['donor']=df['donor'].astype(str)
    md=pd.read_csv(os.path.join(str(config.PAPER1),'metadata_all_cells.csv'),usecols=['cell_id','Disease.status'],low_memory=False)
    df=df.merge(md,on='cell_id',how='left')
    hep=df[(df['annotation']=='Hepatocytes')&(df['lobe']=='Right')].copy()
    hep['stress_mod']=hep[STRESS].sum(axis=1)
    rows=[]
    for (donor,stage),s in hep.groupby(['donor','Disease.status']):
        E=s['E_raw'].values
        for g in GENES+['stress_mod']:
            mm=metrics(s[g].values.astype(float),E)
            rows.append(dict(donor=donor,stage=stage,gene=g,nCells=len(s),**{k:round(v,4) for k,v in mm.items()}))
    PD=pd.DataFrame(rows)
    outd=os.path.join('findings','stress_and_panel_by_stage'); os.makedirs(outd,exist_ok=True)
    PD.to_csv(os.path.join(outd,'per_donor.csv'),index=False)
    # per-group: mean across donors + range + nD
    grp=[]
    for (stage,gene),s in PD.groupby(['stage','gene']):
        rec=dict(stage=stage,stage_short=SHORT.get(stage,stage),gene=gene,nDonors=s['donor'].nunique())
        for k in ['raw_mean','det1','det2','dm_mean','dm_det1']:
            rec[k+'_mean']=round(s[k].mean(),4); rec[k+'_min']=round(s[k].min(),4); rec[k+'_max']=round(s[k].max(),4)
        grp.append(rec)
    G=pd.DataFrame(grp); G['__o']=G['stage'].map({s:i for i,s in enumerate(ORDER)})
    G=G.sort_values(['gene','__o']).drop(columns='__o'); G.to_csv(os.path.join(outd,'per_group.csv'),index=False)
    # console: stress module + key zonation genes, ambient-robust det2 + depth-matched mean
    def show(genes,title):
        print(f"\n=== {title}: ambient-robust detection (UMI>=2) by stage [mean across donors] ===")
        print(f"{'gene':10s}"+''.join(f"{SHORT[s]:>11}" for s in ORDER))
        for g in genes:
            line=f"{g:10s}"
            for s in ORDER:
                v=G[(G.gene==g)&(G.stage==s)]['det2_mean']
                line+=f"{(v.iloc[0] if len(v) else np.nan):>11.3f}"
            print(line)
    show(['stress_mod','FOS','JUN','HSPA1A'],'STRESS')
    show(['GLUL','CYP3A4','CYP2E1','SLCO1B3','PCK1','ALDOB'],'ZONATION')
    print(f"\nnDonors per stage (Right-lobe):")
    print(PD.groupby('stage')['donor'].nunique().reindex(ORDER).to_string())
    print(f"\nwrote {outd}/per_donor.csv (exact per-donor) and per_group.csv")

if __name__=='__main__': main()
