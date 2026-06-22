"""A1 — PC-vs-PP scatter geometry of liver zonation across MASLD progression.

Hepatocytes are zonated along a pericentral<->periportal axis. Each cell carries a
zonation coordinate (coord) and two STANDARDIZED program scores: pc (pericentral) and
pp (periportal). In healthy tissue pc and pp are strongly anti-correlated -> cells lie
on an anti-diagonal cloud. We plot pc (x) vs pp (y) to SEE how that structure changes
with disease and to distinguish three failure modes on the same scatter:

    INTACT zonation        -> strong anti-diagonal cloud (high |anti-corr|, full spread)
    (a) expression TURN-OFF -> cloud collapses toward the low-low corner / origin
    (b) NOISE               -> anti-correlation dissolves into a round blob
    (c) true DE-ZONATION    -> cells pile toward the CENTER of the diagonal (lose the
                               extremes) while keeping the anti-correlation sign

Deliverables (results/figures/h1/):
  1. a1_pcpp_contact_sheet_stage.png      all 47 donors, grid ordered by disease stage
  2. a1_pcpp_contact_sheet_fibrosis.png   all 47 donors, grid ordered by fibrosis F0..F4
  3. a1_pcpp_representatives_stage.png     one large panel per stage vs healthy envelope
  4. a1_pcpp_representatives_fibrosis.png  one large panel per fibrosis level vs healthy

Run:  python src/analysis/a1_scatter.py [signature_set]   (default expanded_curated)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # puts src/ on path
from analysis import common as C
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

# ---- shared aesthetics ----
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 9,
    "axes.linewidth": 0.6,
    "savefig.dpi": 130,
    "figure.dpi": 130,
})
LIM = (-3.0, 4.0)          # fixed equal limits for every PC/PP panel
VMIN, VMAX = -2.5, 2.5     # coord colour range (PuOr centred at 0)

# colour each stage's band so blocks read at a glance in the contact sheets
STAGE_BAND = {
    "Healthy control":      "#2c7a3f",
    "NAFLD":                "#a6a611",
    "NASH w/o cirrhosis":   "#c97a16",
    "NASH with cirrhosis":  "#b03a2e",
    "end stage":            "#6c3483",
}


# ----------------------------------------------------------------------------- helpers
def _frame(ax):
    """Faint x=0 / y=0 guide lines + fixed equal limits + clean frame for a PC/PP panel."""
    ax.axhline(0, color=C.RULE, lw=0.6, zorder=0)
    ax.axvline(0, color=C.RULE, lw=0.6, zorder=0)
    ax.set_xlim(*LIM); ax.set_ylim(*LIM)
    ax.set_aspect("equal", adjustable="box")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def _scatter(ax, sub, s=3, alpha=0.5):
    """pc (x) vs pp (y) coloured by coord (PuOr)."""
    return ax.scatter(sub["pc"], sub["pp"], c=sub["coord"], cmap=C.CMAP,
                      vmin=VMIN, vmax=VMAX, s=s, alpha=alpha, linewidths=0,
                      rasterized=True, zorder=2)


def _anticorr(sub):
    """Pearson r between pc and pp for a cell block (sign = anti-correlation)."""
    if len(sub) < 3 or sub["pc"].std() == 0 or sub["pp"].std() == 0:
        return np.nan
    return float(np.corrcoef(sub["pc"], sub["pp"])[0, 1])


# ----------------------------------------------------------------------------- contact sheets
def _block_color(axis, label, stage_for_label):
    """Band/header colour for a block. By stage we key on the stage name; by fibrosis we
    walk a green->red severity ramp F0..F4."""
    if axis == "stage":
        return STAGE_BAND.get(stage_for_label, C.INK)
    fib_ramp = {"F0": "#2c7a3f", "F1": "#7a9a1f", "F2": "#c9a227",
                "F3": "#c97a16", "F4": "#b03a2e"}
    return fib_ramp.get(label, C.INK)


def contact_sheet(coords, summary, axis, out_path, block_ncol=5):
    """All donors as small PC/PP scatters, grouped into clearly separated BLOCKS by `axis`.

    Each disease-stage (or fibrosis F0..F4) level becomes its own block: a bold coloured
    header band spanning the block width, then a sub-grid of that level's donor panels.
    A thin divider rule + whitespace separates consecutive blocks so the grouping is
    unmistakable. Every panel shows legible per-donor stats (id, n, Spearman r, median
    UMI depth). One shared colorbar lives in its own dedicated axis on the right and never
    overlaps a data panel. Axes are fixed/equal across panels so donors are comparable.
    """
    from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec

    levels = C.staging_levels(summary, axis)
    by_donor = {str(d): sub for d, sub in coords.groupby("donor")}
    srow = summary.set_index("donor")

    # ---- build each block's donor list (keep summary's intra-level ordering) + geometry
    blocks = []   # (label, color, [donors], nrow_in_block)
    for label, donors in levels:
        ds = summary[summary.donor.isin(donors)]["donor"].tolist()
        if not ds:
            continue
        stage_for_label = srow.loc[ds[0], "stage"]
        col = _block_color(axis, label, stage_for_label)
        brow = int(np.ceil(len(ds) / block_ncol))
        blocks.append((label, col, ds, brow))

    n = sum(len(b[2]) for b in blocks)
    # vertical layout: each block contributes 1 header strip + brow panel rows.
    HEADER_H = 0.42          # header strip height in "panel-row" units
    PANEL_H = 1.0
    GAP_H = 0.55             # whitespace between blocks
    block_units = [HEADER_H + b[3] * PANEL_H for b in blocks]
    total_units = sum(block_units) + GAP_H * (len(blocks) - 1)

    # figure size: width from block_ncol; height from total panel-row units
    panel_in = 1.95
    fig_w = block_ncol * panel_in + 1.4          # +room for colorbar/margins
    fig_h = total_units * panel_in * 0.74 + 1.4  # +room for suptitle/key (taller rows)
    fig = plt.figure(figsize=(fig_w, fig_h))

    # outer grid: one row per block-or-gap. We give blocks height ratios in panel-units.
    # interleave gaps as thin spacer rows.
    height_ratios, kind = [], []     # kind: ('block', idx) or ('gap',)
    for bi, bu in enumerate(block_units):
        height_ratios.append(bu); kind.append(("block", bi))
        if bi < len(blocks) - 1:
            height_ratios.append(GAP_H); kind.append(("gap",))

    outer = GridSpec(len(height_ratios), 1, figure=fig,
                     height_ratios=height_ratios,
                     left=0.045, right=0.90, top=0.90, bottom=0.055, hspace=0.0)

    last_pc = None
    for row_idx, k in enumerate(kind):
        if k[0] == "gap":
            # a thin centred divider rule in the spacer row
            gax = fig.add_subplot(outer[row_idx]); gax.axis("off")
            gax.axhline(0.5, color=C.RULE, lw=1.1, xmin=0.01, xmax=0.99)
            continue
        bi = k[1]
        label, col, ds, brow = blocks[bi]
        # split this block's slice into a 1-row header strip + brow x block_ncol panels
        inner = GridSpecFromSubplotSpec(
            1 + brow, block_ncol, subplot_spec=outer[row_idx],
            height_ratios=[HEADER_H] + [PANEL_H] * brow,
            hspace=0.95, wspace=0.32)

        # --- bold header band spanning the block width ---
        hax = fig.add_subplot(inner[0, :]); hax.axis("off")
        hax.add_patch(plt.Rectangle((0.0, 0.18), 1.0, 0.64, transform=hax.transAxes,
                                    facecolor=col, edgecolor="none", alpha=0.16,
                                    clip_on=False))
        head_word = "STAGE" if axis == "stage" else "FIBROSIS"
        hax.text(0.012, 0.5, f"{head_word}: {label}", transform=hax.transAxes,
                 fontsize=12, fontweight="bold", va="center", ha="left", color=col)
        hax.text(0.99, 0.5, f"{len(ds)} donor{'s' if len(ds) != 1 else ''}",
                 transform=hax.transAxes, fontsize=9, va="center", ha="right",
                 color=col, alpha=0.9)
        hax.plot([0.0, 1.0], [0.04, 0.04], transform=hax.transAxes,
                 color=col, lw=2.2, clip_on=False)

        # --- donor panels in this block's sub-grid ---
        for j, donor in enumerate(ds):
            r_, c_ = divmod(j, block_ncol)
            ax = fig.add_subplot(inner[1 + r_, c_])
            sub = by_donor.get(donor)
            last_pc = _scatter(ax, sub, s=4, alpha=0.55)
            _frame(ax)
            meta = srow.loc[donor]
            r = meta["anticorr"]
            rtxt = f"{r:+.2f}" if pd.notna(r) else "n/a"
            depth_k = meta["depth_med"] / 1000.0
            ax.set_title(
                f"donor {donor}  (n={int(meta['n_cells'])})\n"
                f"r={rtxt}, {depth_k:.1f}k UMI",
                fontsize=8, color=C.INK, pad=3, linespacing=1.15)
            ax.tick_params(labelsize=6, length=2)

        # blank out any unused cells in the last panel row of the block
        for j in range(len(ds), brow * block_ncol):
            r_, c_ = divmod(j, block_ncol)
            fig.add_subplot(inner[1 + r_, c_]).axis("off")

    # ---- dedicated colorbar axis on the right (never overlaps a panel) ----
    cax = fig.add_axes([0.925, 0.30, 0.016, 0.40])
    cbar = fig.colorbar(last_pc, cax=cax, ticks=[VMIN, 0, VMAX])
    cbar.ax.set_yticklabels(["periportal\nend", "0", "pericentral\nend"])
    cbar.set_label("zonation coordinate (per cell)", fontsize=9)
    cbar.ax.tick_params(labelsize=7)

    # ---- titles + shared-axes key (stated ONCE) ----
    axis_word = "disease stage" if axis == "stage" else "fibrosis (F0-F4)"
    fig.suptitle(f"A1  PC-vs-PP zonation scatter — all {n} donors, grouped by {axis_word}",
                 fontsize=14, fontweight="bold", y=0.985)
    fig.text(0.045, 0.945,
             "Each panel = one donor: x = pericentral-program score,  y = periportal-program score,  "
             "colour = each cell's zonation coordinate (purple = pericentral, orange = periportal).  "
             "Axes fixed/equal across all donors.",
             fontsize=9.5, ha="left", va="center", color=C.INK)
    fig.text(0.045, 0.925,
             "Reading key:  anti-diagonal cloud = intact zonation;  "
             "round / positive blob = collapse.   "
             "Per panel: n = number of cells in that donor;  r = Spearman(pc, pp) anti-correlation;  "
             "UMI = median sequencing depth.",
             fontsize=9.5, ha="left", va="center", color=C.MUTED)

    fig.savefig(out_path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return out_path


# ----------------------------------------------------------------------------- representatives
def representatives_panel(coords, reps, healthy, axis, out_path):
    """One larger PC/PP panel per axis level (depth-matched representative donor), each
    overlaid on the pooled-healthy reference cloud (light grey) so disease geometry is
    judged against the healthy envelope."""
    srow = C.donor_summary(WHICH, with_raw=False).set_index("donor")
    by_donor = {str(d): sub for d, sub in coords.groupby("donor")}

    n = len(reps)
    fig, axes = plt.subplots(1, n, figsize=(3.5 * n, 3.9))
    axes = np.atleast_1d(axes).ravel()
    last_pc = None

    for ax, (label, donor) in zip(axes, reps):
        # healthy envelope underneath (grey, low alpha)
        ax.scatter(healthy["pc"], healthy["pp"], s=4, alpha=0.10,
                   color=C.MUTED, linewidths=0, rasterized=True, zorder=1,
                   label="pooled healthy")
        sub = by_donor.get(donor)
        last_pc = _scatter(ax, sub, s=6, alpha=0.6)
        _frame(ax)

        meta = srow.loc[donor]
        r = _anticorr(sub)
        rtxt = f"{r:+.2f}" if pd.notna(r) else "n/a"
        depth = meta["depth_med"]
        ax.set_title(f"{label} — donor {donor}", fontsize=10, color=C.INK, pad=6)
        ax.text(0.04, 0.97,
                f"anti-corr r = {rtxt}\nn = {int(meta['n_cells'])}\ndepth = {int(depth):,}",
                transform=ax.transAxes, fontsize=7.5, va="top", ha="left",
                color=C.INK,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=C.RULE, lw=0.5, alpha=0.85))
        ax.set_xlabel("pericentral-program score", fontsize=8.5, color=C.TEAL)
        ax.set_ylabel("periportal-program score", fontsize=8.5, color=C.RUST)
        ax.tick_params(labelsize=7)

    axis_word = "disease stage" if axis == "stage" else "fibrosis stage"
    fig.suptitle(
        f"A1  Representative donor per {axis_word} vs pooled-healthy envelope (grey)\n"
        "Mechanism legend:  intact = anti-diagonal cloud   |   turn-off = collapse to origin"
        "   |   noise = round blob   |   de-zonation = pile-up at diagonal centre",
        fontsize=10.5, y=1.02)

    cbar = fig.colorbar(last_pc, ax=axes.tolist(), fraction=0.015, pad=0.01,
                        shrink=0.8, aspect=30)
    cbar.set_label("zonation coord", fontsize=8)
    cbar.ax.tick_params(labelsize=7)

    fig.subplots_adjust(left=0.05, right=0.93, top=0.82, bottom=0.12, wspace=0.28)
    fig.savefig(out_path, dpi=130)
    plt.close(fig)
    return out_path


# ----------------------------------------------------------------------------- driver
WHICH = "expanded_curated"


def main():
    global WHICH
    WHICH = sys.argv[1] if len(sys.argv) > 1 else "expanded_curated"

    coords = C.load_coords(which=WHICH)
    summary = C.donor_summary(which=WHICH, with_raw=False)
    healthy = coords[coords["stage"] == "Healthy control"]

    p1 = contact_sheet(coords, summary, "stage",
                       C.fig_path("h1", "a1_pcpp_contact_sheet_stage.png"))
    p2 = contact_sheet(coords, summary, "fibrosis",
                       C.fig_path("h1", "a1_pcpp_contact_sheet_fibrosis.png"))

    reps_stage = C.representatives(which=WHICH, axis="stage")
    reps_fib = C.representatives(which=WHICH, axis="fibrosis")
    p3 = representatives_panel(coords, reps_stage, healthy, "stage",
                               C.fig_path("h1", "a1_pcpp_representatives_stage.png"))
    p4 = representatives_panel(coords, reps_fib, healthy, "fibrosis",
                               C.fig_path("h1", "a1_pcpp_representatives_fibrosis.png"))

    for p in (p1, p2, p3, p4):
        ok = os.path.exists(p)
        print(f"[{'OK' if ok else 'MISSING'}] {p}")


if __name__ == "__main__":
    main()
