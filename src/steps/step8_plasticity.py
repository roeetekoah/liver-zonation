"""Step 8 — de-zonation <-> plasticity coupling, DONOR-LEVEL (Artefact A8, H3).

Headline statistic is donor-level (per-donor Spearman + sign test + bootstrap CI over
donors), which removes the stage/donor confound. A pooled OLS is kept but labelled
DESCRIPTIVE (cell-level SE), never the headline.
"""
from __future__ import annotations
import os, sys
import numpy as np, pandas as pd
from scipy.stats import spearmanr
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # src/
import config
from steps.common import log, OUT, SHORT, S2R, smf, _is_na, set_dir
from plotting import artefacts


def plasticity(coord, plast, stage, donor, which="", min_cells=30, seed=0):
    """H3: do de-zonated cells also express plasticity markers? De-zonation proxy per cell:
        dez = -|(coord - median(coord)) / std(coord)|
    cells near the MIDDLE of the coordinate (lost a clear PC/PP position) score HIGH (near 0);
    extremes score low. Headline = donor-level: per-donor Spearman(dez, plasticity), then a
    sign test + bootstrap CI over donor rhos against 0. Writes per_donor_plasticity_<set>.csv.
    """
    log(f"Step 8: H3 de-zonation vs plasticity [set={which}] — DONOR-LEVEL headline")
    if np.allclose(np.nanstd(plast), 0):
        log("  (no plasticity markers present — skipping)"); return None
    dez = -np.abs((coord - np.median(coord)) / (np.std(coord) + 1e-9))
    rows = []
    for d in np.unique(donor):
        m = donor == d
        if _is_na([d]).iat[0] or m.sum() < min_cells or plast[m].std() == 0: continue
        st = pd.Series(stage[m]).mode().iat[0]
        r = spearmanr(dez[m], plast[m])
        rows.append({"signature_set": which, "donor": d, "stage": st,
                     "stage_rank": S2R.get(st, -1), "n_cells": int(m.sum()),
                     "rho_dez_plast": float(r.statistic)})
    dd = pd.DataFrame(rows)
    dd.to_csv(os.path.join(set_dir(which), "per_donor_plasticity.csv"), index=False)
    rs = dd["rho_dez_plast"].values
    n = len(rs); n_pos = int((rs > 0).sum())
    try:
        from scipy.stats import binomtest
        sign_p = binomtest(n_pos, n, 0.5).pvalue if n else np.nan
    except Exception:
        from scipy.stats import binom_test
        sign_p = binom_test(n_pos, n, 0.5) if n else np.nan
    rng = np.random.RandomState(seed)
    bs = [np.nanmean(rs[rng.randint(0, n, n)]) for _ in range(2000)] if n else []
    lo, hi = (np.nanpercentile(bs, [2.5, 97.5]) if bs else (np.nan, np.nan))
    log(f"  PRIMARY: per-donor rho(de-zonation, plasticity): mean={np.nanmean(rs):+.3f} "
        f"(95%CI {lo:+.2f},{hi:+.2f}); >0 in {n_pos}/{n} donors, sign-test p={sign_p:.3g}")
    # H3 figure via the shared plotting layer (plotting/artefacts.py)
    artefacts.plot_h3_per_donor(dd, os.path.join(str(config.FIGURES), f"plasticity_{which}.png"), short=SHORT,
                                title=f"H3 [{which}]: mean={np.nanmean(rs):+.3f}, {n_pos}/{n}>0, p={sign_p:.2g}")
    if smf is not None:
        df = pd.DataFrame({"plast": plast, "dez": dez, "stage": stage, "donor": donor})
        try:
            r = smf.ols("plast ~ dez + C(stage) + C(donor)", data=df).fit()
            log(f"  (descriptive OLS plast~dez+C(stage)+C(donor): dez beta="
                f"{r.params.get('dez', np.nan):+.3f} p={r.pvalues.get('dez', np.nan):.3g} "
                "— cell-level SE, NOT a headline p-value)")
        except Exception as e:
            log(f"  (OLS skipped: {e})")
    return dd
