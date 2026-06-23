"""Per-cell zonal-balance distribution by stage — the gradient-compression test.

WHAT EACH AXIS IS (no vague shorthand):
  x = per-cell zonal balance = (pericentral-program UMIs) / (pericentral + periportal program UMIs),
      computed AFTER binomial down-thinning of each gene's raw UMIs to a common budget of 1,500 UMIs per
      nucleus (probability p = 1500/E_raw per molecule; nuclei below 1,500 dropped; averaged over 8
      independent thinning draws). 0 = the cell's signal is entirely PERIPORTAL, 1 = entirely PERICENTRAL,
      0.5 = balanced. Only "informative" nuclei (>=3 program UMIs after thinning) are shown.
  y = FRACTION OF CELLS in each balance-bin (bars sum to 1 within a panel) — a normalized histogram, so
      panels with different cell numbers are comparable.
WHY look at this: if zonation is intact, cells are POLARIZED -> mass piles near 0 and 1. If zonation
compresses (the classic "de-zonation": cells lose their zonal extremes and drift to the middle), mass
moves toward 0.5. This distribution is the direct count-based test of gradient compression.

DONOR-BALANCED: each donor contributes at most 300 informative nuclei (random subsample, fixed seed), so a
single donor cannot dominate a stage's histogram (e.g. at F4 one donor otherwise supplies ~59% of cells).
This is for honest VISUALIZATION of distribution shape only; statistical inference elsewhere is donor-level.
Output: results/figures/h2/gradient_polarization_dist.png
"""
import os, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
B=1500; NDRAW=8; CAP=300; TEAL='#2C7A86'; INK='#16242B'; GRID='#b9c4c7'
PCprog=['GLUL','CYP3A4','CYP2E1','CYP1A2','ADH4','AKR1D1','SLCO1B3']
PPprog=['CPS1','ASS1','ALDOB','PCK1','HAL','ARG1']
plt.rcParams.update({'font.size':11,'axes.titlesize':12,'axes.labelsize':10.5})

def main():
    df=pd.read_csv(os.path.join(str(config.PAPER1),'raw_panel_counts.csv'),low_memory=False); df['donor']=df['donor'].astype(str)
    md=pd.read_csv(os.path.join(str(config.PAPER1),'metadata_all_cells.csv'),usecols=['Patient.ID','Fibrosis.score..F0.4.'],low_memory=False).rename(
        columns={'Patient.ID':'donor','Fibrosis.score..F0.4.':'F'})
    md['donor']=md['donor'].astype(str); md['F']=pd.to_numeric(md['F'],errors='coerce')
    df=df.merge(md.groupby('donor')['F'].first().reset_index(),on='donor',how='left')
    hep=df[df['annotation']=='Hepatocytes'].copy()
    hep['grp']=np.where(hep['donor'].str.startswith('CL'),'Explant',
               np.where(hep['stage']=='Healthy control','Healthy',hep['F'].map({0:'F0',1:'F1',2:'F2',3:'F3',4:'F4'})))
    h=hep[hep['E_raw']>=B].copy(); E=h['E_raw'].values; rng=np.random.RandomState(0); p=B/E
    def thin(genes):
        acc=np.zeros(len(h))
        for g in genes:
            if g in h:
                a=np.zeros(len(h))
                for _ in range(NDRAW): a+=rng.binomial(h[g].values.astype(int),p)
                acc+=a/NDRAW
        return acc
    PC=thin(PCprog); PP=thin(PPprog); tot=PC+PP
    h['frac']=np.where(tot>0,PC/np.maximum(tot,1),np.nan); h['inf']=tot>=3
    panels=['F0','F1','F2','F3','F4','Explant']
    fig,axes=plt.subplots(2,3,figsize=(12.5,7.0),dpi=200); bins=np.linspace(0,1,21)
    for ax,grp in zip(axes.ravel(),panels):
        s=h[(h['grp']==grp)&(h['inf'])]
        parts=[g.sample(min(len(g),CAP),random_state=1) for _,g in s.groupby('donor')]
        sb=pd.concat(parts) if parts else s; v=sb['frac'].dropna().values
        ax.hist(v,bins=bins,weights=np.ones(len(v))/len(v),color=TEAL,edgecolor='white',linewidth=0.5)
        for x in (0.25,0.75): ax.axvline(x,color=GRID,ls=':',lw=1.1)
        ax.set_title(f"{grp}   (donors={sb['donor'].nunique()}, n={len(v):,})",fontweight='bold',color=INK)
        ax.set_xlabel('per-cell zonal balance  PC / (PC+PP)\n0 = all periportal      1 = all pericentral',color=INK)
        ax.set_ylabel('fraction of cells in bin',color=INK)
        ax.set_xlim(0,1); ax.tick_params(labelsize=9)
        for sp in ['top','right']: ax.spines[sp].set_visible(False)
    fig.suptitle('Per-cell zonal balance by stage — gradient-compression test\n'
                 'counts binomially down-thinned to 1,500 UMIs/nucleus (8-draw avg), donor-balanced ≤300 nuclei/donor\n'
                 'mass at the poles (0,1) = zonation;  drift toward 0.5 = de-zonation / gradient compression',
                 fontsize=12.5,color=INK)
    plt.tight_layout(rect=[0,0,1,0.90])
    out='results/figures/h2/gradient_polarization_dist.png'; os.makedirs(os.path.dirname(out),exist_ok=True)
    plt.savefig(out,dpi=200,bbox_inches='tight',facecolor='white'); print('wrote',out,'(dpi=200, 8-draw)')

if __name__=='__main__': main()
