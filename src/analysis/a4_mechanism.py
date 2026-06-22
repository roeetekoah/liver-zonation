"""A4 — Mechanism of zonation loss with MASLD progression (EXPLORATORY / heuristic).

For each donor we ask WHICH of three mechanisms explains zonation loss, by comparing the donor's
metrics to a HEALTHY BASELINE (median over healthy-control donors):

  (a) expression TURN-OFF : the program's genes go silent -> raw program LEVEL (prog_raw) drops.
      turnoff_score = prog_raw0 - prog_raw                (positive = expression dropped)
  (b) NOISE               : pericentral vs periportal scores stop anti-correlating -> anticorr
      rises toward 0/positive.
      noise_score   = anticorr - anticorr0               (positive = anti-corr moved toward 0/+)
  (c) true DE-ZONATION    : cells lose spatial spread and pile toward the axis center -> coordinate
      RANGE (coord_range) shrinks, expression level retained.
      dezon_score   = coord_range0 - coord_range          (positive = range shrank)

Each raw deviation score is z-scored across donors so the three are comparable, and each donor's
dominant mechanism = argmax of the three z-scores. Donors near baseline (all z-scores small) are
marked "intact". This is a HEURISTIC classification, presented honestly as exploratory; it is
sensitive to low-n / low-depth donors (noisy metrics), so n_cells & depth_med are carried through.

Run:  python src/analysis/a4_mechanism.py [signature_set]   (default expanded_curated)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # src/ on path
from analysis import common as C
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

plt.rcParams.update({
    "figure.dpi": 130, "savefig.dpi": 130,
    "font.family": "serif", "font.size": 9,
    "axes.titlesize": 10, "axes.labelsize": 9,
    "axes.edgecolor": C.MUTED, "axes.linewidth": 0.8,
    "xtick.color": C.INK, "ytick.color": C.INK, "text.color": C.INK,
    "axes.titlecolor": C.INK, "axes.labelcolor": C.INK,
})

HEALTHY = "Healthy control"
# mechanism vocabulary
MECHS = ["turn-off", "noise", "de-zonation"]
SCORE_COLS = {"turn-off": "turnoff_score", "noise": "noise_score", "de-zonation": "dezon_score"}
MECH_COLOR = {"turn-off": C.RUST, "noise": C.TEAL, "de-zonation": C.INK, "intact": C.RULE}
# a donor is "intact" if its largest standardized deviation is below this z
INTACT_Z = 0.5


def _zscore(x):
    x = np.asarray(x, float)
    mu = np.nanmean(x)
    sd = np.nanstd(x)
    if not np.isfinite(sd) or sd == 0:
        return np.zeros_like(x)
    return (x - mu) / sd


def classify(s):
    """Add raw + standardized deviation scores and a dominant-mechanism call to the donor summary."""
    s = s.copy()
    base = s[s["stage"] == HEALTHY]
    anticorr0 = float(np.nanmedian(base["anticorr"]))
    prog_raw0 = float(np.nanmedian(base["prog_raw"]))
    coord_range0 = float(np.nanmedian(base["coord_range"]))

    # raw deviation scores: positive = movement toward collapse
    s["turnoff_score"] = prog_raw0 - s["prog_raw"]
    s["noise_score"] = s["anticorr"] - anticorr0
    s["dezon_score"] = coord_range0 - s["coord_range"]

    # standardize across donors so the three axes are comparable
    z = pd.DataFrame({
        "turn-off": _zscore(s["turnoff_score"]),
        "noise": _zscore(s["noise_score"]),
        "de-zonation": _zscore(s["dezon_score"]),
    }, index=s.index)
    for m in MECHS:
        s["z_" + SCORE_COLS[m]] = z[m].values

    zmax = z.max(axis=1)
    arg = z.idxmax(axis=1)
    call = np.where(zmax < INTACT_Z, "intact", arg)
    s["dominant_mechanism"] = call
    baseline = dict(anticorr0=anticorr0, prog_raw0=prog_raw0, coord_range0=coord_range0)
    return s, baseline


# ----------------------------------------------------------------------------- figures
SUB_NOTE = ("Heuristic / exploratory classification; metrics are n- and depth-sensitive "
            "(low-n donors faint).")


def _alpha_for(n):
    """Faint for low-n donors, opaque for high-n."""
    n = np.asarray(n, float)
    a = 0.15 + 0.75 * np.clip((n - 200.0) / 1500.0, 0, 1)
    return a


def _size_for(n):
    n = np.asarray(n, float)
    return 20 + 130 * np.clip(n / 2500.0, 0, 1)


def _jitter(k, width=0.16, seed=0):
    rng = np.random.default_rng(seed)
    return (rng.random(k) - 0.5) * 2 * width


METRICS = [
    ("anticorr", "anti-corr  Spearman(pc,pp)", "NOISE axis  (healthy ~ -0.5 -> 0)"),
    ("prog_raw", "prog_raw  mean log1p-CP10k", "TURN-OFF axis  (lower = silenced)"),
    ("coord_range", "coord_range  p95-p5", "DE-ZONATION axis  (lower = piled)"),
]


def fig_metrics_by_axis(s, axis, fname):
    levels = C.staging_levels(s, axis)
    labels = [lab for lab, _ in levels]
    fig, axes = plt.subplots(1, 3, figsize=(12.0, 4.0))
    for ax, (col, ylab, sub) in zip(axes, METRICS):
        means = []
        for xi, (lab, donors) in enumerate(levels):
            d = s[s["donor"].isin(donors)]
            if not len(d):
                means.append(np.nan); continue
            jx = xi + _jitter(len(d), seed=xi)
            ax.scatter(jx, d[col].values, s=_size_for(d["n_cells"]),
                       alpha=_alpha_for(d["n_cells"]),
                       color=C.TEAL, edgecolor="white", linewidth=0.4, zorder=3)
            means.append(float(np.nanmean(d[col].values)))
        ax.plot(range(len(levels)), means, "-o", color=C.RUST, lw=1.6, ms=4,
                zorder=4, label="stage mean")
        ax.set_xticks(range(len(levels))); ax.set_xticklabels(labels, rotation=25, ha="right")
        ax.set_ylabel(ylab); ax.set_title(sub)
        ax.axhline(0, color=C.RULE, lw=0.7, zorder=1)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    axes[0].legend(loc="best", frameon=False, fontsize=7)
    fig.suptitle(f"A4 mechanism metrics by {axis} (per-donor; point size/alpha ~ n_cells)",
                 fontsize=11, y=1.00)
    fig.text(0.5, -0.02, SUB_NOTE, ha="center", fontsize=7, color=C.MUTED)
    fig.tight_layout(rect=(0, 0.01, 1, 0.97))
    p = C.fig_path("h1", fname)
    fig.savefig(p, bbox_inches="tight"); plt.close(fig)
    return p


def fig_trajectory(s, baseline, fname):
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.0))
    stages = [st for st in C.STAGE_ORDER if (s["stage"] == st).any()]
    cmap = plt.get_cmap("viridis")
    scolor = {st: cmap(i / max(1, len(stages) - 1)) for i, st in enumerate(stages)}

    # panel 1: noise axis (anticorr) vs turn-off axis (prog_raw)
    ax = axes[0]
    for st in stages:
        d = s[s["stage"] == st]
        ax.scatter(d["anticorr"], d["prog_raw"], s=_size_for(d["n_cells"]),
                   color=scolor[st], edgecolor="white", linewidth=0.4,
                   alpha=0.85, label=C.STAGE_SHORT[st], zorder=3)
    ax.scatter([baseline["anticorr0"]], [baseline["prog_raw0"]], marker="*",
               s=320, color=C.RUST, edgecolor="black", linewidth=0.6, zorder=5,
               label="healthy baseline")
    ax.set_xlabel("anticorr  (noise axis ->)"); ax.set_ylabel("prog_raw  (turn-off axis)")
    ax.set_title("collapse trajectory: noise vs turn-off")
    ax.legend(loc="best", frameon=False, fontsize=7)

    # panel 2: coord_range (de-zonation) vs anticorr (noise)
    ax = axes[1]
    for st in stages:
        d = s[s["stage"] == st]
        ax.scatter(d["anticorr"], d["coord_range"], s=_size_for(d["n_cells"]),
                   color=scolor[st], edgecolor="white", linewidth=0.4, alpha=0.85, zorder=3)
    ax.scatter([baseline["anticorr0"]], [baseline["coord_range0"]], marker="*",
               s=320, color=C.RUST, edgecolor="black", linewidth=0.6, zorder=5)
    ax.set_xlabel("anticorr  (noise axis ->)"); ax.set_ylabel("coord_range  (de-zonation axis)")
    ax.set_title("de-zonation vs noise")
    for ax in axes:
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    fig.suptitle("A4 mechanism trajectory (color = stage, size ~ n_cells)", fontsize=11)
    fig.text(0.5, -0.01, SUB_NOTE, ha="center", fontsize=7, color=C.MUTED)
    fig.tight_layout(rect=(0, 0.01, 1, 0.96))
    p = C.fig_path("h1", fname)
    fig.savefig(p, bbox_inches="tight"); plt.close(fig)
    return p


def fig_calls(s, fname):
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4))
    cats = MECHS + ["intact"]
    for ax, axis, title in ((axes[0], "stage", "by stage"), (axes[1], "fibrosis", "by fibrosis")):
        levels = C.staging_levels(s, axis)
        labels = [lab for lab, _ in levels]
        bottoms = np.zeros(len(levels))
        for cat in cats:
            counts = []
            for _, donors in levels:
                d = s[s["donor"].isin(donors)]
                counts.append(int((d["dominant_mechanism"] == cat).sum()))
            counts = np.array(counts, float)
            ax.bar(range(len(levels)), counts, bottom=bottoms, color=MECH_COLOR[cat],
                   edgecolor="white", linewidth=0.6, label=cat)
            bottoms += counts
        ax.set_xticks(range(len(levels))); ax.set_xticklabels(labels, rotation=25, ha="right")
        ax.set_ylabel("n donors"); ax.set_title(f"dominant mechanism {title}")
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    axes[0].legend(loc="upper left", frameon=False, fontsize=7, ncol=2)
    fig.suptitle("A4 dominant-mechanism calls (heuristic argmax of standardized scores)",
                 fontsize=11)
    fig.text(0.5, -0.02, SUB_NOTE, ha="center", fontsize=7, color=C.MUTED)
    fig.tight_layout(rect=(0, 0.01, 1, 0.95))
    p = C.fig_path("h1", fname)
    fig.savefig(p, bbox_inches="tight"); plt.close(fig)
    return p


# ----------------------------------------------------------------------------- main
def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "expanded_curated"
    s = C.donor_summary(which=which, with_raw=True)
    s, baseline = classify(s)

    cols = ["donor", "stage", "fibrosis", "nas", "n_cells", "depth_med",
            "anticorr", "prog_raw", "coord_range",
            "turnoff_score", "noise_score", "dezon_score", "dominant_mechanism"]
    csv_path = C.table_path("mechanism_by_donor.csv")
    s[cols].to_csv(csv_path, index=False)

    p1 = fig_metrics_by_axis(s, "stage", "a4_mechanism_metrics_by_stage.png")
    p2 = fig_metrics_by_axis(s, "fibrosis", "a4_mechanism_metrics_by_fibrosis.png")
    p3 = fig_trajectory(s, baseline, "a4_mechanism_trajectory.png")
    p4 = fig_calls(s, "a4_mechanism_calls.png")

    print("baseline (healthy median):", {k: round(v, 4) for k, v in baseline.items()})
    print("n donors:", len(s))
    print("dominant mechanism counts:\n", s["dominant_mechanism"].value_counts().to_string())
    print("written:")
    for p in (csv_path, p1, p2, p3, p4):
        print("  ", p, "OK" if os.path.exists(p) else "MISSING")


if __name__ == "__main__":
    main()
