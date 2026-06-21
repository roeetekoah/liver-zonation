"""Step 4b — zone classifier + per-cell entropy de-zonation read-out (Artefact A4b).

Train a calibrated multinomial logistic model on Paper 2 hepatocytes to predict zone, then
apply it to Paper 1 and read per-cell prediction ENTROPY (low = confidently zonated, high =
de-zonated). AUXILIARY layer: the cached Paper-2 labels are eta-over-landmark (signature-
derived), so entropy supports — never overrides — the donor-level H1 collapse.
"""
from __future__ import annotations
import os, sys
import numpy as np, pandas as pd, h5py, scipy.io, scipy.sparse as sp
from scipy.stats import entropy as shannon
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # src/
import config
from steps.common import log, OUT, STAGE_ORDER, DONOR_COLS

P2MAT = str(config.DATA_RAW / "combined_scRNAseq_atlas_M5M6M7M8.mat")
P1 = str(config.PAPER1)
PC = [g.strip() for g in open(str(config.PC_GENES)) if g.strip()]
PP = [g.strip() for g in open(str(config.PP_GENES)) if g.strip()]
# How the cached Paper-2 labels were assigned (prep/02_convert_paper2_mat.py): eta =
# sum_pp/(sum_pp+sum_pc) over the 20+20 LANDMARK genes, binned to terciles. Those landmark
# genes are a SUBSET of the classifier features -> labels are signature-derived -> entropy is
# AUXILIARY. Switch to "paper2_spatial" only if real 8-layer zon_struct labels are wired in.
LABEL_SOURCE = "paper2_eta_landmark"
IS_SIGNATURE_DERIVED = True
ZONE_NAME = {0: "portal", 1: "mid", 2: "central"}
# De-circularization: the labels are eta over the 20+20 landmark genes, so KEEPING those genes
# as classifier features lets the model trivially re-learn the label. Exclude them from the
# feature set (train on the other zonated genes). Reduces — does not remove — circularity, since
# correlated genes remain; real fix is genuine spatial labels (zon_struct). Toggle to compare.
EXCLUDE_LANDMARKS_FROM_FEATURES = True


def norm_z(dense_genes_by_cells, libsize):
    D = np.log1p(dense_genes_by_cells / libsize * 1e4)
    sd = D.std(1, keepdims=True); return (D - D.mean(1, keepdims=True)) / np.where(sd > 0, sd, 1)


def load_p2(feature_genes):
    """Paper 2 hepatocytes for a feature-gene set (chunked, memory-safe). Returns X, feats."""
    f = h5py.File(P2MAT, "r"); t = f["t"]
    dref = lambda r: "".join(chr(int(c)) for c in f[r][:].flatten())
    genes = np.array([dref(t["gene_name"][0, i]) for i in range(t["gene_name"].shape[1])])
    cu = [dref(t["cluster_unique"][0, i]) for i in range(t["cluster_unique"].shape[1])]
    leiden = t["leiden"][0].astype(int); hep = np.where(leiden - leiden.min() == cu.index("Hepatocytes"))[0]
    g2r = {g: i for i, g in enumerate(genes)}
    fr = np.array([g2r[g] for g in feature_genes if g in g2r]); feats = [g for g in feature_genes if g in g2r]
    ir = t["mat_norm/ir"]; dat = t["mat_norm/data"]; jc = t["mat_norm/jc"][:].astype(np.int64); nnz = ir.shape[0]
    wantrow = np.zeros(len(genes), bool); wantrow[fr] = True
    hepmask = np.zeros(leiden.shape[0], bool); hepmask[hep] = True
    cellpos = np.full(leiden.shape[0], -1, np.int64); cellpos[hep] = np.arange(len(hep))
    gpos = np.full(len(genes), -1, np.int64); gpos[fr] = np.arange(len(fr))
    X = np.zeros((len(hep), len(feats)), np.float32); CH = 20_000_000
    for s in range(0, nnz, CH):
        e = min(s + CH, nnz); irc = ir[s:e]; m = wantrow[irc]
        if m.any():
            loc = np.nonzero(m)[0]; c = np.searchsorted(jc, s + loc, "right") - 1; hk = hepmask[c]
            if hk.any(): X[cellpos[c[hk]], gpos[irc[loc[hk]]]] = dat[s:e][loc[hk]]
    return X, feats


def derive_labels(X, feats):
    """Fallback (no cache): zone label = tercile of the PC-PP signature coordinate on Paper 2."""
    fi = {g: j for j, g in enumerate(feats)}
    z = lambda gl: np.mean([(X[:, fi[g]] - X[:, fi[g]].mean()) / (X[:, fi[g]].std() + 1e-9) for g in gl if g in fi], axis=0)
    coord = z(PC) - z(PP); t1, t2 = np.quantile(coord, [1 / 3, 2 / 3])
    return np.where(coord <= t1, 0, np.where(coord >= t2, 2, 1))


def load_p1(feature_genes):
    """Paper 1 hepatocytes (cells x feats) in the SAME shared-gene order, + stage, barcodes, donor."""
    npz = os.path.join(P1, "counts.npz")
    M = sp.load_npz(npz).tocsc() if os.path.exists(npz) else scipy.io.mmread(os.path.join(P1, "counts.mtx")).tocsc()
    genes = np.array([g.strip() for g in open(os.path.join(P1, "genes.txt"))])
    bars = np.array([b.strip() for b in open(os.path.join(P1, "barcodes.txt"))])
    stage = pd.read_csv(os.path.join(P1, "cell_metadata.csv")).set_index("cell_id").reindex(bars)["stage"].values
    allm = pd.read_csv(os.path.join(P1, "metadata_all_cells.csv"), low_memory=False).set_index("cell_id")
    dcol = next((c for c in DONOR_COLS if c in allm.columns), None)
    donor = allm[dcol].astype(str).reindex(bars).values if dcol else np.array(["NA"] * len(bars))
    lib = np.asarray(M.sum(0)).ravel(); g2r = {g: i for i, g in enumerate(genes)}
    rows = [g2r[g] for g in feature_genes if g in g2r]; feats = [g for g in feature_genes if g in g2r]
    D = np.asarray(M[rows].todense()).astype(float)
    return norm_z(D, lib).T, feats, stage, bars, donor


def _fit_calibrated(Xtr, ytr):
    """Calibrated multinomial logistic regression; fall back to plain LR if calibration fails."""
    base = LogisticRegression(max_iter=2000)   # multinomial softmax is the default (lbfgs)
    try:
        from sklearn.calibration import CalibratedClassifierCV
        clf = CalibratedClassifierCV(base, method="sigmoid", cv=3); clf.fit(Xtr, ytr)
        return clf, "calibrated_sigmoid"
    except Exception as ex:
        log(f"  (calibration unavailable: {ex}; using plain LR)")
        base.fit(Xtr, ytr); return base, "plain_lr"


def classify_entropy(Xp2, y_zone, Xp1, p1_stage, p1_barcodes, p1_donor=None,
                     classes=(0, 1, 2), label_source=LABEL_SOURCE, extra_eval=None):
    """Train a zone classifier on Paper 2, evaluate on a held-out Paper 2 split, then score
    Paper 1 -> per-cell zone entropy.

    Writes classifier_eval.csv, classifier_confusion_matrix.csv, classifier_entropy.csv.
    Returns (entropy_df, eval_dict). The Paper-2 scaler is fit on TRAIN only (no leakage).
    """
    # ---- held-out Paper 2 evaluation (scaler on TRAIN only) ----
    Xtr, Xte, ytr, yte = train_test_split(Xp2, y_zone, test_size=0.25, random_state=0, stratify=y_zone)
    sc = StandardScaler().fit(Xtr)
    clf, calib = _fit_calibrated(sc.transform(Xtr), ytr)
    yhat = clf.predict(sc.transform(Xte))
    acc = accuracy_score(yte, yhat); chance = float(np.bincount(yte).max() / len(yte))
    log(f"  held-out Paper2 accuracy={acc:.3f}  (majority-class chance={chance:.3f})  [{calib}]")
    labels_sorted = sorted(np.unique(y_zone))
    cm = confusion_matrix(yte, yhat, labels=labels_sorted)
    cm_df = pd.DataFrame(cm, index=[f"true_{ZONE_NAME.get(c, c)}" for c in labels_sorted],
                         columns=[f"pred_{ZONE_NAME.get(c, c)}" for c in labels_sorted])
    cm_df.insert(0, "label_source", label_source)
    cm_df.to_csv(os.path.join(OUT, "classifier_confusion_matrix.csv"))
    rep = classification_report(yte, yhat, labels=labels_sorted,
                                target_names=[ZONE_NAME.get(c, str(c)) for c in labels_sorted],
                                output_dict=True, zero_division=0)
    eval_dict = {"label_source": label_source, "calibration": calib,
                 "n_features": int(Xp2.shape[1]),
                 "n_train": len(ytr), "n_test": len(yte), "accuracy": acc,
                 "majority_class_chance": chance, "beats_chance": bool(acc > chance),
                 "macro_f1": rep["macro avg"]["f1-score"]}
    if extra_eval: eval_dict.update(extra_eval)
    pd.DataFrame([eval_dict]).to_csv(os.path.join(OUT, "classifier_eval.csv"), index=False)

    # ---- final model on ALL Paper 2, apply to Paper 1 -> per-cell entropy (auxiliary) ----
    scF = StandardScaler().fit(Xp2)
    clfF, _ = _fit_calibrated(scF.transform(Xp2), y_zone)
    proba = clfF.predict_proba(scF.transform(Xp1))
    ent = np.apply_along_axis(lambda p: shannon(p, base=2), 1, proba)
    out = {"cell_id": p1_barcodes}
    if p1_donor is not None: out["donor"] = p1_donor
    out.update({"stage": p1_stage, "label_source": label_source, "entropy": ent,
                **{f"p_zone_{ZONE_NAME.get(c, c)}": proba[:, i] for i, c in enumerate(clfF.classes_)}})
    df = pd.DataFrame(out)
    df.to_csv(os.path.join(OUT, "classifier_entropy.csv"), index=False)
    log("  mean prediction entropy per stage (AUXILIARY; higher = more de-zonated):")
    for st in STAGE_ORDER:
        m = df.stage == st
        if m.sum() > 20: log(f"    {st:22s} n={int(m.sum()):6d}  mean_entropy={df.entropy[m].mean():.3f}")
    return df, eval_dict


def main():
    train = str(config.PAPER2_TRAIN); label_source = LABEL_SOURCE
    if os.path.exists(train):
        log("loading precomputed Paper 2 training set (paper2_train.npz) ...")
        d = np.load(train, allow_pickle=True)
        Xp2 = d["X"]; shared = list(d["feats"]); y = d["zone_label"]
    else:
        log("no paper2_train.npz — reading .mat (run prep/02_convert_paper2_mat.py to cache this) ...")
        feature_genes = list(dict.fromkeys(PC + PP))
        Xp2, feats_p2 = load_p2(feature_genes)
        p1_genes = set(g.strip() for g in open(os.path.join(P1, "genes.txt")))
        shared = [g for g in feats_p2 if g in p1_genes]
        Xp2 = Xp2[:, [feats_p2.index(g) for g in shared]]
        y = derive_labels(Xp2, shared)
    # De-circularize: drop the 20+20 landmark genes (which DEFINE the eta labels) from features.
    extra = {"features_exclude_landmarks": EXCLUDE_LANDMARKS_FROM_FEATURES, "n_landmarks_excluded": 0}
    if EXCLUDE_LANDMARKS_FROM_FEATURES:
        lm = set()
        for p in config.signature_files("paper2_landmark"):
            lm.update(g.strip() for g in open(str(p)) if g.strip())
        keep = [i for i, g in enumerate(shared) if g not in lm]
        n_excl = len(shared) - len(keep)
        extra["n_landmarks_excluded"] = n_excl
        Xp2 = Xp2[:, keep]; shared = [shared[i] for i in keep]
        log(f"  de-circularization: excluded {n_excl} landmark genes from features "
            f"({len(shared)} features remain)")
    log(f"features (shared P1 & P2): {len(shared)}   label_source={label_source} "
        f"(signature_derived={IS_SIGNATURE_DERIVED} -> entropy is AUXILIARY, not a headline)")
    Xp1, _, stage, bars, donor = load_p1(shared)
    classify_entropy(Xp2, y, Xp1, stage, bars, donor, label_source=label_source, extra_eval=extra)
    log(f"\nsaved classifier_entropy.csv, classifier_eval.csv, classifier_confusion_matrix.csv in {OUT}")


if __name__ == "__main__":
    main()
