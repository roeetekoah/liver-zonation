"""
Doublet chase — does the residual biliary signal that SURVIVED decontX (F18) come from
hepatocyte-cholangiocyte doublets that Paper 1's crude ">50,000-count" filter missed?

A true hepatocyte-cholangiocyte DOUBLET co-captures a whole cholangiocyte transcriptome, so it
should show TWO things at once: (a) co-detection of cholangiocyte STRUCTURAL markers (KRT19/KRT7)
that a real hepatocyte does not express, and (b) an inflated TOTAL UMI count (two cells' worth).
Ambient contamination would produce (a) WITHOUT (b) — ambient adds a few stray molecules, it does
not double a nucleus's library size. So total-count elevation is the discriminator doublet-vs-ambient.

Outputs results/tables/analysis/doublet_chase.csv with, per fibrosis stage F0..F4:
  n_hep                : biopsy hepatocyte nuclei
  pct_doublet_suspect  : % with KRT19>=2 OR KRT7>=2 UMI
  med_total_suspect    : median total UMI of the suspects (doublet signature if >> rest)
  med_total_rest       : median total UMI of the other hepatocytes
  n_over_50k           : nuclei above Paper 1's 50,000-count doublet cut (they would remove)
  epcam_frac_in_suspect: share of stage EPCAM UMIs carried by the suspects (how much they explain)
"""
import pandas as pd, numpy as np

PANEL = "data/processed/paper1/raw_panel_counts.csv"
META  = "data/processed/paper1/metadata_all_cells.csv"
OUT   = "results/tables/analysis/doublet_chase.csv"

df = pd.read_csv(PANEL, low_memory=False); df["donor"] = df["donor"].astype(str)
md = (pd.read_csv(META, usecols=["Patient.ID", "Fibrosis.score..F0.4."], low_memory=False)
        .rename(columns={"Patient.ID": "donor", "Fibrosis.score..F0.4.": "F"}))
md["donor"] = md["donor"].astype(str); md["F"] = pd.to_numeric(md["F"], errors="coerce")
df = df.merge(md.groupby("donor")["F"].first().reset_index(), on="donor", how="left")

# biopsy hepatocytes only (drop deceased-donor CL* explants + healthy controls — procurement confound)
hep = df[(df["annotation"] == "Hepatocytes")
         & (~df["donor"].str.startswith("CL"))
         & (df["stage"] != "Healthy control")].copy()
hep["suspect"] = (hep["KRT19"] >= 2) | (hep["KRT7"] >= 2)

rows = []
for F in [0, 1, 2, 3, 4]:
    s = hep[hep.F == F]
    susp = s[s.suspect]
    rows.append(dict(
        F=F, n_hep=len(s),
        pct_doublet_suspect=round(100 * s.suspect.mean(), 3),
        med_total_suspect=int(susp["E_raw"].median()) if len(susp) else 0,
        med_total_rest=int(s[~s.suspect]["E_raw"].median()),
        n_over_50k=int((s["E_raw"] > 50000).sum()),
        epcam_frac_in_suspect=round(susp["EPCAM"].sum() / s["EPCAM"].sum(), 4) if s["EPCAM"].sum() else 0.0,
    ))
res = pd.DataFrame(rows)
res.to_csv(OUT, index=False)
print(res.to_string(index=False))
print(f"\nwrote {OUT}")
print(f"total biopsy hep nuclei over 50,000 counts (Paper 1's filter): {(hep['E_raw']>50000).sum()} of {len(hep)}")
