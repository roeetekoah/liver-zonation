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
def contact_sheet(coords, summary, axis, out_path):
    """All donors as small PC/PP scatters in a grid, grouped/ordered by `axis`.

    Donors are laid out in band-order: each staging level's donors occupy a contiguous
    run of panels, with a coloured band label heading each level's block.
    """
    levels = C.staging_levels(summary, axis)
    # flat donor order, plus which level each panel belongs to (for the band heading)
    order, panel_level = [], []
    for label, donors in levels:
        # keep the summary's intra-level ordering (already by fibrosis then n_cells)
        ds = summary[summary.donor.isin(donors)]["donor"].tolist()
        order.extend(ds)
        panel_level.extend([label] * len(ds))

    n = len(order)
    ncol = 7
    nrow = int(np.ceil(n / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(ncol * 1.9, nrow * 2.05))
    axes = np.atleast_1d(axes).ravel()

    by_donor = {str(d): sub for d, sub in coords.groupby("donor")}
    srow = summary.set_index("donor")
    last_pc = None

    for i, donor in enumerate(order):
        ax = axes[i]
        sub = by_donor.get(donor)
        last_pc = _scatter(ax, sub)
        _frame(ax)
        meta = srow.loc[donor]
        stage = meta["stage"]
        col = STAGE_BAND.get(stage, C.INK)
        r = meta["anticorr"]
        rtxt = f"{r:+.2f}" if pd.notna(r) else "n/a"
        ax.set_title(f"{donor}  n={int(meta['n_cells'])}\nr={rtxt}",
                     fontsize=6.5, color=col, pad=2)
        ax.tick_params(labelsize=5, length=2)
        # a small coloured corner tab reinforces the level grouping
        ax.plot([LIM[0]], [LIM[1]], marker="s", ms=6, color=col,
                clip_on=False, zorder=5)

    for j in range(n, len(axes)):
        axes[j].axis("off")

    # legend: one swatch per level present, in band order
    handles = [plt.Line2D([], [], marker="s", ls="", ms=8,
                          color=STAGE_BAND.get(s, C.INK),
                          label=C.STAGE_SHORT.get(s, s))
               for s in C.STAGE_ORDER if (summary.stage == s).any()]
    axis_word = "disease stage" if axis == "stage" else "fibrosis stage"
    fig.suptitle(f"A1  PC-vs-PP zonation scatter — all {n} donors, ordered by {axis_word}\n"
                 "x = pericentral score, y = periportal score; colour = zonation coord (PuOr); "
                 "r = pc/pp anti-correlation", fontsize=11, y=0.997)
    fig.legend(handles=handles, loc="lower center", ncol=len(handles),
               fontsize=8, frameon=False, bbox_to_anchor=(0.5, 0.0))
    cbar = fig.colorbar(last_pc, ax=axes.tolist(), fraction=0.012, pad=0.01,
                        shrink=0.5, aspect=30)
    cbar.set_label("zonation coord", fontsize=8)
    cbar.ax.tick_params(labelsize=7)

    fig.subplots_adjust(left=0.03, right=0.93, top=0.93, bottom=0.05,
                        wspace=0.25, hspace=0.45)
    fig.savefig(out_path, dpi=130)
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
