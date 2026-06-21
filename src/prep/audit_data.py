#!/usr/bin/env python3
"""
30-second grounding audit — prints exactly what's in the processed data, so we never again
argue from memory about what Paper 1/2 contain. Run any time:

    python src/prep/audit_data.py

Checks: Paper 1 file presence, matrix dims, STAGE + cell_type counts, DONOR id presence
(the make-or-break for donor-level stats), signature overlap with Paper 1, and whether the
Paper 2 classifier cache exists / how its labels were made.
"""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

P = str(config.PAPER1)
DONOR_CANDS = ["Patient.ID", "patient", "donor", "orig.ident", "sample"]

def main():
    print("=== Paper 1 processed files ===")
    for f in ["counts.mtx","genes.txt","barcodes.txt","cell_metadata.csv","metadata_all_cells.csv"]:
        p = os.path.join(P, f)
        print(f"  {f:28s} {'OK' if os.path.exists(p) else 'MISSING':7s} "
              f"{os.path.getsize(p)//1024 if os.path.exists(p) else 0} KB")

    with open(os.path.join(P, "counts.mtx")) as fh:
        for line in fh:
            if line.startswith("%"): continue
            g, c, nnz = line.split()
            print(f"\ncounts.mtx: genes={g}  cells={c}  nnz={nnz}"); break
    genes = [l.strip() for l in open(os.path.join(P, "genes.txt"))]

    cm = pd.read_csv(os.path.join(P, "cell_metadata.csv"))
    print("\n=== cell_metadata.csv ===  cols:", list(cm.columns))
    if "stage" in cm:     print("STAGE (cells):\n", cm["stage"].value_counts().to_string())
    if "cell_type" in cm: print("cell_type:", cm["cell_type"].value_counts().to_dict())

    am = pd.read_csv(os.path.join(P, "metadata_all_cells.csv"), low_memory=False)
    dcol = next((c for c in DONOR_CANDS if c in am.columns), None)
    print("\n=== donor check ===")
    if dcol: print(f"  donor col '{dcol}': {am[dcol].nunique()} unique, {am[dcol].isna().sum()} missing")
    else:    print("  !!! NO donor column — donor-level inference impossible")

    print("\n=== signature overlap with Paper 1 ===")
    gs = set(genes)
    for s in ("full", "expanded", "core", "paper2_landmark"):
        pc = [l.strip() for l in open(config.SIGNATURES / f"pericentral_{s}.txt")]
        pp = [l.strip() for l in open(config.SIGNATURES / f"periportal_{s}.txt")]
        print(f"  {s:16s} PC {sum(g in gs for g in pc)}/{len(pc)}   PP {sum(g in gs for g in pp)}/{len(pp)}")

    print("\n=== Paper 2 classifier cache ===")
    print("  paper2_train.npz:", "present" if os.path.exists(config.PAPER2_TRAIN) else "NOT built")
    print("  (rebuild with 02_convert after any signature/label change — it can be stale)")

if __name__ == "__main__":
    main()
