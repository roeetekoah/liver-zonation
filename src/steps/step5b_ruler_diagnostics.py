"""Step 5b — "ruler" diagnostics: is the coordinate a trustworthy measuring stick? (A5b)

Separates "the signature genes turned off" (program level) from "the zonation axis
dissolved" (restriction lost) — the collapse claim needs the latter. Descriptive only:
NO p-values here; donor-level inference happens in Step 6.
"""
from __future__ import annotations
import os, sys
import numpy as np, pandas as pd
from scipy.stats import spearmanr
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # src/
import config
from steps.common import log, OUT, STAGE_ORDER, S2R, _is_na, set_dir


def _mean_pairwise_corr(col, gene_list, mask, max_genes=200, seed=0):
    """Mean off-diagonal Pearson corr among present genes' z-vectors (sub-sampled for speed)."""
    g = [x for x in gene_list if x in col]
    if len(g) < 2: return np.nan
    rng = np.random.RandomState(seed)
    if len(g) > max_genes: g = list(np.array(g)[rng.choice(len(g), max_genes, replace=False)])
    Z = np.vstack([col[x][mask] for x in g])
    if Z.shape[1] < 3: return np.nan
    C = np.corrcoef(Z); iu = np.triu_indices_from(C, k=1)
    return float(np.nanmean(C[iu]))


def _coord_from_halves(col, pc_g, pp_g, mask, rng):
    """Build two sub-coordinates from disjoint random halves of PC and PP genes (split-half)."""
    def half(genes):
        present = [x for x in genes if x in col]
        if len(present) < 2: return None, None
        idx = rng.permutation(len(present)); h = len(present) // 2
        return [present[i] for i in idx[:h]], [present[i] for i in idx[h:]]
    pcA, pcB = half(pc_g); ppA, ppB = half(pp_g)
    if pcA is None or ppA is None: return None, None
    def arm(genes):
        v = np.mean([col[x][mask] for x in genes], axis=0); return (v - v.mean()) / (v.std() + 1e-9)
    return arm(pcA) - arm(ppA), arm(pcB) - arm(ppB)


def ruler_diagnostics(coord, pc, pp, col, stage, donor, pc_genes, pp_genes,
                      which="", n_splits=20):
    """Per-stage descriptive diagnostics of the coordinate (the 'ruler').

    Per stage: n_cells/n_donors; cross-program anti-correlation corr(pc,pp); coordinate
    spread (std, IQR); within-program coherence (mean pairwise corr among PC; among PP);
    split-half reproducibility (corr of two half-coordinates, repeated n_splits times,
    mean+CI); and program level (mean pc/pp score) vs spread (off vs restriction-lost).
    Writes results/tables/ruler_diagnostics_<set>.csv.
    """
    log(f"Step 5b: ruler diagnostics [set={which}] — descriptive (no p-values)")
    rows = []
    for st in [s for s in STAGE_ORDER if (stage == s).any()]:
        m = stage == st
        n_cells = int(m.sum())
        d_st = donor[m]; n_donors = int(pd.unique(d_st[~_is_na(d_st).values]).size)
        anticorr = float(spearmanr(pc[m], pp[m]).statistic) if n_cells > 3 else np.nan
        c = coord[m]; spread = float(np.nanstd(c))
        iqr = float(np.nanpercentile(c, 75) - np.nanpercentile(c, 25)) if n_cells else np.nan
        coh_pc = _mean_pairwise_corr(col, pc_genes, m)
        coh_pp = _mean_pairwise_corr(col, pp_genes, m)
        rng = np.random.RandomState(S2R.get(st, 0) + 1)
        sh = []
        for _ in range(n_splits if n_cells > 10 else 0):
            c1, c2 = _coord_from_halves(col, pc_genes, pp_genes, m, rng)
            if c1 is not None and c1.std() > 0 and c2.std() > 0:
                sh.append(spearmanr(c1, c2).statistic)
        sh = np.array(sh, float)
        sh_mean = float(np.nanmean(sh)) if sh.size else np.nan
        sh_lo, sh_hi = ((float(np.nanpercentile(sh, 2.5)), float(np.nanpercentile(sh, 97.5)))
                        if sh.size else (np.nan, np.nan))
        rows.append({"signature_set": which, "stage": st, "stage_rank": S2R.get(st, -1),
                     "n_cells": n_cells, "n_donors": n_donors,
                     "pc_pp_anticorr": anticorr, "coord_spread_std": spread, "coord_iqr": iqr,
                     "coherence_pc": coh_pc, "coherence_pp": coh_pp,
                     "splithalf_rho_mean": sh_mean, "splithalf_rho_lo": sh_lo, "splithalf_rho_hi": sh_hi,
                     "mean_pc_score": float(np.nanmean(pc[m])), "mean_pp_score": float(np.nanmean(pp[m]))})
    dd = pd.DataFrame(rows)
    out = os.path.join(set_dir(which), "ruler_diagnostics.csv")
    dd.to_csv(out, index=False)
    for _, r in dd.iterrows():
        log(f"  {r['stage']:20s} n={r['n_cells']:6d} ({r['n_donors']:2d} donors)  "
            f"anticorr={r['pc_pp_anticorr']:+.3f}  spread={r['coord_spread_std']:.3f}  "
            f"split-half rho={r['splithalf_rho_mean']:+.3f}")
    log(f"  wrote {out}")
    return dd
