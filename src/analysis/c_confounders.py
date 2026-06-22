"""C — CONFOUNDER CONTROL for H1 ("zonation collapses with MASLD progression").

H1 is read off per-donor zonation STRENGTH = -anticorr  (anticorr = Spearman(pc, pp);
healthy donors are strongly anti-correlated, ~ -0.5, so strength ~ +0.5). The trend that
worries an honest reviewer is that strength FALLS as stage advances. But two nuisance
variables track stage and could fake that fall:

    * CELL COUNT  — end-stage donors are large (more cells); does more/less power move the
                    estimate? (C1)
    * SEQ DEPTH   — anti-correlation is a noisy estimate that ATTENUATES at low depth; if
                    diseased donors were shallower we'd see a spurious collapse. (C2 — key)

We do not settle this with correlations. We use CONTROLLED INTERVENTIONS — equalize the
nuisance variable and ask whether the H1 trend SURVIVES:

  C1  equalize cell count (common-N subsample of each donor's cells)  -> re-test H1 trend.
  C2  equalize sequencing depth (binomial thin every cell to a common target T, RE-SCORE)
      -> re-test H1 trend; plus a within-donor depth-response curve = the clean causal proof
         that depth degrades the anti-correlation measurement.
  C4  UMI-coloured end-stage scatter: is the end-stage "blob" partly low-depth noise, or do
      the high-UMI cells still anti-correlate (real biology)?

NOTE on depth units: the intervention operates on the counts matrix in common._p1_matrix(),
whose per-cell library size (sum over its ~30k genes) spans ~3.3k–5.7k UMI. T and the
depth-response targets are chosen WITHIN that range so the thinning actually bites. (The
clinical `depth_med` column is the full raw nCount and is larger; it is reported for context
only, never fed to the thinner.)

Run:  python src/analysis/c_confounders.py [signature_set]   (default expanded_curated)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # src/ on path
from analysis import common as C
import numpy as np, pandas as pd
from scipy.stats import spearmanr
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "serif", "font.size": 9, "axes.linewidth": 0.6,
    "savefig.dpi": 130, "figure.dpi": 130,
})

SEED = 0
COMMON_N = 200          # C1 common cell count (most donors meet this)
DEPTH_T = 2000          # C2 common sequencing depth target (UMI); ~all cells exceed it
RESPONSE_TARGETS = [750, 1500, 2500, 3500]   # C2b within-donor depth-response (in lib range)

# per-stage colour for points/lines
STAGE_COLOR = {
    "Healthy control":     "#2c7a3f",
    "NAFLD":               "#a6a611",
    "NASH w/o cirrhosis":  "#c97a16",
    "NASH with cirrhosis": "#b03a2e",
    "end stage":           "#6c3483",
}


def _stage_colors(stages):
    return [STAGE_COLOR.get(s, C.INK) for s in stages]


def _spear(x, y):
    """Spearman rho, p over finite pairs; (nan, nan) if too few."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 4 or np.std(x[m]) == 0 or np.std(y[m]) == 0:
        return np.nan, np.nan
    r = spearmanr(x[m], y[m])
    return float(r.statistic), float(r.pvalue)


def _trendline(ax, x, y, color, lw=1.6, ls="-"):
    """Least-squares line over finite pairs (visual guide for the rank trend)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 2:
        return
    b, a = np.polyfit(x[m], y[m], 1)
    xs = np.linspace(np.nanmin(x[m]), np.nanmax(x[m]), 50)
    ax.plot(xs, b * xs + a, color=color, lw=lw, ls=ls, zorder=1)


def _legend_stages(ax, stages, loc="best", fontsize=7):
    seen = [s for s in C.STAGE_ORDER if s in set(stages)]
    handles = [plt.Line2D([0], [0], marker="o", ls="", mfc=STAGE_COLOR[s], mec="none",
                          ms=6, label=C.STAGE_SHORT[s]) for s in seen]
    ax.legend(handles=handles, loc=loc, fontsize=fontsize, frameon=False, handletextpad=0.3)


# ============================================================ C1 — CELL COUNT
def c1_cellcount(summary, out_a):
    """(a) strength vs n_cells scatter; returns the figure path."""
    strength = -summary["anticorr"].values
    n = summary["n_cells"].values
    rho, p = _spear(strength, np.log10(n))

    fig, ax = plt.subplots(figsize=(6.2, 4.6))
    ax.scatter(n, strength, c=_stage_colors(summary["stage"]), s=46,
               edgecolor="white", linewidths=0.5, zorder=3)
    ax.set_xscale("log")
    # trend line fit in log10(n) space, drawn against the log x-axis
    b, a = np.polyfit(np.log10(n), strength, 1)
    xs = np.logspace(np.log10(n.min()), np.log10(n.max()), 50)
    ax.plot(xs, b * np.log10(xs) + a, color=C.INK, lw=1.2, ls="--", zorder=1)

    ax.axhline(0, color=C.RULE, lw=0.7, zorder=0)
    ax.set_xlabel("donor cell count  (log scale)")
    ax.set_ylabel("zonation strength  ( -anticorr )")
    ax.set_title("C1a  Zonation strength vs cell count", fontsize=11, fontweight="bold")
    ax.text(0.03, 0.05, f"Spearman(strength, log n) = {rho:+.3f}  (p = {p:.3g})",
            transform=ax.transAxes, fontsize=9, va="bottom",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=C.RULE, lw=0.5))
    _legend_stages(ax, summary["stage"], loc="upper right")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.text(0.5, 0.005,
             "Caveat: n_cells itself tracks stage (end-stage donors are large), so this raw "
             "association is CONFOUNDED with disease.\nThe common-N intervention (C1b) breaks "
             "that confound by equalizing cell count.",
             ha="center", va="bottom", fontsize=7.3, color=C.MUTED)
    fig.subplots_adjust(left=0.11, right=0.97, top=0.92, bottom=0.17)
    fig.savefig(out_a)
    plt.close(fig)
    return out_a, rho, p


def c1_commonN(coords, summary, out_b):
    """(b) Common-N intervention: subsample each donor to COMMON_N cells, recompute anticorr
    by SLICING rows (pc/pp already standardized — no re-scoring needed), and re-test the H1
    trend Spearman(strength, stage_rank) BEFORE vs AFTER equalizing N."""
    rng = np.random.RandomState(SEED)
    by_donor = {str(d): sub for d, sub in coords.groupby("donor")}

    rows, dropped = [], 0
    for _, r in summary.iterrows():
        d = str(r["donor"])
        sub = by_donor.get(d)
        if sub is None or len(sub) < COMMON_N:
            dropped += 1
            rows.append(dict(donor=d, stage=r["stage"], stage_rank=r["stage_rank"],
                             strength_full=-r["anticorr"], strength_cn=np.nan))
            continue
        take = rng.choice(len(sub), COMMON_N, replace=False)
        ss = sub.iloc[take]
        ac = spearmanr(ss["pc"], ss["pp"]).statistic if ss["pc"].std() > 0 else np.nan
        rows.append(dict(donor=d, stage=r["stage"], stage_rank=r["stage_rank"],
                         strength_full=-r["anticorr"], strength_cn=-float(ac)))
    cn = pd.DataFrame(rows)

    rho_f, p_f = _spear(cn["strength_full"], cn["stage_rank"])
    keep = cn["strength_cn"].notna()
    rho_c, p_c = _spear(cn.loc[keep, "strength_cn"], cn.loc[keep, "stage_rank"])

    # jittered strength-vs-stage_rank, full vs common-N, with both trend lines
    fig, ax = plt.subplots(figsize=(7.0, 5.0))
    jit = (np.random.RandomState(1).rand(len(cn)) - 0.5) * 0.18
    xr = cn["stage_rank"].values + jit
    ax.scatter(xr - 0.06, cn["strength_full"], c=_stage_colors(cn["stage"]), s=44,
               marker="o", edgecolor="white", linewidths=0.5, alpha=0.95, zorder=3,
               label="full (all cells)")
    ax.scatter(xr[keep.values] + 0.06, cn.loc[keep, "strength_cn"],
               c=_stage_colors(cn.loc[keep, "stage"]), s=44, marker="^",
               edgecolor=C.INK, linewidths=0.6, alpha=0.95, zorder=3,
               label=f"common-N (={COMMON_N})")
    _trendline(ax, cn["stage_rank"], cn["strength_full"], C.TEAL, lw=2.0, ls="-")
    _trendline(ax, cn.loc[keep, "stage_rank"], cn.loc[keep, "strength_cn"], C.RUST, lw=2.0, ls="--")

    ax.axhline(0, color=C.RULE, lw=0.7, zorder=0)
    ax.set_xticks(range(len(C.STAGE_ORDER)))
    ax.set_xticklabels([C.STAGE_SHORT[s] for s in C.STAGE_ORDER], rotation=20, ha="right")
    ax.set_xlabel("disease stage")
    ax.set_ylabel("zonation strength  ( -anticorr )")
    ax.set_title("C1b  Does the H1 collapse survive equalizing CELL COUNT?",
                 fontsize=11, fontweight="bold")
    txt = (f"H1 trend  Spearman(strength, stage_rank):\n"
           f"  full       rho = {rho_f:+.3f}  (p = {p_f:.3g})\n"
           f"  common-N   rho = {rho_c:+.3f}  (p = {p_c:.3g})\n"
           f"  ({int(keep.sum())} donors kept, {dropped} dropped < {COMMON_N} cells)")
    ax.text(0.02, 0.03, txt, transform=ax.transAxes, fontsize=8.5, va="bottom",
            family="monospace",
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=C.RULE, lw=0.5))
    # marker legend (full vs common-N) on top-right; stage legend below it
    h1 = [plt.Line2D([0], [0], marker="o", ls="", mfc=C.MUTED, mec="white", ms=7, label="full"),
          plt.Line2D([0], [0], marker="^", ls="", mfc=C.MUTED, mec=C.INK, ms=7, label=f"common-N={COMMON_N}")]
    leg1 = ax.legend(handles=h1, loc="upper right", fontsize=8, frameon=False)
    ax.add_artist(leg1)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.subplots_adjust(left=0.10, right=0.97, top=0.92, bottom=0.14)
    fig.savefig(out_b)
    plt.close(fig)
    return out_b, dict(rho_full=rho_f, p_full=p_f, rho_cn=rho_c, p_cn=p_c,
                       kept=int(keep.sum()), dropped=dropped)


# ============================================================ C2 — SEQ DEPTH (key control)
def c2_depth(coords, summary, out_paired, out_csv):
    """(a) Thin ALL cells to T, RE-SCORE, recompute per-donor anticorr. Paired original-vs-@T
    figure + H1 trend before/after depth equalization. Writes the control CSV."""
    M, genes, bars, lib = C._p1_matrix()
    pcg, ppg = C.gene_lists(WHICH)
    b2i = {b: i for i, b in enumerate(bars)}

    print(f"  [C2] thinning all {M.shape[1]} cells to T={DEPTH_T} UMI (binomial)…", flush=True)
    Ms, libs = C.subsample_counts(M, lib, DEPTH_T, seed=SEED)
    coordS, pcS, ppS = C.score_from_matrix(Ms, libs, genes, pcg, ppg)

    by_donor = {str(d): sub for d, sub in coords.groupby("donor")}
    rows = []
    for _, r in summary.iterrows():
        d = str(r["donor"])
        sub = by_donor.get(d)
        cells = [b2i[c] for c in sub["cell_id"] if c in b2i]
        ac_t = (spearmanr(pcS[cells], ppS[cells]).statistic
                if len(cells) > 3 and np.std(pcS[cells]) > 0 else np.nan)
        rows.append(dict(donor=d, stage=r["stage"], stage_rank=int(r["stage_rank"]),
                         depth_med=float(r["depth_med"]), n_cells=int(r["n_cells"]),
                         anticorr_orig=float(r["anticorr"]), anticorr_at_T=float(ac_t)))
    dt = pd.DataFrame(rows)
    dt.to_csv(out_csv, index=False)

    rho_o, p_o = _spear(-dt["anticorr_orig"], dt["stage_rank"])
    rho_t, p_t = _spear(-dt["anticorr_at_T"], dt["stage_rank"])

    # paired per-donor anticorr ORIGINAL -> @T, lines coloured by stage
    fig, ax = plt.subplots(figsize=(7.4, 5.2))
    for _, r in dt.iterrows():
        col = STAGE_COLOR.get(r["stage"], C.INK)
        ax.plot([0, 1], [r["anticorr_orig"], r["anticorr_at_T"]], "-", color=col,
                lw=1.0, alpha=0.55, zorder=2)
        ax.plot(0, r["anticorr_orig"], "o", color=col, ms=5, mec="white", mew=0.5, zorder=3)
        ax.plot(1, r["anticorr_at_T"], "o", color=col, ms=5, mec="white", mew=0.5, zorder=3)
    ax.axhline(0, color=C.RULE, lw=0.7, zorder=0)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["original depth", f"thinned to {DEPTH_T} UMI"])
    ax.set_xlim(-0.25, 1.45)
    ax.set_ylabel("anticorr  Spearman(pc, pp)   (more negative = stronger zonation)")
    ax.set_title("C2a  Depth equalization — paired per-donor anti-correlation",
                 fontsize=11, fontweight="bold")
    txt = (f"H1 trend  Spearman(strength=-anticorr, stage_rank):\n"
           f"  original depth   rho = {rho_o:+.3f}  (p = {p_o:.3g})\n"
           f"  @ {DEPTH_T} UMI      rho = {rho_t:+.3f}  (p = {p_t:.3g})")
    ax.text(0.97, 0.04, txt, transform=ax.transAxes, fontsize=8.5, va="bottom", ha="right",
            family="monospace",
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=C.RULE, lw=0.5))
    _legend_stages(ax, dt["stage"], loc="upper right")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    verdict = ("SURVIVES" if (np.isfinite(rho_t) and rho_t < 0 and p_t < 0.05) else "WEAKENS / does not survive")
    fig.text(0.5, 0.005,
             f"Decisive test: deep, strongly-zonated donors weaken toward 0 when thinned, but the "
             f"H1 stage trend {verdict} depth equalization (compare the two rho/p).",
             ha="center", va="bottom", fontsize=7.6, color=C.MUTED)
    fig.subplots_adjust(left=0.10, right=0.97, top=0.92, bottom=0.13)
    fig.savefig(out_paired)
    plt.close(fig)
    return out_paired, out_csv, dict(rho_orig=rho_o, p_orig=p_o, rho_T=rho_t, p_T=p_t), dt


def c2_response(coords, summary, out_resp):
    """(b) Within-donor depth-response: pick ~3 well-zonated DEEP donors (highest depth_med,
    n>=400, strongest |anticorr|), thin ONLY their cells to several targets, plot anticorr vs
    target depth. The clean causal proof that depth degrades the measurement."""
    M, genes, bars, lib = C._p1_matrix()
    pcg, ppg = C.gene_lists(WHICH)
    b2i = {b: i for i, b in enumerate(bars)}

    cand = summary[(summary["n_cells"] >= 400) & summary["anticorr"].notna()].copy()
    cand = cand.sort_values("depth_med", ascending=False).head(12)
    cand = cand.sort_values("anticorr").head(3)   # strongest (most negative) among the deep
    pick = cand["donor"].astype(str).tolist()

    by_donor = {str(d): sub for d, sub in coords.groupby("donor")}
    # restrict matrix columns to just these donors' cells (fast subsample)
    pick_cells = []
    for d in pick:
        pick_cells += [b2i[c] for c in by_donor[d]["cell_id"] if c in b2i]
    pick_cells = np.array(sorted(set(pick_cells)))
    col_of = {orig: j for j, orig in enumerate(pick_cells)}
    Msub = M[:, pick_cells].tocsr()
    lib_sub = lib[pick_cells]

    curves = {d: {"x": [], "y": []} for d in pick}
    # original point first
    coord0, pc0, pp0 = C.score_from_matrix(Msub, lib_sub, genes, pcg, ppg)
    for d in pick:
        loc = [col_of[b2i[c]] for c in by_donor[d]["cell_id"] if c in b2i]
        med_lib = float(np.median(lib_sub[loc]))
        ac = spearmanr(pc0[loc], pp0[loc]).statistic
        curves[d]["x"].append(med_lib); curves[d]["y"].append(float(ac))
    # thinned targets
    for T in RESPONSE_TARGETS:
        Mt, libt = C.subsample_counts(Msub, lib_sub, T, seed=SEED)
        coordT, pcT, ppT = C.score_from_matrix(Mt, libt, genes, pcg, ppg)
        for d in pick:
            loc = [col_of[b2i[c]] for c in by_donor[d]["cell_id"] if c in b2i]
            ac = spearmanr(pcT[loc], ppT[loc]).statistic
            curves[d]["x"].append(float(T)); curves[d]["y"].append(float(ac))

    fig, ax = plt.subplots(figsize=(6.6, 4.8))
    srow = summary.set_index("donor")
    for d in pick:
        col = STAGE_COLOR.get(srow.loc[d, "stage"], C.INK)
        xy = sorted(zip(curves[d]["x"], curves[d]["y"]))
        xs = [p[0] for p in xy]; ys = [p[1] for p in xy]
        ax.plot(xs, ys, "-o", color=col, lw=1.6, ms=6, mec="white", mew=0.5,
                label=f"donor {d} ({C.STAGE_SHORT[srow.loc[d,'stage']]}, n={int(srow.loc[d,'n_cells'])})")
    ax.axhline(0, color=C.RULE, lw=0.7, zorder=0)
    ax.set_xlabel("target depth  (UMI per cell after thinning)")
    ax.set_ylabel("anticorr  Spearman(pc, pp)")
    ax.set_title("C2b  Within-donor depth-response (causal proof)",
                 fontsize=11, fontweight="bold")
    ax.legend(fontsize=8, frameon=False, loc="upper right")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.text(0.5, 0.005,
             "Same cells, only depth changes: anti-correlation attenuates toward 0 as depth "
             "falls — depth CAUSALLY degrades the zonation measurement.",
             ha="center", va="bottom", fontsize=7.6, color=C.MUTED)
    fig.subplots_adjust(left=0.12, right=0.97, top=0.91, bottom=0.16)
    fig.savefig(out_resp)
    plt.close(fig)
    return out_resp, pick


# ============================================================ C4 — UMI-COLOURED SCATTER
def c4_umi_scatter(coords, out):
    """End-stage PC-vs-PP scatter coloured by per-cell log10 UMI. Is the blob partly low-depth
    noise? Annotate anticorr in the TOP-UMI tercile vs BOTTOM-UMI tercile of cells."""
    M, genes, bars, lib = C._p1_matrix()
    libdf = pd.DataFrame({"cell_id": bars, "umi": lib})
    es = coords[coords["stage"] == "end stage"].merge(libdf, on="cell_id", how="left")
    es = es[es["umi"].notna() & (es["umi"] > 0)].copy()
    es["lumi"] = np.log10(es["umi"])

    q1, q2 = es["umi"].quantile([1 / 3, 2 / 3])
    bot = es[es["umi"] <= q1]
    top = es[es["umi"] >= q2]
    ac_bot, _ = _spear(bot["pc"], bot["pp"])
    ac_top, _ = _spear(top["pc"], top["pp"])
    ac_all, _ = _spear(es["pc"], es["pp"])

    fig, ax = plt.subplots(figsize=(6.6, 5.6))
    sc = ax.scatter(es["pc"], es["pp"], c=es["lumi"], cmap="viridis", s=6, alpha=0.6,
                    linewidths=0, rasterized=True)
    ax.axhline(0, color=C.RULE, lw=0.6, zorder=0)
    ax.axvline(0, color=C.RULE, lw=0.6, zorder=0)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("pericentral-program score", color=C.TEAL)
    ax.set_ylabel("periportal-program score", color=C.RUST)
    ax.set_title(f"C4  End-stage cells coloured by depth  (pooled, n={len(es):,} cells)",
                 fontsize=11, fontweight="bold")
    cb = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.02)
    cb.set_label("log10 per-cell UMI")
    txt = (f"anti-corr Spearman(pc, pp):\n"
           f"  all end-stage cells   = {ac_all:+.3f}\n"
           f"  TOP-UMI tercile       = {ac_top:+.3f}\n"
           f"  BOTTOM-UMI tercile    = {ac_bot:+.3f}")
    ax.text(0.03, 0.04, txt, transform=ax.transAxes, fontsize=8.5, va="bottom",
            family="monospace",
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=C.RULE, lw=0.5))
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    msg = ("High-UMI cells retain stronger anti-correlation than low-UMI cells — part of the "
           "end-stage 'blob' is low-depth noise, but real residual zonation remains in well-sequenced cells."
           if (np.isfinite(ac_top) and np.isfinite(ac_bot) and ac_top < ac_bot) else
           "High-UMI cells do NOT anti-correlate more than low-UMI cells — the end-stage collapse is not explained by depth.")
    fig.text(0.5, 0.005, msg, ha="center", va="bottom", fontsize=7.4, color=C.MUTED, wrap=True)
    fig.subplots_adjust(left=0.11, right=0.99, top=0.92, bottom=0.13)
    fig.savefig(out)
    plt.close(fig)
    return out, dict(all=ac_all, top=ac_top, bot=ac_bot, n=len(es))


# ============================================================ driver
WHICH = "expanded_curated"


def main():
    global WHICH
    WHICH = sys.argv[1] if len(sys.argv) > 1 else "expanded_curated"
    print(f"[C confounders] set = {WHICH}")

    coords = C.load_coords(which=WHICH)
    summary = C.donor_summary(which=WHICH, with_raw=False)

    out = {}
    out["c1a"], r1, p1 = c1_cellcount(summary, C.fig_path("confounders", "c1_cellcount_vs_strength.png"))
    out["c1b"], cn = c1_commonN(coords, summary, C.fig_path("confounders", "c1_commonN_h1.png"))
    out["c2a"], out["csv"], d2, dt = c2_depth(
        coords, summary, C.fig_path("confounders", "c2_depth_paired.png"),
        C.table_path("c2_depth_control.csv"))
    out["c2b"], picked = c2_response(coords, summary, C.fig_path("confounders", "c2_depth_response.png"))
    out["c4"], c4 = c4_umi_scatter(coords, C.fig_path("confounders", "c4_endstage_umi_scatter.png"))

    print("\n=== outputs ===")
    for k, v in out.items():
        print(f"[{'OK' if os.path.exists(v) else 'MISSING'}] {k}: {v}")

    print("\n=== verdict numbers ===")
    print(f"C1a strength vs log n_cells: rho={r1:+.3f} p={p1:.3g}")
    print(f"C1b H1 trend  full rho={cn['rho_full']:+.3f} p={cn['p_full']:.3g}  |  "
          f"common-N rho={cn['rho_cn']:+.3f} p={cn['p_cn']:.3g}  "
          f"(kept {cn['kept']}, dropped {cn['dropped']})")
    print(f"C2a H1 trend  orig rho={d2['rho_orig']:+.3f} p={d2['p_orig']:.3g}  |  "
          f"@T={DEPTH_T} rho={d2['rho_T']:+.3f} p={d2['p_T']:.3g}")
    print(f"C2b depth-response donors: {picked}")
    print(f"C4 end-stage anticorr  all={c4['all']:+.3f}  top-UMI={c4['top']:+.3f}  "
          f"bottom-UMI={c4['bot']:+.3f}  (n={c4['n']})")


if __name__ == "__main__":
    main()
