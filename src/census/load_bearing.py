"""Load-bearing donor-level ABSOLUTE-COUNT evidence (per the review): no relative stat, no pooling,
no pseudoreplication. Per donor (biopsy stages + each explant): N nuclei after thinning, PC-anchor n/N,
PP-anchor n/N, dual(>=2 UMI) n/N, null n/N, stress UMIs/10k. Plus: full biliary panel by anchor class,
donor-stratified within-explant dose-response, and the depth-matched discard profile by stage.
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from thinning import thin_genes
PCanch=['GLUL','CYP3A4']; PPanch=['ASS1','PCK1','HAL','ALDOB']
STRESS=['FOS','JUN','JUNB','JUND','ATF3','DUSP1','HSPA1A','HSPA1B']
BILIARY=['KRT7','KRT19','KRT23','EPCAM','SOX4','NCAM1','MUC1','BCL2']
B=1500; M=8; OUTD=str(config.ANALYSIS_TABLES)

def load():
    df=pd.read_csv(os.path.join(str(config.PAPER1),'raw_panel_counts.csv'),low_memory=False); df['donor']=df['donor'].astype(str)
    md=pd.read_csv(os.path.join(str(config.PAPER1),'metadata_all_cells.csv'),
        usecols=['Patient.ID','Fibrosis.score..F0.4.','Steatosis','Ballooning','Inflammation','Lobe'],low_memory=False).rename(
        columns={'Patient.ID':'donor','Fibrosis.score..F0.4.':'F','Lobe':'lobe'})
    md['donor']=md['donor'].astype(str)
    for c in ['F','Steatosis','Ballooning','Inflammation']: md[c]=pd.to_numeric(md[c],errors='coerce')
    md['NAS']=md[['Steatosis','Ballooning','Inflammation']].sum(axis=1,min_count=1)
    mdd=md.groupby('donor').agg(F=('F','first'),NAS=('NAS','first'),
        lobes=('lobe',lambda x:'+'.join(sorted(set(str(v) for v in x))))).reset_index()
    df=df.merge(mdd,on='donor',how='left')
    hep=df[df['annotation']=='Hepatocytes'].copy()
    hep['source']=np.where(hep['donor'].str.startswith('CL'),'explant',np.where(hep['stage']=='Healthy control','healthy','biopsy'))
    return hep

def main():
    hep=load()
    h=hep[hep['E_raw']>=B].copy(); p=(B/h['E_raw'].values)
    draw_frames=[]
    for draw in range(M):
        ds=thin_genes(h,PCanch+PPanch+STRESS+BILIARY,p,base_seed=draw)
        PCh1=sum((ds[g]>0).astype(int) for g in PCanch); PPh1=sum((ds[g]>0).astype(int) for g in PPanch)
        PCh2=sum((ds[g]>=2).astype(int) for g in PCanch); PPh2=sum((ds[g]>=2).astype(int) for g in PPanch)
        d=h[['donor','source','F']].copy()
        d['PC']=(PCh1>=1)&(PPh1<2); d['PP']=(PPh1>=2)&(PCh1<1)
        d['dual2']=(PCh2>=1)&(PPh2>=2); d['null']=(PCh1<1)&(PPh1<2)
        d['weak_dual']=(PCh1>=1)&(PPh1>=2)&(~d['dual2'])
        d['stress']=sum(ds[g] for g in STRESS); d['draw']=draw
        for g in BILIARY: d['b_'+g]=ds[g]>0
        draw_frames.append(d)
    drawn=pd.concat(draw_frames,ignore_index=True)

    # ---- (1) donor-level load-bearing table ----
    base=h.groupby('donor').agg(source=('source','first'),F=('F','first'),NAS=('NAS','first'),
        lobes=('lobes','first'),N_thin=('donor','size')).reset_index()
    metrics=drawn.groupby('donor').agg(PC_n=('PC','sum'),PP_n=('PP','sum'),dual2_n=('dual2','sum'),
        weak_dual_n=('weak_dual','sum'),null_n=('null','sum'),stress_total=('stress','sum')).reset_index()
    for c in ['PC_n','PP_n','dual2_n','weak_dual_n','null_n','stress_total']: metrics[c]/=M
    T=base.merge(metrics,on='donor',how='left')
    T['stress_p10k']=(1e4*T['stress_total']/(B*T['N_thin'])).round(2); T=T.drop(columns='stress_total')
    T['__o']=T['source'].map({'biopsy':0,'explant':1,'healthy':2}); T=T.sort_values(['__o','F','donor']).drop(columns='__o')
    T.to_csv(os.path.join(OUTD,'load_bearing_donor_table.csv'),index=False)
    print("=== (1) donor-level absolute-count table -> load_bearing_donor_table.csv ===")
    print("    per-stage medians (biopsy) + each explant, key columns:")
    bi=T[T.source=='biopsy']
    for F in [0,1,2,3,4]:
        sub=bi[bi.F==F]
        if len(sub)==0: continue
        print(f"    F{F} biopsy (nD={len(sub)}): med N_thin={int(sub.N_thin.median())}  "
              f"PC%={100*(sub.PC_n/sub.N_thin).median():.1f}  dual2%={100*(sub.dual2_n/sub.N_thin).median():.2f}  "
              f"null%={100*(sub.null_n/sub.N_thin).median():.1f}  stress/10k={sub.stress_p10k.median():.1f}")
    for _,r in T[T.source=='explant'].iterrows():
        print(f"    EXPLANT {r.donor}: N={r.N_thin}  PC%={100*r.PC_n/r.N_thin:.1f}  PP%={100*r.PP_n/r.N_thin:.1f}  "
              f"dual2%={100*r.dual2_n/r.N_thin:.2f}  null%={100*r.null_n/r.N_thin:.1f}  stress/10k={r.stress_p10k:.1f}")

    # ---- (2) full biliary panel by anchor class (contamination control) ----
    print("\n=== (2) biliary/plasticity detection by anchor class (biopsy) — full panel ===")
    bih=drawn[drawn.source=='biopsy']; cls=np.where(bih['PC'],'PC',np.where(bih['PP'],'PP',
        np.where(bih['dual2'],'dual',np.where(bih['weak_dual'],'weak_dual','null'))))
    bih=bih.assign(cls=cls)
    hdr="    class  "+" ".join(f"{g:>6}" for g in BILIARY); print(hdr)
    for c in ['PC','PP','dual','weak_dual','null']:
        sub=bih[bih.cls==c]
        print(f"    {c:5s}  "+" ".join(f"{sub['b_'+g].mean():6.4f}" for g in BILIARY))

    # ---- (3) donor-stratified within-explant dose-response (5 slopes) ----
    print("\n=== (3) within-explant dose-response, DONOR-STRATIFIED (PC-anchor low vs high stress) ===")
    es=drawn[drawn.source=='explant']
    for d,s in es.groupby('donor'):
        med=s['stress'].median(); lo=s[s.stress<=med]['PC'].mean(); hi=s[s.stress>med]['PC'].mean()
        print(f"    {d}: PC-anchor low-stress={lo:.3f}  high-stress={hi:.3f}  delta={hi-lo:+.3f}  (n={len(s)})")
    print("    -> 5 donor-specific contrasts; report consistency, not a pooled slope.")

    # ---- (4) depth-matched discard profile by stage ----
    print("\n=== (4) discard profile: are nuclei dropped at B non-random / PC-biased? (biopsy) ===")
    for F in [0,1,2,3,4]:
        full=hep[(hep.source=='biopsy')&(hep.F==F)]
        if len(full)==0: continue
        kept=full[full['E_raw']>=B]; dropped=full[full['E_raw']<B]
        # PC-program detection in dropped vs kept (raw, since dropped can't be thinned)
        pcg=['GLUL','CYP3A4']; dpc=(dropped[pcg]>0).any(axis=1).mean() if len(dropped) else float('nan')
        kpc=(kept[pcg]>0).any(axis=1).mean()
        print(f"    F{F}: discarded {len(dropped)}/{len(full)} ({100*len(dropped)/len(full):.1f}%)  "
              f"PC-marker+ in dropped={dpc:.2f} vs kept={kpc:.2f}")
    print("    -> if dropped PC-marker+ ~ kept, the discard is not PC-biased.")

if __name__=='__main__': main()
