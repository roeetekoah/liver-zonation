"""Gap-fillers for complete H1 scenario coverage, count-based, depth-matched, donor=unit.
Closes: (i) GRADIENT COMPRESSION (per-cell zonal polarization distribution narrowing toward middle),
(ii) the structural census on the NAS (activity) axis (not just fibrosis), (iii) COMPOSITION shift
(PP:PC anchor ratio). All on raw counts, downsampled to a common depth budget.
"""
import os, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
rng=np.random.RandomState(0); B=1500; OUTD=str(config.ANALYSIS_TABLES)

PCprog=['GLUL','CYP3A4','CYP2E1','CYP1A2','ADH4','AKR1D1','SLCO1B3']
PPprog=['CPS1','ASS1','ALDOB','PCK1','HAL','ARG1']
PCanch=['GLUL','CYP3A4']; PPanch=['ASS1','PCK1','HAL','ALDOB']

def load():
    df=pd.read_csv(os.path.join(str(config.PAPER1),'raw_panel_counts.csv'),low_memory=False)
    df['donor']=df['donor'].astype(str); hep=df[df['annotation']=='Hepatocytes'].copy()
    md=pd.read_csv(os.path.join(str(config.PAPER1),'metadata_all_cells.csv'),
        usecols=['Patient.ID','Fibrosis.score..F0.4.','Steatosis','Ballooning','Inflammation'],low_memory=False)
    md=md.rename(columns={'Patient.ID':'donor','Fibrosis.score..F0.4.':'F'}); md['donor']=md['donor'].astype(str)
    for c in ['F','Steatosis','Ballooning','Inflammation']: md[c]=pd.to_numeric(md[c],errors='coerce')
    md['NAS']=md[['Steatosis','Ballooning','Inflammation']].sum(axis=1,min_count=1)
    hep=hep.merge(md.groupby('donor').first().reset_index(),on='donor',how='left')
    hep['biopsy']=(~hep['donor'].str.startswith('CL'))&(hep['stage']!='Healthy control')
    hep['explant']=hep['donor'].str.startswith('CL')
    hep=hep[hep['E_raw']>=B].copy(); p=(B/hep['E_raw']).values
    for g in set(PCprog+PPprog): hep[g+'_ds']=rng.binomial(hep[g].values.astype(int),p)
    hep['PCp']=hep[[g+'_ds' for g in PCprog]].sum(axis=1)
    hep['PPp']=hep[[g+'_ds' for g in PPprog]].sum(axis=1)
    PCh=(hep[[g+'_ds' for g in PCanch]]>0).sum(axis=1); PPh=(hep[[g+'_ds' for g in PPanch]]>0).sum(axis=1)
    hep['cls']=np.where((PCh>=1)&(PPh<2),'PC',np.where((PPh>=2)&(PCh<1),'PP',np.where((PCh>=1)&(PPh>=2),'dual','null')))
    return hep

def per_donor_summary(sub):
    """count-based descriptors for one donor's cells."""
    n=len(sub); cnt=sub['cls'].value_counts()
    pc=cnt.get('PC',0)/n; pp=cnt.get('PP',0)/n; du=cnt.get('dual',0)/n; nu=cnt.get('null',0)/n
    # polarization among cells with enough zonal signal
    z=sub[(sub['PCp']+sub['PPp'])>=3]
    frac=z['PCp']/(z['PCp']+z['PPp'])
    polar=((frac<=0.25)|(frac>=0.75)).mean() if len(z)>=20 else np.nan   # zonal extremes
    middle=((frac>0.25)&(frac<0.75)).mean() if len(z)>=20 else np.nan    # un-polarized middle
    return dict(N=n,PC=pc,PP=pp,dual=du,null=nu,PPtoPC=(pp/pc if pc>0 else np.nan),
                polarized=polar,middle=middle)

def axis_table(hep, axiscol, bins, label):
    rows=[]
    for name,sel in bins:
        s=hep[sel]
        recs=[per_donor_summary(sd) for _,sd in s.groupby('donor') if len(sd)>=50]
        if not recs: continue
        D=pd.DataFrame(recs)
        rows.append(dict(group=name,nD=len(D),medCells=int(D['N'].median()),
            PC=D['PC'].median(),PP=D['PP'].median(),dual=D['dual'].median(),null=D['null'].median(),
            PPtoPC=D['PPtoPC'].median(),polarized=D['polarized'].median(),middle=D['middle'].median()))
    R=pd.DataFrame(rows)
    print(f"\n=== {label} (median across donors; depth-matched B={B}) ===")
    print("PC/PP/dual/null = anchor-class fractions | PPtoPC = composition ratio | "
          "polarized = % cells zonal-extreme (PCfrac<=.25 or >=.75) | middle = % un-polarized")
    print(R.round(3).to_string(index=False))
    return R

def main():
    hep=load()
    # ---- fibrosis axis (biopsy) ----
    bF=[(f'F{F}',hep['biopsy']&(hep['F']==F)) for F in [0,1,2,3,4]]
    RF=axis_table(hep,'F',bF,"H1 scenarios by FIBROSIS (biopsy)")
    # ---- NAS axis (biopsy): bin low/mid/high ----
    nb=[('NAS 1-2',hep['biopsy']&hep['NAS'].between(1,2)),
        ('NAS 3-4',hep['biopsy']&hep['NAS'].between(3,4)),
        ('NAS 5-7',hep['biopsy']&hep['NAS'].between(5,7))]
    RN=axis_table(hep,'NAS',nb,"H1 scenarios by NAS activity (biopsy)")
    # ---- explant for contrast ----
    axis_table(hep,'x',[('Explant',hep['explant'])],"Explant (artifact, for contrast)")
    RF.to_csv(os.path.join(OUTD,'gapfill_fibrosis.csv'),index=False)
    RN.to_csv(os.path.join(OUTD,'gapfill_nas.csv'),index=False)

    # ---- polarization distribution figure (gradient compression) ----
    panels=[('F0',hep['biopsy']&(hep['F']==0)),('F1',hep['biopsy']&(hep['F']==1)),
            ('F2',hep['biopsy']&(hep['F']==2)),('F3',hep['biopsy']&(hep['F']==3)),
            ('F4',hep['biopsy']&(hep['F']==4)),('Explant',hep['explant'])]
    fig,axes=plt.subplots(2,3,figsize=(13,7)); axes=axes.ravel()
    for ax,(nm,sel) in zip(axes,panels):
        s=hep[sel]; z=s[(s['PCp']+s['PPp'])>=3]; frac=(z['PCp']/(z['PCp']+z['PPp'])).values
        ax.hist(frac,bins=np.linspace(0,1,26),color='#1b6e78',alpha=.85)
        ax.axvline(0.25,color='gray',ls=':'); ax.axvline(0.75,color='gray',ls=':')
        ax.set_title(f"{nm} (n={len(z)})"); ax.set_xlabel("per-cell zonal balance  PC/(PC+PP)")
        ax.set_ylabel("cells")
    fig.suptitle("Gradient-compression check: per-cell zonal polarization distribution (depth-matched)\n"
                 "spread 0..1 with mass at the ends = zonation;  collapse toward 0.5 = de-zonation/flattening",fontsize=11)
    fig.tight_layout(rect=(0,0,1,0.94))
    out=os.path.join(str(config.FIG_H2),"gapfill_polarization.png"); os.makedirs(os.path.dirname(out),exist_ok=True)
    fig.savefig(out,dpi=150,bbox_inches='tight'); plt.close(fig)
    print("\nwrote",out,"; gapfill_fibrosis.csv, gapfill_nas.csv")

if __name__=='__main__': main()
