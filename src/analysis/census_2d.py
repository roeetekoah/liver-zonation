"""Final structural check: the 2D JOINT distribution of pericentral-program vs periportal-program
raw counts per cell, depth-matched, one panel per stage. Keeps the full gradient the 4-box census
discards. Zonation present = two separated clouds / anti-diagonal (PC-high/PP-low and PP-high/PC-low,
few in the both-high corner). De-zonation = the both-high corner fills / clouds merge into one blob.
Donor-balanced (<=300 cells/donor) so no single donor dominates. Count-based, no correlation.
"""
import os, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
rng = np.random.RandomState(0)

PCprog=['GLUL','CYP3A4','CYP2E1','CYP1A2','ADH4','AKR1D1','SLCO1B3']   # pericentral program
PPprog=['CPS1','ASS1','ALDOB','PCK1','HAL','ARG1']                     # periportal program
B=1500; CAP=300; T=3   # depth budget, cells/donor cap, threshold for the quadrant summary

def main():
    df=pd.read_csv(os.path.join(str(config.PAPER1),'raw_panel_counts.csv'),low_memory=False)
    df['donor']=df['donor'].astype(str)
    hep=df[df['annotation']=='Hepatocytes'].copy()
    md=pd.read_csv(os.path.join(str(config.PAPER1),'metadata_all_cells.csv'),
        usecols=['Patient.ID','Fibrosis.score..F0.4.'],low_memory=False).rename(
        columns={'Patient.ID':'donor','Fibrosis.score..F0.4.':'F'})
    md['donor']=md['donor'].astype(str); md['F']=pd.to_numeric(md['F'],errors='coerce')
    hep=hep.merge(md.groupby('donor').first().reset_index(),on='donor',how='left')
    def grp(d,s,F):
        d=str(d)
        if d.startswith('CL'): return 'Explant(end)'
        if s=='Healthy control': return 'Healthy'
        return f'F{int(F)}-biopsy' if pd.notna(F) else None
    hep['grp']=[grp(d,s,F) for d,s,F in zip(hep['donor'],hep['stage'],hep['F'])]
    hep=hep[hep['grp'].notna() & (hep['E_raw']>=B)].copy()
    p=(B/hep['E_raw']).values
    for g in set(PCprog+PPprog):
        hep[g+'_ds']=rng.binomial(hep[g].values.astype(int),p)
    hep['PC']=hep[[g+'_ds' for g in PCprog]].sum(axis=1)
    hep['PP']=hep[[g+'_ds' for g in PPprog]].sum(axis=1)
    # donor-balance
    parts=[]
    for (g,d),s in hep.groupby(['grp','donor']):
        parts.append(s.sample(min(CAP,len(s)),random_state=0))
    hb=pd.concat(parts)

    panels=['Healthy','F1-biopsy','F2-biopsy','F3-biopsy','F4-biopsy','Explant(end)']
    panels=[pn for pn in panels if pn in hb['grp'].unique()]
    fig,axes=plt.subplots(2,3,figsize=(13,8.5)); axes=axes.ravel()
    xmax,ymax=18,18
    print("=== quadrant fractions (donor-balanced, depth-matched, threshold>=%d UMIs) ==="%T)
    print(f"{'stage':14s}{'PConly':>8}{'PPonly':>8}{'BOTH':>8}{'neither':>8}{'nCells':>8}")
    for ax,pn in zip(axes,panels):
        s=hb[hb['grp']==pn]
        x=np.clip(s['PP'],0,xmax); y=np.clip(s['PC'],0,ymax)
        ax.hist2d(x,y,bins=[np.arange(0,xmax+2),np.arange(0,ymax+2)],norm=LogNorm(),cmap='magma')
        ax.set_title(f"{pn}  (n={len(s)})",fontsize=11)
        ax.set_xlabel("periportal program (raw UMIs)"); ax.set_ylabel("pericentral program (raw UMIs)")
        # quadrant counts
        pc=s['PC'].values; pp=s['PP'].values; n=len(s)
        po=((pc>=T)&(pp<T)).mean(); ppo=((pp>=T)&(pc<T)).mean()
        both=((pc>=T)&(pp>=T)).mean(); nei=((pc<T)&(pp<T)).mean()
        print(f"{pn:14s}{po:8.3f}{ppo:8.3f}{both:8.3f}{nei:8.3f}{n:8d}")
    fig.suptitle("Joint pericentral vs periportal program (raw counts, depth-matched) by stage\n"
                 "two separated clouds = zonation;  both-high corner filling = de-zonation",fontsize=12)
    fig.tight_layout(rect=(0,0,1,0.95))
    out=os.path.join(str(config.FIG_H2),"census_2d_joint.png")
    os.makedirs(os.path.dirname(out),exist_ok=True)
    fig.savefig(out,dpi=150,bbox_inches='tight'); plt.close(fig)
    print("\nwrote",out)
    print("\nBOTH-high fraction is the de-zonation indicator; watch it across F1->F4 vs Explant.")

if __name__=='__main__':
    main()
