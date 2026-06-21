#!/usr/bin/env python3
"""Combined deck panel: 4 rulers (cols) x 3 hypotheses (rows: H1 spread, H2 slope-loss, H3
plasticity), donor-level. Reads the per-set tables and writes results/figures/ruler_panel.png.
Run:  python src/make_panel_figure.py
"""
import os, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.stats import spearmanr
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # src/
import config

T = config.TABLES; FIG = config.FIGURES
RULERS = ["paper2_landmark", "expanded_curated", "unsupervised_top50", "paper2_full"]
SHORT = ["Hlth", "NAFLD", "NASH", "Cirr", "End"]


def _read(s, name):
    p = os.path.join(T, s, f"{name}.csv")     # per-set subdir
    return pd.read_csv(p) if os.path.exists(p) else None


def main():
    fig, ax = plt.subplots(3, len(RULERS), figsize=(4 * len(RULERS), 10), squeeze=False)
    for j, s in enumerate(RULERS):
        # row 0: H1 coord_spread per donor
        a = ax[0][j]; cpd = _read(s, "collapse_per_donor")
        if cpd is not None and "coord_spread" in cpd:
            a.scatter(cpd["stage_rank"] + np.random.uniform(-.08, .08, len(cpd)), cpd["coord_spread"],
                      s=20, color="#1b6e78", alpha=.7)
            m = cpd.groupby("stage_rank")["coord_spread"].mean(); a.plot(m.index, m.values, "o-", color="#c05621", lw=2)
            tr = _read(s, "collapse_trends")
            sub = tr[tr["metric"] == "coord_spread"].iloc[0] if tr is not None else None
            ttl = f"{s}\nH1 spread rho={sub['rho_vs_stage']:+.2f} p={sub['p_spearman']:.1g}" if sub is not None else s
            a.set_title(ttl, fontsize=9)
        else:
            a.text(.5, .5, f"{s}\n(gate failed / n/a)", ha="center", va="center"); a.set_title(s, fontsize=9)
        a.set_xticks(range(5)); a.set_xticklabels(SHORT, fontsize=7)
        if j == 0: a.set_ylabel("H1: coord spread / donor")
        # row 1: H2 slope-loss histogram
        a = ax[1][j]; h2 = _read(s, "h2_slope_loss")
        if h2 is not None and "mean_slope_trend_rho" in h2:
            tr = h2["mean_slope_trend_rho"].values
            a.hist(tr, bins=30, color="#1b6e78", alpha=.85); a.axvline(0, color="#c05621", lw=2)
            nweak = int((tr < 0).sum())
            a.set_title(f"H2 {nweak}/{len(tr)} weaken, med={np.nanmedian(tr):+.2f}", fontsize=9)
        else:
            a.text(.5, .5, "n/a", ha="center", va="center")
        if j == 0: a.set_ylabel("H2: gene slope trend")
        # row 2: H3 plasticity per donor
        a = ax[2][j]; pl = _read(s, "per_donor_plasticity")
        if pl is not None and "rho_dez_plast" in pl:
            a.axhline(0, color="#888", ls="--", lw=1)
            a.scatter(pl["stage_rank"] + np.random.uniform(-.08, .08, len(pl)), pl["rho_dez_plast"],
                      s=20, color="#7a4ea8", alpha=.75)
            m = pl.groupby("stage_rank")["rho_dez_plast"].mean(); a.plot(m.index, m.values, "o-", color="#c05621", lw=2)
            npos = int((pl["rho_dez_plast"] > 0).sum())
            a.set_title(f"H3 mean={pl['rho_dez_plast'].mean():+.3f}, {npos}/{len(pl)}>0", fontsize=9)
        else:
            a.text(.5, .5, "n/a", ha="center", va="center")
        a.set_xticks(range(5)); a.set_xticklabels(SHORT, fontsize=7)
        if j == 0: a.set_ylabel("H3: rho(dez,plast)/donor")
    fig.suptitle("Zonation-collapse battery: 4 rulers x H1/H2/H3 (donor-level)", fontsize=13)
    plt.tight_layout(rect=[0, 0, 1, 0.98])
    out = os.path.join(str(FIG), "ruler_panel.png"); plt.savefig(out, dpi=130); plt.close(fig)
    print("wrote", out)


if __name__ == "__main__":
    main()
