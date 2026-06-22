"""B3: Program-level zonation GRADIENT -- raw expression of the pericentral program and of the
periportal program as smooth curves vs the zonation coordinate, ONE LINE PER DISEASE STAGE (and a
second figure per fibrosis level).

Scientific question
-------------------
This is the smooth program-level companion to the per-gene heatmap (B1) and the per-zone boxplots
(B2). Instead of three coarse zones, we trace each program's expression LEVEL continuously along the
coordinate. In healthy tissue the pericentral program should RISE steeply along the coordinate
(left=periportal -> right=pericentral) and the periportal program FALL steeply. With disease these
gradients should FLATTEN. Two distinct phenomena to separate:
  * turn-OFF   = the curve drops in overall LEVEL (program expression heads toward 0).
  * de-zonation = the curve FLATTENS (loses its slope/zone-specificity) without necessarily
                  dropping in mean level.

Method (donor = unit of analysis; no cell pseudoreplication)
-----------------------------------------------------------
1. Load coords (signature set, default expanded_curated); merge per-cell pc_raw/pp_raw from
   raw_arm_means (UN-standardized mean log1p-CP10k LEVEL over each program). Attach fibrosis.
2. CONVENTION (matches B1/B2): HIGH coordinate = pericentral. We bin the coordinate into ~15
   GLOBAL quantile bins (left = periportal, right = pericentral).
3. For each (donor, bin): mean pc_raw and mean pp_raw. Then AVERAGE ACROSS DONORS within each stage
   (and within each fibrosis level), with a light SEM band across donors.
4. Per (axis, level, program) fit a straight line expr ~ coord_mid (slope = gradient steepness);
   steep slope in Healthy that decays toward 0 with stage/fibrosis = flattening / de-zonation.

Outputs
-------
  * fig_path("h2","b3_program_vs_coord_stage.png")      -- 2 panels (PC | PP), one line per stage
  * fig_path("h2","b3_program_vs_coord_fibrosis.png")   -- 2 panels (PC | PP), one line per F0..F4
  * table_path("program_gradient_by_coord.csv")         -- (axis, level, program, bin, coord_mid,
                                                            mean_expr, sem, n_donors) + fitted slope
Colors: teal = pericentral program, rust = periportal program; lines colored by sequential cmap
(stage = Blues, fibrosis = Reds) so the reader sees Healthy->End-stage / F0->F4 ordering.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # src/ on path
from analysis import common as C
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

N_BINS = 15                  # ~15 quantile bins along the coordinate
PROGRAMS = [("PC", "pc_raw", "Pericentral program", C.TEAL),
            ("PP", "pp_raw", "Periportal program", C.RUST)]


# ---------------------------------------------------------------- data assembly
def build_cell_table(which):
    """Per-cell DataFrame: donor, stage, fibrosis, coord, bin, coord_mid, pc_raw, pp_raw.

    Bins are GLOBAL quantile bins of the coordinate (left=periportal, right=pericentral), so the
    same coordinate position means the same bin across all donors/stages.
    """
    coords = C.load_coords(which)
    pcg, ppg = C.gene_lists(which)
    raw = C.raw_arm_means(pcg, ppg)                       # cell_id, pc_raw, pp_raw
    df = coords.merge(raw, on="cell_id", how="left")
    df = C.attach_clinical(df)                            # adds fibrosis (+ others)
    df = df[df["pc_raw"].notna() & df["pp_raw"].notna() & df["coord"].notna()].reset_index(drop=True)

    # global quantile bins; drop duplicate edges if the coordinate is degenerate at the tails
    edges = np.unique(np.quantile(df["coord"], np.linspace(0, 1, N_BINS + 1)))
    df["bin"] = pd.cut(df["coord"], bins=edges, labels=False, include_lowest=True)
    df = df[df["bin"].notna()].copy()
    df["bin"] = df["bin"].astype(int)
    mids = 0.5 * (edges[:-1] + edges[1:])
    df["coord_mid"] = df["bin"].map(dict(enumerate(mids)))
    return df


def donor_bin_means(df, axis):
    """Per (donor, level, bin) mean program LEVEL.

    Returns long DataFrame: donor, level (display label), bin, coord_mid, pc_raw, pp_raw, and the
    ordered list of level labels for the lines.
    """
    if axis == "stage":
        df = df[df["stage"].isin(C.STAGE_ORDER)].copy()
        df["level"] = df["stage"].map(C.STAGE_SHORT)
        order = [C.STAGE_SHORT[s] for s in C.STAGE_ORDER if (df["stage"] == s).any()]
    elif axis == "fibrosis":
        df = df[df["fibrosis"].isin(C.FIB_ORDER)].copy()
        df["level"] = df["fibrosis"].map(C.FIB_LABEL)
        order = [C.FIB_LABEL[f] for f in C.FIB_ORDER if (df["fibrosis"] == f).any()]
    else:
        raise ValueError(axis)
    g = (df.groupby(["donor", "level", "bin", "coord_mid"], observed=True)[["pc_raw", "pp_raw"]]
           .mean().reset_index())
    return g, order


def aggregate_across_donors(long_df, level, col):
    """Mean +/- SEM ACROSS DONORS for one level/program, per bin. Returns sorted-by-coord arrays."""
    sub = long_df[long_df["level"] == level]
    g = (sub.groupby(["bin", "coord_mid"], observed=True)[col]
           .agg(mean="mean",
                sem=lambda v: (np.std(v, ddof=1) / np.sqrt(len(v))) if len(v) > 1 else 0.0,
                n_donors="count")
           .reset_index()
           .sort_values("coord_mid"))
    return g


def fit_slope(coord_mid, mean_expr):
    """Least-squares slope of mean_expr ~ coord_mid (gradient steepness). NaN if <2 valid points."""
    x = np.asarray(coord_mid, float)
    y = np.asarray(mean_expr, float)
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 2 or np.ptp(x[m]) == 0:
        return np.nan
    return float(np.polyfit(x[m], y[m], 1)[0])


# ---------------------------------------------------------------- plotting
def _line_colors(n, axis):
    cmap = plt.get_cmap("Blues" if axis == "stage" else "Reds")
    # avoid the very pale low end so early levels stay visible
    return [cmap(0.32 + 0.62 * (i / max(n - 1, 1))) for i in range(n)]


def make_figure(long_df, order, axis, out_png):
    colors = _line_colors(len(order), axis)
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 5.4), squeeze=False)
    axes = axes[0]

    slope_lines = {0: [], 1: []}     # per-panel slope annotations
    for pi, (pcode, col, ptitle, _pcolor) in enumerate(PROGRAMS):
        ax = axes[pi]
        for level, color in zip(order, colors):
            g = aggregate_across_donors(long_df, level, col)
            if g.empty:
                continue
            x = g["coord_mid"].values
            y = g["mean"].values
            sem = g["sem"].values
            slope = fit_slope(x, y)
            ax.plot(x, y, "-", color=color, linewidth=2.0, marker="o", markersize=3.5,
                    label=f"{level}  (slope {slope:+.3f})", zorder=3)
            ax.fill_between(x, y - sem, y + sem, color=color, alpha=0.16, linewidth=0, zorder=1)
            slope_lines[pi].append((level, slope))
        ax.set_title(ptitle, fontsize=12, color=_pcolor, fontweight="bold")
        ax.set_xlabel("Zonation coordinate\n(left = periportal  ->  right = pericentral)")
        ax.grid(color=C.RULE, linewidth=0.6, alpha=0.7)
        ax.set_axisbelow(True)
        ax.legend(title=("Disease stage" if axis == "stage" else "Fibrosis"),
                  fontsize=8.5, title_fontsize=9, loc="best", framealpha=0.9)
    axes[0].set_ylabel("Program expression level\n(mean log1p-CP10k over arm genes)")

    axlabel = "disease stage" if axis == "stage" else "fibrosis stage"
    fig.suptitle(f"Program-level zonation gradient vs coordinate, one line per {axlabel}\n"
                 "(per-donor binned means averaged across donors; band = SEM; slope = gradient "
                 "steepness)", y=1.04, fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.99))
    fig.savefig(out_png, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_png


# ---------------------------------------------------------------- table
def build_table(long_df, axis, order):
    rows = []
    for level in order:
        for pcode, col, _t, _c in PROGRAMS:
            g = aggregate_across_donors(long_df, level, col)
            if g.empty:
                continue
            slope = fit_slope(g["coord_mid"].values, g["mean"].values)
            for _, r in g.iterrows():
                rows.append(dict(axis=axis, level=level, program=pcode,
                                 bin=int(r["bin"]), coord_mid=float(r["coord_mid"]),
                                 mean_expr=float(r["mean"]), sem=float(r["sem"]),
                                 n_donors=int(r["n_donors"]), slope=slope))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- main
def main(which=C.DEFAULT_SET):
    df = build_cell_table(which)

    stage_long, stage_order = donor_bin_means(df, "stage")
    fib_long, fib_order = donor_bin_means(df, "fibrosis")

    p_stage = make_figure(stage_long, stage_order, "stage",
                          C.fig_path("h2", "b3_program_vs_coord_stage.png"))
    p_fib = make_figure(fib_long, fib_order, "fibrosis",
                        C.fig_path("h2", "b3_program_vs_coord_fibrosis.png"))

    tbl = pd.concat([build_table(stage_long, "stage", stage_order),
                     build_table(fib_long, "fibrosis", fib_order)], ignore_index=True)
    p_tbl = C.table_path("program_gradient_by_coord.csv")
    tbl.to_csv(p_tbl, index=False)

    print("wrote:", p_stage)
    print("wrote:", p_fib)
    print("wrote:", p_tbl)
    print(f"cells used: {len(df):,}  donors: {df['donor'].nunique()}  bins: {df['bin'].nunique()}"
          f"  set: {which}")
    # quick slope summary to stdout for sanity
    for axis, lng, order in (("stage", stage_long, stage_order), ("fibrosis", fib_long, fib_order)):
        for pcode, col, _t, _c in PROGRAMS:
            ss = [(lv, fit_slope(*[aggregate_across_donors(lng, lv, col)[k].values
                                   for k in ("coord_mid", "mean")])) for lv in order]
            print(f"  {axis:8s} {pcode}: " + "  ".join(f"{lv}={s:+.3f}" for lv, s in ss))
    return p_stage, p_fib, p_tbl


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else C.DEFAULT_SET
    main(which)
