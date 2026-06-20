#!/usr/bin/env python3
"""
Paper-2 positive control: reconstruct the zonation coordinate on the healthy
snRNA hepatocytes and check it recovers known zonation.
Path-robust (run from anywhere) and memory-safe (chunked sparse read).
Requires: numpy, h5py, scipy, matplotlib.
    python run_p2_validation.py
"""
import os, time, numpy as np, h5py, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))     # .../Hackathon/analysis
BASE = os.path.dirname(HERE)                           # .../Hackathon
MAT  = os.path.join(BASE, "data", "combined_scRNAseq_atlas_M5M6M7M8.mat")
PCf  = os.path.join(HERE, "pericentral_genes.txt")
PPf  = os.path.join(HERE, "periportal_genes.txt")
t0 = time.time(); log = lambda m: print(f"[{time.time()-t0:5.1f}s] {m}", flush=True)

f = h5py.File(MAT, "r"); t = f["t"]
dref = lambda r: "".join(chr(int(c)) for c in f[r][:].flatten())
genes = np.array([dref(t["gene_name"][0, i]) for i in range(t["gene_name"].shape[1])])
g2r = {g: i for i, g in enumerate(genes)}
log(f"{len(genes)} genes")

# hepatocytes via leiden + cluster_unique (avoids decoding 67k strings)
cu = [dref(t["cluster_unique"][0, i]) for i in range(t["cluster_unique"].shape[1])]
leiden = t["leiden"][0].astype(int); base = leiden.min()
hep = np.where(leiden - base == cu.index("Hepatocytes"))[0]
si = t["sample_ind"][0].astype(int); us = [dref(t["unique_sample"][0, i]) for i in range(4)]
donor = np.array([us[s - 1] for s in si[hep]])
log(f"{len(hep)} hepatocytes across donors {us}")

PC = [g.strip() for g in open(PCf) if g.strip()]
PP = [g.strip() for g in open(PPf) if g.strip()]
val = ["GLUL","CYP2E1","CYP1A2","OAT","GLUD1","ASS1","SDS","HAL","PCK1","ARG1"]  # independent check
want = sorted(set(PC+PP+val) & set(genes)); wr = np.array([g2r[g] for g in want])

# chunked CSC read: pull only wanted-gene rows over hepatocyte columns
irds, datds = t["mat_norm/ir"], t["mat_norm/data"]
jc = t["mat_norm/jc"][:].astype(np.int64); nnz = irds.shape[0]; ncell = leiden.shape[0]
wantrow = np.zeros(len(genes), bool); wantrow[wr] = True
hepmask = np.zeros(ncell, bool); hepmask[hep] = True
cellpos = np.full(ncell, -1, np.int64); cellpos[hep] = np.arange(len(hep))
genepos = np.full(len(genes), -1, np.int64); genepos[wr] = np.arange(len(wr))
X = np.zeros((len(hep), len(want)), np.float32); CH = 20_000_000
for s in range(0, nnz, CH):
    e = min(s+CH, nnz); irc = irds[s:e]; m = wantrow[irc]
    if m.any():
        loc = np.nonzero(m)[0]; c = np.searchsorted(jc, s+loc, "right")-1; hk = hepmask[c]
        if hk.any():
            datc = datds[s:e]
            X[cellpos[c[hk]], genepos[irc[loc[hk]]]] = datc[loc[hk]]
    log(f"chunk {e//CH}/{(nnz+CH-1)//CH}")
col = {g: X[:, want.index(g)] for g in want}

zc = lambda v: ((v-v.mean())/v.std() if v.std() > 0 else v*0)
sc = lambda gl: np.mean([zc(col[g]) for g in gl if g in col], axis=0)
pc_s, pp_s = sc(PC), sc(PP); coord = pc_s - pp_s

print("\n=== Paper 2 healthy hepatocytes — positive control ===")
print(f"hepatocytes={len(hep)}  PC/PP module spearman={spearmanr(pc_s,pp_s).statistic:+.3f} (expect negative)")
for g in val:
    if g in col: print(f"  coord vs {g:7s}: rho={spearmanr(coord,col[g]).statistic:+.3f}")
for d in us:
    i = donor == d
    if i.sum() > 20 and "CYP2E1" in col:
        print(f"  donor {d}: n={int(i.sum()):5d}  rho(coord,CYP2E1)={spearmanr(coord[i],col['CYP2E1'][i]).statistic:+.3f}")

fig, ax = plt.subplots(1, 3, figsize=(13, 3.6))
ax[0].hist(coord, bins=60, color="#1b6e78"); ax[0].set_title("Zonation coordinate"); ax[0].set_xlabel("pericentral − periportal")
if "CYP2E1" in col: ax[1].scatter(coord, col["CYP2E1"], s=3, alpha=.15, color="#2c6fb0"); ax[1].set_title("Pericentral: CYP2E1"); ax[1].set_xlabel("coordinate")
if "ASS1"  in col: ax[2].scatter(coord, col["ASS1"],  s=3, alpha=.15, color="#c05621"); ax[2].set_title("Periportal: ASS1"); ax[2].set_xlabel("coordinate")
plt.tight_layout(); out = os.path.join(HERE, "p2_validation.png"); plt.savefig(out, dpi=130)
print("saved", out)
