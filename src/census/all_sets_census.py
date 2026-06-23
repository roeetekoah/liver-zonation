"""All-marker-sets census: is the F0-F4 biopsy null invariant across the WHOLE curated breadth
ladder, not just the 3 sets in markerset_robustness.py? Sets span 2 to ~1,600 genes:
  canonical(2/4) - core(20/20) - program(7/6) - expanded(94/86) - paper2_landmark(20/20) - full(1273/364)
All on RAW counts (per-cell, from src/prep/09 raw_curated_union.mtx), depth-matched at B, donor-level.
Endpoints (set-size-normalized): per-nucleus PC-share = PCsum/(PCsum+PPsum) over informative nuclei,
and zonal-extreme(polar) fraction. Output: all_sets_census.csv
"""
import os, sys
import numpy as np, pandas as pd, scipy.io as sio, scipy.sparse as sp
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
P1=str(config.PAPER1); B=1500

def rd(p):
    x=[l.strip() for l in open(p)]; return [g for g in x if g]

def sets():
    s={}
    s['A canonical(2/4)']=(['GLUL','CYP3A4'],['ASS1','PCK1','HAL','ALDOB'])
    s['B core(20/20)']=(rd('signatures/pericentral_core.txt'),rd('signatures/periportal_core.txt'))
    s['C program(7/6)']=(['GLUL','CYP3A4','CYP2E1','CYP1A2','ADH4','AKR1D1','SLCO1B3'],
                          ['CPS1','ASS1','ALDOB','PCK1','HAL','ARG1'])
    s['D expanded(94/86)']=(rd('signatures/pericentral_expanded.txt'),rd('signatures/periportal_expanded.txt'))
    s['E paper2_landmark(20/20)']=(rd('signatures/pericentral_paper2_landmark.txt'),rd('signatures/periportal_paper2_landmark.txt'))
    s['F full(1273/364)']=(rd('signatures/pericentral_full.txt'),rd('signatures/periportal_full.txt'))
    return s

def main():
    M=sio.mmread(os.path.join(P1,'raw_curated_union.mtx')).tocsr()        # genes x cells
    genes=np.array(rd(os.path.join(P1,'raw_curated_union.genes.txt')))
    cells=pd.read_csv(os.path.join(P1,'raw_curated_union.cells.csv'),low_memory=False)
    cells['donor']=cells['donor'].astype(str)
    md=pd.read_csv(os.path.join(P1,'metadata_all_cells.csv'),usecols=['Patient.ID','Fibrosis.score..F0.4.'],low_memory=False).rename(
        columns={'Patient.ID':'donor','Fibrosis.score..F0.4.':'F'})
    md['donor']=md['donor'].astype(str); md['F']=pd.to_numeric(md['F'],errors='coerce')
    Fd=md.groupby('donor')['F'].first()
    g2i={g:i for i,g in enumerate(genes)}
    # biopsy hepatocytes, depth >= B
    bio=(cells['annotation']=='Hepatocytes')&(~cells['donor'].str.startswith('CL'))&(cells['stage']!='Healthy control')&(cells['E_raw']>=B)
    idx=np.where(bio.values)[0]
    sub=M[:,idx].tocsc(); E=cells['E_raw'].values[idx]; dn=cells['donor'].values[idx]
    Fcell=np.array([Fd.get(d,np.nan) for d in dn])
    rng=np.random.RandomState(0); p=(B/E)
    print(f"biopsy hepatocyte nuclei (>=B): {len(idx)};  depth budget B={B}\n")
    def rowsum(gl):
        ii=[g2i[g] for g in gl if g in g2i]
        if not ii: return np.zeros(len(idx))
        return np.asarray(sub[ii,:].sum(axis=0)).ravel()
    out=[]
    for name,(pcg,ppg) in sets().items():
        npc=sum(g in g2i for g in pcg); npp=sum(g in g2i for g in ppg)
        PCs=rowsum(pcg); PPs=rowsum(ppg)
        PCt=rng.binomial(PCs.astype(int),p); PPt=rng.binomial(PPs.astype(int),p)
        tot=PCt+PPt; frac=np.where(tot>0,PCt/np.maximum(tot,1),np.nan)
        inf=tot>=3; polar=(frac<=0.25)|(frac>=0.75)
        df=pd.DataFrame(dict(donor=dn,F=Fcell,frac=frac,inf=inf,polar=polar))
        rows=[]
        for d,s in df.groupby('donor'):
            si=s[s['inf']]
            if len(si)>=20: rows.append(dict(F=si['F'].iloc[0],share=si['frac'].mean(),pol=si['polar'].mean()))
        R=pd.DataFrame(rows)
        med=lambda F,c: (R[R.F==F][c].median() if (R.F==F).any() else np.nan)
        share={F:med(F,'share') for F in [0,1,2,3,4]}; pol={F:med(F,'pol') for F in [0,1,2,3,4]}
        print(f"=== {name}  (present PC={npc}/{len(pcg)}, PP={npp}/{len(ppg)}) ===")
        print("    PC-share  by F: "+"  ".join(f"F{F}={share[F]:.3f}" for F in [0,1,2,3,4])+f"  | F1-F4={share[1]-share[4]:+.3f}")
        print("    polar     by F: "+"  ".join(f"F{F}={pol[F]:.3f}" for F in [0,1,2,3,4])+f"  | F1-F4={pol[1]-pol[4]:+.3f}\n")
        out.append(dict(marker_set=name,nPC=npc,nPP=npp,
            **{f'share_F{F}':round(share[F],3) for F in [0,1,2,3,4]},share_F1_F4=round(share[1]-share[4],3),
            **{f'polar_F{F}':round(pol[F],3) for F in [0,1,2,3,4]},polar_F1_F4=round(pol[1]-pol[4],3)))
    pd.DataFrame(out).to_csv(os.path.join(str(config.ANALYSIS_TABLES),'all_sets_census.csv'),index=False)
    print("wrote all_sets_census.csv")

if __name__=='__main__': main()
