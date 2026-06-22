"""STEP 1 — tissue-source-controlled, donor-level gene reality check.
No ruler, no slope, no correlation. Just: per donor, per gene, mean log1p-CP10k LEVEL and
FRACTION of cells expressing (>0), grouped by stage and by lobe. SCT-scale (caveat). Unit = donor.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/src")
from analysis import common as C
import numpy as np, pandas as pd

GENES = {
    "PC-identity/Wnt": ["GLUL", "CYP3A4", "CYP1A2"],
    "PC-detox/redox":  ["CYP2E1", "ADH1B", "ADH4", "AKR1D1", "SLCO1B3"],
    "PP-metabolic":    ["PCK1", "ALDOB", "HAL", "ASS1"],
    "ductular/plast":  ["KRT7", "KRT19", "EPCAM"],
    "explant/stress":  ["FOS", "JUN", "VEGFA", "HSPA1A"],
    "housekeep/ident": ["ACTB", "GAPDH", "ALB"],
}
FLAT = [g for v in GENES.values() for g in v]

# ---- metadata: cell_id, donor, stage, lobe ----
md = pd.read_csv(os.path.join(str(C.config.PAPER1), "metadata_all_cells.csv"),
                 usecols=["cell_id", "Patient.ID", "Disease.status", "Lobe"], low_memory=False)
md = md.rename(columns={"Patient.ID": "donor", "Disease.status": "stage", "Lobe": "lobe"})
md["donor"] = md["donor"].astype(str); md["lobe"] = md["lobe"].astype(str)

# ---- expression (log1p-CP10k per cell, SCT-scale) for the requested genes ----
G = C.raw_gene_matrix(FLAT)                       # index = cell_id, cols = present genes
present = [g for g in FLAT if g in G.columns]
miss = [g for g in FLAT if g not in G.columns]
if miss: print("absent genes (skipped):", miss)
G = G.reset_index().merge(md, on="cell_id", how="inner")
print(f"cells joined: {len(G):,}")

STAGES = C.STAGE_ORDER

def per_donor(df, genes):
    """Return per-(donor) level (mean) and frac (>0) for each gene, plus n_cells."""
    rows = []
    for d, s in df.groupby("donor"):
        r = {"donor": d, "n_cells": len(s)}
        for g in genes:
            r[g + "|lvl"] = s[g].mean()
            r[g + "|frc"] = (s[g] > 0).mean()
        rows.append(r)
    return pd.DataFrame(rows)

def across_donor(df, genes, label):
    pd_ = per_donor(df, genes)
    out = {"group": label, "n_donors": len(pd_), "med_cells": int(pd_["n_cells"].median()) if len(pd_) else 0}
    for g in genes:
        out[g + "|lvl"] = pd_[g + "|lvl"].mean()
        out[g + "|frc"] = pd_[g + "|frc"].mean()
    return out, pd_

def show(title, rows, genes):
    print("\n" + "=" * 100); print(title); print("=" * 100)
    df = pd.DataFrame(rows)
    # level table
    lvl = df[["group", "n_donors", "med_cells"] + [g + "|lvl" for g in genes]].copy()
    lvl.columns = ["group", "nD", "medCells"] + genes
    frc = df[["group"] + [g + "|frc" for g in genes]].copy()
    frc.columns = ["group"] + genes
    with pd.option_context("display.width", 200, "display.max_columns", 40, "display.float_format", lambda x: f"{x:.2f}"):
        print("\n-- mean LEVEL (across-donor mean of per-donor mean log1p-CP10k) --")
        print(lvl.to_string(index=False))
        print("\n-- FRACTION expressing (across-donor mean of per-donor frac >0) --")
        print(frc.to_string(index=False))

# ===== (A) by stage, RIGHT-LOBE ONLY vs ALL-LOBE =====
for scope, mask in [("RIGHT-LOBE ONLY", G["lobe"] == "Right"), ("ALL LOBES", G["lobe"].notna())]:
    rows = []
    for st in STAGES:
        sub = G[mask & (G["stage"] == st)]
        if len(sub) == 0: continue
        out, _ = across_donor(sub, present, C.STAGE_SHORT.get(st, st))
        rows.append(out)
    show(f"(A) Stage comparison — {scope}", rows, present)

# ===== (B) WITHIN end-stage CL donors: Right vs Caudate vs Left (paired) =====
es = G[G["stage"] == "end stage"]
print("\n" + "#" * 100)
print("(B) WITHIN-END-STAGE LOBE TEST (same 5 CL donors; paired) — does the signal differ by lobe?")
print("#" * 100)
for g in present:
    line = [f"{g:9s}"]
    for lobe in ["Right", "Caudate", "Left"]:
        sub = es[es["lobe"] == lobe]
        pd_ = per_donor(sub, [g])
        lvl = pd_[g + "|lvl"].mean(); frc = pd_[g + "|frc"].mean()
        line.append(f"{lobe[:3]}: lvl={lvl:.2f} frc={frc:.2f} (nD={len(pd_)})")
    print("  " + " | ".join(line))

# paired per-donor Right vs (Caudate+Left) for the key movers
print("\n-- paired per-donor: end-stage Right vs non-Right (Caudate/Left), key genes --")
key = [g for g in ["GLUL", "CYP2E1", "CYP3A4", "ADH1B", "PCK1", "ALDOB", "HAL"] if g in present]
for d, s in es.groupby("donor"):
    rt = s[s["lobe"] == "Right"]; nr = s[s["lobe"].isin(["Caudate", "Left"])]
    if len(rt) == 0 or len(nr) == 0: continue
    parts = []
    for g in key:
        parts.append(f"{g}:{rt[g].mean():.2f}/{nr[g].mean():.2f}")
    print(f"  CL {d:6s} (R n={len(rt)}, nR n={len(nr)}):  " + "  ".join(parts))
print("  [format  gene:RightLvl/nonRightLvl ;  if these differ, 'change' is lobe-driven, not disease]")
