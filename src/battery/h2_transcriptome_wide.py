#!/usr/bin/env python3
"""H2, taken forward to the WHOLE transcriptome (per gene, donor-level).

Instead of testing only the ruler's genes (h2_slope_loss) or pre-grouped programs (H2b), we:
  1. assign every Paper-1 cell the FROZEN ruler's zonation coordinate (default: expanded_curated),
  2. bin each donor's cells into coordinate quintiles and build a true donor x bin pseudobulk,
  3. fit a zonal slope per donor per gene for ALL ~30k genes,
  4. align each gene by its HEALTHY slope sign, and test whether the (aligned) slope WEAKENS with
     disease stage across donors (Spearman), with BH-FDR.
Genes used to build the coordinate are flagged (is_ruler_gene) so non-ruler hits are the clean,
non-circular transcriptome-wide drivers.

Run:  python src/h2_transcriptome_wide.py [ruler_name]   (default expanded_curated)
"""
import os, sys
import numpy as np, pandas as pd
from scipy.stats import spearmanr
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # src/
import config
from steps.common import log, bh, OUT, S2R
from steps.step2_load_qc import load_qc
from steps.step7_de import _donor_bin_slopes


def main(ruler="expanded_curated"):
    cpath = os.path.join(OUT, ruler, "coordinates.csv")
    if not os.path.exists(cpath):
        print(f"need {cpath} (run the battery for '{ruler}' first)"); return
    M, genes, bars, stage, donor, lib = load_qc()
    coord = pd.read_csv(cpath).set_index("cell_id")["coord"].reindex(bars).astype(float).values
    log(f"H2 transcriptome-wide: coordinate = frozen '{ruler}' ruler; {len(genes)} genes, donor-level")

    slopes, ranks, donors = _donor_bin_slopes(M, np.arange(len(genes)), lib, coord, donor, stage)
    if slopes is None:
        print("no donor slopes computed"); return
    log(f"  per-donor zonal slopes fitted for {slopes.shape[1]} genes over {slopes.shape[0]} donors")
    hmask = ranks == 0                                   # healthy donors
    if hmask.sum() < 2:
        print("too few healthy donors to set gene direction"); return
    hsign = np.sign(np.nanmean(slopes[hmask], axis=0))   # each gene's healthy zonal direction
    hsign[hsign == 0] = 1
    aligned = slopes * hsign[None, :]                    # aligned slope; <0 trend = weakening

    G = slopes.shape[1]; rho = np.full(G, np.nan); pv = np.ones(G)
    for g in range(G):
        col = aligned[:, g]
        if np.isfinite(col).sum() >= 10 and np.nanstd(col) > 0:
            r = spearmanr(ranks, col, nan_policy="omit")
            rho[g], pv[g] = r.statistic, r.pvalue
    q = bh(pv)

    # ruler genes (to flag circularity)
    cand = config.SIGNATURES / "candidates"
    rg = set()
    for arm in ("pericentral", "periportal"):
        p = cand / f"{arm}_{ruler}.txt"
        if p.exists(): rg.update(g.strip() for g in open(p) if g.strip())

    df = pd.DataFrame({"gene": genes, "healthy_slope_sign": hsign,
                       "slope_trend_rho": rho, "p": pv, "q": q,
                       "is_ruler_gene": [g in rg for g in genes]}).dropna(subset=["slope_trend_rho"])
    df = df.sort_values("slope_trend_rho")
    out = os.path.join(OUT, ruler, "h2_transcriptome_wide.csv")
    df.to_csv(out, index=False)

    tested = len(df); weak = int((df["slope_trend_rho"] < 0).sum())
    sig_weak = df[(df["q"] < 0.05) & (df["slope_trend_rho"] < 0)]
    sig_weak_nonruler = sig_weak[~sig_weak["is_ruler_gene"]]
    log(f"  tested {tested} genes; {weak} ({weak/tested*100:.0f}%) weaken; "
        f"{len(sig_weak)} q<0.05 & weakening ({len(sig_weak_nonruler)} are NON-ruler genes = clean drivers)")
    log("  top 20 transcriptome-wide de-zonating genes (most negative slope-trend, q<0.05):")
    top = sig_weak.head(20)
    log("    " + ", ".join(f"{r.gene}{'*' if r.is_ruler_gene else ''}" for _, r in top.iterrows()))
    pd.DataFrame([{"ruler": ruler, "n_tested": tested, "frac_weakening": weak / tested,
                   "n_q05_weakening": len(sig_weak), "n_q05_weakening_nonruler": len(sig_weak_nonruler)}]
                 ).to_csv(os.path.join(OUT, ruler, "h2_transcriptome_wide_summary.csv"), index=False)
    log(f"  wrote {out} (+ summary). '*' = ruler gene (flagged for circularity).")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "expanded_curated")
