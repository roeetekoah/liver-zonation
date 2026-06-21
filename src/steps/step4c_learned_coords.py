"""Step 4c — LEARNED zonation coordinates over (near) the whole transcriptome.

Two modes, both alternatives to the fixed signature-mean scoring:
  * supervised()   — multinomial logistic regression trained on Paper 2 zone labels over all
                     shared+expressed genes (landmarks EXCLUDED). Learns "which gene combination
                     best predicts zonation", applied to Paper 1 -> predicted zone + entropy.
  * unsupervised() — NO labels. PCA on HEALTHY Paper 1 hepatocytes; the leading expression axis
                     is the porto-central axis (the two anti-correlated gene subsets = + vs -
                     loadings). Realizes "learn the two subsets with the best PC-PP anticorrelation".

Memory-safe: features restricted to genes expressed in >=MIN_FRAC of Paper 1 hepatocytes and
present in the Paper 2 atlas; float32 throughout. Run from src/:
    python steps/step4c_learned_coords.py supervised
    python steps/step4c_learned_coords.py unsupervised
"""
from __future__ import annotations
import os, sys, gc
import numpy as np, pandas as pd, scipy.sparse as sp, h5py
from scipy.stats import spearmanr, entropy as shannon
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.decomposition import PCA
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # src/
import config
from steps.common import log, OUT, STAGE_ORDER, S2R, _is_na, VAL

MIN_FRAC = 0.05           # gene must be expressed in >= this fraction of Paper 1 hep cells
ZONE_NAME = {0: "periportal", 1: "mid", 2: "pericentral"}   # per 02_convert: 0=high eta=PP, 2=PC


def _p2_atlas_genes():
    f = h5py.File(str(config.DATA_RAW / "combined_scRNAseq_atlas_M5M6M7M8.mat"), "r"); t = f["t"]
    dref = lambda r: "".join(chr(int(c)) for c in f[r][:].flatten())
    return set(dref(t["gene_name"][0, i]) for i in range(t["gene_name"].shape[1]))


def _landmarks():
    lm = set()
    for p in config.signature_files("paper2_landmark"):
        lm.update(g.strip() for g in open(str(p)) if g.strip())
    return lm


def _p1():
    """Paper 1 hepatocytes: M (CSR genes x cells, csr), genes[], libsize, stage, bars, donor."""
    M = sp.load_npz(str(config.PAPER1 / "counts.npz")).tocsr()
    genes = np.array([g.strip() for g in open(str(config.PAPER1 / "genes.txt"))])
    bars = np.array([b.strip() for b in open(str(config.PAPER1 / "barcodes.txt"))])
    stage = pd.read_csv(str(config.PAPER1 / "cell_metadata.csv")).set_index("cell_id").reindex(bars)["stage"].values
    allm = pd.read_csv(str(config.PAPER1 / "metadata_all_cells.csv"), low_memory=False).set_index("cell_id")
    donor = allm["Patient.ID"].astype(str).reindex(bars).values
    lib = np.asarray(M.sum(0)).ravel()
    return M, genes, lib, stage, bars, donor


def build_feature_genes(M, genes, min_frac, exclude_landmarks):
    det = np.asarray((M > 0).sum(1)).ravel() / M.shape[1]
    p2 = _p2_atlas_genes(); lm = _landmarks() if exclude_landmarks else set()
    feats = [g for g, d in zip(genes, det) if d >= min_frac and g in p2 and g not in lm]
    return feats


def _z_dense_p1(M, genes, lib, feats):
    """cells x feats, per-gene z-scored log1p-CP10k, float32."""
    g2i = {g: i for i, g in enumerate(genes)}
    rows = [g2i[g] for g in feats]
    D = np.asarray(M[rows].todense(), dtype=np.float32)              # feats x cells
    D = np.log1p(D / lib.astype(np.float32) * np.float32(1e4))
    mu = D.mean(1, keepdims=True); sd = D.std(1, keepdims=True); sd[sd == 0] = 1
    Z = ((D - mu) / sd).T.astype(np.float32)                         # cells x feats
    del D; gc.collect()
    return Z


def _markers_z(M, genes, lib):
    g2i = {g: i for i, g in enumerate(genes)}
    out = {}
    for g in VAL["pericentral"] + VAL["periportal"]:
        if g in g2i:
            v = np.log1p(np.asarray(M.getrow(g2i[g]).todense()).ravel() / lib * 1e4)
            out[g] = v
    return out


def _validate_and_h1(coord, M, genes, lib, stage, donor, tag):
    mk = _markers_z(M, genes, lib); h = stage == STAGE_ORDER[0]
    log(f"  [{tag}] healthy validation (PC expect +, PP expect -):")
    for zone, sgn in [("pericentral", "+"), ("periportal", "-")]:
        for g in VAL[zone]:
            if g in mk:
                rho = spearmanr(coord[h], mk[g][h]).statistic
                ok = "ok" if (rho > 0) == (sgn == "+") else "WRONG"
                log(f"    {g:7s} rho={rho:+.3f} expect {sgn} [{ok}]")
    rows = []
    for d in np.unique(donor):
        m = donor == d
        if _is_na([d]).iat[0] or m.sum() < 30: continue
        st = pd.Series(stage[m]).mode().iat[0]
        if st not in S2R: continue
        rows.append((S2R[st], np.nanstd(coord[m])))
    dd = np.array(rows)
    rho, p = spearmanr(dd[:, 0], dd[:, 1])
    log(f"  [{tag}] H1 coord-spread vs stage: rho={rho:+.3f} p={p:.3g} (expect <0) over {len(dd)} donors")


def supervised(min_frac=MIN_FRAC):
    log(f"Step 4c SUPERVISED: whole-transcriptome logistic regression [min_frac={min_frac}]")
    M, genes, lib, stage, bars, donor = _p1()
    feats = build_feature_genes(M, genes, min_frac, exclude_landmarks=True)
    log(f"  features = {len(feats)} genes (shared & expressed & landmarks excluded)")
    from steps.step4b_classifier import load_p2
    Xp2, fp2 = load_p2(feats)                                        # cells x fp2 (atlas order subset)
    d = np.load(str(config.PAPER2_TRAIN), allow_pickle=True)
    y = d["zone_label"]
    assert Xp2.shape[0] == len(y), f"P2 cell mismatch {Xp2.shape[0]} vs {len(y)}"
    # per-gene z-score Paper 2 (float32)
    Xp2 = Xp2.astype(np.float32)
    mu = Xp2.mean(0); sd = Xp2.std(0); sd[sd == 0] = 1
    Xp2 = (Xp2 - mu) / sd
    Xtr, Xte, ytr, yte = train_test_split(Xp2, y, test_size=0.25, random_state=0, stratify=y)
    clf = LogisticRegression(max_iter=300, C=1.0).fit(Xtr, ytr)
    acc = accuracy_score(yte, clf.predict(Xte)); chance = float(np.bincount(yte).max() / len(yte))
    log(f"  held-out Paper2 accuracy={acc:.3f} (chance={chance:.3f}) on {len(fp2)} genes")
    # "best signature": PC-vs-PP coefficient contrast (class central minus class portal)
    cls = list(clf.classes_)
    contrast = clf.coef_[cls.index(2)] - clf.coef_[cls.index(0)]    # +ve => pericentral driver
    order = np.argsort(contrast)
    topPC = [fp2[i] for i in order[::-1][:15]]; topPP = [fp2[i] for i in order[:15]]
    log(f"  learned PERICENTRAL drivers (top15): {', '.join(topPC)}")
    log(f"  learned PERIPORTAL drivers (top15): {', '.join(topPP)}")
    pd.DataFrame({"gene": fp2, "pc_minus_pp_coef": contrast}).sort_values(
        "pc_minus_pp_coef").to_csv(os.path.join(OUT, "learned_signature_supervised.csv"), index=False)
    del Xp2, Xtr, Xte; gc.collect()
    # apply to Paper 1
    Z1 = _z_dense_p1(M, genes, lib, fp2)
    proba = clf.predict_proba((Z1 - mu) / sd if False else Z1)       # Z1 already per-gene z (P1)
    ent = np.array([shannon(p, base=2) for p in proba], dtype=np.float32)
    coord = proba @ np.array(cls, dtype=float)                       # expected zone; high=pericentral
    pd.DataFrame({"signature_set": "supervised", "cell_id": bars, "donor": donor, "stage": stage,
                  "coord": coord, "pred_zone_coord": coord, "entropy": ent}
                 ).to_csv(os.path.join(OUT, "coordinates_learned_supervised.csv"), index=False)
    _validate_and_h1(coord, M, genes, lib, stage, donor, "supervised")
    log(f"  wrote learned_signature_supervised.csv + coordinates_learned_supervised.csv")


def unsupervised(min_frac=MIN_FRAC, n_pc=10):
    log(f"Step 4c UNSUPERVISED: PCA porto-central axis on HEALTHY Paper1 [min_frac={min_frac}]")
    M, genes, lib, stage, bars, donor = _p1()
    feats = build_feature_genes(M, genes, min_frac, exclude_landmarks=False)
    log(f"  features = {len(feats)} genes")
    Z = _z_dense_p1(M, genes, lib, feats)                            # all cells x feats (z)
    h = stage == STAGE_ORDER[0]
    pca = PCA(n_components=n_pc, random_state=0).fit(Z[h])           # learn axis on HEALTHY only
    # pick the PC most aligned with the marker zonation axis (mean PC markers - mean PP markers)
    mk = _markers_z(M, genes, lib)
    pcm = np.mean([(mk[g] - mk[g].mean()) / (mk[g].std() + 1e-9) for g in VAL["pericentral"] if g in mk], 0)
    ppm = np.mean([(mk[g] - mk[g].mean()) / (mk[g].std() + 1e-9) for g in VAL["periportal"] if g in mk], 0)
    marker_axis = (pcm - ppm)
    scores_h = pca.transform(Z[h])
    corrs = [spearmanr(scores_h[:, k], marker_axis[h]).statistic for k in range(n_pc)]
    k = int(np.argmax(np.abs(corrs))); sign = np.sign(corrs[k])
    log(f"  zonation axis = PC{k+1} (|corr| with marker axis={abs(corrs[k]):.3f}, "
        f"variance explained={pca.explained_variance_ratio_[k]*100:.1f}%)")
    load = pca.components_[k] * sign                                 # orient: pericentral high
    coord = (Z @ load).astype(np.float32)
    # the two anti-correlated subsets = +/- loadings
    thr = np.percentile(np.abs(load), 90)
    pc_pole = [feats[i] for i in np.argsort(load)[::-1][:15]]
    pp_pole = [feats[i] for i in np.argsort(load)[:15]]
    n_pc_genes = int((load >= thr).sum()); n_pp_genes = int((load <= -thr).sum())
    log(f"  PERICENTRAL pole (top15 +loadings): {', '.join(pc_pole)}")
    log(f"  PERIPORTAL pole (top15 -loadings): {', '.join(pp_pole)}")
    # confirm the two poles are strongly anti-correlated in healthy (the user's premise)
    pcs = Z[:, [feats.index(g) for g in pc_pole]].mean(1)
    pps = Z[:, [feats.index(g) for g in pp_pole]].mean(1)
    log(f"  healthy anticorr(top PC pole, top PP pole) = {spearmanr(pcs[h], pps[h]).statistic:+.3f} "
        f"(strong negative = the porto-central axis, learned with NO labels)")
    pd.DataFrame({"gene": feats, "loading": load}).sort_values("loading").to_csv(
        os.path.join(OUT, "learned_signature_unsupervised.csv"), index=False)
    pd.DataFrame({"signature_set": "unsupervised", "cell_id": bars, "donor": donor, "stage": stage,
                  "coord": coord, "pca_coord": coord}).to_csv(
        os.path.join(OUT, "coordinates_learned_unsupervised.csv"), index=False)
    _validate_and_h1(coord, M, genes, lib, stage, donor, "unsupervised")
    log("  wrote learned_signature_unsupervised.csv + coordinates_learned_unsupervised.csv")


def unsupervised_p2(min_frac=MIN_FRAC, n_pc=10):
    """CLEAN / LEAKAGE-FREE unsupervised axis: PCA learned on the PAPER 2 HEALTHY ATLAS (external
    to Paper 1), frozen, then applied to Paper 1. Paper 1 is never used to fit the axis."""
    log(f"Step 4c UNSUPERVISED-P2 (CLEAN): PCA axis from PAPER 2 healthy atlas -> applied to Paper1 [min_frac={min_frac}]")
    M, genes, lib, stage, bars, donor = _p1()
    feats = build_feature_genes(M, genes, min_frac, exclude_landmarks=False)
    from steps.step4b_classifier import load_p2
    Xp2, fp2 = load_p2(feats)                                   # Paper 2 healthy hep cells x fp2
    Xp2 = Xp2.astype(np.float32); mu2 = Xp2.mean(0); sd2 = Xp2.std(0); sd2[sd2 == 0] = 1
    Z2 = (Xp2 - mu2) / sd2; del Xp2; gc.collect()
    pca = PCA(n_components=n_pc, random_state=0).fit(Z2)        # FIT ON PAPER 2 ONLY
    fi = {g: j for j, g in enumerate(fp2)}
    def p2z(gl):
        cols = [Z2[:, fi[g]] for g in gl if g in fi]
        return np.mean(cols, 0) if cols else np.zeros(Z2.shape[0], np.float32)
    marker_axis = p2z(VAL["pericentral"]) - p2z(VAL["periportal"])
    scores = pca.transform(Z2)
    corrs = [spearmanr(scores[:, k], marker_axis).statistic for k in range(n_pc)]
    k = int(np.argmax(np.abs(corrs))); sign = np.sign(corrs[k])
    load = pca.components_[k] * sign
    log(f"  zonation axis = PC{k+1} (|corr| Paper2 marker axis={abs(corrs[k]):.3f}, "
        f"var={pca.explained_variance_ratio_[k]*100:.1f}%)")
    del Z2; gc.collect()
    Z1 = _z_dense_p1(M, genes, lib, fp2)                        # apply frozen loadings to Paper 1
    coord = (Z1 @ load).astype(np.float32); del Z1; gc.collect()
    pd.DataFrame({"gene": fp2, "loading": load}).sort_values("loading").to_csv(
        os.path.join(OUT, "learned_signature_unsupervised_p2.csv"), index=False)
    pd.DataFrame({"signature_set": "unsupervised_p2", "cell_id": bars, "donor": donor, "stage": stage,
                  "coord": coord, "pca_coord": coord}).to_csv(
        os.path.join(OUT, "coordinates_learned_unsupervised_p2.csv"), index=False)
    _validate_and_h1(coord, M, genes, lib, stage, donor, "unsupervised_p2")
    log("  wrote learned_signature_unsupervised_p2.csv + coordinates_learned_unsupervised_p2.csv")


def regularized(method="elasticnet", min_frac=MIN_FRAC, n_pc=10, alpha=0.02):
    """Regularized SPARSE unsupervised ruler, trained on PAPER 2 atlas (clean): distill the dense
    PCA porto-central axis into a sparse gene set via Lasso (l1) or Elastic-Net (l1+l2). Writes a
    candidate gene set (nonzero weights, signed) so it runs through the scoring battery. method in
    {dense, lasso, elasticnet}."""
    from sklearn.linear_model import ElasticNet
    log(f"Step 4c REGULARIZED [{method}] on PAPER 2 atlas (alpha={alpha}) -> Paper1")
    M, genes, lib, stage, bars, donor = _p1()
    feats = build_feature_genes(M, genes, min_frac, exclude_landmarks=False)
    from steps.step4b_classifier import load_p2
    Xp2, fp2 = load_p2(feats); Xp2 = Xp2.astype(np.float32)
    mu = Xp2.mean(0); sd = Xp2.std(0); sd[sd == 0] = 1; Z2 = (Xp2 - mu) / sd; del Xp2; gc.collect()
    pca = PCA(n_components=n_pc, random_state=0).fit(Z2)
    fi = {g: j for j, g in enumerate(fp2)}
    p2z = lambda gl: np.mean([Z2[:, fi[g]] for g in gl if g in fi], 0)
    maxis = p2z(VAL["pericentral"]) - p2z(VAL["periportal"])
    sc = pca.transform(Z2); corrs = [spearmanr(sc[:, k], maxis).statistic for k in range(n_pc)]
    k = int(np.argmax(np.abs(corrs))); sign = np.sign(corrs[k])
    y = (sc[:, k] * sign).astype(np.float32)               # dense unsupervised axis = distillation target
    if method == "dense":
        w = pca.components_[k] * sign
    else:
        l1 = 1.0 if method == "lasso" else 0.5
        en = ElasticNet(alpha=alpha, l1_ratio=l1, max_iter=4000, random_state=0,
                        selection="random").fit(Z2, y / (y.std() + 1e-9))
        w = en.coef_.astype(np.float32)
    nz = int((w != 0).sum())
    log(f"  {method}: {nz} nonzero-weight genes (of {len(fp2)})")
    del Z2; gc.collect()
    Z1 = _z_dense_p1(M, genes, lib, fp2); coord = (Z1 @ w).astype(np.float32); del Z1; gc.collect()
    name = f"unsupervised_{method}"
    pd.DataFrame({"gene": fp2, "loading": w}).sort_values("loading").to_csv(
        os.path.join(OUT, f"learned_signature_{name}.csv"), index=False)
    pd.DataFrame({"signature_set": name, "cell_id": bars, "donor": donor, "stage": stage,
                  "coord": coord}).to_csv(os.path.join(OUT, f"coordinates_learned_{name}.csv"), index=False)
    # candidate gene set (signed nonzero weights) so the battery can SCORE it
    if method != "dense":
        cand = config.SIGNATURES / "candidates"; cand.mkdir(parents=True, exist_ok=True)
        pc = [g for g, wt in sorted(zip(fp2, w), key=lambda t: -t[1]) if wt > 0]
        pp = [g for g, wt in sorted(zip(fp2, w), key=lambda t: t[1]) if wt < 0]
        (cand / f"pericentral_{name}.txt").write_text("\n".join(pc) + "\n")
        (cand / f"periportal_{name}.txt").write_text("\n".join(pp) + "\n")
        log(f"  wrote candidate set {name}: {len(pc)} PC + {len(pp)} PP")
    _validate_and_h1(coord, M, genes, lib, stage, donor, name)


def unsupervised_combined(min_frac=MIN_FRAC, n_pc=10):
    """Unsupervised axis learned on the POOLED healthy data: Paper 1 healthy cells + Paper 2 healthy
    atlas (each per-gene z-scored, then concatenated over shared genes), PCA, frozen -> Paper 1.
    Uses the most healthy training data available; still external to Paper 1 *disease*."""
    log(f"Step 4c UNSUPERVISED-COMBINED: PCA on POOLED (Paper1-healthy + Paper2 atlas) -> Paper1 [min_frac={min_frac}]")
    M, genes, lib, stage, bars, donor = _p1()
    feats = build_feature_genes(M, genes, min_frac, exclude_landmarks=False)
    from steps.step4b_classifier import load_p2
    Xp2, fp2 = load_p2(feats); Xp2 = Xp2.astype(np.float32)
    mu2 = Xp2.mean(0); sd2 = Xp2.std(0); sd2[sd2 == 0] = 1; Z2 = (Xp2 - mu2) / sd2; del Xp2; gc.collect()
    Z1 = _z_dense_p1(M, genes, lib, fp2)                     # all Paper1 cells x fp2
    h = stage == STAGE_ORDER[0]
    pooled = np.vstack([Z1[h], Z2]).astype(np.float32)       # Paper1-healthy + Paper2 healthy
    log(f"  pooled healthy training cells = {pooled.shape[0]} ({int(h.sum())} P1 + {Z2.shape[0]} P2), {len(fp2)} genes")
    del Z2; gc.collect()
    pca = PCA(n_components=n_pc, random_state=0).fit(pooled)
    fi = {g: j for j, g in enumerate(fp2)}
    pz = lambda gl, Z: np.mean([Z[:, fi[g]] for g in gl if g in fi], 0)
    maxis = pz(VAL["pericentral"], pooled) - pz(VAL["periportal"], pooled)
    sc = pca.transform(pooled); corrs = [spearmanr(sc[:, k], maxis).statistic for k in range(n_pc)]
    k = int(np.argmax(np.abs(corrs))); sign = np.sign(corrs[k]); load = pca.components_[k] * sign
    log(f"  zonation axis = PC{k+1} (|corr| pooled marker axis={abs(corrs[k]):.3f}, "
        f"var={pca.explained_variance_ratio_[k]*100:.1f}%)")
    del pooled; gc.collect()
    coord = (Z1 @ load).astype(np.float32); del Z1; gc.collect()
    pd.DataFrame({"gene": fp2, "loading": load}).sort_values("loading").to_csv(
        os.path.join(OUT, "learned_signature_unsupervised_combined.csv"), index=False)
    pd.DataFrame({"signature_set": "unsupervised_combined", "cell_id": bars, "donor": donor, "stage": stage,
                  "coord": coord}).to_csv(os.path.join(OUT, "coordinates_learned_unsupervised_combined.csv"), index=False)
    _validate_and_h1(coord, M, genes, lib, stage, donor, "unsupervised_combined")
    log("  wrote learned_signature_unsupervised_combined.csv + coordinates_learned_unsupervised_combined.csv")


def export_poles(src="unsupervised", ns=(50, 100, 250)):
    """Write the unsupervised axis's +/- loading poles as candidate gene-set files so they can be
    SCORED in the battery (parity with paper2_top*). Writes top-N for each n in `ns` AND a 'full'
    set (all signed-loading genes). signatures/candidates/{peri,peri}central_<src>_{topN|full}.txt."""
    cand = config.SIGNATURES / "candidates"; cand.mkdir(parents=True, exist_ok=True)
    sig = pd.read_csv(os.path.join(OUT, f"learned_signature_{src}.csv"))
    col = next(c for c in sig.columns if sig[c].dtype.kind == "f")
    sig = sig.sort_values(col); g = sig["gene"].tolist(); w = sig[col].values
    for n in ns:
        pp = g[:n]; pc = g[-n:][::-1]
        (cand / f"pericentral_{src}_top{n}.txt").write_text("\n".join(pc) + "\n")
        (cand / f"periportal_{src}_top{n}.txt").write_text("\n".join(pp) + "\n")
        print(f"  wrote {src}_top{n}: {len(pc)} PC + {len(pp)} PP")
    # full: ALL signed-loading genes (the equal-weight 'full unsupervised' set — expect dilution)
    pc_full = [gn for gn, wt in zip(g, w) if wt > 0][::-1]; pp_full = [gn for gn, wt in zip(g, w) if wt < 0]
    (cand / f"pericentral_{src}_full.txt").write_text("\n".join(pc_full) + "\n")
    (cand / f"periportal_{src}_full.txt").write_text("\n".join(pp_full) + "\n")
    print(f"  wrote {src}_full: {len(pc_full)} PC + {len(pp_full)} PP")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "supervised"
    fns = {"supervised": supervised, "unsupervised": unsupervised,
           "unsupervised_p2": unsupervised_p2, "unsupervised_combined": unsupervised_combined,
           "export_poles": export_poles,
           "lasso": lambda: regularized("lasso"), "elasticnet": lambda: regularized("elasticnet"),
           "dense": lambda: regularized("dense")}
    fns.get(mode, supervised)()
