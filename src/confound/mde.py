"""Minimum-detectable-effect (MDE) table — make the power limit explicit and reproducible.
Two-sample MDE: Delta_min = (z_{1-a/2}+z_power) * s_pooled * sqrt(1/n1 + 1/n2), z=1.96+0.84=2.80
(alpha=0.05 two-sided, 80% power). s_pooled = pooled donor-level SD of the endpoint. Unit = donor.
Endpoints: PC-anchor / PP-anchor / dual(>=2 UMI) / null fractions, and within-PC detox burden.
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from thinning import thin_genes
PCanch=['GLUL','CYP3A4']; PPanch=['ASS1','PCK1','HAL','ALDOB']; DETOX=['CYP2E1','CYP1A2','ADH4','AKR1D1','SLCO1B3']
PCprog=['GLUL','CYP3A4','CYP2E1','CYP1A2','ADH4','AKR1D1','SLCO1B3']; PPprog=['CPS1','ASS1','ALDOB','PCK1','HAL','ARG1']
B=1500; M=8; Z=1.96+0.84

def load():
    df=pd.read_csv(os.path.join(str(config.PAPER1),'raw_panel_counts.csv'),low_memory=False); df['donor']=df['donor'].astype(str)
    md=pd.read_csv(os.path.join(str(config.PAPER1),'metadata_all_cells.csv'),usecols=['Patient.ID','Fibrosis.score..F0.4.'],low_memory=False).rename(columns={'Patient.ID':'donor','Fibrosis.score..F0.4.':'F'})
    md['donor']=md['donor'].astype(str); md['F']=pd.to_numeric(md['F'],errors='coerce')
    df=df.merge(md.groupby('donor').first().reset_index(),on='donor',how='left')
    hep=df[(df['annotation']=='Hepatocytes')&(~df['donor'].str.startswith('CL'))&(df['stage']!='Healthy control')].copy()
    return hep

def per_donor(hep):
    h=hep[hep['E_raw']>=B].copy(); p=(B/h['E_raw'].values)
    rows=[]
    for draw in range(M):
        ds=thin_genes(h,PCanch+PPanch+DETOX+PCprog+PPprog,p,base_seed=draw)
        PCh1=sum((ds[g]>0).astype(int) for g in PCanch); PPh1=sum((ds[g]>0).astype(int) for g in PPanch)
        PCh2=sum((ds[g]>=2).astype(int) for g in PCanch); PPh2=sum((ds[g]>=2).astype(int) for g in PPanch)
        hd=h.copy(); hd['PC']=(PCh1>=1)&(PPh1<2); hd['PP']=(PPh1>=2)&(PCh1<1)
        hd['dual2']=(PCh2>=1)&(PPh2>=2); hd['null']=(PCh1<1)&(PPh1<2)
        hd['detoxsum']=sum(ds[g] for g in DETOX)
        PCp=sum(ds[g] for g in PCprog); PPp=sum(ds[g] for g in PPprog); tot=PCp+PPp
        frac=np.where(tot>0, PCp/np.maximum(tot,1), np.nan)
        hd['informative']=tot>=3; hd['polar']=(frac<=0.25)|(frac>=0.75)
        for d,s in hd.groupby('donor'):
            pcm=s[s['PC']]; inf=s[s['informative']]
            rows.append(dict(donor=d,F=s['F'].iloc[0],draw=draw,
                PC=s['PC'].mean(),PP=s['PP'].mean(),dual2=s['dual2'].mean(),null=s['null'].mean(),
                detox=(pcm['detoxsum'].mean() if len(pcm)>=20 else np.nan),
                polar=(inf['polar'].mean() if len(inf)>=20 else np.nan)))
    return pd.DataFrame(rows).groupby(['donor','F'],as_index=False).agg(
        PC=('PC','mean'),PP=('PP','mean'),dual2=('dual2','mean'),null=('null','mean'),
        detox=('detox','mean'),polar=('polar','mean'))

def mde(D,col,g1,g2):
    a=D[D.F==g1][col].dropna().values; b=D[D.F==g2][col].dropna().values
    n1,n2=len(a),len(b)
    sp=np.sqrt(((n1-1)*a.var(ddof=1)+(n2-1)*b.var(ddof=1))/(n1+n2-2))
    delta=Z*sp*np.sqrt(1/n1+1/n2)
    mean=np.concatenate([a,b]).mean()
    return n1,n2,sp,delta,mean

def main():
    D=per_donor(load())
    print(f"donors: {len(D)}  (F0..F4 = {[ (D.F==f).sum() for f in [0,1,2,3,4]]})\n")
    print("MDE = 2.80 * pooled_donor_SD * sqrt(1/n1 + 1/n2)   (alpha=0.05 two-sided, 80% power, unit=donor)\n")
    endpoints=[('PC-anchor fraction','PC'),('PP-anchor fraction','PP'),('dual (>=2 UMI) fraction','dual2'),
               ('null fraction','null'),('gradient: zonal-extreme fraction','polar'),('within-PC detox burden (UMIs/nuc)','detox')]
    comps=[('F0 vs F4',0,4),('F1 vs F4',1,4),('F1 vs F3 (interior)',1,3)]
    print(f"{'endpoint':34s}{'comparison':20s}{'n1':>3}{'n2':>3}{'donorSD':>9}{'MDE':>8}{'mean':>8}{'MDE/mean':>9}")
    rows=[]
    for ename,col in endpoints:
        for cname,g1,g2 in comps:
            n1,n2,sp,delta,mean=mde(D,col,g1,g2)
            print(f"{ename:34s}{cname:20s}{n1:>3}{n2:>3}{sp:>9.3f}{delta:>8.3f}{mean:>8.3f}{100*delta/mean:>8.0f}%")
            rows.append(dict(endpoint=ename,comparison=cname,n1=n1,n2=n2,donor_SD=round(sp,3),MDE=round(delta,3),mean=round(mean,3),MDE_pct_of_mean=round(100*delta/mean)))
    pd.DataFrame(rows).to_csv(os.path.join(str(config.ANALYSIS_TABLES),'mde_table.csv'),index=False)
    print("\nwrote mde_table.csv")
    print("Read: MDE is the smallest true difference detectable at 80% power; MDE/mean >> 100% at the thin")
    print("ends (F0 n=2, F4 n=4) => only near-total collapse is excludable, not moderate change.")

if __name__=='__main__': main()
