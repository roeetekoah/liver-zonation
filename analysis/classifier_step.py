#!/usr/bin/env python3
"""
Step 4b (headline upgrade): a ZONE CLASSIFIER whose prediction entropy = de-zonation.

Idea: train a classifier on Paper 2's snRNA hepatocytes (same platform as Paper 1)
to predict zone, then apply it to Paper 1 and read the per-cell zone-probability
ENTROPY — low = confidently zonated, high = de-zonated. Mean entropy per disease
stage is the headline collapse metric, and per-class confidence tests H2 (does
pericentral identity decay first?).

STATUS: runnable scaffold. The one piece to firm up during the hackathon is how the
Paper 2 training cells get their zone LABEL. Two options:
  (A) [implemented here, quick] derive labels by computing the same PC-PP signature
      coordinate on Paper 2's hepatocytes and binning into terciles (portal/mid/central).
      Caveat: labels are signature-derived, so the classifier partly re-learns the
      signature — but it uses the *whole* transcriptome, which can generalize better
      and gives the entropy read-out.
  (B) [better, more work] use Paper 2's own Visium-HD -> snRNA zonation mapping
      (their repo: parse_snRNAseq_combined_atlas.m + extract_zonation*.m) to get
      ground-truth zone indices, then bin those. Swap into `derive_labels` when ready.

Needs: combined_scRNAseq_atlas_M5M6M7M8.mat (Paper 2) + analysis/paper1/ (Paper 1) +
the signature files. Memory: restricts to a shared feature-gene set, so it stays light.
Run from the Hackathon folder:  python analysis/classifier_step.py
"""
import os, numpy as np, pandas as pd, h5py, scipy.io
from scipy.stats import entropy as shannon
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
P2MAT = os.path.join(BASE, "data", "combined_scRNAseq_atlas_M5M6M7M8.mat")
P1 = os.path.join(HERE, "paper1"); OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
STAGE_ORDER = ["Healthy control","NAFLD","NASH w/o cirrhosis","NASH with cirrhosis","end stage"]
PC = [g.strip() for g in open(os.path.join(HERE,"pericentral_genes.txt")) if g.strip()]
PP = [g.strip() for g in open(os.path.join(HERE,"periportal_genes.txt")) if g.strip()]

def norm_z(dense_genes_by_cells, libsize):
    D = np.log1p(dense_genes_by_cells / libsize * 1e4)
    sd = D.std(1, keepdims=True); return (D - D.mean(1, keepdims=True)) / np.where(sd>0, sd, 1)

# ---- Paper 2: load hepatocytes for a feature-gene set (chunked, memory-safe) ----
def load_p2(feature_genes):
    f = h5py.File(P2MAT, "r"); t = f["t"]
    dref = lambda r: "".join(chr(int(c)) for c in f[r][:].flatten())
    genes = np.array([dref(t["gene_name"][0,i]) for i in range(t["gene_name"].shape[1])])
    cu = [dref(t["cluster_unique"][0,i]) for i in range(t["cluster_unique"].shape[1])]
    leiden = t["leiden"][0].astype(int); hep = np.where(leiden-leiden.min()==cu.index("Hepatocytes"))[0]
    g2r = {g:i for i,g in enumerate(genes)}
    fr = np.array([g2r[g] for g in feature_genes if g in g2r]); feats=[g for g in feature_genes if g in g2r]
    ir=t["mat_norm/ir"]; dat=t["mat_norm/data"]; jc=t["mat_norm/jc"][:].astype(np.int64); nnz=ir.shape[0]
    wantrow=np.zeros(len(genes),bool); wantrow[fr]=True
    hepmask=np.zeros(leiden.shape[0],bool); hepmask[hep]=True
    cellpos=np.full(leiden.shape[0],-1,np.int64); cellpos[hep]=np.arange(len(hep))
    gpos=np.full(len(genes),-1,np.int64); gpos[fr]=np.arange(len(fr))
    X=np.zeros((len(hep),len(feats)),np.float32); CH=20_000_000
    for s in range(0,nnz,CH):
        e=min(s+CH,nnz); irc=ir[s:e]; m=wantrow[irc]
        if m.any():
            loc=np.nonzero(m)[0]; c=np.searchsorted(jc,s+loc,"right")-1; hk=hepmask[c]
            if hk.any(): X[cellpos[c[hk]],gpos[irc[loc[hk]]]]=dat[s:e][loc[hk]]
    return X, feats   # cells x feats (already mat_norm normalized)

def derive_labels(X, feats):
    """Option A: zone label = tercile of the PC-PP signature coordinate on Paper 2."""
    fi={g:j for j,g in enumerate(feats)}
    z=lambda gl: np.mean([(X[:,fi[g]]-X[:,fi[g]].mean())/(X[:,fi[g]].std()+1e-9) for g in gl if g in fi],axis=0)
    coord=z(PC)-z(PP); t1,t2=np.quantile(coord,[1/3,2/3])
    return np.where(coord<=t1,0,np.where(coord>=t2,2,1))   # 0 portal,1 mid,2 central

def load_p1(feature_genes):
    M=scipy.io.mmread(os.path.join(P1,"counts.mtx")).tocsc()
    genes=np.array([g.strip() for g in open(os.path.join(P1,"genes.txt"))])
    bars=np.array([b.strip() for b in open(os.path.join(P1,"barcodes.txt"))])
    stage=pd.read_csv(os.path.join(P1,"cell_metadata.csv")).set_index("cell_id").reindex(bars)["stage"].values
    lib=np.asarray(M.sum(0)).ravel(); g2r={g:i for i,g in enumerate(genes)}
    rows=[g2r[g] for g in feature_genes if g in g2r]; feats=[g for g in feature_genes if g in g2r]
    D=np.asarray(M[rows].todense()).astype(float)
    return norm_z(D,lib).T, feats, stage, bars   # cells x feats

def main():
    train = os.path.join(HERE, "paper2_train.npz")
    if os.path.exists(train):                                    # fast path: Phase-0 cache
        print("loading precomputed Paper 2 training set (paper2_train.npz) ...")
        d = np.load(train, allow_pickle=True)
        Xp2 = d["X"]; shared = list(d["feats"]); y = d["zone_label"]
    else:                                                        # slow path: read the .mat directly
        print("no paper2_train.npz — reading .mat (run convert_paper2_mat.py to cache this) ...")
        feature_genes = list(dict.fromkeys(PC + PP))
        Xp2, feats_p2 = load_p2(feature_genes)
        p1_genes = set(g.strip() for g in open(os.path.join(P1, "genes.txt")))
        shared = [g for g in feats_p2 if g in p1_genes]
        Xp2 = Xp2[:, [feats_p2.index(g) for g in shared]]
        y = derive_labels(Xp2, shared)
    Xp1, _, stage, bars = load_p1(shared)                        # P1 in the SAME shared order
    print(f"features (shared P1 & P2): {len(shared)}")
    sc = StandardScaler().fit(Xp2)
    clf = LogisticRegression(max_iter=2000, multi_class="multinomial").fit(sc.transform(Xp2), y)
    proba = clf.predict_proba(sc.transform(Xp1))                 # use P2 scaler on P1
    ent = np.apply_along_axis(lambda p: shannon(p, base=2), 1, proba)
    df = pd.DataFrame({"cell_id":bars,"stage":stage,"entropy":ent,
                       **{f"p_zone{c}":proba[:,i] for i,c in enumerate(clf.classes_)}})
    df.to_csv(os.path.join(OUT,"classifier_entropy.csv"), index=False)
    print("mean prediction entropy per stage (higher = more de-zonated):")
    for st in STAGE_ORDER:
        m = df.stage==st
        if m.sum()>20: print(f"  {st:22s} n={int(m.sum()):6d}  mean_entropy={df.entropy[m].mean():.3f}")
    print(f"\nsaved {OUT}/classifier_entropy.csv")

if __name__ == "__main__":
    main()
