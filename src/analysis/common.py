"""Shared loaders + helpers for the biology deep-dive (A/B/C/D). Single source of truth so every
analysis module pulls the SAME coordinates, clinical metadata, raw expression, per-donor summary,
representative donors and staging axes. See PLAN.md.

Key distinction the modules rely on:
  * coords.pc / coords.pp  = per-cell program scores, STANDARDIZED (mean 0, unit var across all cells).
                             Good for anti-correlation / coordinate geometry; CANNOT see global turn-off.
  * raw_arm_means()        = per-cell mean log1p-CP10k over a program's genes, UN-standardized.
                             This is the one that detects expression turn-off (level dropping toward 0).
"""
from __future__ import annotations
import os, sys
import numpy as np, pandas as pd, scipy.sparse as sp
from scipy.stats import spearmanr
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # src/
import config

# ---- palette (shared with the rest of the project) ----
TEAL, RUST, INK, MUTED, RULE = "#1b6e78", "#c05621", "#1a1a1a", "#5a5a5a", "#cdd6d8"
CMAP = "PuOr"                      # pericentral (purple) <-> periportal (orange), centered at 0

# ---- staging vocabulary ----
STAGE_ORDER = ["Healthy control", "NAFLD", "NASH w/o cirrhosis", "NASH with cirrhosis", "end stage"]
STAGE_SHORT = {"Healthy control": "Healthy", "NAFLD": "NAFLD", "NASH w/o cirrhosis": "NASH",
               "NASH with cirrhosis": "Cirrhosis", "end stage": "End-stage"}
S2R = {s: i for i, s in enumerate(STAGE_ORDER)}
FIB_ORDER = [0, 1, 2, 3, 4]
FIB_LABEL = {0: "F0", 1: "F1", 2: "F2", 3: "F3", 4: "F4"}

DEFAULT_SET = "expanded_curated"        # the interpretable co-primary ruler


# ---------------- paths ----------------
def fig_path(group, name):
    """Path under results/figures/<group>/ (group in {h1,h2,confounders,staging}); ensures the dir."""
    base = {"h1": config.FIG_H1, "h2": config.FIG_H2,
            "confounders": config.FIG_CONF, "staging": config.FIG_STAGING}[group]
    os.makedirs(str(base), exist_ok=True)
    return os.path.join(str(base), name)


def table_path(name):
    os.makedirs(str(config.ANALYSIS_TABLES), exist_ok=True)
    return os.path.join(str(config.ANALYSIS_TABLES), name)


def coord_path(which=DEFAULT_SET):
    return os.path.join(str(config.TABLES), which, "coordinates.csv")


# ---------------- coordinates ----------------
def load_coords(which=DEFAULT_SET):
    """Per-cell DataFrame: cell_id, donor(str), stage, coord, pc, pp (pc/pp STANDARDIZED)."""
    df = pd.read_csv(coord_path(which), low_memory=False)
    df["donor"] = df["donor"].astype(str)
    return df[df["coord"].notna() & df["pc"].notna() & df["pp"].notna()].reset_index(drop=True)


# ---------------- clinical metadata (already in the repo; no download) ----------------
_CLIN = None
def load_clinical():
    """Per-cell clinical/QC: cell_id, donor, fibrosis(0-4), nas(0-8), saf(str), depth(nCount),
    n_genes(nFeature), mt(%). Cached. Source: data/processed/paper1/metadata_all_cells.csv."""
    global _CLIN
    if _CLIN is not None:
        return _CLIN
    cols = ["cell_id", "Patient.ID", "SAF.Score", "Steatosis", "Ballooning", "Inflammation",
            "Fibrosis.score..F0.4.", "nCount_RNA", "nFeature_RNA", "percent.mt.RNA"]
    m = pd.read_csv(os.path.join(str(config.PAPER1), "metadata_all_cells.csv"),
                    usecols=cols, low_memory=False)
    m = m.rename(columns={"Patient.ID": "donor", "Fibrosis.score..F0.4.": "fibrosis",
                          "SAF.Score": "saf", "nCount_RNA": "depth",
                          "nFeature_RNA": "n_genes", "percent.mt.RNA": "mt"})
    m["donor"] = m["donor"].astype(str)
    for c in ["Steatosis", "Ballooning", "Inflammation"]:
        m[c] = pd.to_numeric(m[c], errors="coerce")
    m["nas"] = m[["Steatosis", "Ballooning", "Inflammation"]].sum(axis=1, min_count=1)
    m["fibrosis"] = pd.to_numeric(m["fibrosis"], errors="coerce")
    _CLIN = m[["cell_id", "donor", "fibrosis", "nas", "saf", "depth", "n_genes", "mt"]]
    return _CLIN


def attach_clinical(coords):
    """coords + per-cell fibrosis/nas/saf/depth/n_genes/mt (merged on cell_id)."""
    cl = load_clinical().drop(columns="donor")
    return coords.merge(cl, on="cell_id", how="left")


# ---------------- signature gene lists + raw expression ----------------
def gene_lists(which=DEFAULT_SET):
    """(PC_genes, PP_genes) for a candidate set from signatures/candidates/."""
    cand = config.SIGNATURES / "candidates"
    def rd(p):
        return [l.strip() for l in open(str(p)) if l.strip()] if os.path.exists(str(p)) else []
    return rd(cand / f"pericentral_{which}.txt"), rd(cand / f"periportal_{which}.txt")


_P1 = None
def _p1_matrix():
    """Paper-1 hepatocyte counts: (M csr genes x cells, genes[], barcodes[], libsize[]). Cached."""
    global _P1
    if _P1 is not None:
        return _P1
    M = sp.load_npz(os.path.join(str(config.PAPER1), "counts.npz")).tocsr()
    genes = np.array([g.strip() for g in open(os.path.join(str(config.PAPER1), "genes.txt"))])
    bars = np.array([b.strip() for b in open(os.path.join(str(config.PAPER1), "barcodes.txt"))])
    lib = np.asarray(M.sum(0)).ravel().astype(float)
    lib[lib <= 0] = 1.0
    _P1 = (M, genes, bars, lib)
    return _P1


def raw_gene_matrix(genes):
    """Per-cell raw log1p-CP10k expression, one column per requested gene present (UN-standardized).
    DataFrame indexed by cell_id. For marker profiles (A3) and gene x cell heatmaps (B1/B2).
    Memory-safe-ish: densifies only the requested gene block (keep the list to <~500 genes)."""
    M, allg, bars, lib = _p1_matrix()
    g2i = {g: i for i, g in enumerate(allg)}
    keep = [g for g in genes if g in g2i]
    if not keep:
        return pd.DataFrame(index=pd.Index(bars, name="cell_id"))
    sub = M[[g2i[g] for g in keep]].tocsr().astype(np.float64)
    sub = sub.multiply((1.0 / lib)[None, :]).multiply(1e4).tocsr()
    sub.data = np.log1p(sub.data)
    D = np.asarray(sub.todense()).T                       # cells x genes
    return pd.DataFrame(D, columns=keep, index=pd.Index(bars, name="cell_id"))


def raw_arm_means(pc_genes, pp_genes):
    """Per-cell mean log1p-CP10k over present PC genes and over present PP genes, UN-standardized
    (so a global drop toward 0 = turn-off is visible). Returns DataFrame[cell_id, pc_raw, pp_raw]."""
    M, genes, bars, lib = _p1_matrix()
    g2i = {g: i for i, g in enumerate(genes)}
    inv_lib = (1.0 / lib)[None, :]                         # (1, cells) for column broadcast
    def arm(gl):
        idx = [g2i[g] for g in gl if g in g2i]
        if not idx:
            return np.zeros(M.shape[1])
        sub = M[idx].tocsr().astype(np.float64)            # present x cells (sparse, no densify)
        sub = sub.multiply(inv_lib).multiply(1e4).tocsr()  # CP10k per cell
        sub.data = np.log1p(sub.data)                      # log1p on nonzeros (zeros -> log1p(0)=0)
        return np.asarray(sub.sum(0)).ravel() / len(idx)   # mean of log1p over the arm's genes
    return pd.DataFrame({"cell_id": bars, "pc_raw": arm(pc_genes), "pp_raw": arm(pp_genes)})


# ---------------- per-donor summary ----------------
def donor_summary(which=DEFAULT_SET, with_raw=True):
    """One row per donor: stage, stage_rank, fibrosis, nas, depth_med, n_cells, and the H1 readouts
    sd / iqr / coord_range / anticorr (+ raw program means pc_raw/pp_raw if with_raw). Sorted by
    stage then fibrosis then n_cells."""
    coords = load_coords(which)
    clin = load_clinical()
    dc = clin.groupby("donor").agg(fibrosis=("fibrosis", "median"), nas=("nas", "median"),
                                   depth_med=("depth", "median"),
                                   genes_med=("n_genes", "median")).reset_index()
    if with_raw:
        pcg, ppg = gene_lists(which)
        coords = coords.merge(raw_arm_means(pcg, ppg), on="cell_id", how="left")
    rows = []
    for d, sub in coords.groupby("donor"):
        st = sub["stage"].mode().iat[0]
        c = sub["coord"].values
        ac = float(spearmanr(sub["pc"], sub["pp"]).statistic) if sub["pc"].std() > 0 else np.nan
        row = dict(donor=str(d), stage=st, stage_rank=S2R.get(st, -1), n_cells=len(sub),
                   sd=float(np.std(c)),
                   iqr=float(np.percentile(c, 75) - np.percentile(c, 25)),
                   coord_range=float(np.percentile(c, 95) - np.percentile(c, 5)),
                   anticorr=ac)
        if with_raw:
            row["pc_raw"] = float(np.nanmean(sub["pc_raw"]))
            row["pp_raw"] = float(np.nanmean(sub["pp_raw"]))
            row["prog_raw"] = float(np.nanmean([row["pc_raw"], row["pp_raw"]]))
        rows.append(row)
    s = pd.DataFrame(rows).merge(dc, on="donor", how="left")
    return s.sort_values(["stage_rank", "fibrosis", "n_cells"]).reset_index(drop=True)


# ---------------- staging axes + representatives ----------------
def staging_levels(summary, axis="stage"):
    """Ordered list of (label, [donor ids]) for axis in {stage, fibrosis, nas}."""
    if axis == "stage":
        return [(STAGE_SHORT[s], summary.loc[summary.stage == s, "donor"].tolist())
                for s in STAGE_ORDER if (summary.stage == s).any()]
    if axis == "fibrosis":
        return [(FIB_LABEL[f], summary.loc[summary.fibrosis == f, "donor"].tolist())
                for f in FIB_ORDER if (summary.fibrosis == f).any()]
    if axis == "nas":
        return [(f"NAS{int(n)}", summary.loc[summary.nas == n, "donor"].tolist())
                for n in sorted(summary.nas.dropna().unique())]
    raise ValueError(axis)


def representatives(which=DEFAULT_SET, axis="stage", strategy="best_powered", min_cells=400):
    """One representative donor per axis level (selection is OUTCOME-INDEPENDENT — never by
    anti-correlation/zonation strength — so it can't cherry-pick the result; the contact sheet
    remains the honest full view). Strategies (all restrict to n>=min_cells when possible):
      'best_powered'  = highest median sequencing depth  (DEFAULT — zonation is under-powered at low
                        depth, so show the best-measured donor per level; depth does not track stage).
      'depth_matched' = depth closest to the cohort median (panels comparable, but can land on a
                        low-depth, under-powered donor).
      'max_n'         = the largest donor.
    Returns [(level_label, donor_id), ...]."""
    s = donor_summary(which, with_raw=False)
    target = float(np.nanmedian(s["depth_med"]))
    out = []
    for label, donors in staging_levels(s, axis):
        cand = s[s.donor.isin(donors) & (s.n_cells >= min_cells)]
        if not len(cand):
            cand = s[s.donor.isin(donors)]
        if not len(cand):
            continue
        if strategy == "best_powered":
            d = cand.sort_values("depth_med").iloc[-1]["donor"]
        elif strategy == "depth_matched":
            d = cand.iloc[(cand["depth_med"] - target).abs().values.argsort()[0]]["donor"]
        else:
            d = cand.sort_values("n_cells").iloc[-1]["donor"]
        out.append((label, str(d)))
    return out


if __name__ == "__main__":          # smoke test
    s = donor_summary()
    print(f"donor_summary: {len(s)} donors, cols={list(s.columns)}")
    print(s[["donor", "stage", "fibrosis", "nas", "n_cells", "depth_med",
             "sd", "anticorr", "prog_raw"]].head(8).to_string(index=False))
    print("\nrepresentatives by stage (depth-matched):", representatives(axis="stage"))
    print("representatives by fibrosis (depth-matched):", representatives(axis="fibrosis"))
