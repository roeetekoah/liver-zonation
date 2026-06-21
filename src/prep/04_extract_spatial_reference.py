#!/usr/bin/env python3
"""
Extract Paper 2's REAL spatial zonation reference (gene -> zone) from zon_struct_all_full.mat
and cache it for the pipeline. This is the genuine spatial ground truth (Visium-HD 8-layer
reconstruction), independent of the eta-over-landmark proxy.

zon_struct_all_full.mat holds 10 condition elements; element 1 = "healthy donors all M4-8"
(matches the M5M6M7M8 snRNA atlas) is the healthy reference. Each element has, per gene:
  mn   (8 layers x genes) : mean expression per zonation layer (layer 0 = PERICENTRAL,
                            high layers = PERIPORTAL; verified via GLUL/CYP2E1 vs ASS1/HAL)
  com  (genes,)           : center of mass along the 1..8 layer axis (low = pericentral)
  qval (genes,)           : zonation FDR (qval<0.05 = significantly zonated)

Writes:
  data/processed/paper2_zonation_reference.csv  {gene, com, qval, peak_layer}
  data/processed/paper2_zonation_profiles.npz   {genes, mn (8 x G), com, qval}

Run:  python src/prep/04_extract_spatial_reference.py
"""
import os, sys, numpy as np, pandas as pd, h5py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # src/
import config

MAT = str(config.DATA_RAW / "zon_struct_all_full.mat")
HEALTHY_ELEM = 1   # "healthy donors all M4-8"


def main():
    f = h5py.File(MAT, "r"); Z = f["zon_struct_all_full"]
    o = f[Z[HEALTHY_ELEM, 0]]
    cat = "".join(chr(int(c)) for c in o["category"][:].flatten())
    print(f"reference element {HEALTHY_ELEM}: category={cat!r}")
    gn = o["gene_name"]
    genes = np.array(["".join(chr(int(c)) for c in f[gn[0, i]][:].flatten())
                      for i in range(gn.shape[1])])
    mn = np.asarray(o["mn"][:], dtype=float)            # (8 layers, G)
    com = np.asarray(o["com"][:]).ravel()
    qval = np.asarray(o["qval"][:]).ravel()
    peak_layer = np.argmax(mn, axis=0)
    print(f"  genes={len(genes)}  layers={mn.shape[0]}  zonated (qval<0.05)={int((qval<0.05).sum())}")

    ref = pd.DataFrame({"gene": genes, "com": com, "qval": qval, "peak_layer": peak_layer})
    ref.to_csv(config.DATA_PROC / "paper2_zonation_reference.csv", index=False)
    np.savez(config.DATA_PROC / "paper2_zonation_profiles.npz",
             genes=genes, mn=mn.astype(np.float32), com=com, qval=qval)
    print(f"wrote paper2_zonation_reference.csv ({len(ref)} genes) + paper2_zonation_profiles.npz")


if __name__ == "__main__":
    main()
