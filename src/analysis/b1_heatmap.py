#!/usr/bin/env python3
"""B1 -- the centerpiece H2 figure: gene x (zone-binned cells) heatmaps showing how hepatocyte
zonation changes across MASLD disease.

A reviewer found the old single "z vs healthy" encoding confusing because it ENTANGLES two distinct
things: a change in overall LEVEL (a gene turning off) and a change in spatial PATTERN (the
left->right gradient washing out / de-zonation). When a pericentral gene simply turns off, the whole
top of that panel goes one color and it reads as "a flip" rather than "level dropped."

To separate the two mechanisms cleanly we render THREE distinctly-labelled encodings, each its own
figure:

  (1) PATTERN view (de-zonation)  -- b1_heatmap_pattern_stage.png / _fibrosis.png
      Each gene is z-scored WITHIN EACH PANEL (normalized to that stage's OWN mean/SD across its
      bins). This asks, for THAT stage alone, "is there still a left->right gradient?", INDEPENDENT
      of overall level. cmap PuOr, symmetric +/-1.8. Healthy -> crisp diagonal. A later stage that
      keeps a diagonal still has spatial structure; one that washes to noise = de-zonation. KEY VIEW.

  (2) LEVEL view (turn-off)       -- b1_heatmap_level_stage.png / _fibrosis.png
      Raw mean log1p-CP10k expression on a SHARED color scale across all panels (cmap magma). A
      fading row/panel = the gene(s) turning off.

  (3) DEVIATION view              -- b1_heatmap_vs_healthy_stage.png
      Per-gene z vs the HEALTHY reference: what changed relative to healthy. Explicitly labelled
      "orange = below healthy level" so it is not misread as a pattern flip.

LAYOUT (every figure): rows = signature genes, ordered ONCE by their HEALTHY zonal slope
(pericentral-rising at top, periportal-rising at bottom) and REUSED for every panel. Columns within
a panel = cells binned into ~50 quantile bins of the zonation coordinate (LEFT=periportal ->
RIGHT=pericentral); each cell of the heatmap is the mean expression over the cells in that bin
(pseudobulk). Bins with < MIN_CELLS_PER_BIN cells are masked.

PSEUDOBULK / UNIT NOTE: the unit here is the CELL (bins aggregate cells, not donors). That is fine
for a *visualization*; the donor-level statistics live in the H2 tests elsewhere. This figure is
meant to be SEEN, not tested.

Usage:  python src/analysis/b1_heatmap.py [signature_set]      (default expanded_curated)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # src/ on path
from analysis import common as C
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

# ---- parameters ----
N_GENE_BINS = 20          # quantile bins of coordinate used to estimate each gene's HEALTHY slope
N_CELL_BINS = 50          # quantile bins of coordinate per panel (the x-axis of every heatmap)
MIN_CELLS_PER_BIN = 5     # bins with fewer cells -> NaN (masked / shown as background)
Z_LIM_PATTERN = 1.8       # symmetric vmin/vmax for the PATTERN (within-panel z) figures
Z_LIM_DEV = 2.0           # symmetric vmin/vmax for the DEVIATION (z-vs-healthy) figure
# marker rows to label on the y-axis (whichever are present)
MARKER_ROWS = ["GLUL", "CYP2E1", "CYP1A2", "CYP3A4", "ASS1", "ALDOB", "PCK1", "HAL", "ARG1"]

YLABEL = ("signature genes\n(top = pericentral-rising, bottom = periportal-rising; "
          "order fixed from healthy)")
XLABEL = "cells binned by zonation coordinate\n(left = periportal  ->  right = pericentral)"
READING_KEY = ("reading key: diagonal banding = zonation;  PATTERN view washing out = de-zonation;  "
               "LEVEL view fading = turn-off")


# ------------------------------------------------------------------ helpers
def _quantile_edges(x, nbins):
    """Unique quantile edges over x; fall back to linear if too many ties collapse the edges."""
    edges = np.unique(np.quantile(x, np.linspace(0, 1, nbins + 1)))
    if len(edges) < nbins + 1:
        edges = np.linspace(float(np.min(x)), float(np.max(x)), nbins + 1)
    return edges


def _binned_pseudobulk(coord, G, edges, nbins):
    """Per-bin mean expression for each gene -> (n_genes x nbins) array; bins with < MIN_CELLS_PER_BIN
    cells become NaN columns. G is (n_cells x n_genes) aligned to `coord`. Bins are ordered so that
    column 0 = LOW coord = periportal (left) and the last column = HIGH coord = pericentral (right)."""
    coord = np.asarray(coord)
    b = pd.cut(coord, bins=edges, labels=False, include_lowest=True)
    b = np.asarray(b)
    n_genes = G.shape[1]
    out = np.full((n_genes, nbins), np.nan, dtype=float)
    for j in range(nbins):
        m = (b == j)
        if int(m.sum()) >= MIN_CELLS_PER_BIN:
            out[:, j] = np.nanmean(G[m], axis=0)
    return out


def _healthy_gene_order(coord_h, G_h):
    """Order genes by HEALTHY zonal slope. Bin healthy coord into N_GENE_BINS quantile bins, take each
    gene's per-bin mean, fit slope of (mean vs bin index). Bin index increases LOW->HIGH coord =
    periportal->pericentral, so a POSITIVE slope = pericentral-rising. We sort DESCENDING by slope so
    pericentral-rising genes sit at the TOP and periportal-rising genes at the BOTTOM.
    Returns (order_idx, slopes_in_that_order)."""
    edges = _quantile_edges(coord_h, N_GENE_BINS)
    pb = _binned_pseudobulk(coord_h, G_h, edges, N_GENE_BINS)   # genes x N_GENE_BINS
    xb = np.arange(N_GENE_BINS, dtype=float)
    slopes = np.full(pb.shape[0], np.nan)
    for i in range(pb.shape[0]):
        y = pb[i]
        ok = np.isfinite(y)
        if ok.sum() >= 3 and np.ptp(xb[ok]) > 0:
            slopes[i] = np.polyfit(xb[ok], y[ok], 1)[0]
    slopes = np.where(np.isfinite(slopes), slopes, 0.0)
    order = np.argsort(-slopes)            # descending: pericentral-rising (top) -> periportal (bottom)
    return order, slopes[order]


def _healthy_ref_stats(coord_h, G_h, edges_ref):
    """Healthy per-gene mean & SD computed over the HEALTHY per-bin pseudobulk (same binning the panels
    use), so the deviation z-score is on the same footing as what is plotted. Returns (mu[g], sd[g])."""
    pb = _binned_pseudobulk(coord_h, G_h, edges_ref, N_CELL_BINS)   # genes x N_CELL_BINS
    mu = np.nanmean(pb, axis=1)
    sd = np.nanstd(pb, axis=1)
    sd = np.where((sd > 1e-9) & np.isfinite(sd), sd, 1.0)
    mu = np.where(np.isfinite(mu), mu, 0.0)
    return mu, sd


def _within_panel_z(pb):
    """Z-score EACH ROW (gene) of a panel against that panel's OWN mean/SD across its (finite) bins.
    This is the PATTERN view: it removes the gene's overall level so only the left->right SHAPE
    survives. Rows that are flat (no gradient) -> ~0 everywhere; rows with a gradient keep their
    diagonal sign. NaN bins stay NaN (masked)."""
    out = np.full_like(pb, np.nan, dtype=float)
    for i in range(pb.shape[0]):
        row = pb[i]
        ok = np.isfinite(row)
        if ok.sum() < 3:
            continue
        mu = np.nanmean(row[ok])
        sd = np.nanstd(row[ok])
        if not (sd > 1e-9):
            out[i, ok] = 0.0
        else:
            out[i, ok] = (row[ok] - mu) / sd
    return out


def _group_levels(coords, axis):
    """Ordered [(label, mask_array), ...] for axis in {'stage','fibrosis'} over the coords rows."""
    if axis == "stage":
        out = []
        for s in C.STAGE_ORDER:
            m = (coords["stage"] == s).values
            if m.sum() >= MIN_CELLS_PER_BIN * 2:
                out.append((C.STAGE_SHORT[s], m))
        return out
    if axis == "fibrosis":
        out = []
        for f in C.FIB_ORDER:
            m = (coords["fibrosis"] == f).values
            if m.sum() >= MIN_CELLS_PER_BIN * 2:
                out.append((C.FIB_LABEL[f], m))
        return out
    raise ValueError(axis)


def _build_matrices(coords, G, order, axis, ref_mu, ref_sd):
    """For each group level along `axis`, compute the (genes x N_CELL_BINS) pseudobulk in shared gene
    order, then derive the three encodings. Returns (labels, raw_mats, pattern_mats, dev_mats):
      raw_mats     = per-bin mean log1p-CP10k expression          (LEVEL view)
      pattern_mats = each gene z-scored WITHIN its own panel      (PATTERN view)
      dev_mats     = each gene z-scored vs the HEALTHY reference  (DEVIATION view)
    Each group uses its OWN quantile bins of coord, so a panel always fills its x-axis."""
    levels = _group_levels(coords, axis)
    labels, raw_mats, pattern_mats, dev_mats = [], [], [], []
    for lab, m in levels:
        sub_coord = coords.loc[m, "coord"].values
        sub_G = G[m]                                    # cells x genes (group subset)
        edges = _quantile_edges(sub_coord, N_CELL_BINS)
        pb = _binned_pseudobulk(sub_coord, sub_G, edges, N_CELL_BINS)  # genes x bins
        pb = pb[order]                                  # reorder rows to shared gene order
        raw_mats.append(pb)
        pattern_mats.append(_within_panel_z(pb))
        dev_mats.append((pb - ref_mu[order][:, None]) / ref_sd[order][:, None])
        labels.append(lab)
    return labels, raw_mats, pattern_mats, dev_mats


# ------------------------------------------------------------------ plotting
def _draw_panels(mats, labels, order, gene_names, *, cmap, vmin, vmax,
                 suptitle, outpath, cbar_label):
    """mats = list of (genes x N_CELL_BINS) arrays (already in plot order), one per group level."""
    n = len(mats)
    fig_w = max(8.0, 2.05 * n + 1.8)
    fig, axes = plt.subplots(1, n, figsize=(fig_w, 7.0), squeeze=False,
                             gridspec_kw=dict(wspace=0.07))
    axes = axes[0]

    # y positions of marker rows (in the shared gene order)
    name_to_row = {gene_names[order[r]]: r for r in range(len(order))}
    marker_rows = [(g, name_to_row[g]) for g in MARKER_ROWS if g in name_to_row]

    im = None
    for k, (mat, lab) in enumerate(zip(mats, labels)):
        ax = axes[k]
        masked = np.ma.masked_invalid(mat)
        im = ax.imshow(masked, aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax,
                       interpolation="nearest", origin="upper")
        ax.set_title(lab, fontsize=11, family="serif", fontweight="bold", color=C.INK)
        # x ticks: periportal (left) -> pericentral (right)
        ax.set_xticks([0, mat.shape[1] - 1])
        ax.set_xticklabels(["PP", "PC"], fontsize=8, family="serif")
        if k == 0:
            ax.set_yticks([r for _, r in marker_rows])
            ax.set_yticklabels([g for g, _ in marker_rows], fontsize=8, family="serif")
            ax.set_ylabel(YLABEL, fontsize=8.5, family="serif")
        else:
            ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color(C.RULE)

    cbar = fig.colorbar(im, ax=list(axes), fraction=0.025, pad=0.012)
    cbar.set_label(cbar_label, fontsize=8.5, family="serif")
    cbar.ax.tick_params(labelsize=7)

    # shared x-axis label centered under the panels
    fig.supxlabel(XLABEL, fontsize=9, family="serif", y=0.015, color=C.INK)
    fig.suptitle(suptitle, fontsize=10.0, family="serif", y=0.995)
    fig.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("wrote", outpath)
    return outpath


def _shared_raw_scale(mats):
    """Robust shared (vmin, vmax) over the finite values of all LEVEL-view matrices."""
    vals = np.concatenate([m[np.isfinite(m)] for m in mats]) if mats else np.array([0.0])
    vmin = float(np.nanpercentile(vals, 1))
    vmax = float(np.nanpercentile(vals, 99))
    if not (vmax > vmin):
        vmin, vmax = float(np.nanmin(vals)), float(np.nanmax(vals) + 1e-6)
    return vmin, vmax


# ------------------------------------------------------------------ main
def main(which="expanded_curated"):
    coords = C.load_coords(which)
    coords = C.attach_clinical(coords)
    coords["donor"] = coords["donor"].astype(str)

    pc_genes, pp_genes = C.gene_lists(which)
    genes = list(dict.fromkeys(pc_genes + pp_genes))     # de-dup, keep order
    Gdf = C.raw_gene_matrix(genes)
    present = [g for g in genes if g in Gdf.columns]
    if not present:
        raise SystemExit(f"no signature genes for set '{which}' found in the expression matrix")
    missing = [g for g in genes if g not in Gdf.columns]
    if missing:
        print(f"{len(missing)} signature genes absent from data (skipped):", missing[:12],
              "..." if len(missing) > 12 else "")
    print(f"signature genes used: {len(present)}  (PC+PP from set '{which}')")

    # align expression to coords order, as a plain array (cells x genes)
    Gdf = Gdf.reindex(coords["cell_id"])[present]
    G = Gdf.values.astype(float)
    gene_names = np.array(present)

    # ---- HEALTHY reference: gene order + per-gene mean/SD (computed ONCE, reused everywhere) ----
    h_mask = (coords["stage"] == "Healthy control").values
    if h_mask.sum() < N_CELL_BINS:
        raise SystemExit(f"too few Healthy-control cells ({int(h_mask.sum())}) to build the reference")
    coord_h = coords.loc[h_mask, "coord"].values
    G_h = G[h_mask]
    order, ordered_slopes = _healthy_gene_order(coord_h, G_h)
    ref_edges = _quantile_edges(coord_h, N_CELL_BINS)
    ref_mu, ref_sd = _healthy_ref_stats(coord_h, G_h, ref_edges)
    print(f"Healthy reference: {int(h_mask.sum())} cells; gene order fixed by healthy zonal slope.")
    print("  top (pericentral-rising):", ", ".join(gene_names[order][:5]))
    print("  bottom (periportal-rising):", ", ".join(gene_names[order][-5:]))

    outs = []

    # ============================== STAGE panels ==============================
    labels, raw_mats, pattern_mats, dev_mats = _build_matrices(
        coords, G, order, "stage", ref_mu, ref_sd)

    # (1) PATTERN view (de-zonation) -- within-panel z
    outs.append(_draw_panels(
        pattern_mats, labels, order, gene_names,
        cmap="PuOr", vmin=-Z_LIM_PATTERN, vmax=Z_LIM_PATTERN,
        suptitle=("B1 PATTERN view (de-zonation)   [ruler: " + which + "]\n"
                  "each gene z-scored WITHIN ITS OWN stage panel -> shows the left->right gradient "
                  "INDEPENDENT of overall level.\n" + READING_KEY),
        outpath=C.fig_path("h2", "b1_heatmap_pattern_stage.png"),
        cbar_label="within-panel z\n(purple = high / pericentral end,\norange = low / periportal end)"))

    # (2) LEVEL view (turn-off) -- raw expression, shared scale
    rvmin, rvmax = _shared_raw_scale(raw_mats)
    outs.append(_draw_panels(
        raw_mats, labels, order, gene_names,
        cmap="magma", vmin=rvmin, vmax=rvmax,
        suptitle=("B1 LEVEL view (turn-off)   [ruler: " + which + "]\n"
                  "raw mean expression on a SHARED color scale across panels -> fading rows = genes "
                  "turning off.\n" + READING_KEY),
        outpath=C.fig_path("h2", "b1_heatmap_level_stage.png"),
        cbar_label="mean expression\n(log1p-CP10k; bright = high)"))

    # (3) DEVIATION view -- z vs healthy reference
    outs.append(_draw_panels(
        dev_mats, labels, order, gene_names,
        cmap="PuOr", vmin=-Z_LIM_DEV, vmax=Z_LIM_DEV,
        suptitle=("B1 DEVIATION view: change vs HEALTHY   [ruler: " + which + "]\n"
                  "per-gene z relative to the healthy reference -> orange = BELOW healthy level, "
                  "purple = ABOVE.  (level + pattern combined; read with the two views above.)\n"
                  + READING_KEY),
        outpath=C.fig_path("h2", "b1_heatmap_vs_healthy_stage.png"),
        cbar_label="deviation from healthy\n(orange = below healthy level,\npurple = above)"))

    # ============================== FIBROSIS panels ==============================
    flabels, fraw_mats, fpattern_mats, fdev_mats = _build_matrices(
        coords, G, order, "fibrosis", ref_mu, ref_sd)

    # PATTERN view by fibrosis
    outs.append(_draw_panels(
        fpattern_mats, flabels, order, gene_names,
        cmap="PuOr", vmin=-Z_LIM_PATTERN, vmax=Z_LIM_PATTERN,
        suptitle=("B1 PATTERN view (de-zonation) by FIBROSIS stage   [ruler: " + which + "]\n"
                  "each gene z-scored WITHIN ITS OWN F-stage panel -> diagonal at F0 washing out "
                  "toward F4 = de-zonation tracking fibrosis.\n" + READING_KEY),
        outpath=C.fig_path("h2", "b1_heatmap_pattern_fibrosis.png"),
        cbar_label="within-panel z\n(purple = high / pericentral end,\norange = low / periportal end)"))

    # LEVEL view by fibrosis
    fvmin, fvmax = _shared_raw_scale(fraw_mats)
    outs.append(_draw_panels(
        fraw_mats, flabels, order, gene_names,
        cmap="magma", vmin=fvmin, vmax=fvmax,
        suptitle=("B1 LEVEL view (turn-off) by FIBROSIS stage   [ruler: " + which + "]\n"
                  "raw mean expression on a SHARED color scale -> rows fading from F0 -> F4 = "
                  "expression turn-off with fibrosis.\n" + READING_KEY),
        outpath=C.fig_path("h2", "b1_heatmap_level_fibrosis.png"),
        cbar_label="mean expression\n(log1p-CP10k; bright = high)"))

    print("\nB1 done. Figures:")
    for o in outs:
        print("  ", o)
    return outs


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "expanded_curated")
