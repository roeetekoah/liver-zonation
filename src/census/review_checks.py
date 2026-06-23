"""Post-review count-based checks (professor reviews): (A) within-explant collapse-vs-stress
dose-response; (B) k=2 dual contrast biopsy-vs-explant + dual-slope invariance across B; (C) per-donor
explant heterogeneity; (D) confounder tests on data already in hand — donor ambient (ALB), cholangiocyte
contamination (KRT19/EPCAM) in dual/PP nuclei, ploidy/depth vs fibrosis. All raw counts, depth-matched.
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
PCanch=['GLUL','CYP3A4']; PPanch=['ASS1','PCK1','HAL','ALDOB']
PCprog=['GLUL','CYP3A4','CYP2E1','CYP1A2','ADH4','AKR1D1','SLCO1B3']; PPprog=['CPS1','ASS1','ALDOB','PCK1','HAL','ARG1']
STRESS=['FOS','JUN','JUNB','JUND','ATF3','DUSP1','HSPA1A','HSPA1B']
B=1500

def load():
    df=pd.read_csv(os.path.join(str(config.PAPER1),'raw_panel_counts.csv'),low_memory=False); df['donor']=df['donor'].astype(str)
    md=pd.read_csv(os.path.join(str(config.PAPER1),'metadata_all_cells.csv'),
        usecols=['cell_id','Patient.ID','Fibrosis.score..F0.4.','nFeature_RNA'],low_memory=False).rename(
        columns={'Patient.ID':'donor','Fibrosis.score..F0.4.':'F','nFeature_RNA':'nFeat'})
    md['donor']=md['donor'].astype(str); md['F']=pd.to_numeric(md['F'],errors='coerce')
    df=df.merge(md[['cell_id','F','nFeat']],on='cell_id',how='left')
    hep=df[df['annotation']=='Hepatocytes'].copy()
    hep['source']=np.where(hep['donor'].str.startswith('CL'),'explant',np.where(hep['stage']=='Healthy control','healthy','biopsy'))
    return hep

def thin(h,rng):
    p=(B/h['E_raw'].values);
    out={}
    for g in set(PCanch+PPanch+PCprog+PPprog+STRESS+['KRT19','EPCAM','ALB']):
        if g in h.columns: out[g]=rng.binomial(h[g].values.astype(int),p)
    return out

def classify(ds):
    PCh=sum((ds[g]>0).astype(int) for g in PCanch); PPh=sum((ds[g]>0).astype(int) for g in PPanch)
    cls=np.where((PCh>=1)&(PPh<2),'PC',np.where((PPh>=2)&(PCh<1),'PP',np.where((PCh>=1)&(PPh>=2),'dual','null')))
    PCp=sum(ds[g] for g in PCprog); PPp=sum(ds[g] for g in PPprog)
    return cls,PCp,PPp

def main():
    hep=load(); rng=np.random.RandomState(0)
    # ---------- A. within-explant dose-response ----------
    es=hep[(hep.source=='explant')&(hep['E_raw']>=B)].copy()
    ds=thin(es,rng); cls,PCp,PPp=classify(ds)
    stress=sum(ds[g] for g in STRESS)
    es['cls']=cls; es['stress']=stress; es['PCp']=PCp; es['PPp']=PPp
    es['ppole']=(PPp>=3)&(PCp==0)
    print("="*70+"\n(A) WITHIN-EXPLANT dose-response: collapse vs per-nucleus stress (depth-matched)\n"+"="*70)
    es['sb']=pd.qcut(es['stress'].rank(method='first'),4,labels=['Q1(low)','Q2','Q3','Q4(high)'])
    g=es.groupby('sb',observed=True).agg(n=('cls','size'),PC_anchor=('cls',lambda s:(s=='PC').mean()),
        dual=('cls',lambda s:(s=='dual').mean()),PP_pole=('ppole','mean'),med_stress=('stress','median'))
    print(g.round(3).to_string())
    print("  -> if PC_anchor falls & PP_pole/dual rise from Q1->Q4, collapse tracks stress dose.")
    # within-donor consistency: PC-anchor in low vs high stress half, per donor
    print("\n  per-donor (stress below/above donor-median): PC-anchor low | high")
    for d,s in es.groupby('donor'):
        med=s['stress'].median(); lo=(s[s.stress<=med]['cls']=='PC').mean(); hi=(s[s.stress>med]['cls']=='PC').mean()
        print(f"    {d}: {lo:.3f} | {hi:.3f}  (n={len(s)})")

    # ---------- B. k=2 dual contrast + B-slope ----------
    print("\n"+"="*70+"\n(B) dual co-expression: k=2 biopsy vs explant; and F0->F4 slope across B\n"+"="*70)
    def dual_by(group_mask, k, Bv):
        h=hep[group_mask & (hep['E_raw']>=Bv)].copy(); r=np.random.RandomState(1); p=(Bv/h['E_raw'].values)
        PCh=sum((r.binomial(h[g].values.astype(int),p)>=k).astype(int) for g in PCanch)
        PPh=sum((r.binomial(h[g].values.astype(int),p)>=k).astype(int) for g in PPanch)
        h['dual']=((PCh>=1)&(PPh>=2)); return h
    for k in [1,2]:
        row=[]
        for F in [1,2,3,4]:
            h=dual_by((hep.source=='biopsy')&(hep.F==F),k,B)
            row.append(np.median([h[h.donor==d]['dual'].mean() for d in h.donor.unique()]))
        he=dual_by(hep.source=='explant',k,B)
        ex=np.median([he[he.donor==d]['dual'].mean() for d in he.donor.unique()])
        print(f"  k={k}: biopsy F1-F4 dual = {[round(x,4) for x in row]}   explant = {ex:.4f}")
    print("  dual F1->F4 slope (k=1) across depth budget B:")
    for Bv in [1000,1500,3000]:
        row=[]
        for F in [1,2,3,4]:
            h=dual_by((hep.source=='biopsy')&(hep.F==F),1,Bv)
            row.append(np.median([h[h.donor==d]['dual'].mean() for d in h.donor.unique()]))
        slope=np.polyfit([1,2,3,4],row,1)[0]
        print(f"    B={Bv}: F1-F4={[round(x,3) for x in row]}  slope={slope:+.4f}")

    # ---------- C. per-donor explant heterogeneity ----------
    print("\n"+"="*70+"\n(C) per-donor EXPLANT heterogeneity (depth-matched)\n"+"="*70)
    print("  donor    n    PC-anchor  dual   PP-pole   PP:PC")
    for d,s in es.groupby('donor'):
        pc=(s.cls=='PC').mean(); pp=(s.cls=='PP').mean(); du=(s.cls=='dual').mean(); ppole=s['ppole'].mean()
        print(f"  {d:7s} {len(s):5d}  {pc:8.3f}  {du:.3f}  {ppole:.3f}   {pp/pc if pc>0 else float('nan'):.2f}")

    # ---------- D. confounders ----------
    print("\n"+"="*70+"\n(D) confounder tests (data already in hand)\n"+"="*70)
    bi=hep[(hep.source=='biopsy')&(hep['E_raw']>=B)].copy(); dsb=thin(bi,np.random.RandomState(2)); clsb,PCp2,PPp2=classify(dsb)
    bi['cls']=clsb; bi['KRT19d']=(dsb['KRT19']>0); bi['EPCAMd']=(dsb['EPCAM']>0)
    bi['ALB10k']=1e4*bi['ALB']/bi['E_raw']
    # contamination: biliary detection by anchor class
    print("  contamination — KRT19/EPCAM detection by anchor class (biopsy):")
    for c in ['PC','PP','dual','null']:
        sub=bi[bi.cls==c]; print(f"    {c:5s}: KRT19+ {sub['KRT19d'].mean():.4f}  EPCAM+ {sub['EPCAMd'].mean():.4f}  (n={len(sub)})")
    # ambient: per-donor ALB vs dual/null
    print("\n  ambient — per biopsy donor: ALB/10k vs dual% , null% (sorted by ALB):")
    rows=[]
    for d,s in bi.groupby('donor'):
        rows.append((d, s['ALB10k'].median(), (s.cls=='dual').mean(), (s.cls=='null').mean()))
    rows.sort(key=lambda x:x[1])
    for d,a,du,nu in rows[:3]+rows[-3:]:
        print(f"    {d:6s} ALB10k={a:6.0f}  dual={du:.3f}  null={nu:.3f}")
    alb=np.array([r[1] for r in rows]); dual=np.array([r[2] for r in rows])
    print(f"    (across {len(rows)} donors: corr(ALB, dual) = {np.corrcoef(alb,dual)[0,1]:+.2f})")
    # ploidy/depth vs fibrosis
    print("\n  ploidy/depth — per biopsy donor median nFeat & E_raw by fibrosis:")
    for F in [0,1,2,3,4]:
        s=hep[(hep.source=='biopsy')&(hep.F==F)]
        if len(s)==0: continue
        nf=np.median([hep[(hep.donor==d)]['nFeat'].median() for d in s.donor.unique()])
        er=np.median([hep[(hep.donor==d)]['E_raw'].median() for d in s.donor.unique()])
        print(f"    F{F}: med nFeat={nf:.0f}  med E_raw={er:.0f}  (nD={s.donor.nunique()})")

if __name__=='__main__': main()
