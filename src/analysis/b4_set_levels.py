"""B4 -- Program EXPRESSION LEVEL across disease, per candidate signature set.

Scientific goal: for each candidate signature SET (different pericentral/periportal gene
lists), track the raw EXPRESSION LEVEL of its program across disease stage and across
fibrosis (F0-F4), separately for the pericentral (PC) and periportal (PP) arm.

This separates two distinct ways a zonation program can be lost in disease:
  * TURN-OFF      : the raw expression LEVEL of the program drops toward 0 with disease.
  * DE-ZONATION   : the LEVEL is held roughly flat, but the spatial gradient collapses
                    (the latter is measured elsewhere; here a FLAT level is the signature
                    of de-zonation rather than turn-off).

y-axis = mean per-DONOR raw log1p-CP10k expression over the arm's genes (UN-standardized
level). Unit of aggregation = DONOR (never raw cells): per-cell raw -> per-donor mean ->
average of donor means within each stage / fibrosis level; error bar = SEM across donors.

Outputs:
  results/figures/h2/b4_set_expression_by_stage.png
  results/figures/h2/b4_set_expression_by_fibrosis.png
  results/tables/analysis/set_expression_levels.csv
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # src/ on path
from analysis import common as C
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

# Candidate sets to try; keep the ones non-empty for BOTH arms.
CANDIDATE_SETS = ["expanded_curated", "paper2_landmark", "core_curated",
                  "paper2_top100", "paper2_full"]

# Distinct colors + markers per set (kept stable across both figures).
SET_STYLE = {
    "expanded_curated": (C.TEAL,   "o"),
    "paper2_landmark":  (C.RUST,   "s"),
    "core_curated":     ("#3b6ea5", "^"),
    "paper2_top100":    ("#7a4fa3", "D"),
    "paper2_full":      ("#5a5a5a", "v"),
}


def _per_donor_levels(set_name, donor_map):
    """Return DataFrame[donor, stage, fibrosis, pc_raw, pp_raw] = per-donor mean raw level
    for one set, or None if either arm's gene list is empty."""
    pc_genes, pp_genes = C.gene_lists(set_name)
    if not pc_genes or not pp_genes:
        return None
    cell_raw = C.raw_arm_means(pc_genes, pp_genes)          # cell_id, pc_raw, pp_raw
    m = cell_raw.merge(donor_map, on="cell_id", how="inner")
    # per-cell raw -> per-donor mean (donor is the unit)
    g = (m.groupby("donor")
           .agg(pc_raw=("pc_raw", "mean"), pp_raw=("pp_raw", "mean"))
           .reset_index())
    return g


def _aggregate(donor_levels, arm_col, axis, levels):
    """Average donor means within each axis level. Returns list of dicts with
    level_label, n_donors, mean_expr, sem_expr (sem = SEM across donors)."""
    out = []
    for label, key in levels:
        sub = donor_levels[donor_levels[axis] == key]
        vals = sub[arm_col].dropna().values
        n = len(vals)
        if n == 0:
            continue
        mean = float(np.mean(vals))
        sem = float(np.std(vals, ddof=1) / np.sqrt(n)) if n > 1 else 0.0
        out.append(dict(level_label=label, key=key, n_donors=n,
                        mean_expr=mean, sem_expr=sem, vals=vals))
    return out


SUBTITLE = ("y = mean per-DONOR raw log1p-CP10k expression (un-standardized LEVEL); "
            "donor = unit of aggregation; error bars = SEM across donors.\n"
            "Falling level with disease = TURN-OFF; flat level (with collapsing spatial "
            "gradient) = DE-ZONATION.")


def _plot(axis, levels, set_donor_levels, fname, xlabel):
    """One figure: 2 panels (PC, PP); one line per set; faint jittered per-donor points."""
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 6.2), sharex=True)
    arms = [("pc_raw", "Pericentral (PC) arm", C.TEAL),
            ("pp_raw", "Periportal (PP) arm", C.RUST)]
    xpos = {key: i for i, (_, key) in enumerate(levels)}
    xticklabels = [lab for lab, _ in levels]

    table_rows = []
    rng = np.random.default_rng(0)
    for ax, (arm_col, arm_title, arm_color) in zip(axes, arms):
        for set_name, dl in set_donor_levels.items():
            color, marker = SET_STYLE.get(set_name, (C.MUTED, "o"))
            agg = _aggregate(dl, arm_col, axis, levels)
            if not agg:
                continue
            xs = [xpos[r["key"]] for r in agg]
            ys = [r["mean_expr"] for r in agg]
            es = [r["sem_expr"] for r in agg]
            # faint jittered per-donor points behind the line
            for r in agg:
                jit = rng.uniform(-0.10, 0.10, size=len(r["vals"]))
                ax.scatter(np.full(len(r["vals"]), xpos[r["key"]]) + jit, r["vals"],
                           s=8, color=color, alpha=0.12, zorder=1, linewidths=0)
            ax.errorbar(xs, ys, yerr=es, color=color, marker=marker, ms=6, lw=1.8,
                        capsize=3, label=set_name, zorder=3)
            for r in agg:
                table_rows.append(dict(set=set_name, arm=arm_col.replace("_raw", ""),
                                       axis=axis, level_label=r["level_label"],
                                       n_donors=r["n_donors"],
                                       mean_expr=round(r["mean_expr"], 6),
                                       sem_expr=round(r["sem_expr"], 6)))
        ax.set_title(arm_title, fontsize=12, color=arm_color, fontweight="bold")
        ax.set_xticks(range(len(levels)))
        ax.set_xticklabels(xticklabels, rotation=20, ha="right")
        ax.set_xlabel(xlabel)
        ax.set_ylabel("mean per-donor raw log1p-CP10k level")
        ax.grid(axis="y", color=C.RULE, lw=0.6, alpha=0.7)
        ax.set_axisbelow(True)
    axes[0].legend(title="signature set", fontsize=8.5, title_fontsize=9, frameon=False)
    fig.suptitle("B4  Program expression LEVEL across disease, by signature set",
                 fontsize=14, fontweight="bold", y=0.99)
    fig.text(0.5, 0.90, SUBTITLE, ha="center", va="top", fontsize=8.5, color=C.MUTED)
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    fig.savefig(fname, dpi=150)
    plt.close(fig)
    return table_rows


def main():
    # cell -> donor & stage (shared key cell_id)
    coords = C.load_coords()[["cell_id", "donor", "stage"]].copy()
    coords["donor"] = coords["donor"].astype(str)

    # donor -> fibrosis (F0-4) from the per-donor summary
    dsum = C.donor_summary(with_raw=False)[["donor", "fibrosis"]].copy()
    dsum["donor"] = dsum["donor"].astype(str)
    donor_fib = dict(zip(dsum["donor"], dsum["fibrosis"]))

    # per-set per-donor levels (compute once, reuse for both axes)
    set_donor_levels = {}
    for set_name in CANDIDATE_SETS:
        dl = _per_donor_levels(set_name, coords)
        if dl is None or dl.empty:
            print(f"[skip] {set_name}: empty gene list for an arm.")
            continue
        # attach stage (donor mode) and fibrosis per donor
        donor_stage = (coords.groupby("donor")["stage"]
                       .agg(lambda s: s.mode().iat[0]).to_dict())
        dl["stage"] = dl["donor"].map(donor_stage)
        dl["fibrosis"] = dl["donor"].map(donor_fib)
        set_donor_levels[set_name] = dl
        print(f"[ok]   {set_name}: {len(dl)} donors")

    if not set_donor_levels:
        raise SystemExit("No usable signature sets (all arms empty).")

    # axis level definitions (label, key)
    stage_levels = [(C.STAGE_SHORT[s], s) for s in C.STAGE_ORDER]
    fib_levels = [(C.FIB_LABEL[f], f) for f in C.FIB_ORDER]

    rows = []
    rows += _plot("stage", stage_levels, set_donor_levels,
                  C.fig_path("h2", "b4_set_expression_by_stage.png"), "disease stage")
    rows += _plot("fibrosis", fib_levels, set_donor_levels,
                  C.fig_path("h2", "b4_set_expression_by_fibrosis.png"), "fibrosis (F0-F4)")

    tbl = pd.DataFrame(rows, columns=["set", "arm", "axis", "level_label",
                                      "n_donors", "mean_expr", "sem_expr"])
    tpath = C.table_path("set_expression_levels.csv")
    tbl.to_csv(tpath, index=False)

    print("\nWrote:")
    print(" ", C.fig_path("h2", "b4_set_expression_by_stage.png"))
    print(" ", C.fig_path("h2", "b4_set_expression_by_fibrosis.png"))
    print(" ", tpath)
    print(f"\nTable rows: {len(tbl)}")


if __name__ == "__main__":
    main()
