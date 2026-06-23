"""Raw-data QUALITY CHECK: is the sequencing batch (SLX run) randomized w.r.t. disease stage, or confounded?
Batch field = the SLX run extracted from orig.ident (e.g. 'SLX-21151-SITTB7' -> run 'SLX-21151').
(manuscript.expt = 'CG' for all 47 donors — a single experiment label, no separation there.)
Reports: run x stage and run x fibrosis cross-tabs (donor-level), a Cramer's V association, whether any
stage sits on a dedicated run, and — critically for the DGE — whether the F4 biopsy donors share runs with
earlier stages (so the F1-vs-F4 contrast is estimable apart from batch). Output: results/tables/analysis/batch_qc.csv
"""
import os, sys, re
import numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def cramers_v(ct):
    chi2 = stats.chi2_contingency(ct, correction=False)[0]
    n = ct.values.sum(); r, k = ct.shape
    return np.sqrt((chi2/n) / max(1, min(r-1, k-1)))

def main():
    md = pd.read_csv(os.path.join(str(config.PAPER1), 'metadata_all_cells.csv'), low_memory=False)
    md['donor'] = md['Patient.ID'].astype(str)
    md['F'] = pd.to_numeric(md['Fibrosis.score..F0.4.'], errors='coerce')
    dd = md.groupby('donor').agg(stage=('Disease.status','first'), F=('F','first'),
                                 orig=('orig.ident','first')).reset_index()
    dd['run'] = dd['orig'].astype(str).str.extract(r'(SLX-\d+)')
    dd['source'] = np.where(dd['donor'].str.startswith('CL'),'explant',
                    np.where(dd['stage']=='Healthy control','healthy','biopsy'))
    dd.to_csv(os.path.join(str(config.ANALYSIS_TABLES),'batch_qc.csv'), index=False)
    print(f"{dd['run'].nunique()} SLX runs over {len(dd)} donors\n")

    print("=== run x stage (donor counts) ===")
    print(pd.crosstab(dd['run'], dd['stage']).to_string())
    print(f"\nrun x source Cramer's V = {cramers_v(pd.crosstab(dd['run'],dd['source'])):.2f} "
          "(1 = run perfectly predicts tissue source)")
    # dedicated runs (single stage)
    ded = pd.crosstab(dd['run'],dd['stage']); single = ded[(ded>0).sum(axis=1)==1]
    print(f"runs carrying only ONE stage: {list(single.index)}")

    bi = dd[dd['source']=='biopsy']
    print(f"\n=== BIOPSY only (n={len(bi)}): run x fibrosis F ===")
    ctb = pd.crosstab(bi['run'], bi['F']); print(ctb.to_string())
    print(f"\nbiopsy run x F Cramer's V = {cramers_v(ctb):.2f}")
    # the crux for F1-vs-F4: which runs hold the F4 donors, and do they also hold earlier stages?
    f4runs = bi[bi['F']==4]['run'].unique()
    print(f"\nF4 biopsy donors (n={int((bi['F']==4).sum())}) are on runs: {list(f4runs)}")
    for r in f4runs:
        stages_here = sorted(bi[bi['run']==r]['F'].dropna().astype(int).unique())
        print(f"  {r}: also carries F = {stages_here}  -> {'MIXED (within-batch contrast exists)' if len(stages_here)>1 else 'F4-ONLY (confounded!)'}")
    print("\nRead: if each F4 run also carries earlier-F donors, the F1-vs-F4 effect is NOT collinear with")
    print("batch (estimable within-run). If an F4 run is F4-only, that part is confounded -> sensitivity needed.")

if __name__ == '__main__':
    main()
