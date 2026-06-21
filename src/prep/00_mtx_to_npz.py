#!/usr/bin/env python3
"""
One-time conversion: text MatrixMarket `counts.mtx` -> compact SciPy sparse `counts.npz`.

WHY: `scipy.io.mmread` re-parses the whole text matrix into memory every run, which spikes
RAM (several GB, possibly ~8-12 GB on the real Paper 1 file). A binary `.npz` loads fast and
with far lower peak memory. After this runs once, `pipeline.load()` prefers `counts.npz`.

Run once (after data/processed/paper1/counts.mtx exists):
    python src/prep/00_mtx_to_npz.py
"""
import os, sys, scipy.io, scipy.sparse as sp
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # src/ on path
import config

src = str(config.PAPER1 / "counts.mtx")
dst = str(config.PAPER1 / "counts.npz")

def main():
    if not os.path.exists(src):
        sys.exit(f"missing {src} — run prep/01 first")
    print(f"reading {src}  (this is the memory-heavy text parse) ...", flush=True)
    M = scipy.io.mmread(src).tocsc().astype("float32")
    print(f"  shape={M.shape}  nnz={M.nnz}", flush=True)
    sp.save_npz(dst, M)
    print(f"wrote {dst}  ({os.path.getsize(dst)/1e6:.0f} MB). pipeline.load() will prefer it.",
          flush=True)

if __name__ == "__main__":
    main()
