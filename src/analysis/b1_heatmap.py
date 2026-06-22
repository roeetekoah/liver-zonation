#!/usr/bin/env python3
"""B1 -- the centerpiece H2 figure: gene x (zone-ordered cells) heatmaps showing how the zonation
PATTERN of the signature genes DISSOLVES with MASLD disease.

SCIENTIFIC IDEA: order genes by their HEALTHY zonal slope (most pericentral-rising at top, most
periportal-rising at bottom) and order cells by zonation coordinate (LEFT=periportal, RIGHT=
pericentral). In healthy tissue this yields a clean diagonal "staircase" of banding. With disease
the banding should wash out. We render TWO complementary versions so the two mechanisms separate:

  (1) per-gene Z-SCORED expression (z-scored against the HEALTHY reference, shared scale, cmap PuOr,
      vmin/vmax symmetric): isolates PATTERN loss (de-zonation), independent of overall level.
  (2) library-normalized RAW expression on a SHARED color scale across panels (cmap magma): a fading
      panel = LEVEL loss (turn-off).

PSEUDOBULK / UNIT NOTE (descriptive figure): within each group we bin the coordinate into 50
quantile bins and average cells per bin -> a (genes x 50) pseudobulk matrix. The unit here is the
CELL (bins aggregate cells, not donors). That is acceptable for a *visualization*; the donor-level
statistics live in the H2 tests elsewhere. This figure is meant to be SEEN, not tested.

The GENE ORDER is computed ONCE on Healthy-control cells and REUSED for every panel, so you can
literally watch the same ordering go from a crisp diagonal to noise as disease advances.

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
Z_LIM = 2.0               # symmetric vmin/vmax for the z-scored panels
# marker rows to label on the y-axis (whichever are present)
MARKER_ROWS = ["GLUL", "CYP2E1", "CYP1A2", "CYP3A4", "ASS1", "ALDOB", "PCK1", "HAL", "ARG1"]


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
    b = pd.cut(coord, bins=edges, labels=False, include_lowest=True)
    n_genes = G.shape[1]
    out = np.full((n_genes, nbins), np.nan, dtype=float)
    for j in range(nbins):
        m = (b == j)
        if int(m.sum()) >= MIN_CELLS_PER_BIN:
            out[:, j] = np.nanmean(G[m.values if hasattr(m, "values") else m], axis=0)
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
    use), so z-scoring is on the same footing as what is plotted. Returns (mu[g], sd[g])."""
    pb = _binned_pseudobulk(coord_h, G_h, edges_ref, N_CELL_BINS)   # genes x N_CELL_BINS
    mu = np.nanmean(pb, axis=1)
    sd = np.nanstd(pb, axis=1)
    sd = np.where((sd > 1e-9) & np.isfinite(sd), sd, 1.0)
    mu = np.where(np.isfinite(mu), mu, 0.0)
    return mu, sd


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


# ------------------------------------------------------------------ plotting
def _draw_panels(mats, labels, order, gene_names, *, cmap, vmin, vmax, norm_kind,
                 suptitle, outpath, cbar_label):
    """mats = list of (genes x N_CELL_BINS) arrays (already in plot order), one per group level."""
    n = len(mats)
    fig_w = max(7.5, 2.05 * n + 1.6)
    fig, axes = plt.subplots(1, n, figsize=(fig_w, 6.6), squeeze=False,
                             gridspec_kw=dict(wspace=0.08))
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
        ax.set_xlabel("zonation coord", fontsize=7.5, family="serif", color=C.MUTED)
        if k == 0:
            ax.set_yticks([r for _, r in marker_rows])
            ax.set_yticklabels([g for g, _ in marker_rows], fontsize=7.5, family="serif")
            ax.set_ylabel("signature genes\n(pericentral-rising  ->  periportal-rising)",
                          fontsize=8.5, family="serif")
        else:
            ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color(C.RULE)

    cbar = fig.colorbar(im, ax=list(axes), fraction=0.025, pad=0.012)
    cbar.set_label(cbar_label, fontsize=8.5, family="serif")
    cbar.ax.tick_params(labelsize=7)

    fig.suptitle(suptitle, fontsize=10.5, family="serif", y=0.985)
    fig.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("wrote", outpath)
    return outpath


def _build_matrices(coords, G, order, axis, ref_mu, ref_sd, ref_edges):
    """For each group level along `axis`, compute the (genes x N_CELL_BINS) pseudobulk in shared gene
    order. Returns (labels, raw_mats, z_mats). raw_mats use each group's OWN quantile bins of coord;
    z_mats subtract/divide the HEALTHY reference mean/SD per gene."""
    levels = _group_levels(coords, axis)
    labels, raw_mats, z_mats = [], [], []
    for lab, m in levels:
        sub_coord = coords.loc[m, "coord"].values
        sub_G = G[m]                                   # cells x genes (group subset)
        edges = _quantile_edges(sub_coord, N_CELL_BINS)
        pb = _binned_pseudobulk(coords.loc[m, "coord"], sub_G, edges, N_CELL_BINS)  # genes x bins
        pb = pb[order]                                 # reorder rows to shared gene order
        raw_mats.append(pb)
        z = (pb - ref_mu[order][:, None]) / ref_sd[order][:, None]
        z_mats.append(z)
        labels.append(lab)
    return labels, raw_mats, z_mats


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
    ref_mu, ref_sd = _healthy_ref_stats(coords.loc[h_mask, "coord"], G_h, ref_edges)
    print(f"Healthy reference: {int(h_mask.sum())} cells; gene order fixed by healthy zonal slope.")
    print("  top (pericentral-rising):", ", ".join(gene_names[order][:5]))
    print("  bottom (periportal-rising):", ", ".join(gene_names[order][-5:]))

    outs = []

    # ============ STAGE panels ============
    labels, raw_mats, z_mats = _build_matrices(coords, G, order, "stage",
                                               ref_mu, ref_sd, ref_edges)

    # (1) z-scored by stage
    outs.append(_draw_panels(
        z_mats, labels, order, gene_names, cmap="PuOr", vmin=-Z_LIM, vmax=Z_LIM, norm_kind="z",
        suptitle=("B1  de-zonation: per-gene expression Z-SCORED to the HEALTHY reference   "
                  f"[ruler: {which}]\n"
                  "rows = signature genes (fixed HEALTHY zonal-slope order, pericentral-rising top -> "
                  "periportal-rising bottom);  cols = zonation-coord bins (LEFT=periportal -> "
                  "RIGHT=pericentral).\nclean diagonal banding in Healthy that WASHES OUT with disease "
                  "= loss of zonal pattern (de-zonation), independent of level.  "
                  "(descriptive pseudobulk: cells, not donors, are the unit)"),
        outpath=C.fig_path("h2", "b1_heatmap_zscored_stage.png"),
        cbar_label="z vs Healthy\n(per gene)"))

    # shared raw scale across stage panels (robust percentiles over finite values)
    raw_all = np.concatenate([m[np.isfinite(m)] for m in raw_mats]) if raw_mats else np.array([0.0])
    rvmin = float(np.nanpercentile(raw_all, 1))
    rvmax = float(np.nanpercentile(raw_all, 99))
    if not (rvmax > rvmin):
        rvmin, rvmax = float(np.nanmin(raw_all)), float(np.nanmax(raw_all) + 1e-6)

    # (2) raw by stage, shared scale
    outs.append(_draw_panels(
        raw_mats, labels, order, gene_names, cmap="magma", vmin=rvmin, vmax=rvmax, norm_kind="raw",
        suptitle=("B1  turn-off: library-normalized RAW expression on a SHARED color scale   "
                  f"[ruler: {which}]\n"
                  "same gene order & layout as the z-scored figure;  cols = zonation-coord bins "
                  "(LEFT=periportal -> RIGHT=pericentral).\na whole panel FADING toward dark = loss of "
                  "expression LEVEL (turn-off); top (pericentral) rows are expected to fade most.  "
                  "(descriptive pseudobulk: cells, not donors, are the unit)"),
        outpath=C.fig_path("h2", "b1_heatmap_raw_stage.png"),
        cbar_label="mean raw expr\n(log1p-CP10k)"))

    # ============ FIBROSIS panels ============
    flabels, fraw_mats, fz_mats = _build_matrices(coords, G, order, "fibrosis",
                                                  ref_mu, ref_sd, ref_edges)

    # (3) z-scored by fibrosis
    outs.append(_draw_panels(
        fz_mats, flabels, order, gene_names, cmap="PuOr", vmin=-Z_LIM, vmax=Z_LIM, norm_kind="z",
        suptitle=("B1  de-zonation by fibrosis stage: per-gene Z-SCORED to the HEALTHY reference   "
                  f"[ruler: {which}]\n"
                  "rows = signature genes (fixed HEALTHY zonal-slope order);  cols = zonation-coord "
                  "bins (LEFT=periportal -> RIGHT=pericentral).\ndiagonal banding at F0 washing out "
                  "toward F4 = de-zonation tracking fibrosis.  "
                  "(descriptive pseudobulk: cells, not donors, are the unit)"),
        outpath=C.fig_path("h2", "b1_heatmap_zscored_fibrosis.png"),
        cbar_label="z vs Healthy\n(per gene)"))

    # (4) raw by fibrosis (cheap -- same shared-scale logic)
    fraw_all = (np.concatenate([m[np.isfinite(m)] for m in fraw_mats])
                if fraw_mats else np.array([0.0]))
    fvmin = float(np.nanpercentile(fraw_all, 1))
    fvmax = float(np.nanpercentile(fraw_all, 99))
    if not (fvmax > fvmin):
        fvmin, fvmax = float(np.nanmin(fraw_all)), float(np.nanmax(fraw_all) + 1e-6)
    outs.append(_draw_panels(
        fraw_mats, flabels, order, gene_names, cmap="magma", vmin=fvmin, vmax=fvmax, norm_kind="raw",
        suptitle=("B1  turn-off by fibrosis stage: library-normalized RAW expression, SHARED scale   "
                  f"[ruler: {which}]\n"
                  "same gene order & layout;  cols = zonation-coord bins (LEFT=periportal -> "
                  "RIGHT=pericentral).\npanels fading toward dark from F0 -> F4 = expression turn-off "
                  "with fibrosis.  (descriptive pseudobulk: cells, not donors, are the unit)"),
        outpath=C.fig_path("h2", "b1_heatmap_raw_fibrosis.png"),
        cbar_label="mean raw expr\n(log1p-CP10k)"))

    print("\nB1 done. Figures:")
    for o in outs:
        print("  ", o)
    return outs


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "expanded_curated")
