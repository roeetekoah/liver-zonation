"""Precision and fixed-margin equivalence checks for donor-level zonation metrics.

The "zonation preserved" claim (D3) currently rests on a descriptive null ("nothing was
significant") = absence-of-evidence. This script provides the AFFIRMATIVE form a referee
wants: report estimates and confidence intervals on the existing DONOR-LEVEL anchor-
classification metrics, then test only the pre-specified equivalence margins.

Reuses the EXISTING depth-controlled donor-level metrics in
results/tables/analysis/load_bearing_donor_table.csv (B=1500 binomial down-thinned).
Does NOT recompute classification, does NOT re-test de-zonation, does NOT touch DGE.

Metrics (per biopsy donor):
  - PC-anchor fraction = PC_n / N_thin
  - PP-anchor fraction = PP_n / N_thin
  - PP:PC ratio        = PP_n / PC_n   (composition)

Contrasts:
  - F1 vs F4  (n=8 vs n=4)  : the headline fibrosis->cirrhotic biopsy contrast
  - F1 vs F3  (n=8 vs n=12) : better-powered interior contrast

For each (contrast, metric):
  observed difference (mean_high - mean_low), 90% t-CI (Welch), 90% bootstrap CI,
  and TOST equivalence against pre-specified margins. Equivalence is established only
  when the whole 90% CI lies inside a pre-specified +-margin.
"""
import os, sys
import numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

OUTD = str(config.ANALYSIS_TABLES)
IN = os.path.join(OUTD, "load_bearing_donor_table.csv")
RNG = np.random.RandomState(0)
NBOOT = 20000
ALPHA = 0.10  # 90% CI / TOST at alpha=0.05 per side

# Pre-specified, biologically-motivated equivalence margins.
# Anchor fractions are proportions in [0,1]; the PP:PC ratio is unbounded, so for it we
# use a RELATIVE margin (fraction of the F1 baseline mean) instead of an absolute one.
ABS_MARGINS = [0.05, 0.10]   # absolute change in an anchor fraction
REL_MARGIN  = 0.20           # +-20% relative change (applied to the low-group baseline mean)


def metrics(df):
    df = df.copy()
    df["PCfrac"] = df["PC_n"] / df["N_thin"]
    df["PPfrac"] = df["PP_n"] / df["N_thin"]
    df["PPPC"]   = df["PP_n"] / df["PC_n"]
    return df


def t_ci(lo, hi, alpha=ALPHA):
    """Welch two-sample CI for (mean_hi - mean_lo) at confidence 1-alpha."""
    n1, n2 = len(lo), len(hi)
    m1, m2 = lo.mean(), hi.mean()
    v1, v2 = lo.var(ddof=1), hi.var(ddof=1)
    se = np.sqrt(v1 / n1 + v2 / n2)
    # Welch-Satterthwaite df
    dfree = (v1 / n1 + v2 / n2) ** 2 / ((v1 / n1) ** 2 / (n1 - 1) + (v2 / n2) ** 2 / (n2 - 1))
    tcrit = stats.t.ppf(1 - alpha / 2, dfree)
    diff = m2 - m1
    return diff, diff - tcrit * se, diff + tcrit * se, se, dfree


def boot_ci(lo, hi, alpha=ALPHA, nboot=NBOOT):
    """Percentile bootstrap CI for (mean_hi - mean_lo)."""
    lo = np.asarray(lo); hi = np.asarray(hi)
    diffs = np.empty(nboot)
    for i in range(nboot):
        bl = lo[RNG.randint(0, len(lo), len(lo))]
        bh = hi[RNG.randint(0, len(hi), len(hi))]
        diffs[i] = bh.mean() - bl.mean()
    return np.percentile(diffs, 100 * alpha / 2), np.percentile(diffs, 100 * (1 - alpha / 2))


def excluded(ci_lo, ci_hi, margin):
    """A margin is affirmatively EXCLUDED iff the whole CI lies within +-margin."""
    return (ci_lo > -margin) and (ci_hi < margin)


def main():
    df = pd.read_csv(IN)
    df = df[df["source"] == "biopsy"].copy()
    df = metrics(df)

    contrasts = [("F1", "F4", 1, 4), ("F1", "F3", 1, 3)]
    metric_defs = [
        ("PC_anchor_fraction", "PCfrac", "abs"),
        ("PP_anchor_fraction", "PPfrac", "abs"),
        ("PP_to_PC_ratio",     "PPPC",   "rel"),
    ]

    rows = []
    print("=" * 78)
    print("PRECISION AND EQUIVALENCE on donor-level zonation metrics (biopsy only)")
    print("Metric scale: PC/PP anchor fractions are proportions in [0,1];")
    print("PP:PC is a dimensionless ratio. Diff = mean(high F) - mean(low F).")
    print("Equivalence is established only if the 90% CI is inside a pre-specified +-margin.")
    print("=" * 78)

    for lname, hname, lF, hF in contrasts:
        lo_df = df[df["F"] == lF]; hi_df = df[df["F"] == hF]
        print(f"\n### {lname}(n={len(lo_df)}) vs {hname}(n={len(hi_df)})")
        for mlabel, col, kind in metric_defs:
            lo = lo_df[col].values; hi = hi_df[col].values
            diff, tlo, thi, se, dfree = t_ci(lo, hi)
            blo, bhi = boot_ci(lo, hi)
            base = lo.mean()  # low-group baseline for relative margins

            # candidate margins on this metric's native scale
            if kind == "abs":
                margin_notes = (f"abs {ABS_MARGINS}; "
                                f"rel20%={REL_MARGIN*base:.4f} (=0.20*F1mean {base:.4f})")
            else:
                # ratio: only the relative margin is meaningful
                margin_notes = f"rel20%={REL_MARGIN*base:.4f} (=0.20*F1mean {base:.4f})"

            # report exclusion per fixed absolute margin (anchor fractions only) + the rel margin
            excl_005 = excluded(tlo, thi, 0.05) if kind == "abs" else None
            excl_010 = excluded(tlo, thi, 0.10) if kind == "abs" else None
            excl_rel = excluded(tlo, thi, REL_MARGIN * base)
            # Descriptive precision only; these values are not pre-specified equivalence margins.
            max_endpoint_t = max(abs(tlo), abs(thi))
            max_endpoint_b = max(abs(blo), abs(bhi))

            print(f"  {mlabel}: mean {lname}={lo.mean():.4f} {hname}={hi.mean():.4f} "
                  f"Diff={diff:+.4f}")
            print(f"     90% t-CI   [{tlo:+.4f}, {thi:+.4f}] (Welch df={dfree:.1f}, se={se:.4f})")
            print(f"     90% boot-CI[{blo:+.4f}, {bhi:+.4f}]")
            print(f"     margins: {margin_notes}")
            if kind == "abs":
                print(f"     EXCLUDE +-0.05? {excl_005}   EXCLUDE +-0.10? {excl_010}   "
                      f"EXCLUDE +-20%? {excl_rel}")
            else:
                print(f"     EXCLUDE +-20%? {excl_rel}")
            print(f"     max |CI endpoint| (descriptive): t={max_endpoint_t:.4f}, bootstrap={max_endpoint_b:.4f}")

            rows.append(dict(
                contrast=f"{lname}v{hname}", n_low=len(lo), n_high=len(hi),
                metric=mlabel, scale=("fraction" if kind == "abs" else "ratio"),
                mean_low=round(lo.mean(), 5), mean_high=round(hi.mean(), 5),
                diff=round(diff, 5), se=round(se, 5), welch_df=round(dfree, 2),
                t_ci90_lo=round(tlo, 5), t_ci90_hi=round(thi, 5),
                boot_ci90_lo=round(blo, 5), boot_ci90_hi=round(bhi, 5),
                rel20_margin=round(REL_MARGIN * base, 5),
                exclude_abs_0p05=excl_005, exclude_abs_0p10=excl_010,
                exclude_rel_20pct=excl_rel,
                max_abs_t_ci_endpoint=round(max_endpoint_t, 5),
                max_abs_boot_ci_endpoint=round(max_endpoint_b, 5),
            ))

    out = pd.DataFrame(rows)
    outpath = os.path.join(OUTD, "equivalence_bound.csv")
    out.to_csv(outpath, index=False)
    print(f"\nwrote {outpath}  ({len(out)} rows)")


if __name__ == "__main__":
    main()
