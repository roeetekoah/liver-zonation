#!/usr/bin/env python3
"""Look at the REAL data before any summary statistic: for a representative patient at each disease
stage, show (top) the continuous distribution of that patient's cells along the zonation axis -- i.e.
what 'coordinate spread' actually measures -- and (bottom) the PC-arm vs PP-arm scatter that
distinguishes intact zonation from the three collapse modes (turn-off / noise / de-zonation).

Usage:  python src/explore_zonation_distributions.py [signature_set]   (default expanded_curated)
"""
import os, sys
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde, spearmanr
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # src/ on path
import config

STAGE_ORDER = ["Healthy control", "NAFLD", "NASH w/o cirrhosis", "NASH with cirrhosis", "end stage"]
SHORT = {"Healthy control": "Healthy", "NAFLD": "NAFLD", "NASH w/o cirrhosis": "NASH",
         "NASH with cirrhosis": "Cirrhosis", "end stage": "End-stage"}
TEAL, RUST, INK, MUTED = "#1b6e78", "#c05621", "#1a1a1a", "#5a5a5a"


def _depth_by_donor():
    """median UMI (nCount_RNA) per donor from Paper-1 metadata, for the confounder annotation."""
    try:
        m = pd.read_csv(os.path.join(str(config.PAPER1), "metadata_all_cells.csv"),
                        usecols=["Patient.ID", "nCount_RNA"], low_memory=False)
        return m.groupby(m["Patient.ID"].astype(str))["nCount_RNA"].median()
    except Exception:
        return pd.Series(dtype=float)


def main(which="expanded_curated"):
    cpath = os.path.join(str(config.TABLES), which, "coordinates.csv")
    df = pd.read_csv(cpath, low_memory=False)
    df = df[df["coord"].notna() & df["pc"].notna() & df["pp"].notna()]
    depth = _depth_by_donor()

    # representative donor per stage = the one with the MOST cells (cleanest distribution)
    reps = []
    for st in STAGE_ORDER:
        sub = df[df["stage"] == st]
        if not len(sub):
            continue
        d = sub["donor"].value_counts().idxmax()
        reps.append((st, str(d), sub[sub["donor"].astype(str) == str(d)]))

    # healthy reference coordinate distribution (pooled healthy) for overlay
    href = df[df["stage"] == "Healthy control"]["coord"].values
    xs = np.linspace(np.percentile(df["coord"], 0.5), np.percentile(df["coord"], 99.5), 300)
    kde_h = gaussian_kde(href)(xs)

    n = len(reps)
    fig, axes = plt.subplots(2, n, figsize=(3.5 * n, 7.0), gridspec_kw={"height_ratios": [1, 1.2]})
    if n == 1:
        axes = axes.reshape(2, 1)

    for j, (st, d, sub) in enumerate(reps):
        coord = sub["coord"].values
        pc = sub["pc"].values; pp = sub["pp"].values
        sd = float(np.std(coord)); q1, q3 = np.percentile(coord, [25, 75]); iqr = q3 - q1
        ac = float(spearmanr(pc, pp).statistic)

        # ---- top: distribution along the zonation axis ----
        a = axes[0, j]
        a.hist(coord, bins=40, range=(xs[0], xs[-1]), density=True, color=TEAL, alpha=0.30)
        if len(coord) > 5 and np.std(coord) > 0:
            a.plot(xs, gaussian_kde(coord)(xs), color=TEAL, lw=2.0)
        a.plot(xs, kde_h, color=MUTED, lw=1.0, ls="--", alpha=0.8)            # healthy reference
        a.axvspan(q1, q3, color=TEAL, alpha=0.10)                             # IQR band
        mu = coord.mean()
        a.annotate("", xy=(mu + sd, a.get_ylim()[1] * 0.82), xytext=(mu - sd, a.get_ylim()[1] * 0.82),
                   arrowprops=dict(arrowstyle="<->", color=INK, lw=1.0))
        dep = depth.get(str(d), np.nan)
        deps = f"{dep/1000:.1f}k UMI" if np.isfinite(dep) else "depth n/a"
        a.text(0.5, 0.975, f"{SHORT[st]} — donor {d}  (n={len(coord)})", transform=a.transAxes,
               ha="center", va="top", fontsize=9.5, color=INK, family="serif", fontweight="bold")
        a.text(0.5, 0.015, f"SD={sd:.2f}   IQR={iqr:.2f}   med depth {deps}", transform=a.transAxes,
               ha="center", va="bottom", fontsize=8, color=MUTED, family="serif")
        a.set_yticks([])
        if j == 0:
            a.set_ylabel("cell density", fontsize=9, family="serif")
        a.set_xlabel("zonation coordinate", fontsize=8.5, family="serif")
        for s in a.spines.values():
            s.set_color("#cdd6d8")

        # ---- bottom: PC-arm vs PP-arm scatter (mechanism view) ----
        b = axes[1, j]
        b.scatter(pc, pp, s=5, c=coord, cmap="PuOr", alpha=0.55, vmin=-2.5, vmax=2.5, rasterized=True)
        b.set_xlabel("pericentral-program score", fontsize=8.5, color=TEAL, family="serif")
        if j == 0:
            b.set_ylabel("periportal-program score", fontsize=8.5, color=RUST, family="serif")
        b.text(0.5, 0.98, f"anti-corr(PC,PP) = {ac:+.2f}", transform=b.transAxes, ha="center",
               va="top", fontsize=8.5, color=INK, family="serif")
        b.axhline(0, color="#cdd6d8", lw=0.7); b.axvline(0, color="#cdd6d8", lw=0.7)
        b.set_xlim(-3, 4); b.set_ylim(-3, 4)
        b.set_xticks([]); b.set_yticks([])
        for s in b.spines.values():
            s.set_color("#cdd6d8")

    fig.suptitle(f"Zonation distribution per patient across disease stages   [ruler: {which}]\n"
                 "top: cells along the score axis (dashed = pooled-healthy reference);  "
                 "bottom: PC vs PP (intact = anti-diagonal; origin = turn-off; blob = noise; center = de-zonation)",
                 fontsize=10.5, family="serif", y=0.99)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    out = os.path.join(str(config.FIG_H1), f"a2_zonation_distribution_by_patient_{which}.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, dpi=130)
    plt.close(fig)
    print("wrote", out)
    # also print the per-representative numbers
    print("\nrepresentative donors (max-n per stage):")
    for st, d, sub in reps:
        c = sub["coord"].values
        print(f"  {SHORT[st]:10s} donor {d:5s}  n={len(c):5d}  SD={np.std(c):.2f}  "
              f"IQR={np.percentile(c,75)-np.percentile(c,25):.2f}  "
              f"anticorr={spearmanr(sub['pc'],sub['pp']).statistic:+.2f}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "expanded_curated")
