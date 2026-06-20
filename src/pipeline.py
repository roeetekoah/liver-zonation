#!/usr/bin/env python3
"""
Spatial Degradation of Hepatocyte Zonation — pipeline (Steps 2-8), DONOR-LEVEL.

KEY STATISTICAL RULE (read this): the unit of inference is the DONOR (47 biopsies),
NOT the cell (~69k). Cell-level p-values are pseudoreplication and are statistically
invalid here. So:
  * H1 collapse: compute one metric PER DONOR, then test the trend across stages on
    those donor values (+ donor-level bootstrap, + donor-level label shuffle).
  * H2 DE: PSEUDOBULK per donor x zone, then test the stage effect on those aggregates.
  * H3 plasticity: test WITHIN stage/donor (or regress out stage+donor), never pooled.

Inputs: data/processed/paper1/{counts.mtx, genes.txt, barcodes.txt, cell_metadata.csv,
        metadata_all_cells.csv}, signatures/{pericentral,periportal}_core.txt
Outputs: results/tables/{coordinates.csv, collapse_per_donor.csv, de_*.csv},
         results/figures/*.png
Memory: scipy.io.mmread loads the full sparse matrix (~8-12 GB for the real file).
Run from the src/ folder:  python pipeline.py
"""
import os, sys, numpy as np, pandas as pd, scipy.io, scipy.sparse as sp
from scipy.stats import spearmanr, rankdata
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
try:
    from statsmodels.stats.multitest import multipletests
    import statsmodels.formula.api as smf
except Exception:
    multipletests = None; smf = None

P1 = str(config.PAPER1)
OUT = str(config.TABLES); os.makedirs(OUT, exist_ok=True)
STAGE_ORDER = ["Healthy control", "NAFLD", "NASH w/o cirrhosis", "NASH with cirrhosis", "end stage"]
SHORT = ["Healthy", "NAFLD", "NASH", "Cirrhosis", "End-stage"]
S2R = {s: i for i, s in enumerate(STAGE_ORDER)}
PLAST = ["KRT7", "KRT19", "SOX9", "SOX4", "KRT23", "NCAM1"]
VAL = {"pericentral": ["CYP2E1", "CYP1A2", "GLUL", "PCK2"],     # PCK2 is pericentral in humans
       "periportal":  ["ASS1", "ALDOB", "PCK1", "HAL"]}
DONOR_COLS = ["Patient.ID", "patient", "donor", "orig.ident", "sample"]

def log(m): print(m, flush=True)
def bh(p):
    p = np.asarray(p, float)
    if multipletests is not None: return multipletests(np.nan_to_num(p, nan=1.0), method="fdr_bh")[1]
    n = len(p); o = np.argsort(p); q = np.empty(n)
    q[o] = np.minimum.accumulate((p[o]*n/np.arange(n,0,-1))[::-1])[::-1]; return np.clip(q,0,1)

# ---------- Step 2: load (now also reads DONOR) ----------
def load():
    log("Step 2: load Paper 1 hepatocytes ...")
    M = scipy.io.mmread(os.path.join(P1, "counts.mtx")).tocsc()
    genes = np.array([g.strip() for g in open(os.path.join(P1, "genes.txt"))])
    bars  = np.array([b.strip() for b in open(os.path.join(P1, "barcodes.txt"))])
    meta  = pd.read_csv(os.path.join(P1, "cell_metadata.csv")).set_index("cell_id").reindex(bars)
    stage = meta["stage"].astype(str).values
    allm  = pd.read_csv(os.path.join(P1, "metadata_all_cells.csv")).set_index("cell_id")
    dcol  = next((c for c in DONOR_COLS if c in allm.columns), None)
    donor = allm[dcol].astype(str).reindex(bars).values if dcol else np.array(["NA"]*len(bars))
    log(f"  donor column = {dcol}; {len(np.unique(donor))} donors")
    libsize = np.asarray(M.sum(0)).ravel()
    return M, genes, bars, stage, donor, libsize

def zrows(M, genes, libsize, wanted):
    gi = {g: i for i, g in enumerate(genes)}; out = {}
    for g in wanted:
        if g in gi:
            v = np.log1p(np.asarray(M.getrow(gi[g]).todense()).ravel().astype(float)/libsize*1e4)
            sd = v.std(); out[g] = (v-v.mean())/sd if sd>0 else v*0
    return out

# ---------- Steps 3-4a: score ----------
def score(M, genes, libsize):
    log("Steps 3-4a: signature scoring ...")
    PC = [g.strip() for g in open(str(config.PC_GENES)) if g.strip()]
    PP = [g.strip() for g in open(str(config.PP_GENES)) if g.strip()]
    col = zrows(M, genes, libsize, set(PC+PP+PLAST+VAL["pericentral"]+VAL["periportal"]))
    pc = np.mean([col[g] for g in PC if g in col], axis=0)
    pp = np.mean([col[g] for g in PP if g in col], axis=0)
    coord = pc-pp
    plast = np.mean([col[g] for g in PLAST if g in col], axis=0) if any(g in col for g in PLAST) else np.zeros_like(coord)
    return coord, pc, pp, plast, col, set(PC+PP)

# ---------- Step 5: validate on healthy ----------
def validate(coord, col, stage):
    log("Step 5: healthy validation (positive control)")
    h = stage == STAGE_ORDER[0]
    if h.sum() < 20: log("  (few healthy cells)"); return
    ZTAG = {"pericentral": "PC (expect +)", "periportal": "PP (expect -)"}
    for z, gl in VAL.items():
        for g in gl:
            if g in col: log(f"  healthy rho(coord,{g:6s})={spearmanr(coord[h],col[g][h]).statistic:+.3f} {ZTAG[z]}")

# ---------- Step 6: DONOR-LEVEL collapse ----------
def collapse(coord, pc, pp, stage, donor):
    log("Step 6: collapse — metrics PER DONOR, then trend across stages")
    rows = []
    for d in np.unique(donor):
        m = donor == d
        if m.sum() < 30: continue
        st = pd.Series(stage[m]).mode().iat[0]
        if st not in S2R: continue
        rows.append({"donor": d, "stage": st, "stage_rank": S2R[st], "n": int(m.sum()),
                     "spread": float(np.nanstd(coord[m])),
                     "anticorr": float(spearmanr(pc[m], pp[m]).statistic)})
    dd = pd.DataFrame(rows); dd.to_csv(os.path.join(OUT,"collapse_per_donor.csv"), index=False)
    log(f"  {len(dd)} donors usable")
    for metric, direction in [("spread","down"),("anticorr","up→0")]:
        rho, p = spearmanr(dd["stage_rank"], dd[metric])
        # donor bootstrap CI on rho
        bs = [spearmanr(*(lambda s: (dd["stage_rank"].values[s], dd[metric].values[s]))(np.random.randint(0,len(dd),len(dd)))).statistic for _ in range(2000)]
        lo, hi = np.nanpercentile(bs, [2.5, 97.5])
        # donor-level label shuffle (negative control)
        null = [abs(spearmanr(np.random.permutation(dd["stage_rank"].values), dd[metric].values).statistic) for _ in range(2000)]
        pperm = (np.sum(np.array(null) >= abs(rho))+1)/(len(null)+1)
        log(f"  {metric:9s} vs stage: rho={rho:+.3f} (95%CI {lo:+.2f},{hi:+.2f}) p={p:.3g} perm_p={pperm:.3g}  [{direction}]")
    # figure: donor points + per-stage mean
    fig, ax = plt.subplots(1,2,figsize=(10,3.8))
    for i,(metric,t) in enumerate([("spread","coordinate spread (per donor)"),("anticorr","PC–PP corr (per donor)")]):
        ax[i].scatter(dd["stage_rank"]+np.random.uniform(-.08,.08,len(dd)), dd[metric], s=22, color="#1b6e78", alpha=.7)
        mean = dd.groupby("stage_rank")[metric].mean()
        ax[i].plot(mean.index, mean.values, "o-", color="#c05621", lw=2)
        ax[i].set_xticks(range(5)); ax[i].set_xticklabels(SHORT, rotation=20); ax[i].set_title(t)
    plt.tight_layout(); plt.savefig(os.path.join(str(config.FIGURES),"collapse.png"), dpi=130)
    return dd

# ---------- Step 7: PSEUDOBULK donor x zone DE ----------
def de(M, genes, libsize, coord, stage, donor, sig_genes, min_frac=0.10):
    log("Step 7: pseudobulk (donor x zone) DE across stages — heavy step")
    terc = np.quantile(coord, [1/3, 2/3]); zone = np.digitize(coord, terc)  # 0 portal,1 mid,2 central
    sr = np.array([S2R.get(s,-1) for s in stage]); ok = sr>=0
    G = len(genes); res = {}
    # normalized matrix lazily per gene-chunk to build pseudobulk (donor x zone) means
    for zid, zname in [(0,"portal"),(2,"central")]:
        cells = np.where(ok & (zone==zid))[0]
        keys = list(zip(donor[cells], )) ;
        grp = pd.DataFrame({"i":cells, "donor":donor[cells], "rank":sr[cells]})
        gb = grp.groupby("donor")
        donors = [d for d,idx in gb.groups.items() if len(idx)>=20]
        if len(donors) < 6: log(f"  zone {zname}: too few donors ({len(donors)})"); continue
        didx = {d: grp.index[grp.donor==d].values for d in donors}
        ranks = np.array([sr[cells[grp.index[grp.donor==d][0]]] for d in donors])  # donor stage rank
        # pseudobulk mean log1p-CP10k per donor for all genes (chunked)
        PBcols = []
        cols_cells = {d: cells[grp.index[grp.donor==d].values] for d in donors}
        PB = np.zeros((len(donors), G), np.float32)
        for j,d in enumerate(donors):
            cc = cols_cells[d]; sub = M[:, cc]
            cp = np.asarray(sub.sum(0)).ravel();
            x = sub.multiply(1.0/np.where(cp>0,cp,1)).tocsc()  # per-cell CP1
            pbmean = np.asarray(x.mean(1)).ravel()*1e4
            PB[j] = np.log1p(pbmean)
        det = (PB>0).mean(0) >= min_frac
        rho = np.full(G, np.nan); pv = np.ones(G)
        for g in np.where(det)[0]:
            if PB[:,g].std()>0: rho[g], pv[g] = spearmanr(PB[:,g], ranks)
        q = bh(pv)
        d = pd.DataFrame({"gene":genes,"rho_vs_stage":rho,"p":pv,"q":q,
                          "is_signature":[g in sig_genes for g in genes]}).dropna().sort_values("q")
        d.to_csv(os.path.join(OUT,f"de_{zname}.csv"), index=False)
        nsig = int((d["q"]<0.05).sum()); nsig_nonsig = int(((d["q"]<0.05) & (~d["is_signature"])).sum())
        log(f"  zone {zname}: {len(donors)} donors, {nsig} genes q<0.05 ({nsig_nonsig} excluding signature genes)")
        res[zname]=d
    return res

# ---------- Step 8: plasticity WITHIN donor/stage ----------
def plasticity(coord, plast, stage, donor):
    log("Step 8: de-zonation vs plasticity — within donor/stage")
    if np.allclose(plast.std(),0): log("  (no plasticity markers)"); return
    dez = -np.abs((coord-np.median(coord))/ (np.std(coord)+1e-9))  # near-middle => more de-zonated (proxy)
    # per-donor correlation (within donor removes stage/donor confound)
    rs = []
    for d in np.unique(donor):
        m = donor==d
        if m.sum()>=30 and plast[m].std()>0: rs.append(spearmanr(dez[m], plast[m]).statistic)
    rs = np.array(rs)
    log(f"  per-donor rho(de-zonation, plasticity): mean={np.nanmean(rs):+.3f}  (>0 in {np.mean(rs>0)*100:.0f}% of {len(rs)} donors)")
    if smf is not None:
        df = pd.DataFrame({"plast":plast,"dez":dez,"stage":stage,"donor":donor})
        try:
            r = smf.ols("plast ~ dez + C(stage) + C(donor)", data=df).fit()
            log(f"  OLS plast~dez+stage+donor: dez beta={r.params.get('dez',np.nan):+.3f} p={r.pvalues.get('dez',np.nan):.3g}")
        except Exception as e: log(f"  (OLS skipped: {e})")

def main():
    M, genes, bars, stage, donor, libsize = load()
    coord, pc, pp, plast, col, sig = score(M, genes, libsize)
    pd.DataFrame({"cell_id":bars,"donor":donor,"stage":stage,"coord":coord,"pc":pc,"pp":pp,
                  "plasticity":plast}).to_csv(os.path.join(OUT,"coordinates.csv"), index=False)
    validate(coord, col, stage)
    collapse(coord, pc, pp, stage, donor)
    de(M, genes, libsize, coord, stage, donor, sig)
    plasticity(coord, plast, stage, donor)
    log(f"\nDone. Outputs in {OUT}")

if __name__ == "__main__":
    main()
