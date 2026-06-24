"""TEST 4 of the adversarial detox-dimming verification: the ABSOLUTE, NON-COMPOSITIONAL
measure. Within-PC-cell detox burden = detox UMIs per pericentral nucleus on DEPTH-MATCHED
(binomial-thinned to B=1500 UMIs) counts. This is per-cell and depth-matched, so it is immune
to the compositional/library-budget concern that afflicts CPM camera/GSEA.

Reproduces mde.py's pipeline EXACTLY (same DETOX genes, same PC gate, same thinning), then
tabulates the per-stage mean within-PC detox burden + donor-level Spearman trend + the F1->F4
contrast vs the published MDE. Donor-level inference, biopsy-only (CL*/Healthy excluded).

Output: results/tables/analysis/geneset_verify_within_pc_detox.csv
"""
import os, sys
import numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# --- identical to src/confound/mde.py ---
PCanch = ['GLUL', 'CYP3A4']
PPanch = ['ASS1', 'PCK1', 'HAL', 'ALDOB']
DETOX  = ['CYP2E1', 'CYP1A2', 'ADH4', 'AKR1D1', 'SLCO1B3']
B = 1500
OUT = os.path.join(str(config.ANALYSIS_TABLES), 'geneset_verify_within_pc_detox.csv')


def load():
    df = pd.read_csv(os.path.join(str(config.PAPER1), 'raw_panel_counts.csv'), low_memory=False)
    df['donor'] = df['donor'].astype(str)
    md = pd.read_csv(os.path.join(str(config.PAPER1), 'metadata_all_cells.csv'),
                     usecols=['Patient.ID', 'Fibrosis.score..F0.4.'], low_memory=False).rename(
        columns={'Patient.ID': 'donor', 'Fibrosis.score..F0.4.': 'F'})
    md['donor'] = md['donor'].astype(str)
    md['F'] = pd.to_numeric(md['F'], errors='coerce')
    df = df.merge(md.groupby('donor').first().reset_index(), on='donor', how='left')
    hep = df[(df['annotation'] == 'Hepatocytes') & (~df['donor'].str.startswith('CL'))
             & (df['stage'] != 'Healthy control')].copy()
    return hep


def per_donor(hep):
    rng = np.random.RandomState(0)
    h = hep[hep['E_raw'] >= B].copy()
    p = (B / h['E_raw'].values)
    genes = set(PCanch + PPanch + DETOX)
    ds = {g: rng.binomial(h[g].values.astype(int), p) for g in genes}
    PCh1 = sum((ds[g] > 0).astype(int) for g in PCanch)
    PPh1 = sum((ds[g] > 0).astype(int) for g in PPanch)
    h['PC'] = (PCh1 >= 1) & (PPh1 < 2)           # PC gate exactly as mde.py
    h['detoxsum'] = sum(ds[g] for g in DETOX)
    rows = []
    for d, s in h.groupby('donor'):
        pcm = s[s['PC']]
        rows.append(dict(donor=d, F=s['F'].iloc[0],
                         n_pc=len(pcm),
                         detox=(pcm['detoxsum'].mean() if len(pcm) >= 20 else np.nan)))
    return pd.DataFrame(rows)


def main():
    D = per_donor(load())
    Dd = D.dropna(subset=['detox', 'F']).copy()
    print(f"biopsy donors with >=20 PC nuclei: n={len(Dd)} of {len(D)}")
    print(f"F dist among usable: {[int((Dd.F==f).sum()) for f in [0,1,2,3,4]]}\n")

    # per-stage mean within-PC detox burden (UMIs/nucleus), donor-level
    rows = []
    print(f"{'stage':6s}{'nDonors':>8}{'mean':>9}{'sd':>8}{'min':>8}{'max':>8}")
    for f in [0, 1, 2, 3, 4]:
        v = Dd[Dd.F == f]['detox'].values
        if len(v):
            print(f"F{f:<5d}{len(v):>8d}{v.mean():>9.3f}{v.std(ddof=1) if len(v)>1 else float('nan'):>8.3f}{v.min():>8.3f}{v.max():>8.3f}")
            rows.append(dict(stage=f"F{f}", nDonors=len(v), mean=round(v.mean(), 3),
                             sd=round(v.std(ddof=1), 3) if len(v) > 1 else np.nan,
                             vmin=round(v.min(), 3), vmax=round(v.max(), 3)))

    # donor-level trend across all stages
    rho = stats.spearmanr(Dd['F'], Dd['detox'])
    print(f"\ndonor-level Spearman(detox, F) = {rho.correlation:+.3f}  p={rho.pvalue:.3f}  (n={len(Dd)})")

    # F1 -> F4 contrast (the published '12.7->8.9' direction) with Welch t-test + 95% CI of diff
    a = Dd[Dd.F == 1]['detox'].values
    b = Dd[Dd.F == 4]['detox'].values
    diff = b.mean() - a.mean()
    se = np.sqrt(a.var(ddof=1)/len(a) + b.var(ddof=1)/len(b))
    tt = stats.ttest_ind(a, b, equal_var=False)
    dfw = (a.var(ddof=1)/len(a) + b.var(ddof=1)/len(b))**2 / (
        (a.var(ddof=1)/len(a))**2/(len(a)-1) + (b.var(ddof=1)/len(b))**2/(len(b)-1))
    tcrit = stats.t.ppf(0.975, dfw)
    ci = (diff - tcrit*se, diff + tcrit*se)
    sp = np.sqrt(((len(a)-1)*a.var(ddof=1)+(len(b)-1)*b.var(ddof=1))/(len(a)+len(b)-2))
    cohend = diff/sp
    print(f"\nF1->F4 within-PC detox burden: {a.mean():.3f} -> {b.mean():.3f} "
          f"(diff {diff:+.3f}, 95% CI [{ci[0]:+.3f}, {ci[1]:+.3f}])")
    print(f"  Welch t={tt.statistic:.3f} p={tt.pvalue:.3f}  Cohen d={cohend:+.3f}")
    print(f"  published MDE (F1 vs F4, 80% power) = 2.782 UMIs/nuc; |observed diff| = {abs(diff):.3f}")

    rows.append(dict(stage='trend_rho', nDonors=len(Dd), mean=round(rho.correlation, 3),
                     sd=round(rho.pvalue, 4), vmin=np.nan, vmax=np.nan))
    rows.append(dict(stage='F1_to_F4_diff', nDonors=f"{len(a)}vs{len(b)}", mean=round(diff, 3),
                     sd=round(tt.pvalue, 4), vmin=round(ci[0], 3), vmax=round(ci[1], 3)))
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"\nwrote {OUT}")


if __name__ == '__main__':
    main()
