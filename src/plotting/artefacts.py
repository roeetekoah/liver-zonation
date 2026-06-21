"""Premade plotting machinery for the zonation-collapse pipeline.

One function per artefact; each takes the artefact's data (DataFrame / arrays / path)
and saves a figure to results/figures/. Bodies are mostly real matplotlib and tolerant
of reasonable input; where the artefact is not yet pinned down they raise
NotImplementedError with a clear note.

Artefact -> function map
  A1  reference PC/PP zonation profiles ......... plot_a1_reference_profiles
  A4  zonation coordinate + marker scatters ..... plot_a4_coordinate
  A5  validation Spearman bars .................. plot_a5_validation
  A5b ruler diagnostics per stage .............. plot_a5b_ruler
  A6  donor-level collapse curve ................ plot_a6_collapse
  A7  DE volcano ............................... plot_a7_volcano
  A8  de-zonation vs plasticity, by stage ...... plot_a8_plasticity
"""
from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PC_COLOR = "#1b6e78"
PP_COLOR = "#c05621"
SHORT_STAGES = ["Healthy", "NAFLD", "NASH", "Cirrhosis", "End-stage"]


def _save(fig, out):
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out


def plot_a1_reference_profiles(profiles_df, out="results/figures/a1_reference_profiles.png"):
    """PC vs PP gene zonation profiles: mean expression across zone bins (opposite gradients).

    Expected input
      profiles_df : long DataFrame with columns {gene, zone_bin, mean_expr, program}
                    where program in {"pericentral", "periportal"}.
    """
    fig, ax = plt.subplots(figsize=(6.5, 4))
    for prog, color in [("pericentral", PC_COLOR), ("periportal", PP_COLOR)]:
        sub = profiles_df[profiles_df["program"] == prog]
        for g, gg in sub.groupby("gene"):
            gg = gg.sort_values("zone_bin")
            ax.plot(gg["zone_bin"], gg["mean_expr"], color=color, alpha=0.5, lw=1)
        # program mean
        m = sub.groupby("zone_bin")["mean_expr"].mean()
        ax.plot(m.index, m.values, color=color, lw=3, label=prog)
    ax.set_xlabel("zone bin (portal -> central)")
    ax.set_ylabel("mean expression (z / norm)")
    ax.set_title("A1 — reference zonation profiles")
    ax.legend()
    return _save(fig, out)


def plot_a4_coordinate(coord_df, out="results/figures/a4_coordinate.png",
                       pc_marker="CYP2E1", pp_marker="ASS1"):
    """Histogram of zonation_coord + 2 scatter panels (a PC and a PP marker vs coord).

    Expected input
      coord_df : DataFrame with a coordinate column ("coord" or "zonation_coord") and
                 marker columns (pc_marker, pp_marker) of per-cell expression.
    """
    coord_col = "coord" if "coord" in coord_df.columns else "zonation_coord"
    coord = coord_df[coord_col].values
    fig, ax = plt.subplots(1, 3, figsize=(13, 3.6))
    ax[0].hist(coord, bins=60, color=PC_COLOR)
    ax[0].set_title("Zonation coordinate")
    ax[0].set_xlabel("pericentral - periportal")
    if pc_marker in coord_df.columns:
        ax[1].scatter(coord, coord_df[pc_marker], s=3, alpha=0.15, color="#2c6fb0")
        ax[1].set_title(f"Pericentral: {pc_marker}"); ax[1].set_xlabel("coordinate")
    if pp_marker in coord_df.columns:
        ax[2].scatter(coord, coord_df[pp_marker], s=3, alpha=0.15, color=PP_COLOR)
        ax[2].set_title(f"Periportal: {pp_marker}"); ax[2].set_xlabel("coordinate")
    return _save(fig, out)


def plot_a5_validation(coord_df, markers, out="results/figures/a5_validation.png"):
    """Bar of Spearman(coord, marker) per validation marker, colored by expected sign.

    Expected input
      coord_df : DataFrame with a coordinate column + each marker's expression column.
      markers  : dict {marker_name: expected_sign in {+1, -1}}.
    """
    from scipy.stats import spearmanr
    coord_col = "coord" if "coord" in coord_df.columns else "zonation_coord"
    coord = coord_df[coord_col].values
    names, rhos, colors = [], [], []
    for m, sign in markers.items():
        if m not in coord_df.columns:
            continue
        rho = spearmanr(coord, coord_df[m].values).statistic
        names.append(m); rhos.append(rho)
        colors.append(PC_COLOR if sign > 0 else PP_COLOR)
    fig, ax = plt.subplots(figsize=(max(5, 0.7 * len(names)), 4))
    ax.bar(names, rhos, color=colors)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_ylabel("Spearman rho(coord, marker)")
    ax.set_title("A5 — healthy validation (PC teal expect +, PP orange expect -)")
    ax.set_xticklabels(names, rotation=30, ha="right")
    return _save(fig, out)


def plot_a5b_ruler(diag_df, out="results/figures/a5b_ruler.png"):
    """Per-stage curves of coherence / anti-correlation / split-half reproducibility.

    Expected input
      diag_df : DataFrame indexed/ordered by stage with columns
                {internal_coherence, cross_program_anticorr, split_half_repro}
                (plus optionally a 'stage' column).
    """
    metrics = [c for c in ("internal_coherence", "cross_program_anticorr", "split_half_repro")
               if c in diag_df.columns]
    if not metrics:
        raise NotImplementedError(
            "A5b: diag_df must carry internal_coherence / cross_program_anticorr / "
            "split_half_repro columns (Step 5b output)."
        )
    x = np.arange(len(diag_df))
    labels = diag_df["stage"].tolist() if "stage" in diag_df.columns else SHORT_STAGES[:len(diag_df)]
    fig, ax = plt.subplots(figsize=(7, 4))
    for met in metrics:
        ax.plot(x, diag_df[met].values, "o-", lw=2, label=met)
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=20)
    ax.set_ylabel("diagnostic value"); ax.set_title("A5b — ruler diagnostics per stage")
    ax.legend()
    return _save(fig, out)


def plot_a6_collapse(per_donor_df, out="results/figures/a6_collapse.png"):
    """Donor points + per-stage mean for coordinate spread & PC-PP anti-correlation.

    Expected input
      per_donor_df : DataFrame with {stage_rank, spread, anticorr} (one row per donor).
    """
    dd = per_donor_df
    panels = [("spread", "coordinate spread (per donor)"),
              ("anticorr", "PC-PP corr (per donor)")]
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    rng = np.random.default_rng(0)
    for i, (metric, title) in enumerate(panels):
        jitter = rng.uniform(-0.08, 0.08, len(dd))
        ax[i].scatter(dd["stage_rank"] + jitter, dd[metric], s=22, color=PC_COLOR, alpha=0.7)
        mean = dd.groupby("stage_rank")[metric].mean()
        ax[i].plot(mean.index, mean.values, "o-", color=PP_COLOR, lw=2)
        ax[i].set_xticks(range(len(SHORT_STAGES)))
        ax[i].set_xticklabels(SHORT_STAGES, rotation=20)
        ax[i].set_title(title)
    fig.suptitle("A6 — donor-level zonation collapse (H1)")
    return _save(fig, out)


def plot_collapse_metrics(per_donor_df, metrics, out, short=None, title=None):
    """H1 figure: per-donor scatter + per-stage mean, one panel per metric (A6, generalized)."""
    short = short or SHORT_STAGES
    dd = per_donor_df
    fig, ax = plt.subplots(1, len(metrics), figsize=(4 * len(metrics), 3.8), squeeze=False)
    rng = np.random.default_rng(0)
    for i, m in enumerate(metrics):
        a = ax[0][i]
        a.scatter(dd["stage_rank"] + rng.uniform(-0.08, 0.08, len(dd)), dd[m], s=22, color=PC_COLOR, alpha=0.7)
        mean = dd.groupby("stage_rank")[m].mean()
        a.plot(mean.index, mean.values, "o-", color=PP_COLOR, lw=2)
        a.set_xticks(range(len(short))); a.set_xticklabels(short, rotation=20)
        a.set_title(f"{m} (per donor)")
    if title:
        fig.suptitle(title)
    return _save(fig, out)


def plot_h2_histogram(trend_values, out, title=None):
    """H2 figure: distribution of per-gene zonal-slope trend (negative = weakening)."""
    tr = np.asarray(trend_values, float)
    fig, a = plt.subplots(figsize=(5, 3.8))
    a.hist(tr, bins=40, color=PC_COLOR, alpha=0.85)
    a.axvline(0, color=PP_COLOR, lw=2)
    a.axvline(np.nanmedian(tr), color="#222", lw=1.5, ls="--")
    a.set_xlabel("per-gene zonal-slope trend rho  (<0 = weakening)")
    a.set_ylabel("genes")
    if title:
        a.set_title(title)
    return _save(fig, out)


def plot_h3_per_donor(per_donor_df, out, short=None, title=None, col="rho_dez_plast"):
    """H3 figure: per-donor rho(de-zonation, plasticity) vs stage + per-stage mean."""
    short = short or SHORT_STAGES
    dd = per_donor_df
    fig, a = plt.subplots(figsize=(5, 3.8))
    rng = np.random.default_rng(0)
    a.axhline(0, color="#888", ls="--", lw=1)
    a.scatter(dd["stage_rank"] + rng.uniform(-0.08, 0.08, len(dd)), dd[col], s=24, color="#7a4ea8", alpha=0.75)
    mean = dd.groupby("stage_rank")[col].mean()
    a.plot(mean.index, mean.values, "o-", color=PP_COLOR, lw=2)
    a.set_xticks(range(len(short))); a.set_xticklabels(short, rotation=20)
    a.set_ylabel("per-donor rho(de-zonation, plasticity)")
    if title:
        a.set_title(title)
    return _save(fig, out)


def plot_a7_volcano(de_df, out="results/figures/a7_volcano.png"):
    """Volcano: effect (x) vs -log10(q) (y); signature genes flagged.

    Expected input
      de_df : DataFrame with {effect (or rho_vs_stage), q, is_signature}.
    """
    eff_col = "effect" if "effect" in de_df.columns else "rho_vs_stage"
    q = np.clip(de_df["q"].values.astype(float), 1e-300, 1)
    y = -np.log10(q)
    eff = de_df[eff_col].values
    sig = de_df["is_signature"].values.astype(bool) if "is_signature" in de_df.columns \
        else np.zeros(len(de_df), bool)
    fig, ax = plt.subplots(figsize=(6.5, 5))
    ax.scatter(eff[~sig], y[~sig], s=8, alpha=0.4, color="#444", label="other genes")
    ax.scatter(eff[sig], y[sig], s=18, alpha=0.8, color=PP_COLOR, label="signature gene")
    ax.axhline(-np.log10(0.05), color="grey", ls="--", lw=0.8)
    ax.set_xlabel(f"{eff_col} (zonal change vs stage)")
    ax.set_ylabel("-log10(q)")
    ax.set_title("A7 — collapse-driver volcano (H2)")
    ax.legend()
    return _save(fig, out)


def plot_a8_plasticity(coord_df, out="results/figures/a8_plasticity.png"):
    """Stage-stratified scatter of de-zonation vs plasticity.

    Expected input
      coord_df : DataFrame with {dez (or coord), plasticity, stage}.
    """
    if "dez" in coord_df.columns:
        dez = coord_df["dez"].values
    elif "coord" in coord_df.columns:
        c = coord_df["coord"].values
        dez = -np.abs((c - np.median(c)) / (np.std(c) + 1e-9))
    else:
        raise NotImplementedError("A8: coord_df needs a 'dez' or 'coord' column.")
    if "plasticity" not in coord_df.columns or "stage" not in coord_df.columns:
        raise NotImplementedError("A8: coord_df needs 'plasticity' and 'stage' columns.")
    stages = list(dict.fromkeys(coord_df["stage"].tolist()))
    cmap = plt.cm.viridis(np.linspace(0, 1, max(len(stages), 1)))
    fig, ax = plt.subplots(figsize=(6.5, 5))
    for st, col in zip(stages, cmap):
        m = (coord_df["stage"] == st).values
        ax.scatter(dez[m], coord_df["plasticity"].values[m], s=6, alpha=0.3,
                   color=col, label=str(st))
    ax.set_xlabel("de-zonation (higher = more de-zonated)")
    ax.set_ylabel("plasticity score")
    ax.set_title("A8 — de-zonation vs plasticity by stage (H3)")
    ax.legend(markerscale=2, fontsize=8)
    return _save(fig, out)
