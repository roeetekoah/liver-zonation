"""Step 7 — H2: which gene programs lose their zonal restriction with disease?

Two methods live here:
  * h2_slope_loss()  — PRIMARY. Donor-level zonal SLOPE that weakens with stage, tested on a
                       held-out gene split (non-circular). This is the real H2.
  * de()             — EXPLORATORY FALLBACK. Pseudobulk donor x zone DE across stages: "genes
                       that change within a fixed zone", NOT slope loss. Kept, clearly labelled.
Pseudobulk (donor-level) is the unit throughout — never cell pseudoreplication.
"""
from __future__ import annotations
import os, sys
import numpy as np, pandas as pd
from scipy.stats import spearmanr, ttest_1samp
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # src/
import config
from steps.common import log, bh, OUT, S2R, _is_na, set_dir
from plotting import artefacts


# ---------------- PRIMARY H2: donor-level zonal slope loss ----------------
def _donor_bin_slopes(Mc, local_idx, libsize, coord, donor, stage,
                      n_bins=5, min_cells_bin=10, min_bins=3):
    """For each donor: bin that donor's cells into `n_bins` quantiles of `coord`, build a TRUE
    pseudobulk per bin (log1p(1e4 * sum_counts / sum_libsize)) for the requested genes, then fit
    one slope (expression vs bin ordinal) per gene. Returns (slopes[n_donors x n_genes], ranks,
    donors). Mc = CSC counts (gene-subset rows x cells); local_idx = rows of Mc to use."""
    local_idx = np.asarray(local_idx)
    sub = Mc[local_idx].tocsc()
    slope_rows, ranks, donors = [], [], []
    for d in np.unique(donor):
        m = np.where(donor == d)[0]
        if _is_na([d]).iat[0] or len(m) < min_cells_bin * min_bins: continue
        st = pd.Series(stage[m]).mode().iat[0]
        if st not in S2R: continue
        c = coord[m]
        edges = np.quantile(c, np.linspace(0, 1, n_bins + 1))
        edges[0] -= 1e-9; edges[-1] += 1e-9
        bid = np.clip(np.digitize(c, edges[1:-1]), 0, n_bins - 1)
        xs, ys = [], []
        for b in range(n_bins):
            cb = m[bid == b]
            if len(cb) < min_cells_bin: continue
            lib_b = libsize[cb].sum()
            if lib_b <= 0: continue
            cnt = np.asarray(sub[:, cb].sum(1)).ravel()
            ys.append(np.log1p(1e4 * cnt / lib_b)); xs.append(b)
        if len(xs) < min_bins: continue
        x = np.array(xs, float); Y = np.vstack(ys)            # bins_present x n_genes
        xc = x - x.mean(); denom = (xc ** 2).sum()
        slope_rows.append((Y * xc[:, None]).sum(0) / denom)   # n_genes
        ranks.append(S2R[st]); donors.append(d)
    if not donors: return None, None, None
    return np.vstack(slope_rows), np.array(ranks), donors


def h2_slope_loss(M, genes, libsize, col, coord, stage, donor, pc_genes, pp_genes,
                  which="", K=20, seed=0):
    """PRIMARY H2: does each gene's ZONAL SLOPE weaken with disease, donor-level?
    aligned_slope = slope * sign(Paper2 direction) (+1 PC, -1 PP); collapse => aligned_slope
    DECREASES with stage_rank across donors. Non-circular HELD-OUT split: build the coordinate
    from a random half of PC/PP, test slope-loss only on the OTHER half; repeat K times.
    Writes h2_slope_loss_<set>.csv (per gene) + h2_slope_loss_summary_<set>.csv.
    """
    log(f"Step 7b [PRIMARY H2]: donor-level zonal slope-loss [set={which}], held-out split K={K}")
    g2i = {g: i for i, g in enumerate(genes)}
    PCp = [g for g in pc_genes if g in g2i]; PPp = [g for g in pp_genes if g in g2i]
    direction = {g: +1 for g in PCp}; direction.update({g: -1 for g in PPp})
    if min(len(PCp), len(PPp)) < 4:
        log(f"  too few present signature genes (PC={len(PCp)}, PP={len(PPp)}) for a held-out split; skipping.")
        return None
    sig_all = PCp + PPp; sig_idx = [g2i[g] for g in sig_all]
    Msig = M[sig_idx].tocsc(); local = {g: j for j, g in enumerate(sig_all)}
    rng = np.random.RandomState(seed)
    nph, npp = len(PCp) // 2, len(PPp) // 2
    per_gene = {}
    for _k in range(K):
        pcp = rng.permutation(PCp); ppp = rng.permutation(PPp)
        pc_coord, pc_test = list(pcp[:nph]), list(pcp[nph:])
        pp_coord, pp_test = list(ppp[:npp]), list(ppp[npp:])
        # coordinate from the COORD-half, reusing precomputed z-vectors (col) — no M re-read
        pcz = np.mean([col[g] for g in pc_coord if g in col], axis=0)
        ppz = np.mean([col[g] for g in pp_coord if g in col], axis=0)
        pcz = (pcz - pcz.mean()) / (pcz.std() + 1e-9); ppz = (ppz - ppz.mean()) / (ppz.std() + 1e-9)
        coord_k = pcz - ppz
        test_genes = pc_test + pp_test
        slopes, ranks, _ = _donor_bin_slopes(Msig, [local[g] for g in test_genes],
                                             libsize, coord_k, donor, stage)
        if slopes is None: continue
        aligned = slopes * np.array([direction[g] for g in test_genes])[None, :]
        for j, g in enumerate(test_genes):
            a = aligned[:, j]
            if np.isfinite(a).sum() >= 6 and np.nanstd(a) > 0:
                per_gene.setdefault(g, []).append(spearmanr(ranks, a, nan_policy="omit").statistic)
    if not per_gene:
        log("  no genes accumulated trends; skipping."); return None
    rows = []
    for g, rl in per_gene.items():
        rr = np.array(rl, float)
        p = ttest_1samp(rr, 0, nan_policy="omit").pvalue if (rr.size >= 2 and np.nanstd(rr) > 0) else np.nan
        rows.append({"signature_set": which, "gene": g, "direction": "PC" if direction[g] > 0 else "PP",
                     "held_out": True, "n_splits_tested": int(rr.size),
                     "mean_slope_trend_rho": float(np.nanmean(rr)),
                     "frac_splits_weakening": float(np.mean(rr < 0)), "p_trend": p})
    res = pd.DataFrame(rows)
    res["q_trend"] = bh(np.nan_to_num(res["p_trend"].values, nan=1.0))
    res = res.sort_values("mean_slope_trend_rho")
    sd = set_dir(which)
    res.to_csv(os.path.join(sd, "h2_slope_loss.csv"), index=False)
    tr = res["mean_slope_trend_rho"].values; n = len(tr); n_weak = int((tr < 0).sum())
    try:
        from scipy.stats import binomtest; sgp = binomtest(n_weak, n, 0.5).pvalue
    except Exception:
        from scipy.stats import binom_test; sgp = binom_test(n_weak, n, 0.5)
    n_sig = int(((res["q_trend"] < 0.05) & (res["mean_slope_trend_rho"] < 0)).sum())
    summ = pd.DataFrame([{"signature_set": which, "mode": "held_out_split", "K": K,
                          "n_genes_tested": n, "frac_weakening": n_weak / n,
                          "median_trend_rho": float(np.nanmedian(tr)),
                          "sign_test_p_2sided": sgp, "n_genes_q05_weakening": n_sig,
                          "n_donors_basis": int(len(set(donor)))}])
    summ.to_csv(os.path.join(sd, "h2_slope_loss_summary.csv"), index=False)
    log(f"  {n} held-out genes tested: {n_weak} weaken / {n - n_weak} strengthen "
        f"(median trend rho={np.nanmedian(tr):+.3f}, sign-test p={sgp:.3g}); "
        f"{n_sig} genes q<0.05 & weakening")
    # H2 figure via the shared plotting layer (plotting/artefacts.py)
    artefacts.plot_h2_histogram(tr, os.path.join(str(config.FIGURES), f"h2_slope_loss_{which}.png"),
                                title=f"H2 [{which}]: {n_weak}/{n} weaken, median={np.nanmedian(tr):+.2f}, p={sgp:.1g}")
    log(f"  wrote h2_slope_loss_{which}.csv + .png + summary")
    return res


# ---------------- COMPLEMENTARY H2: explicit interaction OLS ----------------
def _donor_bin_long(Mc, local_idx, libsize, coord, donor, stage,
                    n_bins=5, min_cells_bin=10, min_bins=3):
    """Like `_donor_bin_slopes` but returns the LONG-FORM (donor x coord-bin) pseudobulk instead of
    collapsing to a slope. One row per (donor, bin): a true pseudobulk (log1p(1e4*sum_counts/sum_lib))
    for the requested genes, tagged with the bin ordinal, the donor's stage rank, and the donor id
    (for clustering). Returns (Y[n_obs x n_genes], bin_ord[n_obs], stage_rank[n_obs], donor_id[n_obs])
    or None. Donor stays the unit of inference — cells are aggregated, never used as observations."""
    local_idx = np.asarray(local_idx)
    sub = Mc[local_idx].tocsc()
    Yrows, xord, srank, did = [], [], [], []
    for d in np.unique(donor):
        m = np.where(donor == d)[0]
        if _is_na([d]).iat[0] or len(m) < min_cells_bin * min_bins: continue
        st = pd.Series(stage[m]).mode().iat[0]
        if st not in S2R: continue
        c = coord[m]
        edges = np.quantile(c, np.linspace(0, 1, n_bins + 1))
        edges[0] -= 1e-9; edges[-1] += 1e-9
        bid = np.clip(np.digitize(c, edges[1:-1]), 0, n_bins - 1)
        rows_d = []
        for b in range(n_bins):
            cb = m[bid == b]
            if len(cb) < min_cells_bin: continue
            lib_b = libsize[cb].sum()
            if lib_b <= 0: continue
            cnt = np.asarray(sub[:, cb].sum(1)).ravel()
            rows_d.append((b, np.log1p(1e4 * cnt / lib_b)))
        if len(rows_d) < min_bins: continue          # donor must span >= min_bins zones
        for b, yv in rows_d:
            Yrows.append(yv); xord.append(b); srank.append(S2R[st]); did.append(d)
    if not Yrows: return None
    return np.vstack(Yrows), np.array(xord, float), np.array(srank, float), np.asarray(did)


def _cluster_robust_ols(X, y, groups):
    """OLS of y on X with cluster-robust (by `groups`) covariance — the sandwich estimator that
    respects donor as the unit when (donor x bin) rows repeat within a donor. Stata-style finite-
    sample correction c = G/(G-1) * (n-1)/(n-k). Returns (beta, se[k], G clusters)."""
    XtX_inv = np.linalg.pinv(X.T @ X)
    beta = XtX_inv @ (X.T @ y)
    resid = y - X @ beta
    k = X.shape[1]; n = X.shape[0]
    meat = np.zeros((k, k))
    uniq = np.unique(groups)
    for g in uniq:
        idx = np.where(groups == g)[0]
        s = X[idx].T @ resid[idx]
        meat += np.outer(s, s)
    G = len(uniq)
    c = (G / (G - 1.0)) * ((n - 1.0) / (n - k)) if (G > 1 and n > k) else 1.0
    cov = c * (XtX_inv @ meat @ XtX_inv)
    return beta, np.sqrt(np.maximum(np.diag(cov), 0.0)), G


def h2_interaction_ols(M, genes, libsize, coord, stage, donor, pc_genes, pp_genes,
                       which="", n_bins=5):
    """COMPLEMENTARY H2 — the primer's explicit model  expr ~ coord + stage + coord:stage,  fit
    donor-level (per-donor coord-bin pseudobulk; cluster-robust SE clustered by donor) for every
    signature gene. The coord:stage coefficient, sign-ALIGNED to the Paper-2 direction (+1 PC, -1 PP),
    is the direct slope-loss test: aligned beta < 0 == the gene's zonal slope flattens with disease.

    This is the IN-SAMPLE, parametric, single-coefficient companion to the held-out, non-parametric
    two-stage h2_slope_loss(): it uses the full frozen coordinate (not a held-out split), so the two
    bracket the effect. Writes h2_interaction_ols.csv (per gene) + h2_interaction_ols_summary.csv.
    """
    log(f"Step 7c [H2 interaction OLS]: expr ~ coord + stage + coord:stage, cluster-robust by donor [set={which}]")
    g2i = {g: i for i, g in enumerate(genes)}
    PCp = [g for g in pc_genes if g in g2i]; PPp = [g for g in pp_genes if g in g2i]
    direction = {g: +1 for g in PCp}; direction.update({g: -1 for g in PPp})
    sig_all = PCp + PPp
    if min(len(PCp), len(PPp)) < 4:
        log(f"  too few present signature genes (PC={len(PCp)}, PP={len(PPp)}); skipping."); return None
    Msig = M[[g2i[g] for g in sig_all]].tocsc()
    out = _donor_bin_long(Msig, range(len(sig_all)), libsize, coord, donor, stage, n_bins=n_bins)
    if out is None:
        log("  no donor x bin pseudobulk rows; skipping."); return None
    Y, xord, srank, did = out
    n_obs, n_donor = len(xord), len(np.unique(did))
    if n_donor < 6:
        log(f"  too few donors with >= 3 zones ({n_donor}); skipping."); return None
    xc = xord - xord.mean(); sc = srank - srank.mean()                 # center -> stable main effects
    X = np.column_stack([np.ones_like(xc), xc, sc, xc * sc])           # 1, coord, stage, coord:stage
    rows = []
    for j, g in enumerate(sig_all):
        y = Y[:, j]
        if np.std(y) == 0: continue
        beta, se, G = _cluster_robust_ols(X, y, did)
        sgn = direction[g]
        b_coord = beta[1] * sgn                                        # aligned baseline zonal slope
        b_int, s_int = beta[3] * sgn, se[3]                            # aligned interaction (slope-loss)
        t = b_int / s_int if s_int > 0 else np.nan
        p = float(2 * stats.t.sf(abs(t), G - 1)) if np.isfinite(t) else np.nan
        rows.append({"signature_set": which, "gene": g,
                     "direction": "PC" if sgn > 0 else "PP",
                     "beta_coord_aligned": float(b_coord),
                     "beta_interaction_aligned": float(b_int),
                     "se_interaction": float(s_int), "t_interaction": float(t),
                     "p_interaction": p, "n_clusters": int(G)})
    if not rows:
        log("  no genes fit; skipping."); return None
    res = pd.DataFrame(rows)
    res["q_interaction"] = bh(np.nan_to_num(res["p_interaction"].values, nan=1.0))
    res = res.sort_values("beta_interaction_aligned")
    sd = set_dir(which)
    res.to_csv(os.path.join(sd, "h2_interaction_ols.csv"), index=False)

    bi = res["beta_interaction_aligned"].values
    n = len(bi); n_weak = int((bi < 0).sum())
    try:
        from scipy.stats import binomtest; sgp = binomtest(n_weak, n, 0.5).pvalue
    except Exception:
        from scipy.stats import binom_test; sgp = binom_test(n_weak, n, 0.5)
    n_sig = int(((res["q_interaction"] < 0.05) & (bi < 0)).sum())
    prog = (res.assign(weak=bi < 0).groupby("direction")
            .agg(n=("gene", "size"), n_weakening=("weak", "sum"),
                 median_beta_interaction=("beta_interaction_aligned", "median"),
                 n_q05_weakening=("q_interaction", lambda s: int(((s < 0.05) & (res.loc[s.index, "beta_interaction_aligned"] < 0)).sum())))
            .reset_index())
    prog.insert(0, "signature_set", which)
    summ = pd.DataFrame([{"signature_set": which, "model": "expr ~ coord + stage + coord:stage",
                          "se": "cluster_robust_by_donor", "n_obs_donor_x_bin": int(n_obs),
                          "n_donors": int(n_donor), "n_genes": n,
                          "frac_weakening": n_weak / n, "median_beta_interaction": float(np.median(bi)),
                          "sign_test_p_2sided": float(sgp), "n_genes_q05_weakening": n_sig}])
    summ.to_csv(os.path.join(sd, "h2_interaction_ols_summary.csv"), index=False)
    prog.to_csv(os.path.join(sd, "h2_interaction_ols_by_program.csv"), index=False)
    log(f"  {n} signature genes, {n_donor} donors, {n_obs} (donor x bin) rows: "
        f"{n_weak}/{n} have aligned coord:stage < 0 (median={np.median(bi):+.4f}, sign-test p={sgp:.3g}); "
        f"{n_sig} genes q<0.05 & weakening")
    for _, r in prog.iterrows():
        log(f"    {r['direction']}: {int(r['n_weakening'])}/{int(r['n'])} weaken "
            f"(median interaction beta={r['median_beta_interaction']:+.4f})")
    artefacts.plot_h2_interaction(
        bi, os.path.join(str(config.FIGURES), f"h2_interaction_ols_{which}.png"),
        title=f"H2 interaction [{which}]: {n_weak}/{n} coord:stage<0, p={sgp:.1g}")
    log(f"  wrote h2_interaction_ols_{which}.csv + by_program + summary + .png")
    return res


# ---------------- EXPLORATORY FALLBACK: pseudobulk donor x zone DE ----------------
def de(M, genes, libsize, coord, stage, donor, sig_genes, which="", min_donor_cells=20, min_frac=0.10):
    """EXPLORATORY/FALLBACK: pseudobulk (donor x zone) DE across stages. This is 'genes that
    change within a fixed zone across stages', NOT zonal-slope loss (that's h2_slope_loss).
    Writes de_portal.csv / de_central.csv with an is_signature circularity flag."""
    log("Step 7 [EXPLORATORY/FALLBACK]: pseudobulk (donor x zone) DE across stages — heavy step")
    log("  NOTE: NOT zonal-slope loss; the PRIMARY H2 is h2_slope_loss() (held-out split).")
    terc = np.quantile(coord, [1 / 3, 2 / 3]); zone = np.digitize(coord, terc)  # 0 portal,1 mid,2 central
    sr = np.array([S2R.get(s, -1) for s in stage]); ok = sr >= 0
    G = len(genes); res = {}
    for zid, zname in [(0, "portal"), (2, "central")]:
        cells = np.where(ok & (zone == zid))[0]
        grp = pd.DataFrame({"i": cells, "donor": donor[cells], "rank": sr[cells]})
        gb = grp.groupby("donor")
        donors = [d for d, idx in gb.groups.items() if len(idx) >= min_donor_cells]
        if len(donors) < 6:
            log(f"  zone {zname}: too few donors ({len(donors)})"); continue
        ranks = np.array([sr[cells[grp.index[grp.donor == d][0]]] for d in donors])
        cols_cells = {d: cells[grp.index[grp.donor == d].values] for d in donors}
        PB = np.zeros((len(donors), G), np.float32)
        for j, d in enumerate(donors):
            cc = cols_cells[d]; sub = M[:, cc]
            cp = np.asarray(sub.sum(0)).ravel()
            x = sub.multiply(1.0 / np.where(cp > 0, cp, 1)).tocsc()   # per-cell CP1
            PB[j] = np.log1p(np.asarray(x.mean(1)).ravel() * 1e4)
        det = (PB > 0).mean(0) >= min_frac
        rho = np.full(G, np.nan); pv = np.ones(G)
        for g in np.where(det)[0]:
            if PB[:, g].std() > 0: rho[g], pv[g] = spearmanr(PB[:, g], ranks)
        q = bh(pv)
        d = pd.DataFrame({"gene": genes, "rho_vs_stage": rho, "p": pv, "q": q,
                          "is_signature": [g in sig_genes for g in genes]}).dropna().sort_values("q")
        d.to_csv(os.path.join(set_dir(which) if which else OUT, f"de_{zname}.csv"), index=False)
        nsig = int((d["q"] < 0.05).sum()); nsig_nonsig = int(((d["q"] < 0.05) & (~d["is_signature"])).sum())
        log(f"  zone {zname}: {len(donors)} donors, {nsig} genes q<0.05 ({nsig_nonsig} excluding signature genes)")
        res[zname] = d
    return res
