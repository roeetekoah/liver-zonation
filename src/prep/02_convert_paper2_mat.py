#!/usr/bin/env python3
"""
Phase 0 (one-time) — convert Paper 2's MATLAB .mat into a Python-native cache so the
rest of the pipeline never touches MATLAB. Builds the classifier training set directly.

Reads:
  data/raw/combined_scRNAseq_atlas_M5M6M7M8.mat   (Paper 2 snRNA atlas, v7.3 HDF5)
  signatures/{pericentral,periportal}_core.txt    (signatures)
  data/processed/paper1/genes.txt                 (to keep only features shared w/ Paper 1)
Writes:
  data/processed/paper2_train.npz = { X (cells x feats, float32), feats (str[]),
                       zone_label (int[]: 0 portal / 1 mid / 2 central), donor (str[]) }

Zone labels (Option A): tercile of the PC-PP signature coordinate on Paper 2's own
hepatocytes. Swap in Paper 2's Visium-HD zonation mapping later for ground-truth labels.

Run from the src/prep/ folder:   python 02_convert_paper2_mat.py
Memory-safe: reads the sparse matrix in chunks; keeps only the feature genes.
"""
import os, sys, numpy as np, h5py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # src/ on path
import config

MAT  = str(config.DATA_RAW / "combined_scRNAseq_atlas_M5M6M7M8.mat")
PC   = [g.strip() for g in open(str(config.PC_GENES)) if g.strip()]
PP   = [g.strip() for g in open(str(config.PP_GENES)) if g.strip()]
P1G  = set(g.strip() for g in open(str(config.PAPER1 / "genes.txt")))
OUT  = str(config.PAPER2_TRAIN)

def main():
    f = h5py.File(MAT, "r"); t = f["t"]
    dref = lambda r: "".join(chr(int(c)) for c in f[r][:].flatten())
    genes = np.array([dref(t["gene_name"][0, i]) for i in range(t["gene_name"].shape[1])])
    g2r = {g: i for i, g in enumerate(genes)}
    cu = [dref(t["cluster_unique"][0, i]) for i in range(t["cluster_unique"].shape[1])]
    leiden = t["leiden"][0].astype(int)
    hep = np.where(leiden - leiden.min() == cu.index("Hepatocytes"))[0]
    si = t["sample_ind"][0].astype(int); us = [dref(t["unique_sample"][0, i]) for i in range(4)]
    donor = np.array([us[s - 1] for s in si[hep]])

    # features = signature genes present in BOTH Paper 2 and Paper 1
    feats = [g for g in dict.fromkeys(PC + PP) if g in g2r and g in P1G]
    fr = np.array([g2r[g] for g in feats])
    print(f"hepatocytes={len(hep)}  shared signature features={len(feats)}")

    # chunked CSC read -> dense (hep cells x feats)
    ir = t["mat_norm/ir"]; dat = t["mat_norm/data"]; jc = t["mat_norm/jc"][:].astype(np.int64)
    nnz = ir.shape[0]; ncell = leiden.shape[0]
    wantrow = np.zeros(len(genes), bool); wantrow[fr] = True
    hepmask = np.zeros(ncell, bool); hepmask[hep] = True
    cellpos = np.full(ncell, -1, np.int64); cellpos[hep] = np.arange(len(hep))
    gpos = np.full(len(genes), -1, np.int64); gpos[fr] = np.arange(len(fr))
    X = np.zeros((len(hep), len(feats)), np.float32); CH = 20_000_000
    for s in range(0, nnz, CH):
        e = min(s + CH, nnz); irc = ir[s:e]; m = wantrow[irc]
        if m.any():
            loc = np.nonzero(m)[0]; c = np.searchsorted(jc, s + loc, "right") - 1; hk = hepmask[c]
            if hk.any():
                X[cellpos[c[hk]], gpos[irc[loc[hk]]]] = dat[s:e][loc[hk]]

    # Option-A zone labels: tercile of PC-PP signature coordinate
    fi = {g: j for j, g in enumerate(feats)}
    z = lambda gl: np.mean([(X[:, fi[g]] - X[:, fi[g]].mean()) / (X[:, fi[g]].std() + 1e-9)
                            for g in gl if g in fi], axis=0)
    coord = z(PC) - z(PP); t1, t2 = np.quantile(coord, [1/3, 2/3])
    y = np.where(coord <= t1, 0, np.where(coord >= t2, 2, 1)).astype(int)

    np.savez(OUT, X=X, feats=np.array(feats), zone_label=y, donor=donor)
    print(f"wrote {OUT}  (X={X.shape}, zone counts: "
          f"{ {int(k): int((y==k).sum()) for k in (0,1,2)} })")

if __name__ == "__main__":
    main()
