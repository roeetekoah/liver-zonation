"""C3 — LEVEL vs SLOPE, per signature gene (the last confounder control, splitting the two H2
mechanisms gene-by-gene).

H2 says zonation reorganizes across MASLD: a dominant PERICENTRAL TURN-OFF plus PERIPORTAL
DE-ZONATION. But "de-zonation" read off a flattened gradient is ambiguous — a gene whose
spatial gradient goes flat could either (a) have genuinely LOST its spatial restriction while
still being expressed at the same average level (true de-zonation), or (b) simply have been
switched OFF, so there is nothing left to be zonated (turn-off). A naive gradient test cannot
tell these apart, and reading a mere level drop as de-zonation would over-claim.

C3 disentangles them PER GENE by separating two quantities:

  LEVEL = the gene's mean raw expression in a stage (donor-then-stage mean of log1p-CP10k).
          A drop toward 0 = the gene going silent.
  SLOPE = the gene's ZONAL GRADIENT in a stage = OLS slope of (mean raw expression per ~10
          zonation-coordinate bins) vs bin index. |SLOPE| is how steeply the gene is spatially
          restricted; |SLOPE| -> 0 = flattened = lost spatial restriction.

Per gene we take Healthy -> End-stage deltas:
  dLevel    = level_end - level_healthy
  dSlopeMag = |slope_end| - |slope_healthy|      (negative = the gradient flattened)
Slopes are sign-aligned to each gene's HEALTHY direction first, so "flattening" is comparable
for pericentral (negative healthy slope vs coord) and periportal (positive) genes alike.

The 2-D picture (dLevel x dSlopeMag) reads as quadrants:
  bottom-LEFT  (lost level AND flattened) ............ TURN-OFF  (went silent)
  bottom-RIGHT / top-LEFT (flattened, level kept) .... DE-ZONATION (lost spatial restriction)
  near origin .......................................... STABLE

Transparent call (no black box), thresholds stated below:
  FLAT_FRAC = 0.40   -> "flattened" if |slope| dropped by >= 40% of its healthy magnitude.
  LEVEL_FRAC = 0.25  -> "level lost" if level dropped by >= 25% of its healthy level.
    flattened & level lost  -> turn_off
    flattened & level kept   -> de_zonation
    not flattened            -> stable

Run:  python src/analysis/c3_level_vs_slope.py [signature_set]   (default expanded_curated)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # src/
from analysis import common as C
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "serif", "font.size": 9, "axes.linewidth": 0.6,
    "savefig.dpi": 130, "figure.dpi": 130,
})

N_BINS = 10           # zonation-coordinate bins per stage for the slope estimate
MIN_CELLS_BIN = 5     # a bin must have >= this many cells to contribute to the slope
MIN_CELLS_STAGE = 80  # a (gene's) stage needs at least this many cells overall to be trusted
FLAT_FRAC = 0.40      # |slope| must drop by >= this fraction of healthy magnitude to be "flattened"
LEVEL_FRAC = 0.25     # level must drop by >= this fraction of healthy level to be "level lost"

HEALTHY = "Healthy control"
END = "end stage"


# ---------------------------------------------------------------- slope helper
def _zonal_slope(coord, expr, n_bins=N_BINS):
    """OLS slope of binned mean expression vs bin index, within one group of cells.

    coord = per-cell zonation coordinate; expr = per-cell raw log1p-CP10k for one gene.
    We bin cells by coord into `n_bins` equal-width bins, take the mean expression in each
    populated bin (>= MIN_CELLS_BIN cells), and regress those bin means on the bin index.
    The slope's SIGN encodes the gene's pole (vs the coord axis); its MAGNITUDE is gradient
    steepness. Returns nan if too few populated bins."""
    coord = np.asarray(coord, float); expr = np.asarray(expr, float)
    m = np.isfinite(coord) & np.isfinite(expr)
    coord, expr = coord[m], expr[m]
    if len(coord) < MIN_CELLS_BIN * 2 or coord.min() == coord.max():
        return np.nan
    edges = np.linspace(coord.min(), coord.max(), n_bins + 1)
    idx = np.clip(np.digitize(coord, edges[1:-1]), 0, n_bins - 1)
    bx, by = [], []
    for b in range(n_bins):
        sel = idx == b
        if sel.sum() >= MIN_CELLS_BIN:
            bx.append(b); by.append(expr[sel].mean())
    if len(bx) < 3:
        return np.nan
    slope = np.polyfit(np.asarray(bx, float), np.asarray(by, float), 1)[0]
    return float(slope)


def _level(coord_df, expr_col):
    """Donor-then-stage mean level: average expression within each donor, then average the
    donor means (so a few large donors don't dominate). Falls back to a plain cell mean if a
    stage has only one donor."""
    per_donor = coord_df.groupby("donor")[expr_col].mean()
    return float(per_donor.mean())


# ---------------------------------------------------------------- per-gene table
def build_table(coords, genes, arm_of, axis_col, healthy_label, end_label):
    """For each gene: LEVEL (donor-then-stage mean) and SLOPE (sign-aligned by healthy direction)
    at the healthy and end levels of `axis_col`, plus deltas and a transparent call.

    axis_col is the staging axis whose `healthy_label`/`end_label` are the two endpoints
    (stage or fibrosis). coords already carries the gene expression columns + 'coord'."""
    rows = []
    for g in genes:
        if g not in coords.columns:
            continue
        sub = coords[["donor", "coord", axis_col, g]].dropna(subset=["coord", g])
        hc = sub[sub[axis_col] == healthy_label]
        ec = sub[sub[axis_col] == end_label]
        if len(hc) < MIN_CELLS_STAGE or len(ec) < MIN_CELLS_STAGE:
            continue
        lvl_h, lvl_e = _level(hc, g), _level(ec, g)
        slp_h_raw = _zonal_slope(hc["coord"].values, hc[g].values)
        slp_e_raw = _zonal_slope(ec["coord"].values, ec[g].values)
        if not (np.isfinite(slp_h_raw) and np.isfinite(slp_e_raw) and np.isfinite(lvl_h)):
            continue
        # sign-align by the gene's HEALTHY slope direction so "flattening" is comparable
        sgn = np.sign(slp_h_raw) if slp_h_raw != 0 else 1.0
        slp_h = sgn * slp_h_raw          # >= 0 after alignment
        slp_e = sgn * slp_e_raw
        dlevel = lvl_e - lvl_h
        dslopemag = abs(slp_e_raw) - abs(slp_h_raw)   # magnitude change (negative = flattened)

        # transparent call
        flattened = (abs(slp_h_raw) > 0) and (abs(slp_e_raw) <= (1 - FLAT_FRAC) * abs(slp_h_raw))
        level_lost = (lvl_h > 0) and (lvl_e <= (1 - LEVEL_FRAC) * lvl_h)
        if flattened and level_lost:
            call = "turn_off"
        elif flattened:
            call = "de_zonation"
        else:
            call = "stable"

        rows.append(dict(
            gene=g, arm=arm_of[g],
            level_healthy=round(lvl_h, 4), level_end=round(lvl_e, 4), dLevel=round(dlevel, 4),
            slope_healthy=round(slp_h, 4), slope_end=round(slp_e, 4),
            dSlopeMag=round(dslopemag, 4), call=call,
            n_healthy=int(len(hc)), n_end=int(len(ec))))
    df = pd.DataFrame(rows)
    return df.sort_values(["arm", "dSlopeMag"]).reset_index(drop=True) if len(df) else df


# ---------------------------------------------------------------- plotting
def _scatter_panel(ax, df, title, label_genes=True):
    """One dLevel x dSlopeMag quadrant scatter, points coloured by arm."""
    ax.axhline(0, color=C.RULE, lw=0.8, zorder=0)
    ax.axvline(0, color=C.RULE, lw=0.8, zorder=0)
    col = {"pericentral": C.TEAL, "periportal": C.RUST}
    for arm, g in df.groupby("arm"):
        ax.scatter(g["dLevel"], g["dSlopeMag"], c=col.get(arm, C.INK), s=46,
                   edgecolor="white", linewidths=0.5, zorder=3, label=arm)
    if label_genes and len(df):
        # label the notable ones: strongest flatteners + strongest level drops
        notable = set(df.nsmallest(5, "dSlopeMag")["gene"]) | set(df.nsmallest(4, "dLevel")["gene"])
        for _, r in df[df["gene"].isin(notable)].iterrows():
            ax.annotate(r["gene"], (r["dLevel"], r["dSlopeMag"]), fontsize=6.5,
                        xytext=(3, 3), textcoords="offset points", color=C.INK, alpha=0.85)
    ax.set_xlabel("change in LEVEL  (Healthy -> End-stage)")
    ax.set_ylabel("change in |SLOPE|   (< 0 = flattened)")
    ax.set_title(title, fontsize=10.5, fontweight="bold")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def make_figure(df_stage, df_fib, out):
    has_fib = df_fib is not None and len(df_fib)
    if has_fib:
        fig, axes = plt.subplots(1, 2, figsize=(12.4, 5.8))
        ax0, ax1 = axes
    else:
        fig, ax0 = plt.subplots(figsize=(7.2, 6.0))
        ax1 = None

    _scatter_panel(ax0, df_stage, "C3  Level vs slope per gene  (stage: Healthy -> End-stage)")
    # quadrant guide text in the panel corners
    ax0.text(0.02, 0.02, "TURN-OFF\nlost level + flattened", transform=ax0.transAxes,
             fontsize=7.2, va="bottom", ha="left", color=C.MUTED, style="italic")
    ax0.text(0.98, 0.02, "DE-ZONATION\nflattened, level kept", transform=ax0.transAxes,
             fontsize=7.2, va="bottom", ha="right", color=C.MUTED, style="italic")
    ax0.legend(fontsize=8, frameon=False, loc="upper left")

    if has_fib:
        _scatter_panel(ax1, df_fib, "C3  Level vs slope per gene  (fibrosis: F0 -> F4)")
        ax1.legend(fontsize=8, frameon=False, loc="upper left")

    cap = ("Each point = one signature gene. x = change in mean LEVEL, y = change in zonal "
           "gradient magnitude |SLOPE| (slope of binned expression vs zonation coordinate), "
           "Healthy->End-stage.\nQuadrants:  BOTTOM-LEFT = lost level AND slope = TURN-OFF (gene "
           "went silent).  BOTTOM-RIGHT / TOP-LEFT = slope lost but level kept = DE-ZONATION "
           "(real loss of spatial restriction).  Near origin = stable.\n"
           "teal = pericentral, rust = periportal. Slopes sign-aligned to each gene's healthy pole.")
    fig.text(0.5, 0.005, cap, ha="center", va="bottom", fontsize=7.3, color=C.MUTED)
    fig.subplots_adjust(left=0.08, right=0.98, top=0.93, bottom=0.20 if not has_fib else 0.17,
                        wspace=0.22)
    fig.savefig(out)
    plt.close(fig)
    return out


# ---------------------------------------------------------------- driver
WHICH = C.DEFAULT_SET


def main():
    global WHICH
    WHICH = sys.argv[1] if len(sys.argv) > 1 else C.DEFAULT_SET
    print(f"[C3 level vs slope] set = {WHICH}")

    coords = C.load_coords(which=WHICH)
    pcg, ppg = C.gene_lists(WHICH)
    genes = list(pcg) + list(ppg)
    arm_of = {g: "pericentral" for g in pcg}
    arm_of.update({g: "periportal" for g in ppg})

    # attach raw expression (one column per gene) on cell_id
    expr = C.raw_gene_matrix(genes)
    present = [g for g in genes if g in expr.columns]
    print(f"  genes present: {len(present)}/{len(genes)}  (pc {sum(g in pcg for g in present)}, "
          f"pp {sum(g in ppg for g in present)})")
    coords = coords.merge(expr, on="cell_id", how="left")

    # ---- stage axis (Healthy -> End-stage) ----
    df_stage = build_table(coords, present, arm_of, "stage", HEALTHY, END)

    # ---- fibrosis axis (F0 -> F4), if both endpoints present ----
    df_fib = None
    cl = C.attach_clinical(coords)[["cell_id", "fibrosis"]]
    coords_f = coords.merge(cl, on="cell_id", how="left")
    have = set(coords_f["fibrosis"].dropna().unique())
    if 0 in have and 4 in have:
        df_fib = build_table(coords_f, present, arm_of, "fibrosis", 0, 4)

    out_csv = C.table_path("c3_gene_level_slope.csv")
    df_stage.to_csv(out_csv, index=False)

    out_fig = make_figure(df_stage, df_fib, C.fig_path("confounders", "c3_level_vs_slope.png"))

    # ---- console summary ----
    print(f"\n=== outputs ===")
    print(f"[{'OK' if os.path.exists(out_fig) else 'MISSING'}] fig: {out_fig}")
    print(f"[{'OK' if os.path.exists(out_csv) else 'MISSING'}] csv: {out_csv}")

    if len(df_stage):
        print("\n=== stage call counts by arm ===")
        print(pd.crosstab(df_stage["arm"], df_stage["call"]).to_string())
        print("\n=== strongest flatteners (most negative dSlopeMag) ===")
        cols = ["gene", "arm", "dLevel", "dSlopeMag", "call"]
        print(df_stage.nsmallest(8, "dSlopeMag")[cols].to_string(index=False))
        print("\n=== biggest level drops (most negative dLevel) ===")
        print(df_stage.nsmallest(8, "dLevel")[cols].to_string(index=False))
    else:
        print("  (no genes passed the cell-count thresholds)")


if __name__ == "__main__":
    main()
