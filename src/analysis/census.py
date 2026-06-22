"""PC/PP/dual/null anchor census on RAW counts, depth-matched, with sensitivity grid + the
skew/normalization check. Unit = donor. Implements the consensus scheme (ChatGPT + both agents).

Outputs (results/tables/analysis/):
  census_donor_level.csv        per donor: F, N_hep, PC/PP/dual/null counts+fractions, within-PC detox
  census_sensitivity.csv        PC/PP/dual/null by F-stage across threshold variants
Prints: (0) skew/normalization check, (1) census by stage + sensitivity, (2) within-PC detox burden,
        (3) donor-level detox ranges (is the 66->49 drift shared or driven by a few donors?).
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
rng = np.random.RandomState(0)
OUTD = str(config.ANALYSIS_TABLES)

PCid=['GLUL','CYP3A4']; PPset=['ASS1','PCK1','HAL','ALDOB']; CPS=['CPS1']
DETOX=['CYP2E1','CYP1A2','ADH4','AKR1D1','SLCO1B3']
B=1500

def load():
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
        return f'F{int(F)}-biopsy' if pd.notna(F) else 'F?'
    hep['grp']=[grp(d,s,F) for d,s,F in zip(hep['donor'],hep['stage'],hep['F'])]
    return hep

def downsample(hep):
    hep=hep[hep['E_raw']>=B].copy()
    p=(B/hep['E_raw']).values
    for g in set(PCid+PPset+CPS+DETOX+['ALB']):
        if g in hep.columns: hep[g+'_ds']=rng.binomial(hep[g].values.astype(int),p)
    return hep

ORDER=['Healthy','F0-biopsy','F1-biopsy','F2-biopsy','F3-biopsy','F4-biopsy','Explant(end)']
def by_stage(hep,colfun):
    rows=[]
    for g,s in hep.groupby('grp'):
        vals=[colfun(sd) for _,sd in s.groupby('donor')]
        vals=[v for v in vals if v is not None and np.isfinite(v)]
        rows.append((g,len(vals),np.median(vals) if vals else np.nan))
    R=pd.DataFrame(rows,columns=['group','nD','median']).set_index('group')
    return R.reindex([g for g in ORDER if g in R.index])

def census(hep, pcgenes, ppgenes, k, nPC, nPP, sfx='_ds'):
    PChit=(hep[[g+sfx for g in pcgenes]]>=k).sum(axis=1)
    PPhit=(hep[[g+sfx for g in ppgenes]]>=k).sum(axis=1)
    pc=(PChit>=nPC)&(PPhit<nPP); pp=(PPhit>=nPP)&(PChit<nPC)
    dual=(PChit>=nPC)&(PPhit>=nPP); null=(PChit<nPC)&(PPhit<nPP)
    return np.select([pc,pp,dual],['PC','PP','dual'],default='null')

def main():
    hep=load(); hd=downsample(hep)
    print(f"hepatocytes: {len(hep):,}  after depth>= {B}: {len(hd):,}  donors: {hd['donor'].nunique()}")

    # ===== (0) SKEW / NORMALIZATION CHECK =====
    print("\n"+"="*70+"\n(0) SKEW / NORMALIZATION CHECK\n"+"="*70)
    # ALB share of library by stage (does the denominator drift?)
    alb=by_stage(hep, lambda s: 100*s['ALB'].sum()/s['E_raw'].sum())
    # detox as RATIO (UMIs/10k) vs ABSOLUTE count at matched depth (per cell, downsampled)
    ratio=by_stage(hep, lambda s: 1e4*s[DETOX].values.sum()/s['E_raw'].sum())
    absol=by_stage(hd,  lambda s: s[[g+'_ds' for g in DETOX]].values.sum()/len(s))
    cmp=pd.DataFrame({'ALB_%lib':alb['median'],'detox_UMIs/10k(ratio)':ratio['median'],
                      'detox_count/cell @B1500(absolute)':absol['median'],'nD':alb['nD']})
    with pd.option_context('display.float_format',lambda x:f'{x:.2f}'):
        print(cmp.to_string())
    print("If ALB%lib is stable across F and the absolute (depth-matched) detox count tracks the ratio,")
    print("the 66->49 ratio drift is NOT a denominator/skew artifact.")

    # ===== (1) CENSUS + SENSITIVITY =====
    print("\n"+"="*70+"\n(1) CENSUS by stage (median donor fraction) + SENSITIVITY\n"+"="*70)
    variants={
      'primary k1 PC1of2 PP2of4':       (PCid, PPset, 1,1,2),
      'k2 (single-UMI fragility)':       (PCid, PPset, 2,1,2),
      'PP excl ALDOB (2of3)':            (PCid, ['ASS1','PCK1','HAL'], 1,1,2),
      'PP=CPS1/ALDOB/ASS1 (2of3)':       (PCid, ['CPS1','ALDOB','ASS1'], 1,1,2),
      'strict identity PC2of2 PP3of4':   (PCid, PPset, 1,2,3),
    }
    sens_rows=[]
    for name,(pcg,ppg,k,nPC,nPP) in variants.items():
        hd['cls']=census(hd,pcg,ppg,k,nPC,nPP)
        for cls in ['PC','PP','dual','null']:
            r=by_stage(hd, lambda s,c=cls: (s['cls']==c).mean())
            for grp in r.index:
                sens_rows.append(dict(variant=name,cls=cls,group=grp,frac=r.loc[grp,'median']))
        # print compact PC + dual rows (the decisive ones)
        pcr=by_stage(hd, lambda s: (s['cls']=='PC').mean())['median']
        dur=by_stage(hd, lambda s: (s['cls']=='dual').mean())['median']
        print(f"\n[{name}]")
        print("  PC-anchor:", "  ".join(f"{g.split('-')[0]}={pcr.get(g,np.nan):.3f}" for g in pcr.index))
        print("  dual:     ", "  ".join(f"{g.split('-')[0]}={dur.get(g,np.nan):.3f}" for g in dur.index))
    pd.DataFrame(sens_rows).to_csv(os.path.join(OUTD,'census_sensitivity.csv'),index=False)

    # ===== (2) WITHIN-PC DETOX BURDEN (dimming readout, burden not detection) =====
    print("\n"+"="*70+"\n(2) WITHIN-PC-anchor detox BURDEN (downsampled counts/cell @B1500)\n"+"="*70)
    hd['cls']=census(hd,PCid,PPset,1,1,2)
    bur=by_stage(hd[hd['cls']=='PC'], lambda s: s[[g+'_ds' for g in DETOX]].values.sum()/len(s) if len(s)>=20 else None)
    det=by_stage(hd[hd['cls']=='PC'], lambda s: (s[[g+'_ds' for g in DETOX]]>0).any(axis=1).mean() if len(s)>=20 else None)
    print(pd.DataFrame({'detox_count/PCcell':bur['median'],'detox_detect_in_PC':det['median'],'nD':bur['nD']}).round(3).to_string())

    # ===== (3) DONOR-LEVEL detox ranges (is 66->49 shared or a few donors?) =====
    print("\n"+"="*70+"\n(3) DONOR-LEVEL detox UMIs/10k by F (biopsy) — min / median / max per stage\n"+"="*70)
    pv=[]
    for g,s in hep[hep['grp'].str.endswith('biopsy')].groupby('grp'):
        vals=sorted(round(1e4*sd[DETOX].values.sum()/sd['E_raw'].sum(),0) for _,sd in s.groupby('donor'))
        pv.append((g,len(vals),min(vals),float(np.median(vals)),max(vals),vals))
    for g,n,mn,md_,mx,vals in sorted(pv):
        print(f"  {g}: n={n}  min={mn:.0f} med={md_:.0f} max={mx:.0f}   donors={[int(v) for v in vals]}")

    # donor-level census CSV
    rows=[]
    for d,s in hd.groupby('donor'):
        s=s.copy(); s['cls']=census(s,PCid,PPset,1,1,2)
        n=len(s); cnt=s['cls'].value_counts()
        rows.append(dict(donor=d,F=s['F'].iloc[0],grp=s['grp'].iloc[0],N_hep=n,
            PC=int(cnt.get('PC',0)),PP=int(cnt.get('PP',0)),dual=int(cnt.get('dual',0)),null=int(cnt.get('null',0))))
    pd.DataFrame(rows).to_csv(os.path.join(OUTD,'census_donor_level.csv'),index=False)
    print("\nwrote census_donor_level.csv, census_sensitivity.csv")

if __name__=='__main__':
    main()
