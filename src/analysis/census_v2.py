"""Hardened census/polarization: (1) MULTI-DRAW depth-matching (average over M thinning draws, not one
seed); (2) committed B-sweep {1000,1500,3000}; (3) gradient-compression as ABSOLUTE count-bins with an
informative floor q + sensitivity {2,3,5}; (4) anchor-definition sensitivity (GLUL-only / CYP3A4-only /
both); (5) within-PC detox with PC defined WITHOUT the detox genes. Unit = donor; language = nuclei.
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
OUTD=str(config.ANALYSIS_TABLES)

PCprog=['GLUL','CYP3A4','CYP2E1','CYP1A2','ADH4','AKR1D1','SLCO1B3']
PPprog=['CPS1','ASS1','ALDOB','PCK1','HAL','ARG1']
PPanch=['ASS1','PCK1','HAL','ALDOB']; DETOX=['CYP2E1','CYP1A2','ADH4','AKR1D1','SLCO1B3']
STAGES=['F0','F1','F2','F3','F4']

def load():
    df=pd.read_csv(os.path.join(str(config.PAPER1),'raw_panel_counts.csv'),low_memory=False)
    df['donor']=df['donor'].astype(str); hep=df[df['annotation']=='Hepatocytes'].copy()
    md=pd.read_csv(os.path.join(str(config.PAPER1),'metadata_all_cells.csv'),
        usecols=['Patient.ID','Fibrosis.score..F0.4.'],low_memory=False).rename(
        columns={'Patient.ID':'donor','Fibrosis.score..F0.4.':'F'})
    md['donor']=md['donor'].astype(str); md['F']=pd.to_numeric(md['F'],errors='coerce')
    hep=hep.merge(md.groupby('donor').first().reset_index(),on='donor',how='left')
    hep['biopsy']=(~hep['donor'].str.startswith('CL'))&(hep['stage']!='Healthy control')
    return hep

def thin(vals,p,rng): return rng.binomial(vals.astype(int),p)

def multidraw_census(hep,B,pcg,M=8):
    """avg over M draws: donor-level PC/PP/dual/null fractions, then median across biopsy donors by F."""
    h=hep[hep['biopsy']&(hep['E_raw']>=B)].copy()
    acc={c:{F:[] for F in range(5)} for c in ['PC','PP','dual','null']}
    perdonor={c:{} for c in ['PC','dual']}
    for m in range(M):
        rng=np.random.RandomState(m); p=(B/h['E_raw']).values
        PCh=sum((thin(h[g].values,p,rng)>0) for g in pcg)
        PPh=sum((thin(h[g].values,p,rng)>0) for g in PPanch)
        cls=np.where((PCh>=1)&(PPh<2),'PC',np.where((PPh>=2)&(PCh<1),'PP',
              np.where((PCh>=1)&(PPh>=2),'dual','null')))
        h['_c']=cls
        for (d,F),s in h.groupby(['donor','F']):
            if len(s)<50 or pd.isna(F): continue
            for c in ['PC','PP','dual','null']:
                acc[c][int(F)].append((d,(s['_c']==c).mean()))
    out={}
    for c in ['PC','PP','dual','null']:
        out[c]=[np.median([v for dd,v in acc[c][F]]) if acc[c][F] else np.nan for F in range(5)]
    return out

def main():
    hep=load()
    print("=== (1+2+4) CENSUS robustness: multi-draw (M=8), B-sweep, anchor-definition sweep ===")
    print("PC-anchor & dual median-donor fraction by F (biopsy). Flat across F at every setting = no collapse.")
    for pcg,lab in [(['GLUL','CYP3A4'],'PC=GLUL|CYP3A4'),(['GLUL'],'PC=GLUL-only'),(['CYP3A4'],'PC=CYP3A4-only')]:
        for B in [1000,1500,3000]:
            o=multidraw_census(hep,B,pcg)
            pc=' '.join(f'{x:.3f}' for x in o['PC']); du=' '.join(f'{x:.3f}' for x in o['dual'])
            print(f"  [{lab:16s} B={B}] PC: {pc}   dual: {du}   (F0 F1 F2 F3 F4)")

    print("\n=== (3) GRADIENT COMPRESSION as absolute count-bins, informative floor q (sensitivity) ===")
    print("among INFORMATIVE nuclei (PC+PP>=q): fractions in PC-pole/PC-lean/middle/PP-lean/PP-pole;")
    print("informative = % of nuclei above floor. Compression = poles shrink, middle grows. (median donor)")
    B=1500
    for q in [2,3,5]:
        h=hep[hep['biopsy']&(hep['E_raw']>=B)].copy()
        rows=[]
        M=8
        # accumulate per (donor,F) bin fractions averaged over draws
        binacc={}
        for m in range(M):
            rng=np.random.RandomState(m); p=(B/h['E_raw']).values
            PC=sum(thin(h[g].values,p,rng) for g in PCprog)
            PP=sum(thin(h[g].values,p,rng) for g in PPprog)
            h['PC']=PC; h['PP']=PP; tot=PC+PP
            info=tot>=q
            cls=np.full(len(h),'uninf',dtype=object)
            cls[info&(PP==0)]='PCpole'; cls[info&(PC==0)]='PPpole'
            cls[info&(PC>PP)&(PP>0)]='PClean'; cls[info&(PP>PC)&(PC>0)]='PPlean'
            cls[info&(PC==PP)&(tot>=q)]='mid'
            h['_b']=cls
            for (d,F),s in h.groupby(['donor','F']):
                if len(s)<50 or pd.isna(F): continue
                inf=s[s['_b']!='uninf']
                key=(d,int(F))
                rec=binacc.setdefault(key,{k:[] for k in ['info','PCpole','PClean','mid','PPlean','PPpole']})
                rec['info'].append((s['_b']!='uninf').mean())
                for k in ['PCpole','PClean','mid','PPlean','PPpole']:
                    rec[k].append((inf['_b']==k).mean() if len(inf) else np.nan)
        # median across donors by F
        print(f"\n  -- floor q={q} --   F:  info%  PCpole PClean  mid   PPlean PPpole")
        for F in range(5):
            dd=[ (np.mean(r['info']),np.nanmean(r['PCpole']),np.nanmean(r['PClean']),np.nanmean(r['mid']),
                  np.nanmean(r['PPlean']),np.nanmean(r['PPpole'])) for (d,f),r in binacc.items() if f==F]
            if not dd: continue
            a=np.nanmedian(np.array(dd),axis=0)
            print(f"        F{F}: {a[0]:.3f}  {a[1]:.3f}  {a[2]:.3f}  {a[3]:.3f}  {a[4]:.3f}  {a[5]:.3f}")

    print("\n=== (5) within-PC detox burden (PC=GLUL|CYP3A4, detox EXCLUDED from anchor); donor-level ===")
    B=1500; h=hep[hep['biopsy']&(hep['E_raw']>=B)].copy(); M=8
    perF={F:[] for F in range(5)}
    for m in range(M):
        rng=np.random.RandomState(m); p=(B/h['E_raw']).values
        PCh=sum((thin(h[g].values,p,rng)>0) for g in ['GLUL','CYP3A4'])
        PPh=sum((thin(h[g].values,p,rng)>0) for g in PPanch)
        isPC=(PCh>=1)&(PPh<2)
        dx=sum(thin(h[g].values,p,rng) for g in DETOX)
        h['_pc']=isPC; h['_dx']=dx
        for (d,F),s in h.groupby(['donor','F']):
            pc=s[s['_pc']]
            if len(pc)>=20 and not pd.isna(F): perF[int(F)].append((d,pc['_dx'].mean()))
    print("   F:  median detox UMIs/PC-nucleus (depth-matched, M-draw avg)   [min..max donor]")
    for F in range(5):
        if not perF[F]: continue
        vals=[v for d,v in perF[F]]; print(f"   F{F}: {np.median(vals):.2f}   [{min(vals):.2f}..{max(vals):.2f}]  nD={len(set(d for d,v in perF[F]))}")

if __name__=='__main__': main()
