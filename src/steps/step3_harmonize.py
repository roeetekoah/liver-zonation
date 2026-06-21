"""Step 3 — gene-ID harmonization across Paper1 ∩ Paper2 ∩ signatures (Artefact A3).

Deterministic plumbing (no science numbers): reconcile gene symbols across the two
datasets and the signature sets, and emit a coverage/mapping QC report. This is the
feasibility-doc advance gate ("confirm mapping ≥80% on real genes").

NOTE: scoring (pipeline.score) and the classifier (paper2_train.npz) already operate on
the shared gene space — the signatures were derived from Paper 2 and the npz cache was
restricted to P1∩P2 — so the *transform* is covered elsewhere. This module's job is the
explicit A3 QC artefact + a reusable, importable harmonize() primitive.

Run as a one-shot to (re)build the report:
    python steps/step3_harmonize.py        # writes results/tables/gene_mapping.csv
"""
from __future__ import annotations
import os, sys
import numpy as np, pandas as pd


def _canon(sym, aliases):
    """Canonicalize a gene symbol: strip + uppercase, then apply an optional alias map.
    The alias map (canonical UPPER -> preferred symbol) is the only judgment-laden hook;
    here it defaults to empty (a no-op) because P1∩P2 coverage is already complete."""
    s = sym.strip()
    return aliases.get(s.upper(), s)


def harmonize(p1_genes, p2_genes, signature_genes, M=None, libsize=None, aliases=None):
    """Reconcile gene identifiers across datasets; optionally build the shared feature matrix.

    Inputs
      p1_genes        : Paper 1 gene symbols (data/processed/paper1/genes.txt).
      p2_genes        : Paper 2 gene symbols (decoded from the .mat gene_name vector).
      signature_genes : the signature genes to check (a set's PC∪PP, or the global union).
      M, libsize      : optional Paper 1 counts (genes x cells) + libsizes -> z features.
      aliases         : optional {UPPER_symbol: preferred} synonym map (default: none).
    Outputs
      shared_genes    : signature symbols present in BOTH P1 and P2 (P1's original casing).
      mapping_report  : DataFrame {gene, in_p1, in_p2, in_sig, kept}.
      rate            : fraction of signature genes kept (in_p1 & in_p2).
      features        : (cells x shared_genes) z-scored log1p-CP10k, or None if M not given.
    Acceptance
      rate is high (>~0.80); any dropped anchor is visible row-by-row in mapping_report.
    """
    aliases = aliases or {}
    # canonical -> original-P1-symbol (so downstream indexing uses P1's own spelling)
    p1_canon = {}
    for g in p1_genes:
        p1_canon.setdefault(_canon(g, aliases), g)
    p2_set = {_canon(g, aliases) for g in p2_genes}

    rows, shared = [], []
    for g in dict.fromkeys(_canon(s, aliases) for s in signature_genes):   # de-dup, keep order
        in_p1 = g in p1_canon
        in_p2 = g in p2_set
        kept = in_p1 and in_p2
        rows.append({"gene": g, "in_p1": in_p1, "in_p2": in_p2, "in_sig": True, "kept": kept})
        if kept:
            shared.append(p1_canon[g])
    report = pd.DataFrame(rows, columns=["gene", "in_p1", "in_p2", "in_sig", "kept"])
    rate = float(report["kept"].mean()) if len(report) else float("nan")

    features = None
    if M is not None and libsize is not None and shared:
        gi = {g: i for i, g in enumerate(p1_genes)}
        rowsidx = [gi[g] for g in shared]
        D = np.asarray(M[rowsidx].todense()).astype(float)              # shared_genes x cells
        D = np.log1p(D / np.asarray(libsize).ravel() * 1e4)
        sd = D.std(1, keepdims=True)
        features = ((D - D.mean(1, keepdims=True)) / np.where(sd > 0, sd, 1)).T  # cells x shared
    return shared, report, rate, features


# ----------------------------- one-shot A3 report -----------------------------
def _load_p2_genes(mat_path):
    """Decode the full Paper 2 gene_name vector from the v7.3/HDF5 .mat (names only)."""
    import h5py
    with h5py.File(mat_path, "r") as f:
        t = f["t"]
        dref = lambda r: "".join(chr(int(c)) for c in f[r][:].flatten())
        return [dref(t["gene_name"][0, i]) for i in range(t["gene_name"].shape[1])]


def main():
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # src/ on path
    import config
    for _s in (sys.stdout, sys.stderr):       # UTF-8 so non-ASCII logs never crash on Windows cp1252
        try: _s.reconfigure(encoding="utf-8")
        except Exception: pass

    _read = lambda p: [g.strip() for g in open(str(p)) if g.strip()]
    p1_genes = _read(config.PAPER1 / "genes.txt")
    print("decoding Paper 2 gene namespace from the .mat ...", flush=True)
    p2_genes = _load_p2_genes(str(config.DATA_RAW / "combined_scRNAseq_atlas_M5M6M7M8.mat"))
    print(f"  P1 genes={len(p1_genes)}  P2 genes={len(p2_genes)}", flush=True)

    # families to audit: each signature tier (per arm) + the validation + plasticity anchors
    families = []
    for name, (pcp, ppp) in config.SIGNATURE_SETS.items():
        families.append((name, "pericentral", _read(pcp)))
        families.append((name, "periportal",  _read(ppp)))
    VAL_PC = ["CYP2E1", "CYP1A2", "GLUL", "PCK2"]                 # PCK2 pericentral in humans
    VAL_PP = ["ASS1", "ALDOB", "PCK1", "HAL"]
    PLAST  = ["KRT7", "KRT19", "SOX9", "SOX4", "KRT23", "NCAM1"]
    families += [("validation_anchors", "pericentral", VAL_PC),
                 ("validation_anchors", "periportal",  VAL_PP),
                 ("plasticity_markers", "plasticity",  PLAST)]

    parts, summary = [], []
    for name, arm, genes in families:
        shared, rep, rate, _ = harmonize(p1_genes, p2_genes, genes)
        rep.insert(0, "set", name); rep.insert(1, "arm", arm)
        parts.append(rep)
        summary.append({"set": name, "arm": arm, "n": len(rep), "kept": int(rep["kept"].sum()),
                        "rate": rate})

    out = pd.concat(parts, ignore_index=True)
    dst = os.path.join(str(config.TABLES), "gene_mapping.csv")
    out.to_csv(dst, index=False)

    sm = pd.DataFrame(summary)
    print("\nA3 mapping report (kept = in Paper1 AND Paper2):")
    for _, r in sm.iterrows():
        print(f"  {r['set']:18s} {r['arm']:11s} {r['kept']:4d}/{r['n']:<4d}  rate={r['rate']*100:5.1f}%")
    dropped = out[~out["kept"]]
    if len(dropped):
        print(f"\n  DROPPED ({len(dropped)}) — review before live:")
        for _, r in dropped.iterrows():
            print(f"    {r['set']}/{r['arm']}: {r['gene']} (in_p1={r['in_p1']} in_p2={r['in_p2']})")
    else:
        print("\n  no genes dropped across any family.")
    print(f"\nwrote {dst}  ({len(out)} rows)")


if __name__ == "__main__":
    main()
