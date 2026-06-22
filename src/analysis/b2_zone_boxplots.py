"""B2: Zone x program expression boxplots across donors, faceted by disease stage and fibrosis.

Scientific question
-------------------
Split cells into three zones by zonation coordinate -- pericentral (PC), mid, periportal (PP) --
and show, as boxplots across donors, the expression LEVEL of the pericentral program and the
periportal program in each zone. Does the PERICENTRAL program lose its expression specifically in
the PERICENTRAL zone as disease advances (turn-off), while the periportal program holds level (but
perhaps de-zonates -- i.e. loses zone-specificity rather than level)?

Method (donor = unit of analysis; no cell pseudoreplication)
-----------------------------------------------------------
1. Load coords (which signature set, default expanded_curated); merge per-cell pc_raw/pp_raw from
   raw_arm_means (UN-standardized mean log1p-CP10k LEVEL over each program). Attach fibrosis.
2. Define zones by GLOBAL coordinate terciles across all cells. CONVENTION: HIGH coordinate =
   pericentral. So the TOP tercile -> PC zone, middle tercile -> mid, BOTTOM tercile -> PP zone.
3. For each (donor, axis-level, zone): mean pc_raw and mean pp_raw -> per-donor zone-level values.
   Boxplots are taken ACROSS DONORS within each (axis-level, zone). Individual donor points are
   drawn jittered over the boxes.

Outputs
-------
  * fig_path("h2","b2_zone_program_boxplots_stage.png")     -- panels = disease stage
  * fig_path("h2","b2_zone_program_boxplots_fibrosis.png")  -- panels = fibrosis F0..F4
  * table_path("zone_program_levels.csv")                   -- (axis, level, zone, program,
                                                               n_donors, median, q25, q75)
Colors: teal = pericentral program, rust = periportal program (consistent project palette).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # src/ on path
from analysis import common as C
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

ZONES = ["PC", "mid", "PP"]          # display order, pericentral -> periportal
ZONE_FULL = {"PC": "Pericentral", "mid": "Mid", "PP": "Periportal"}


# ---------------------------------------------------------------- data assembly
def assign_zones(coord):
    """Tercile zone labels for a coordinate Series. HIGH coordinate = pericentral (top tercile)."""
    q1, q2 = np.quantile(coord, [1.0 / 3.0, 2.0 / 3.0])
    z = np.where(coord >= q2, "PC", np.where(coord >= q1, "mid", "PP"))
    return pd.Series(z, index=coord.index)


def build_cell_table(which):
    """Per-cell DataFrame: donor, stage, fibrosis, coord, zone, pc_raw, pp_raw."""
    coords = C.load_coords(which)
    pcg, ppg = C.gene_lists(which)
    raw = C.raw_arm_means(pcg, ppg)                       # cell_id, pc_raw, pp_raw
    df = coords.merge(raw, on="cell_id", how="left")
    df = C.attach_clinical(df)                            # adds fibrosis (+ others)
    df = df[df["pc_raw"].notna() & df["pp_raw"].notna()].reset_index(drop=True)
    df["zone"] = assign_zones(df["coord"])
    return df


def donor_zone_means(df, axis):
    """Per (donor, level, zone) mean program LEVEL.

    Returns long DataFrame: donor, level (display label), zone, pc_raw, pp_raw, and the ordered
    list of level labels for paneling.
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
    g = (df.groupby(["donor", "level", "zone"], observed=True)[["pc_raw", "pp_raw"]]
           .mean().reset_index())
    return g, order


# ---------------------------------------------------------------- plotting
def _box_series(ax, data, center, color, width=0.30):
    """One box (+ jittered donor points) at x=center. data = 1D array of per-donor values."""
    data = np.asarray(data, float)
    data = data[np.isfinite(data)]
    if len(data) == 0:
        return
    bp = ax.boxplot([data], positions=[center], widths=width, patch_artist=True,
                    showfliers=False, manage_ticks=False)
    for patch in bp["boxes"]:
        patch.set_facecolor(color); patch.set_alpha(0.35); patch.set_edgecolor(color)
    for key in ("whiskers", "caps", "medians"):
        for ln in bp[key]:
            ln.set_color(color); ln.set_linewidth(1.4)
    jit = (np.random.RandomState(0).rand(len(data)) - 0.5) * width * 0.8
    ax.scatter(center + jit, data, s=14, color=color, edgecolor="white",
               linewidth=0.4, zorder=3, alpha=0.9)


def make_figure(long_df, order, axis, out_png):
    n = len(order)
    fig, axes = plt.subplots(1, n, figsize=(3.0 * n + 1.0, 4.6), sharey=True, squeeze=False)
    axes = axes[0]
    # symmetric pair of boxes per zone: teal (PC program) left, rust (PP program) right
    base = {z: i for i, z in enumerate(ZONES)}
    off = 0.18
    for ax, level in zip(axes, order):
        sub = long_df[long_df["level"] == level]
        for z in ZONES:
            zd = sub[sub["zone"] == z]
            cx = base[z]
            _box_series(ax, zd["pc_raw"].values, cx - off, C.TEAL)
            _box_series(ax, zd["pp_raw"].values, cx + off, C.RUST)
        ax.set_xticks([base[z] for z in ZONES])
        ax.set_xticklabels([ZONE_FULL[z] for z in ZONES])
        ax.set_xlim(-0.6, len(ZONES) - 0.4)
        n_don = sub["donor"].nunique()
        ax.set_title(f"{level}\n(n={n_don} donors)", fontsize=10)
        ax.grid(axis="y", color=C.RULE, linewidth=0.6, alpha=0.7)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("Program expression level\n(mean log1p-CP10k over arm genes)")
    handles = [plt.Line2D([0], [0], marker="s", color="none", markerfacecolor=C.TEAL,
                          markeredgecolor=C.TEAL, markersize=10, alpha=0.6,
                          label="Pericentral program"),
               plt.Line2D([0], [0], marker="s", color="none", markerfacecolor=C.RUST,
                          markeredgecolor=C.RUST, markersize=10, alpha=0.6,
                          label="Periportal program")]
    fig.legend(handles=handles, loc="upper center", ncol=2, frameon=False,
               bbox_to_anchor=(0.5, 1.005), fontsize=10)
    axlabel = "disease stage" if axis == "stage" else "fibrosis stage"
    fig.suptitle(f"Zone-resolved program expression across donors, by {axlabel}\n"
                 "(zones = global coordinate terciles; high coord = pericentral)",
                 y=1.10, fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    fig.savefig(out_png, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_png


# ---------------------------------------------------------------- table
def build_table(long_df, axis, order):
    rows = []
    for level in order:
        sub = long_df[long_df["level"] == level]
        for z in ZONES:
            zd = sub[sub["zone"] == z]
            for prog, col in (("PC", "pc_raw"), ("PP", "pp_raw")):
                v = zd[col].dropna().values
                if len(v) == 0:
                    continue
                rows.append(dict(axis=axis, level=level, zone=z, program=prog,
                                 n_donors=int(len(v)),
                                 median=float(np.median(v)),
                                 q25=float(np.percentile(v, 25)),
                                 q75=float(np.percentile(v, 75))))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- main
def main(which=C.DEFAULT_SET):
    df = build_cell_table(which)

    stage_long, stage_order = donor_zone_means(df, "stage")
    fib_long, fib_order = donor_zone_means(df, "fibrosis")

    p_stage = make_figure(stage_long, stage_order, "stage",
                          C.fig_path("h2", "b2_zone_program_boxplots_stage.png"))
    p_fib = make_figure(fib_long, fib_order, "fibrosis",
                        C.fig_path("h2", "b2_zone_program_boxplots_fibrosis.png"))

    tbl = pd.concat([build_table(stage_long, "stage", stage_order),
                     build_table(fib_long, "fibrosis", fib_order)], ignore_index=True)
    p_tbl = C.table_path("zone_program_levels.csv")
    tbl.to_csv(p_tbl, index=False)

    print("wrote:", p_stage)
    print("wrote:", p_fib)
    print("wrote:", p_tbl)
    print(f"cells used: {len(df):,}  donors: {df['donor'].nunique()}  set: {which}")
    return p_stage, p_fib, p_tbl


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else C.DEFAULT_SET
    main(which)
