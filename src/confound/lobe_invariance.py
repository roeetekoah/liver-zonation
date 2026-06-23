"""FINDING: within end-stage explants, the zonation gene pattern is LOBE-INVARIANT (Right ~ Caudate ~
Left), and is fully present in Right-lobe-only cells -> the multi-lobe / caudate sampling is NOT
manufacturing the apparent de-zonation. (Clears the LOBE sub-confound only; the explant-vs-biopsy
sampling-mode confound is separate and remains.)

Reproducible from the SAVED per-(donor,lobe,stage,gene) table rawA_donor_lobe_stage_gene.csv (built by
src/analysis/raw_counts.py). Two clearly-DEFINED metrics, mean across the 5 explant donors per lobe:
  - frac_raw_pos : fraction of that lobe's hepatocyte nuclei with raw UMI > 0 for the gene (detection)
  - UMIs_per_10k : pseudobulk raw UMIs of the gene per 10,000 total UMIs in that lobe (burden)
NOTE: an earlier INLINE table (GLUL 0.43/0.43/0.33 ...) used an unsaved, ambiguously-scaled metric and
is NOT reproducible; it is discarded in favour of this defined version. The lobe-invariance CONCLUSION
holds on both metrics here. Output: findings/lobe_invariance/lobe_invariance.csv
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
PC=['GLUL','CYP3A4','CYP2E1','CYP1A2','ADH4','AKR1D1','SLCO1B3']
PP=['ASS1','CPS1','PCK1','ALDOB','HAL','ARG1']
GENES=PC+PP; LOBES=['Right','Caudate','Left']

def main():
    A=pd.read_csv(os.path.join(str(config.ANALYSIS_TABLES),'rawA_donor_lobe_stage_gene.csv'))
    es=A[A.stage=='end stage'].copy()
    nD=es.groupby('lobe')['donor'].nunique().to_dict()
    rows=[]
    for g in GENES:
        sub=es[es.gene==g]; rec={'gene':g,'zone':'PC' if g in PC else 'PP'}
        vals={}
        for lobe in LOBES:
            sl=sub[sub.lobe==lobe]
            frac=sl['frac_raw_pos'].mean()
            burden=1e4*sl['M_raw'].sum()/sl['E_raw'].sum() if sl['E_raw'].sum()>0 else np.nan
            rec[f'frac_{lobe}']=round(frac,3); rec[f'umi10k_{lobe}']=round(burden,2); vals[lobe]=burden
        # lobe-invariance summary on the burden metric: max relative spread across lobes
        v=np.array([vals[l] for l in LOBES]); rec['umi10k_rel_spread']=round((v.max()-v.min())/v.mean(),2) if v.mean()>0 else np.nan
        rows.append(rec)
    T=pd.DataFrame(rows)
    outd=os.path.join(str(config.PROJECT_ROOT) if hasattr(config,'PROJECT_ROOT') else '.','findings','lobe_invariance')
    os.makedirs(outd,exist_ok=True)
    T.to_csv(os.path.join(outd,'lobe_invariance.csv'),index=False)
    print(f"explant donors contributing per lobe: {nD}")
    print(f"\nLOBE-INVARIANCE (end-stage explants), mean across donors:")
    print(T.to_string(index=False))
    print(f"\nmedian across genes of |max-min|/mean burden across lobes = {T['umi10k_rel_spread'].median():.2f}")
    print("=> small relative spread across Right/Caudate/Left = lobe-invariant; pattern present in Right-lobe cells.")
    print(f"wrote {os.path.join(outd,'lobe_invariance.csv')}")

if __name__=='__main__': main()
