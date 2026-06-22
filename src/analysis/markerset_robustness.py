"""Marker-set robustness: is the F0-F4 biopsy null invariant to which zonation gene set we use?
We re-run the SAME count-based, depth-matched, donor-level census on three sets of increasing
breadth, all on RAW counts (never Paper 2's fitted relative coordinate):
  (A) canonical anchors      : PC = GLUL,CYP3A4            PP = ASS1,PCK1,HAL,ALDOB   (2 vs 4)
  (B) curated program        : PC = 7 detox+identity       PP = 6 urea/gluconeo       (7 vs 6)
  (C) Paper-2 landmark genes : PC = 20 LM                  PP = 20 LM   (Paper 2's OWN ruler genes,
       extracted verbatim from Hepatocyte-{PC,PP}-LM.csv via prep/08 — the gene IDENTITIES, used
       in a detection census, NOT their z-scored eta coordinate).
Set-invariant endpoints (naturally comparable across set sizes):
  - mean PC-share  = per-nucleus PC/(PC+PP) summed counts, averaged over informative nuclei (tot>=3)
  - zonal-extreme (polar) fraction = share of informative nuclei with PC-share <=0.25 or >=0.75
Run: python src/analysis/markerset_robustness.py
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
B=1500; P1=str(config.PAPER1)

SETS = {
 'A canonical anchors':   (['GLUL','CYP3A4'],
                           ['ASS1','PCK1','HAL','ALDOB']),
 'B curated program':     (['GLUL','CYP3A4','CYP2E1','CYP1A2','ADH4','AKR1D1','SLCO1B3'],
                           ['CPS1','ASS1','ALDOB','PCK1','HAL','ARG1']),
 'C paper2 landmark(40)': (None, None),   # filled from the LM file below
}

def load():
    df=pd.read_csv(os.path.join(P1,'raw_panel_counts.csv'),low_memory=False); df['donor']=df['donor'].astype(str)
    md=pd.read_csv(os.path.join(P1,'metadata_all_cells.csv'),usecols=['Patient.ID','Fibrosis.score..F0.4.'],low_memory=False).rename(
        columns={'Patient.ID':'donor','Fibrosis.score..F0.4.':'F'})
    md['donor']=md['donor'].astype(str); md['F']=pd.to_numeric(md['F'],errors='coerce')
    df=df.merge(md.groupby('donor').first().reset_index(),on='donor',how='left')
    lm=pd.read_csv(os.path.join(P1,'paper2_landmark_raw_counts.csv'),low_memory=False)
    lmpc=[g for g in open('signatures/pericentral_paper2_landmark.txt').read().split() if g in lm.columns]
    lmpp=[g for g in open('signatures/periportal_paper2_landmark.txt').read().split() if g in lm.columns]
    SETS['C paper2 landmark(40)']=(lmpc,lmpp)
    # join LM-only genes (those not already in the panel) on cell_id
    extra=[g for g in (lmpc+lmpp) if g not in df.columns]
    df=df.merge(lm[['cell_id']+extra],on='cell_id',how='left')
    hep=df[(df['annotation']=='Hepatocytes')&(~df['donor'].str.startswith('CL'))&(df['stage']!='Healthy control')].copy()
    return hep

def per_donor(hep, pcg, ppg):
    rng=np.random.RandomState(0); h=hep[hep['E_raw']>=B].copy(); p=(B/h['E_raw'].values)
    genes=[g for g in set(pcg+ppg) if g in h.columns]
    ds={g:rng.binomial(h[g].fillna(0).values.astype(int),p) for g in genes}
    PCp=sum(ds[g] for g in pcg if g in ds); PPp=sum(ds[g] for g in ppg if g in ds)
    tot=PCp+PPp; frac=np.where(tot>0, PCp/np.maximum(tot,1), np.nan)
    h['tot']=tot; h['frac']=frac; h['informative']=tot>=3; h['polar']=(frac<=0.25)|(frac>=0.75)
    rows=[]
    for d,s in h.groupby('donor'):
        inf=s[s['informative']]
        rows.append(dict(donor=d,F=s['F'].iloc[0],N=len(s),
            mean_share=(inf['frac'].mean() if len(inf)>=20 else np.nan),
            polar=(inf['polar'].mean() if len(inf)>=20 else np.nan)))
    return pd.DataFrame(rows)

def main():
    hep=load()
    print(f"biopsy hepatocyte nuclei (>= B): see per-set N; depth budget B={B}\n")
    out=[]
    for name,(pcg,ppg) in SETS.items():
        D=per_donor(hep,pcg,ppg)
        meds={F:D[D.F==F] for F in [0,1,2,3,4]}
        def med(F,col):
            v=meds[F][col].dropna(); return v.median() if len(v) else np.nan
        polar={F:med(F,'polar') for F in [0,1,2,3,4]}
        share={F:med(F,'mean_share') for F in [0,1,2,3,4]}
        d14=polar[1]-polar[4]; s14=share[1]-share[4]
        print(f"=== {name}  (PC={len(pcg)} genes, PP={len(ppg)} genes) ===")
        print("    zonal-extreme(polar) fraction by F:  "+"  ".join(f"F{F}={polar[F]:.3f}" for F in [0,1,2,3,4])
              +f"   | F1-F4 delta={d14:+.3f}")
        print("    mean PC-share by F:                  "+"  ".join(f"F{F}={share[F]:.3f}" for F in [0,1,2,3,4])
              +f"   | F1-F4 delta={s14:+.3f}\n")
        out.append(dict(marker_set=name,n_PC=len(pcg),n_PP=len(ppg),
            polar_F0=round(polar[0],3),polar_F1=round(polar[1],3),polar_F2=round(polar[2],3),
            polar_F3=round(polar[3],3),polar_F4=round(polar[4],3),polar_F1_minus_F4=round(d14,3),
            share_F1=round(share[1],3),share_F4=round(share[4],3),share_F1_minus_F4=round(s14,3)))
    pd.DataFrame(out).to_csv(os.path.join(str(config.ANALYSIS_TABLES),'markerset_robustness.csv'),index=False)
    print("wrote markerset_robustness.csv")
    print("Read: if the F0-F4 profile is flat/non-monotone in ALL THREE sets, the biopsy null is")
    print("invariant to marker-set choice — including Paper 2's own 40 landmark genes.")

if __name__=='__main__': main()
