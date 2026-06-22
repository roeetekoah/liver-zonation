"""E -- interpret the LEARNED PCA ruler (label-free co-primary axis).

The professor's question: what did the unsupervised PCA actually pick? We reconstruct the
PCA on Paper-1 HEALTHY hepatocytes (self-contained, label-free) and answer:
  (1) how much variance each PC explains (scree),
  (2) WHICH PC is the zonation axis and how strongly it aligns with KNOWN markers
      (pericentral GLUL/CYP2E1/... minus periportal ASS1/ALDOB/...) and the curated coord,
  (3) the top genes loading on that zonation PC -- do they read as real PC/PP biology?
  (4) what the OTHER leading PCs capture -- is PC1 zonation, or a technical/quality factor
      (sequencing depth, genes-detected)?

Run:  python src/analysis/e_pca_interpretation.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # src/
from analysis import common as C
import numpy as np, pandas as pd
from scipy.stats import spearmanr
from sklearn.decomposition import PCA
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

SEED = 0
N_PC = 20
N_HVG = 2000
MIN_FRAC = 0.05                          # gene expressed in >=5% of all cells
PC_MARKERS = ["GLUL", "CYP2E1", "CYP1A2", "CYP3A4", "ADH4", "SLCO1B3"]   # pericentral pole
PP_MARKERS = ["ASS1", "ALDOB", "PCK1", "HAL", "ASL", "ARG1"]            # periportal pole
CANON = set(PC_MARKERS) | set(PP_MARKERS)


def _build_z(M, genes, lib):
    """Return (Z cells x HVG z-scored from log1p-CP10k, hvg_gene_names, genes_detected_per_cell).

    Feature selection: keep genes expressed in >=5% of all cells, then top ~2000 by variance of
    log1p-CP10k. Z is z-scored per gene across ALL cells; PCA is then FIT on the healthy subset.
    Memory-safe: densify only the ~2000 HVG block.
    """
    M = M.tocsr()
    ncell = M.shape[1]
    # genes-detected per cell (nonzero genes) -- a technical/quality covariate
    genes_detected = np.asarray((M > 0).sum(0)).ravel().astype(float)
    # expressed fraction per gene
    frac = np.asarray((M > 0).sum(1)).ravel().astype(float) / ncell
    keep = np.where(frac >= MIN_FRAC)[0]
    inv_lib = (1.0 / lib)[None, :]
    sub = M[keep].tocsr().astype(np.float64)
    sub = sub.multiply(inv_lib).multiply(1e4).tocsr()       # CP10k
    sub.data = np.log1p(sub.data)                           # log1p-CP10k (sparse, zeros stay 0)
    D = np.asarray(sub.todense()).T                         # cells x kept-genes (dense)
    var = D.var(axis=0)
    order = np.argsort(var)[::-1][:N_HVG]
    hvg_idx = keep[order]
    X = D[:, order]                                         # cells x HVG, log1p-CP10k
    mu = X.mean(axis=0); sd = X.std(axis=0); sd[sd == 0] = 1.0
    Z = (X - mu) / sd                                       # z-scored per gene across all cells
    return Z, genes[hvg_idx], genes_detected


def _marker_axis(M, genes, lib):
    """Per-cell marker axis = mean z(pericentral markers) - mean z(periportal markers).

    Recomputed from raw log1p-CP10k (per-gene z across all cells), independent of the HVG block.
    """
    allmk = [g for g in (PC_MARKERS + PP_MARKERS) if g in set(genes)]
    R = C.raw_gene_matrix(allmk)                            # cells x markers, log1p-CP10k, indexed by cell_id
    Z = (R - R.mean(axis=0)) / (R.std(axis=0) + 1e-9)
    pc = Z[[g for g in PC_MARKERS if g in Z.columns]].mean(axis=1)
    pp = Z[[g for g in PP_MARKERS if g in Z.columns]].mean(axis=1)
    return (pc - pp)                                        # Series indexed by cell_id


def _absnan(a, b):
    """|Spearman| handling constant inputs."""
    a = np.asarray(a, float); b = np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 3 or np.std(a[ok]) == 0 or np.std(b[ok]) == 0:
        return np.nan
    return abs(float(spearmanr(a[ok], b[ok]).statistic))


def main():
    M, genes, bars, lib = C._p1_matrix()
    coords = C.load_coords("expanded_curated")
    cid2coord = dict(zip(coords["cell_id"], coords["coord"]))
    cid2stage = dict(zip(coords["cell_id"], coords["stage"]))

    healthy = np.array([cid2stage.get(b) == "Healthy control" for b in bars])
    print(f"[data] cells={len(bars)}  healthy={int(healthy.sum())}")

    # ---- feature matrix + PCA fit on healthy, projected on all ----
    Z, hvg, genes_detected = _build_z(M, genes, lib)
    print(f"[features] HVG={Z.shape[1]} genes, z-matrix {Z.shape}")
    pca = PCA(n_components=N_PC, random_state=SEED)
    pca.fit(Z[healthy])
    scores = pca.transform(Z)                              # all cells x N_PC
    var_ratio = pca.explained_variance_ratio_

    # ---- covariates ----
    marker = _marker_axis(M, genes, lib).reindex(bars).values   # per-cell marker axis, aligned to bars
    curated = np.array([cid2coord.get(b, np.nan) for b in bars])
    depth = lib.astype(float)

    # restrict the alignment metrics to HEALTHY cells (where the ruler was learned)
    h = healthy
    rows = []
    for k in range(N_PC):
        s = scores[:, k]
        cm = _absnan(s[h], marker[h])
        cc = _absnan(s[h], curated[h])
        cd = _absnan(s[h], depth[h])
        cg = _absnan(s[h], genes_detected[h])
        rows.append(dict(PC=k + 1, variance_ratio=float(var_ratio[k]),
                         abs_corr_marker_axis=cm, abs_corr_curated_coord=cc,
                         abs_corr_depth=cd, abs_corr_genes_detected=cg))
    tab = pd.DataFrame(rows)

    # zonation PC = max |corr with marker axis|
    zpc = int(tab.loc[tab["abs_corr_marker_axis"].idxmax(), "PC"])
    zk = zpc - 1
    # label guess per PC
    def label(r):
        if int(r["PC"]) == zpc:
            return "zonation"
        # depth-like if it tracks depth or genes-detected more than the marker axis (and meaningfully)
        tech = max(r["abs_corr_depth"], r["abs_corr_genes_detected"])
        if tech >= 0.3 and tech > r["abs_corr_marker_axis"]:
            return "depth-like"
        return "other"
    tab["label_guess"] = tab.apply(label, axis=1)
    tab.to_csv(C.table_path("e_pca_components.csv"), index=False)
    print(f"[zonation] PC{zpc}  |corr marker|={tab.loc[zk,'abs_corr_marker_axis']:.3f}  "
          f"|corr curated|={tab.loc[zk,'abs_corr_curated_coord']:.3f}")
    print(tab.to_string(index=False))

    # orient the zonation PC so + = pericentral pole (positive marker axis), for interpretable loadings
    sign = np.sign(spearmanr(scores[h, zk], marker[h]).statistic) or 1.0
    load = pca.components_[zk] * sign                      # loading per HVG gene, oriented
    sc_z = scores[:, zk] * sign

    # ============================== FIGURE 1: scree ==============================
    fig, ax = plt.subplots(figsize=(9, 4.6))
    xs = np.arange(1, N_PC + 1)
    bars_c = [C.TEAL if k != zk else C.RUST for k in range(N_PC)]
    ax.bar(xs, var_ratio * 100, color=bars_c, edgecolor="white", linewidth=0.5)
    ax.set_xticks(xs)
    ax.set_xlabel("Principal component (fit on healthy hepatocytes)")
    ax.set_ylabel("Variance explained (%)")
    ax.set_title("PCA scree -- which PC is the zonation axis?", fontsize=12, color=C.INK)
    top = (var_ratio[zk]) * 100
    ax.annotate(
        f"PC{zpc} = ZONATION axis\n|corr| marker axis = {tab.loc[zk,'abs_corr_marker_axis']:.2f}\n"
        f"|corr| curated coord = {tab.loc[zk,'abs_corr_curated_coord']:.2f}",
        xy=(zpc, top), xytext=(zpc + 2.5, max(top, var_ratio.max()*100*0.55) + var_ratio.max()*100*0.18),
        fontsize=9.5, color=C.RUST,
        arrowprops=dict(arrowstyle="->", color=C.RUST, lw=1.3),
        bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=C.RUST, lw=1.1))
    # annotate PC1's nature (technical?) if it isn't the zonation PC
    if zk != 0:
        r0 = tab.loc[0]
        ax.annotate(f"PC1: |corr depth|={r0['abs_corr_depth']:.2f}, "
                    f"|corr genesdet|={r0['abs_corr_genes_detected']:.2f}",
                    xy=(1, var_ratio[0]*100), xytext=(2.0, var_ratio[0]*100*0.7),
                    fontsize=8.5, color=C.MUTED)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(C.fig_path("staging", "e_pca_scree.png"), dpi=150); plt.close(fig)

    # ============================== FIGURE 2: loadings ==============================
    order = np.argsort(load)
    n_each = 15
    neg_idx = order[:n_each]                               # most negative -> periportal pole
    pos_idx = order[::-1][:n_each]                         # most positive -> pericentral pole
    sel = np.concatenate([neg_idx[::-1], pos_idx[::-1]])   # bottom->top: most -, ... , most +
    vals = load[sel]; names = hvg[sel]
    colors = ["#5e3c99" if v >= 0 else "#e66101" for v in vals]   # purple=+/PC, orange=-/PP
    fig, ax = plt.subplots(figsize=(8.4, 9.5))
    y = np.arange(len(sel))
    ax.barh(y, vals, color=colors, edgecolor="white", linewidth=0.4)
    ax.set_yticks(y)
    labels = [(f"$\\bf{{{g}}}$*" if g in CANON else g) for g in names]
    ax.set_yticklabels(labels, fontsize=8.5)
    ax.axvline(0, color=C.INK, lw=0.8)
    ax.set_xlabel(f"Loading on PC{zpc} (oriented: + = pericentral pole)")
    ax.set_title(f"Top genes on the learned zonation axis (PC{zpc})\n"
                 f"purple = pericentral (+),  orange = periportal (-);  * = canonical marker",
                 fontsize=11, color=C.INK)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(C.fig_path("staging", "e_pca_loadings.png"), dpi=150); plt.close(fig)

    # ============================== FIGURE 3: PC1 vs PC2 map ==============================
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.4))
    finite = np.isfinite(curated)
    # (a) colored by curated zonation coordinate
    sca = axes[0].scatter(scores[finite, 0], scores[finite, 1], c=curated[finite],
                          cmap="PuOr", s=4, alpha=0.6, linewidths=0,
                          vmin=np.nanpercentile(curated, 2), vmax=np.nanpercentile(curated, 98))
    axes[0].set_title(f"PC1 vs PC2 -- colored by curated zonation coord\n"
                      f"(zonation axis = PC{zpc})", fontsize=10.5, color=C.INK)
    plt.colorbar(sca, ax=axes[0], shrink=0.85, label="curated coord (PC<->PP)")
    # (b) colored by depth
    dd = np.log10(depth)
    scb = axes[1].scatter(scores[:, 0], scores[:, 1], c=dd, cmap="viridis",
                          s=4, alpha=0.6, linewidths=0,
                          vmin=np.percentile(dd, 2), vmax=np.percentile(dd, 98))
    axes[1].set_title("PC1 vs PC2 -- colored by sequencing depth (log10 total counts)",
                      fontsize=10.5, color=C.INK)
    plt.colorbar(scb, ax=axes[1], shrink=0.85, label="log10 depth")
    for ax in axes:
        ax.set_xlabel("PC1"); ax.set_ylabel("PC2")
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Is the dominant axis biology or a quality factor?", fontsize=12, color=C.INK)
    fig.tight_layout(); fig.savefig(C.fig_path("staging", "e_pca_pc12_map.png"), dpi=150); plt.close(fig)

    print("[figs]",
          C.fig_path("staging", "e_pca_scree.png"),
          C.fig_path("staging", "e_pca_loadings.png"),
          C.fig_path("staging", "e_pca_pc12_map.png"), sep="\n  ")
    print("[table]", C.table_path("e_pca_components.csv"))

    # quick console interpretation
    pos_names = hvg[pos_idx][:8].tolist()
    neg_names = hvg[neg_idx][:8].tolist()
    print(f"[interp] PC{zpc} + pole (pericentral) top: {pos_names}")
    print(f"[interp] PC{zpc} - pole (periportal) top: {neg_names}")
    return tab, zpc


if __name__ == "__main__":
    main()
