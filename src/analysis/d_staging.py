"""D - higher-resolution staging: re-run the headline H1/H2 readouts along FIBROSIS (F0-F4) and
NAS (NAFLD activity score, 0-8) instead of only the 5 coarse clinical stages.

Question: does zonation loss track FIBROSIS specifically (the graded biological axis), activity
(NAS), or both? Fibrosis being the graded axis makes "zonation grades with fibrosis" a stronger
claim than "collapses across coarse stage".

Readouts (donor = unit throughout):
  * zonation strength   = -anticorr  (PC<->PP anti-correlation; higher = more intact zonation)
  * PC program level    = pc_raw     (un-standardized mean log1p-CP10k over PC genes; sees turn-off)
  * coordinate spread   = sd         (spread of the zonation coordinate within a donor)

Outputs:
  results/figures/staging/d_zonation_vs_fibrosis.png
  results/figures/staging/d_zonation_vs_nas.png
  results/figures/staging/d_fibrosis_vs_nas.png
  results/figures/staging/d_nash_fibrosis_split.png
  results/tables/.../d_staging_trends.csv

Honesty: finer strata = fewer donors per level. n per level is printed on every panel; low-n
levels (< MIN_SOLID_N donors) are drawn faint and we do NOT over-claim there.
"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # src/
from analysis import common as C
import numpy as np, pandas as pd
from scipy.stats import spearmanr
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

# readout label, column, "higher = ?" direction note
READOUTS = [
    ("strength", "Zonation strength (-anticorr)", lambda df: -df["anticorr"]),
    ("pc_level", "PC program level (pc_raw)",      lambda df: df["pc_raw"]),
    ("spread",   "Coordinate spread (sd)",         lambda df: df["sd"]),
]
MIN_SOLID_N = 4          # levels with fewer donors than this are drawn faint / treated with caution


# ---------------- small helpers ----------------
def _spear(x, y):
    """Spearman rho, p over rows where both are finite. Returns (rho, p, n)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 3:
        return np.nan, np.nan, int(m.sum())
    r = spearmanr(x[m], y[m])
    return float(r.statistic), float(r.pvalue), int(m.sum())


def _partial_spear(x, y, z):
    """Spearman partial correlation of x,y controlling for z: correlate the rank-residuals.
    Returns (rho, n). Uses Pearson on ranks of residuals (Spearman-style partial)."""
    x = np.asarray(x, float); y = np.asarray(y, float); z = np.asarray(z, float)
    m = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
    if m.sum() < 4:
        return np.nan, int(m.sum())
    rx, ry, rz = (pd.Series(v[m]).rank().values for v in (x, y, z))
    def resid(a, b):
        b1 = np.c_[np.ones_like(b), b]
        beta, *_ = np.linalg.lstsq(b1, a, rcond=None)
        return a - b1 @ beta
    ex, ey = resid(rx, rz), resid(ry, rz)
    if ex.std() == 0 or ey.std() == 0:
        return np.nan, int(m.sum())
    return float(np.corrcoef(ex, ey)[0, 1]), int(m.sum())


def _sizes(n_cells):
    """Marker sizes scaled by n_cells (sqrt); used so small-n donors read as small points."""
    n = np.asarray(n_cells, float)
    return 18 + 120 * np.sqrt(n / np.nanmax(n))


def _alphas(df, level_col):
    """Per-point alpha: faint if the donor sits in a low-n stratum (< MIN_SOLID_N donors)."""
    counts = df[level_col].map(df[level_col].value_counts())
    return np.where(counts.values >= MIN_SOLID_N, 0.85, 0.30)


def _panel(ax, df, level_col, levels, ycol, ylabel, axis_label, color):
    """One readout-vs-axis scatter panel: per-donor points (sized by n_cells, faint if low-n stratum),
    per-level median line (solid where n>=MIN_SOLID_N, dashed/faint where tiny), Spearman rho/p."""
    y = df[ycol].values
    x = df[level_col].values.astype(float)
    al = _alphas(df, level_col)
    sz = _sizes(df["n_cells"].values)
    # jitter x a touch so overlapping donors at the same integer level are visible
    rng = np.random.RandomState(0)
    xj = x + rng.uniform(-0.13, 0.13, size=len(x))
    for i in range(len(x)):
        ax.scatter(xj[i], y[i], s=sz[i], color=color, alpha=al[i],
                   edgecolor="white", linewidth=0.4, zorder=3)
    # per-level median line
    med_x, med_y, solid = [], [], []
    for lv in levels:
        sel = np.isfinite(x) & (x == lv) & np.isfinite(y)
        if sel.sum() == 0:
            continue
        med_x.append(lv); med_y.append(np.median(y[sel])); solid.append(sel.sum() >= MIN_SOLID_N)
    med_x, med_y = np.array(med_x), np.array(med_y)
    if len(med_x) >= 2:
        ax.plot(med_x, med_y, "-", color=C.INK, lw=1.8, alpha=0.9, zorder=4)
        ax.scatter(med_x[np.array(solid)], med_y[np.array(solid)],
                   marker="D", s=42, color=C.INK, zorder=5, label="level median (n>=%d)" % MIN_SOLID_N)
        faint = ~np.array(solid)
        if faint.any():
            ax.scatter(med_x[faint], med_y[faint], marker="D", s=42, facecolor="white",
                       edgecolor=C.INK, linewidth=1.2, zorder=5, label="median (tiny n)")
    # n per level annotation along the top
    yl = ax.get_ylim()
    ytop = yl[1] + 0.04 * (yl[1] - yl[0])
    for lv in levels:
        nlv = int((x == lv).sum())
        if nlv:
            ax.text(lv, ytop, f"n={nlv}", ha="center", va="bottom",
                    fontsize=7, color=(C.MUTED if nlv >= MIN_SOLID_N else C.RUST))
    ax.set_ylim(yl[0], ytop + 0.10 * (yl[1] - yl[0]))
    rho, p, n = _spear(x, y)
    ax.set_title(f"{ylabel}\nSpearman vs {axis_label}: rho={rho:+.2f}, p={p:.1e} (n={n})",
                 fontsize=9.5)
    ax.set_xlabel(axis_label); ax.set_ylabel(ylabel, fontsize=8)
    ax.set_xticks(levels)
    return rho, p, n


# ---------------- figures ----------------
def fig_vs_axis(df, axis, axis_label, levels, level_col, outname, color):
    """3-panel figure: each readout vs a staging axis (fibrosis or NAS)."""
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 5.0))
    trends = []
    for ax, (key, ylabel, getter) in zip(axes, READOUTS):
        d = df.copy(); d["_y"] = getter(d)
        rho, p, n = _panel(ax, d, level_col, levels, "_y", ylabel, axis_label, color)
        trends.append(dict(readout=key, axis=axis, rho=rho, p=p, n_donors=n))
    axes[0].legend(loc="best", fontsize=7, framealpha=0.9)
    fig.suptitle(f"D - zonation readouts vs {axis_label} (donor = unit; point size ~ n_cells; "
                 f"orange n = low-n stratum)", fontsize=11, y=1.02)
    fig.tight_layout()
    path = C.fig_path("staging", outname)
    fig.savefig(path, dpi=130, bbox_inches="tight"); plt.close(fig)
    return path, trends


def fig_fibrosis_vs_nas(df):
    """Direct comparison: which axis does zonation STRENGTH track better? Two scatter panels
    (strength vs fibrosis | strength vs NAS) with marginal Spearman rho side by side + a partial-
    correlation note (strength~fibrosis | NAS, and strength~NAS | fibrosis)."""
    strength = -df["anticorr"]
    rf, pf, nf = _spear(df["fibrosis"], strength)
    rn, pn, nn = _spear(df["nas"], strength)
    pr_f, npf = _partial_spear(strength, df["fibrosis"], df["nas"])   # strength~fibrosis | NAS
    pr_n, npn = _partial_spear(strength, df["nas"], df["fibrosis"])   # strength~NAS | fibrosis

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.2))
    for ax, col, lab, levels, color, (r, p, n) in [
        (axes[0], "fibrosis", "Fibrosis (F0-F4)", C.FIB_ORDER, C.TEAL, (rf, pf, nf)),
        (axes[1], "nas", "NAS (0-8)", sorted(df["nas"].dropna().unique()), C.RUST, (rn, pn, nn)),
    ]:
        d = df.copy(); d["_y"] = strength
        _panel(ax, d, col, [int(l) for l in levels], "_y",
               "Zonation strength (-anticorr)", lab, color)

    note = (f"Marginal Spearman (strength vs axis):  fibrosis rho={rf:+.2f} (p={pf:.1e}, n={nf})   |   "
            f"NAS rho={rn:+.2f} (p={pn:.1e}, n={nn})\n"
            f"Partial Spearman:  strength~fibrosis | NAS = {pr_f:+.2f} (n={npf})   |   "
            f"strength~NAS | fibrosis = {pr_n:+.2f} (n={npn})\n"
            f"-> zonation strength tracks {'FIBROSIS' if abs(rf) >= abs(rn) else 'NAS'} more strongly "
            f"on the marginal; partial corr shows whether each survives controlling for the other.")
    fig.suptitle("D - which axis does zonation strength track? fibrosis vs NAS", fontsize=11, y=1.05)
    fig.text(0.5, -0.06, note, ha="center", va="top", fontsize=8.5,
             bbox=dict(boxstyle="round", fc="#f4f6f6", ec=C.RULE))
    fig.tight_layout()
    path = C.fig_path("staging", "d_fibrosis_vs_nas.png")
    fig.savefig(path, dpi=130, bbox_inches="tight"); plt.close(fig)
    trends = [
        dict(readout="strength_partial_fib_ctrl_nas", axis="fibrosis", rho=pr_f, p=np.nan, n_donors=npf),
        dict(readout="strength_partial_nas_ctrl_fib", axis="nas", rho=pr_n, p=np.nan, n_donors=npn),
    ]
    return path, trends


def fig_nash_split(df):
    """Within the single coarse stage 'NASH w/o cirrhosis' (which spans F1/F2/F3), does zonation
    already grade by fibrosis at FIXED coarse stage? Strength + PC level across F1->F2->F3."""
    sub = df[df["stage"] == "NASH w/o cirrhosis"].copy()
    levels = sorted(int(f) for f in sub["fibrosis"].dropna().unique())
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 5.2))
    out = []
    for ax, (key, ylabel, getter), color in zip(
            axes, [READOUTS[0], READOUTS[1]], [C.TEAL, C.RUST]):
        d = sub.copy(); d["_y"] = getter(d)
        rho, p, n = _panel(ax, d, "fibrosis", levels, "_y", ylabel, "Fibrosis (within NASH)", color)
        out.append(dict(readout=key, axis="fibrosis_within_NASH", rho=rho, p=p, n_donors=n))
    fig.suptitle("D - within 'NASH w/o cirrhosis': does zonation grade by fibrosis at FIXED "
                 "coarse stage? (F1/F2/F3)", fontsize=10.5, y=1.02)
    fig.tight_layout()
    path = C.fig_path("staging", "d_nash_fibrosis_split.png")
    fig.savefig(path, dpi=130, bbox_inches="tight"); plt.close(fig)
    return path, out


# ---------------- main ----------------
def main():
    which = sys.argv[1] if len(sys.argv) > 1 else C.DEFAULT_SET
    df = C.donor_summary(which=which, with_raw=True)
    print(f"[d_staging] set={which}  donors={len(df)}  "
          f"fibrosis-levels={sorted(df['fibrosis'].dropna().unique())}  "
          f"nas-levels={sorted(df['nas'].dropna().unique())}")

    all_trends = []
    p1, t1 = fig_vs_axis(df, "fibrosis", "Fibrosis (F0-F4)", C.FIB_ORDER, "fibrosis",
                         "d_zonation_vs_fibrosis.png", C.TEAL)
    nas_levels = [int(n) for n in sorted(df["nas"].dropna().unique())]
    p2, t2 = fig_vs_axis(df.dropna(subset=["nas"]), "nas", "NAS (0-8)", nas_levels, "nas",
                         "d_zonation_vs_nas.png", C.RUST)
    p3, t3 = fig_fibrosis_vs_nas(df)
    p4, t4 = fig_nash_split(df)
    all_trends = t1 + t2 + t3 + t4

    tbl = pd.DataFrame(all_trends)[["readout", "axis", "rho", "p", "n_donors"]]
    tpath = C.table_path("d_staging_trends.csv")
    tbl.to_csv(tpath, index=False)

    for p in (p1, p2, p3, p4, tpath):
        print("  wrote", p, "OK" if os.path.exists(p) else "MISSING")
    print("\nTrend table:\n" + tbl.to_string(index=False))
    return tbl


if __name__ == "__main__":
    main()
