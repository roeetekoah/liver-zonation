#!/usr/bin/env python3
"""A3 -- canonical marker spatial profiles across disease.

SCIENTIFIC GOAL: for each canonical zonation MARKER gene, show whether its spatial gradient along
the zonation coordinate FLATTENS with disease (de-zonation: gene still expressed but loses its
position-dependence) or DROPS toward zero (turn-off: gene silenced). We bin the zonation coordinate
into ~12 quantile bins, average RAW (un-standardized) log1p-CP10k expression per (donor, bin), then
average those per-donor-bin means across donors WITHIN a disease stage (and within a fibrosis level)
-- so the UNIT IS THE DONOR (no cell pseudoreplication). One colored line per stage, then per
fibrosis level. A reader can SEE:
   * healthy line steep, later-stage lines flatter, same overall level  -> de-zonation
   * whole family of lines collapsing toward zero                       -> turn-off

x-axis: coordinate bin. coord is pericentral-high / periportal-low (see common.load_coords), so we
plot LEFT = periportal (low coord) -> RIGHT = pericentral (high coord). Pericentral markers should
ride high on the RIGHT; periportal markers high on the LEFT.

Usage:  python src/analysis/a3_marker_profiles.py [signature_set]   (default expanded_curated;
        only used to pick which coordinates.csv to read -- markers are fixed canonical genes.)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # src/ on path
from analysis import common as C
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# canonical zonation markers (expected pole given coord = pericentral-high / periportal-low)
PC_MARKERS = ["GLUL", "CYP2E1", "CYP1A2", "CYP3A4", "ADH1A", "SLCO1B3"]   # high at HIGH coord (right)
PP_MARKERS = ["ASS1", "ALDOB", "PCK1", "HAL", "SDS", "ASL", "ARG1"]       # high at LOW coord (left)

N_BINS = 12
MIN_CELLS_PER_DONORBIN = 5     # require a donor to have >= this many cells in a bin to use that mean
MIN_DONORS_PER_LEVEL = 2       # need >= this many donors contributing to a (level, bin) to draw it


def _donor_binned(coords, gene_mat, gene, bin_edges):
    """For one gene, return DataFrame[donor, bin, mean_expr] -- mean raw expression per (donor,bin),
    keeping only (donor,bin) cells >= MIN_CELLS_PER_DONORBIN."""
    df = coords[["donor", "coord"]].copy()
    df["expr"] = gene_mat[gene].reindex(coords["cell_id"]).values
    df = df[np.isfinite(df["expr"].values)]
    df["bin"] = pd.cut(df["coord"], bins=bin_edges, labels=False, include_lowest=True)
    df = df[df["bin"].notna()]
    df["bin"] = df["bin"].astype(int)
    g = df.groupby(["donor", "bin"])["expr"].agg(["mean", "size"]).reset_index()
    g = g[g["size"] >= MIN_CELLS_PER_DONORBIN]
    return g.rename(columns={"mean": "mean_expr"})


def _level_curve(donor_binned, donors_in_level):
    """Average per-donor-bin means across the donors in this level. Returns (x_bins, mean, sem, n)
    arrays aligned to bin index 0..N_BINS-1; positions with < MIN_DONORS_PER_LEVEL donors are NaN."""
    sub = donor_binned[donor_binned["donor"].isin(set(map(str, donors_in_level)))]
    mean = np.full(N_BINS, np.nan); sem = np.full(N_BINS, np.nan); ndon = np.zeros(N_BINS, int)
    for b in range(N_BINS):
        vals = sub.loc[sub["bin"] == b, "mean_expr"].values
        ndon[b] = len(vals)
        if len(vals) >= MIN_DONORS_PER_LEVEL:
            mean[b] = float(np.mean(vals))
            sem[b] = float(np.std(vals, ddof=1) / np.sqrt(len(vals))) if len(vals) > 1 else 0.0
    return np.arange(N_BINS), mean, sem, ndon


def _stage_colors():
    cmap = plt.get_cmap("viridis")
    return {C.STAGE_SHORT[s]: cmap(i / max(1, len(C.STAGE_ORDER) - 1))
            for i, s in enumerate(C.STAGE_ORDER)}


def _fib_colors():
    cmap = plt.get_cmap("magma")
    return {C.FIB_LABEL[f]: cmap(0.15 + 0.7 * i / max(1, len(C.FIB_LABEL) - 1))
            for i, f in enumerate(sorted(C.FIB_LABEL))}


def _make_figure(donor_binned_by_gene, levels, colors, axis_label, which, outname):
    """levels = [(label,[donors]),...] ordered; colors = {label: color}. One panel per marker."""
    markers = [("PC", g, C.TEAL) for g in PC_MARKERS] + [("PP", g, C.RUST) for g in PP_MARKERS]
    # keep only genes actually present (a donor_binned table exists and is non-empty)
    markers = [(pole, g, col) for (pole, g, col) in markers
               if g in donor_binned_by_gene and len(donor_binned_by_gene[g])]
    ncol = 4
    nrow = int(np.ceil(len(markers) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(3.2 * ncol, 2.5 * nrow), squeeze=False)

    for k, (pole, gene, polecol) in enumerate(markers):
        ax = axes[k // ncol][k % ncol]
        db = donor_binned_by_gene[gene]
        ymax = 0.0
        for label, donors in levels:
            x, mean, sem, ndon = _level_curve(db, donors)
            m = np.isfinite(mean)
            if not m.any():
                continue
            col = colors[label]
            ax.plot(x[m], mean[m], "-", color=col, lw=1.6, marker="o", ms=2.5, label=label)
            band_lo = mean[m] - sem[m]; band_hi = mean[m] + sem[m]
            ax.fill_between(x[m], band_lo, band_hi, color=col, alpha=0.12, linewidth=0)
            ymax = max(ymax, float(np.nanmax(band_hi)))
        pole_word = "pericentral" if pole == "PC" else "periportal"
        side = "right" if pole == "PC" else "left"
        ax.set_title(f"{gene}", fontsize=10, family="serif", color=polecol, fontweight="bold")
        ax.text(0.5, 0.92, f"{pole_word} (expect high {side})", transform=ax.transAxes,
                ha="center", va="top", fontsize=7, color=C.MUTED, family="serif")
        ax.set_xlim(-0.5, N_BINS - 0.5)
        if ymax > 0:
            ax.set_ylim(0, ymax * 1.18)
        ax.set_xticks([0, N_BINS - 1])
        ax.set_xticklabels(["PP", "PC"], fontsize=7.5, family="serif")
        ax.tick_params(axis="y", labelsize=6.5)
        for s in ax.spines.values():
            s.set_color(C.RULE)
        if k % ncol == 0:
            ax.set_ylabel("mean raw expr\n(log1p-CP10k)", fontsize=7.5, family="serif")

    # blank any unused panels
    for k in range(len(markers), nrow * ncol):
        axes[k // ncol][k % ncol].axis("off")

    # shared legend
    handles = [Line2D([0], [0], color=colors[lab], lw=2.2, marker="o", ms=4, label=lab)
               for lab, _ in levels]
    fig.legend(handles=handles, loc="lower center", ncol=min(len(levels), 6),
               fontsize=8.5, frameon=False, title=axis_label, title_fontsize=9)

    fig.suptitle(
        "A3  canonical marker spatial profiles across disease   "
        f"[ruler: {which}]\n"
        "x = zonation-coordinate bin (LEFT=periportal -> RIGHT=pericentral, ~12 donor-averaged "
        "quantile bins);  y = mean RAW expression (log1p-CP10k).  "
        "flattening gradient = de-zonation;  whole curve dropping = turn-off",
        fontsize=10.5, family="serif", y=0.995)
    fig.tight_layout(rect=[0, 0.055, 1, 0.93])
    out = C.fig_path("h1", outname)
    fig.savefig(out, dpi=140)
    plt.close(fig)
    print("wrote", out)
    return out


def main(which="expanded_curated"):
    coords = C.load_coords(which)
    coords = C.attach_clinical(coords)
    coords["donor"] = coords["donor"].astype(str)

    genes = PC_MARKERS + PP_MARKERS
    gene_mat = C.raw_gene_matrix(genes)
    present = [g for g in genes if g in gene_mat.columns]
    missing = [g for g in genes if g not in gene_mat.columns]
    if missing:
        print("markers absent from data (skipped):", missing)
    print("markers used:", present)

    # global quantile bin edges over ALL cells (shared across stages/fibrosis so x is comparable)
    bin_edges = np.unique(np.quantile(coords["coord"].values, np.linspace(0, 1, N_BINS + 1)))
    if len(bin_edges) < N_BINS + 1:
        # degenerate ties -> fall back to linear edges
        bin_edges = np.linspace(coords["coord"].min(), coords["coord"].max(), N_BINS + 1)

    # precompute per-(donor,bin) means for every present gene once
    donor_binned_by_gene = {g: _donor_binned(coords, gene_mat, g, bin_edges) for g in present}

    # ---- per-donor stage / fibrosis labels (one representative value per donor) ----
    donor_stage = coords.groupby("donor")["stage"].agg(lambda s: s.mode().iat[0])
    donor_fib = coords.groupby("donor")["fibrosis"].median()

    stage_levels = [(C.STAGE_SHORT[s], donor_stage[donor_stage == s].index.tolist())
                    for s in C.STAGE_ORDER if (donor_stage == s).any()]
    fib_levels = []
    for f in sorted(C.FIB_LABEL):
        donors = donor_fib[donor_fib == f].index.tolist()
        if donors:
            fib_levels.append((C.FIB_LABEL[f], donors))

    out_stage = _make_figure(donor_binned_by_gene, stage_levels, _stage_colors(),
                             "disease stage", which, "a3_marker_profiles_stage.png")
    out_fib = _make_figure(donor_binned_by_gene, fib_levels, _fib_colors(),
                           "fibrosis level", which, "a3_marker_profiles_fibrosis.png")

    # ---- quantitative summary printed to stdout: gradient (PC-end minus PP-end) per level ----
    print("\nGradient = (mean of top-2 bins) - (mean of bottom-2 bins); positive => pericentral-high."
          "  Healthy vs later tells flatten; level0 = mean over all bins tells turn-off.")
    for pole, mk in (("pericentral", PC_MARKERS), ("periportal", PP_MARKERS)):
        for g in mk:
            if g not in donor_binned_by_gene or not len(donor_binned_by_gene[g]):
                continue
            db = donor_binned_by_gene[g]
            line = [f"  {g:7s}({pole[:2]})"]
            for label, donors in stage_levels:
                _, mean, _, _ = _level_curve(db, donors)
                if np.isfinite(mean).sum() < 4:
                    line.append(f"{label}:n/a")
                    continue
                top = np.nanmean(mean[-2:]); bot = np.nanmean(mean[:2]); lvl = np.nanmean(mean)
                line.append(f"{label}:grad{top - bot:+.2f}/lvl{lvl:.2f}")
            print("  ".join(line))

    return out_stage, out_fib


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "expanded_curated")
