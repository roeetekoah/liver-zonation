#!/usr/bin/env python3
"""
Spatial Degradation of Hepatocyte Zonation — prep-day pipeline (Steps 2-8, baseline).
Consumes the R-extracted Paper 1 hepatocytes + the Paper 2 landmark-gene signatures.

Inputs (relative to the Hackathon folder):
  analysis/paper1/counts.mtx          genes x cells raw counts (writeMM)
  analysis/paper1/genes.txt           gene symbols, row order of the mtx
  analysis/paper1/barcodes.txt        cell ids, column order of the mtx
  analysis/paper1/cell_metadata.csv   cell_id, cell_type, stage
  analysis/pericentral_genes.txt      pericentral signature (Paper 2 landmarks)
  analysis/periportal_genes.txt       periportal signature

Outputs: analysis/out/{coordinates.csv, collapse.csv, de_*.csv, *.png, RESULTS.txt}

NOTE ON MEMORY: scipy.io.mmread loads the full sparse matrix (~8-12 GB RAM for the
real file). Close other apps. Steps 2-6 need only the signature genes and are light;
Step 7 (DE) touches all genes and is the heavy/slow part (a few minutes).

Run from the Hackathon folder:   python analysis/pipeline.py
"""
import os, sys, numpy as np, pandas as pd, scipy.io, scipy.sparse as sp
from scipy.stats import spearmanr, mannwhitneyu, rankdata
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
try:
    from statsmodels.stats.multitest import multipletests
except Exception:
    multipletests = None  # BH fallback implemented below

HERE = os.path.dirname(os.path.abspath(__file__))
P1   = os.path.join(HERE, "paper1")
OUT  = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
STAGE_ORDER = ["Healthy control", "NAFLD", "NASH w/o cirrhosis", "NASH with cirrhosis", "end stage"]
STAGE_SHORT = ["Healthy", "NAFLD", "NASH", "Cirrhosis", "End-stage"]
PLAST = ["KRT7", "KRT19", "SOX9", "SOX4", "KRT23", "NCAM1"]   # H3 plasticity markers
VAL   = {"pericentral": ["CYP2E1", "CYP1A2", "GLUL", "OAT"],   # independent validation markers
         "periportal":  ["ASS1", "SDS", "HAL", "PCK1"]}

def log(m): print(m, flush=True)

def bh(p):
    if multipletests is not None: return multipletests(p, method="fdr_bh")[1]
    p = np.asarray(p); n = len(p); o = np.argsort(p); q = np.empty(n)
    q[o] = np.minimum.accumulate((p[o] * n / (np.arange(n, 1-1e-9, -1)))[::-1])[::-1]
    return np.clip(q, 0, 1)

# ---------- Step 2: load ----------
def load():
    log("Step 2: loading Paper 1 hepatocytes ...")
    M = scipy.io.mmread(os.path.join(P1, "counts.mtx")).tocsc()          # genes x cells
    genes = np.array([g.strip() for g in open(os.path.join(P1, "genes.txt"))])
    bars  = np.array([b.strip() for b in open(os.path.join(P1, "barcodes.txt"))])
    meta  = pd.read_csv(os.path.join(P1, "cell_metadata.csv")).set_index("cell_id").reindex(bars)
    stage = meta["stage"].astype(str).values
    libsize = np.asarray(M.sum(axis=0)).ravel()                          # per-cell total UMIs
    log(f"  {M.shape[0]} genes x {M.shape[1]} cells; stages: {dict(pd.Series(stage).value_counts())}")
    return M, genes, bars, stage, libsize

# ---------- Step 3/4a: normalize signature genes + score ----------
def zrows(M, genes, libsize, wanted):
    """CP10k -> log1p -> per-gene z, for a small set of genes; returns dict gene->vector."""
    gi = {g: i for i, g in enumerate(genes)}
    out = {}
    for g in wanted:
        if g in gi:
            v = np.asarray(M.getrow(gi[g]).todense()).ravel().astype(float)
            v = np.log1p(v / libsize * 1e4)
            sd = v.std(); out[g] = (v - v.mean()) / sd if sd > 0 else v * 0
    return out

def score(M, genes, libsize):
    log("Step 3-4a: signature scoring ...")
    PC = [g.strip() for g in open(os.path.join(HERE, "pericentral_genes.txt")) if g.strip()]
    PP = [g.strip() for g in open(os.path.join(HERE, "periportal_genes.txt")) if g.strip()]
    need = set(PC + PP + PLAST + VAL["pericentral"] + VAL["periportal"])
    col = zrows(M, genes, libsize, need)
    pc = np.mean([col[g] for g in PC if g in col], axis=0)
    pp = np.mean([col[g] for g in PP if g in col], axis=0)
    coord = pc - pp
    plast = np.mean([col[g] for g in PLAST if g in col], axis=0) if any(g in col for g in PLAST) else np.zeros_like(coord)
    return coord, pc, pp, plast, col

# ---------- Step 5: validate on healthy ----------
def validate(coord, col, stage):
    log("Step 5: validation on healthy donors (positive control)")
    h = stage == STAGE_ORDER[0]
    if h.sum() < 20: log("  (few healthy cells)"); return
    for z, gl in VAL.items():
        for g in gl:
            if g in col:
                log(f"  healthy rho(coord, {g:6s}) = {spearmanr(coord[h], col[g][h]).statistic:+.3f}  ({z[:4]} expect {'+' if z=='pericentral' else '-'})")

# ---------- Step 5b: ruler-validity diagnostics ----------
def ruler(pc, pp, stage):
    log("Step 5b: ruler-validity per stage (internal coherence proxy + PC/PP anti-corr)")
    rows = []
    for st, sh in zip(STAGE_ORDER, STAGE_SHORT):
        m = stage == st
        if m.sum() < 20: continue
        ac = spearmanr(pc[m], pp[m]).statistic
        rows.append((sh, int(m.sum()), ac)); log(f"  {sh:10s} n={m.sum():6d}  PC-PP corr={ac:+.3f}")
    return rows

# ---------- Step 6: collapse curve + trend ----------
def collapse(coord, pc, pp, stage):
    log("Step 6: collapse metrics across stages")
    rows = []
    for st, sh in zip(STAGE_ORDER, STAGE_SHORT):
        m = stage == st
        if m.sum() < 20: continue
        rows.append({"stage": sh, "n": int(m.sum()), "spread": float(coord[m].std()),
                     "pc_pp_corr": float(spearmanr(pc[m], pp[m]).statistic)})
    df = pd.DataFrame(rows); rk = np.arange(len(df))
    tr_spread = spearmanr(rk, df["spread"]).statistic
    tr_anti   = spearmanr(rk, df["pc_pp_corr"]).statistic
    log(f"  TREND coord-spread vs stage: rho={tr_spread:+.3f}")
    log(f"  TREND PC-PP corr  vs stage: rho={tr_anti:+.3f}")
    df.to_csv(os.path.join(OUT, "collapse.csv"), index=False)
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    ax[0].plot(df["stage"], df["spread"], "o-", color="#1b6e78"); ax[0].set_title("Coordinate spread (std) per stage"); ax[0].tick_params(axis="x", rotation=20)
    ax[1].plot(df["stage"], df["pc_pp_corr"], "o-", color="#c05621"); ax[1].set_title("PC-PP correlation per stage"); ax[1].tick_params(axis="x", rotation=20)
    plt.tight_layout(); plt.savefig(os.path.join(OUT, "collapse.png"), dpi=130)
    return df

# ---------- Step 7: zone-resolved DE across stages (FDR) ----------
def de(M, genes, libsize, coord, stage, min_frac=0.10, chunk=2000):
    log("Step 7: zone-binned differential expression vs stage (FDR) — heavy step")
    stage_rank = np.array([STAGE_ORDER.index(s) if s in STAGE_ORDER else -1 for s in stage])
    keep = stage_rank >= 0
    terc = np.quantile(coord[keep], [1/3, 2/3])
    zone = np.digitize(coord, terc)                      # 0 portal-ish, 1 mid, 2 central-ish
    res = {}
    for zid, zname in [(0, "portal"), (2, "central")]:   # the two ends carry the signal
        cells = np.where(keep & (zone == zid))[0]
        sr = stage_rank[cells]
        rho = np.full(len(genes), np.nan); pv = np.ones(len(genes))
        for s in range(0, len(genes), chunk):
            e = min(s + chunk, len(genes))
            D = np.asarray(M[s:e][:, cells].todense()).astype(float)
            D = np.log1p(D / libsize[cells] * 1e4)
            det = (D > 0).mean(1) >= min_frac
            for j in range(e - s):
                if det[j] and D[j].std() > 0:
                    r, p = spearmanr(D[j], sr); rho[s + j], pv[s + j] = r, p
        q = bh(np.nan_to_num(pv, nan=1.0))
        d = pd.DataFrame({"gene": genes, "rho_vs_stage": rho, "p": pv, "q": q}).dropna().sort_values("q")
        d.to_csv(os.path.join(OUT, f"de_{zname}.csv"), index=False)
        nsig = int((d["q"] < 0.05).sum())
        log(f"  zone={zname}: {len(cells)} cells, {nsig} genes q<0.05")
        res[zname] = d
    return res

# ---------- Step 8: de-zonation <-> plasticity ----------
def plasticity(coord, plast, stage):
    log("Step 8: de-zonation vs plasticity link")
    dz = np.abs(coord - np.median(coord))          # ambiguous/de-zonated = far from typical? use |coord| proxy
    # define de-zonated = middle tercile of coord (ambiguous), zonated = extremes
    terc = np.quantile(coord, [1/3, 2/3])
    mid = (coord >= terc[0]) & (coord <= terc[1])
    ends = ~mid
    if plast.std() == 0: log("  (no plasticity markers found)"); return
    U, p = mannwhitneyu(plast[mid], plast[ends], alternative="greater")
    r = spearmanr(np.abs(coord), plast).statistic
    log(f"  plasticity higher in de-zonated (mid) than zonated (ends)? Mann-Whitney p={p:.2e}")
    log(f"  corr(|coord|, plasticity) = {r:+.3f}")

def main():
    M, genes, bars, stage, libsize = load()
    coord, pc, pp, plast, col = score(M, genes, libsize)
    pd.DataFrame({"cell_id": bars, "stage": stage, "coord": coord,
                  "pc": pc, "pp": pp, "plasticity": plast}).to_csv(os.path.join(OUT, "coordinates.csv"), index=False)
    validate(coord, col, stage)
    ruler(pc, pp, stage)
    collapse(coord, pc, pp, stage)
    de(M, genes, libsize, coord, stage)
    plasticity(coord, plast, stage)
    log(f"\nDone. Outputs in {OUT}")

if __name__ == "__main__":
    main()
