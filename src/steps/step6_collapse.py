"""Step 6 — DONOR-LEVEL zonation collapse across disease stages (Artefact A6, H1).

UNIT OF INFERENCE = DONOR, never cell. One metric value per donor, THEN an ordered-trend
test on the ~47 donor values (+ donor bootstrap CI + donor-label-shuffle null).
"""
from __future__ import annotations
import os, sys
import numpy as np, pandas as pd
from scipy.stats import spearmanr
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # src/
import config
from steps.common import log, OUT, SHORT, S2R, _is_na, set_dir, jonckheere_terpstra
from plotting import artefacts


def _align_entropy(entropy, bars):
    """Per-cell entropy aligned to `bars`, or None. Accepts None | aligned ndarray |
    pd.Series indexed by cell_id | DataFrame with cell_id+entropy columns."""
    if entropy is None: return None
    if isinstance(entropy, pd.DataFrame):
        entropy = entropy.set_index("cell_id")["entropy"]
    if isinstance(entropy, pd.Series):
        return entropy.reindex(bars).astype(float).values
    arr = np.asarray(entropy, float)
    if bars is not None and arr.shape[0] != len(bars):
        log(f"  WARNING: entropy length {arr.shape[0]} != n_cells {len(bars)}; ignoring entropy.")
        return None
    return arr


def collapse(coord, pc, pp, stage, donor, entropy=None, bars=None,
             which="", min_cells=30, n_boot=2000, seed=0):
    """H1: one collapse metric PER DONOR, then test the trend across stage_rank on those donor
    values. NO cell-level p-values. Optional `entropy` (aligned by cell_id via `bars`, or a
    pre-aligned array) adds a mean_entropy metric. Expected with disease: spread DOWN,
    pc_pp_anticorr toward 0, entropy UP.

    Writes collapse_per_donor_<set>.csv, collapse_trends_<set>.csv (one row per metric),
    and figures/collapse_<set>.png. Returns the per-donor DataFrame.
    """
    log(f"Step 6: H1 collapse [set={which}] — metrics PER DONOR, trend across stages")
    ent = _align_entropy(entropy, bars)
    has_ent = ent is not None and np.isfinite(np.nanstd(ent)) and np.nanstd(ent) > 0
    rows = []
    for d in np.unique(donor):
        m = donor == d
        if _is_na([d]).iat[0] or m.sum() < min_cells: continue
        st = pd.Series(stage[m]).mode().iat[0]
        if st not in S2R: continue
        c = coord[m]
        row = {"signature_set": which, "donor": d, "stage": st, "stage_rank": S2R[st],
               "n_cells": int(m.sum()),
               "coord_spread": float(np.nanstd(c)),
               "coord_iqr": float(np.nanpercentile(c, 75) - np.nanpercentile(c, 25)),
               "pc_pp_anticorr": float(spearmanr(pc[m], pp[m]).statistic)}
        if has_ent: row["mean_entropy"] = float(np.nanmean(ent[m]))
        rows.append(row)
    dd = pd.DataFrame(rows)
    sd = set_dir(which)
    dd.to_csv(os.path.join(sd, "collapse_per_donor.csv"), index=False)
    log(f"  {len(dd)} donors usable (>={min_cells} cells)")
    rng = np.random.RandomState(seed)
    metrics = [("coord_spread", "down"), ("coord_iqr", "down"), ("pc_pp_anticorr", "toward 0")]
    if has_ent: metrics.append(("mean_entropy", "up"))
    trows = []; x = dd["stage_rank"].values
    for metric, direction in metrics:
        y = dd[metric].values
        rho, p = spearmanr(x, y)
        bs = [spearmanr(x[s], y[s]).statistic
              for s in (rng.randint(0, len(dd), len(dd)) for _ in range(n_boot))]
        lo, hi = np.nanpercentile(bs, [2.5, 97.5])
        null = [abs(spearmanr(rng.permutation(x), y).statistic) for _ in range(n_boot)]
        pperm = (np.sum(np.array(null) >= abs(rho)) + 1) / (len(null) + 1)
        jt_z, jt_p = jonckheere_terpstra(y, x)            # primer's dedicated ordered-trend test
        trows.append({"signature_set": which, "metric": metric, "n_donors": len(dd),
                      "rho_vs_stage": rho, "ci_lo": lo, "ci_hi": hi,
                      "p_spearman": p, "perm_p": pperm, "jt_z": jt_z, "jt_perm_p": jt_p,
                      "expected_direction": direction})
        log(f"  {metric:14s} vs stage: rho={rho:+.3f} (95%CI {lo:+.2f},{hi:+.2f}) "
            f"p={p:.3g} perm_p={pperm:.3g}  JT z={jt_z:+.2f} p={jt_p:.3g}  [expect {direction}]")
    pd.DataFrame(trows).to_csv(os.path.join(sd, "collapse_trends.csv"), index=False)
    # H1 figure via the shared plotting layer (plotting/artefacts.py). Entropy is AUXILIARY -> in
    # the CSV but NOT plotted (figure shows only the coordinate-based collapse metrics).
    fig_metrics = [m for m, _ in metrics if m != "mean_entropy"]
    artefacts.plot_collapse_metrics(dd, fig_metrics, os.path.join(str(config.FIGURES), f"collapse_{which}.png"),
                                    short=SHORT)
    return dd
