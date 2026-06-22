"""RAW-COUNT analysis (replaces SCT exploratory work). Unit = donor, never the cell.
Builds: (A) donor-level raw gene table, (B) right-lobe-only primary stage result,
(F) QC/source/batch table + stage-collinearity check. Source: data/processed/paper1/raw_panel_counts.csv
(raw RNA UMIs extracted from the Seurat object) joined to per-cell QC from metadata_all_cells.csv.
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

RAW = os.path.join(str(config.PAPER1), "raw_panel_counts.csv")
META = os.path.join(str(config.PAPER1), "metadata_all_cells.csv")
OUTD = str(config.ANALYSIS_TABLES); os.makedirs(OUTD, exist_ok=True)

STAGE_ORDER = ["Healthy control", "NAFLD", "NASH w/o cirrhosis", "NASH with cirrhosis", "end stage"]
SHORT = {"Healthy control":"Healthy","NAFLD":"NAFLD","NASH w/o cirrhosis":"NASH",
         "NASH with cirrhosis":"Cirrhosis","end stage":"End-stage"}

GROUPS = {
 "detox":      ["CYP2E1","CYP1A2","ADH4","ADH1B","AKR1D1","SLCO1B3"],
 "pc_ident":   ["GLUL","CYP3A4","LGR5","AXIN2"],
 "pp":         ["PCK1","ALDOB","HAL","ASS1","CPS1","ARG1"],
 "stress":     ["FOS","JUN","JUNB","JUND","ATF3","DUSP1","HSPA1A","HSPA1B"],
 "house":      ["ACTB","GAPDH","B2M","ALB","TTR","APOA1"],
 "ductular":   ["KRT7","KRT19","EPCAM","SOX4","KRT23","NCAM1","MUC1","BCL2"],
}

def tissue_source(donor, stage):
    """INFERRED (pending paper confirmation) from donor-ID scheme + stage.
    CL* = cirrhotic explant; HL* = surgical healthy; 30/98 = healthy atlas (other);
    plain numeric disease = needle biopsy."""
    d = str(donor)
    if d.startswith("CL"): return "explant"
    if d.startswith("HL"): return "surgical_healthy"
    if stage == "Healthy control": return "healthy_other"
    return "needle_biopsy"

def main():
    df = pd.read_csv(RAW, low_memory=False)
    df["donor"] = df["donor"].astype(str); df["lobe"] = df["lobe"].astype(str)
    genes = [g for grp in GROUPS.values() for g in grp if g in df.columns]

    # hepatocytes only
    print("annotations:", df["annotation"].value_counts().to_dict())
    hep = df[df["annotation"] == "Hepatocytes"].copy()
    print(f"hepatocyte nuclei: {len(hep):,}  donors: {hep['donor'].nunique()}")

    # join per-cell QC
    qc = pd.read_csv(META, usecols=["cell_id","nFeature_RNA","percent.mt.RNA","percent.rp.RNA"],
                     low_memory=False).rename(columns={"nFeature_RNA":"nFeat","percent.mt.RNA":"mt",
                                                       "percent.rp.RNA":"rp"})
    hep = hep.merge(qc, on="cell_id", how="left")
    hep["source"] = [tissue_source(d, s) for d, s in zip(hep["donor"], hep["stage"])]
    hep["stress_umi"] = hep[GROUPS["stress"]].sum(axis=1)

    # ---------- (A) donor x lobe x stage gene table ----------
    rows = []
    for (donor, lobe, stage), s in hep.groupby(["donor","lobe","stage"]):
        N = len(s); E = s["E_raw"].sum()
        base = dict(donor=donor, lobe=lobe, stage=stage, N_hep=N, E_raw=int(E))
        for g in genes:
            k = int((s[g] > 0).sum()); M = int(s[g].sum())
            rows.append({**base, "gene":g, "k_raw_pos":k, "frac_raw_pos":k/N,
                         "M_raw":M, "UMIs_per_10k": 1e4*M/E if E>0 else np.nan})
    A = pd.DataFrame(rows)
    A.to_csv(os.path.join(OUTD,"rawA_donor_lobe_stage_gene.csv"), index=False)
    # also donor x stage (all lobes) and right-lobe-only donor x stage
    def donor_stage(hsub, tag):
        r = []
        for (donor, stage), s in hsub.groupby(["donor","stage"]):
            N=len(s); E=s["E_raw"].sum()
            for g in genes:
                k=int((s[g]>0).sum()); M=int(s[g].sum())
                r.append(dict(donor=donor, stage=stage, N_hep=N, gene=g, frac_raw_pos=k/N,
                              UMIs_per_10k=1e4*M/E if E>0 else np.nan))
        d=pd.DataFrame(r); d.to_csv(os.path.join(OUTD,f"rawA_donor_stage_{tag}.csv"),index=False); return d
    dA_all   = donor_stage(hep, "alllobe")
    dA_right = donor_stage(hep[hep["lobe"]=="Right"], "right")

    # ---------- (B) RIGHT-LOBE-ONLY primary: across-donor summary by stage ----------
    def across(dft, metric):
        piv = (dft.groupby(["stage","gene"])[metric].mean().unstack("gene"))
        piv = piv.reindex([s for s in STAGE_ORDER if s in piv.index])
        piv.index = [SHORT[s] for s in piv.index]
        nD = dft.groupby("stage")["donor"].nunique().reindex([s for s in STAGE_ORDER if s in dft["stage"].unique()])
        nD.index = [SHORT[s] for s in nD.index]
        return piv, nD
    print("\n" + "="*90 + "\n(B) RIGHT-LOBE-ONLY primary result  (donor = unit)\n" + "="*90)
    for metric, lab in [("frac_raw_pos","FRACTION of hepatocytes expressing (raw UMI>0)"),
                        ("UMIs_per_10k","raw UMIs per 10k (pseudobulk)")]:
        piv, nD = across(dA_right, metric)
        show = ["CYP2E1","CYP1A2","AKR1D1","SLCO1B3","ADH4","GLUL","CYP3A4","PCK1","ALDOB","HAL","ASS1",
                "FOS","JUN","HSPA1A","ALB","ACTB"]
        show = [g for g in show if g in piv.columns]
        out = piv[show].copy(); out.insert(0,"nD", nD)
        with pd.option_context("display.width",200,"display.max_columns",40,"display.float_format",lambda x:f"{x:.2f}"):
            print(f"\n-- {lab} --"); print(out.to_string())

    # ---------- (F) QC / source / batch table per donor ----------
    print("\n" + "="*90 + "\n(F) QC / SOURCE table per donor  (is stage collinear with technical?)\n" + "="*90)
    frows = []
    for donor, s in hep.groupby("donor"):
        frows.append(dict(donor=donor, stage=s["stage"].iloc[0], source=s["source"].iloc[0],
                          lobes="+".join(sorted(str(x) for x in s["lobe"].unique())), n_hep=len(s),
                          med_nCountRNA=int(s["E_raw"].median()), med_nFeat=int(s["nFeat"].median()),
                          med_mt=round(s["mt"].median(),2), med_rp=round(s["rp"].median(),2),
                          stress_umi_mean=round(s["stress_umi"].mean(),2),
                          ALB_p10k=round(1e4*s["ALB"].sum()/s["E_raw"].sum(),1),
                          KRT19_frac=round((s["KRT19"]>0).mean(),3),
                          EPCAM_frac=round((s["EPCAM"]>0).mean(),3)))
    F = pd.DataFrame(frows)
    F["__o"]=F["stage"].map({s:i for i,s in enumerate(STAGE_ORDER)}); F=F.sort_values(["__o","donor"]).drop(columns="__o")
    F.to_csv(os.path.join(OUTD,"rawF_qc_source.csv"), index=False)
    with pd.option_context("display.width",220,"display.max_columns",40):
        print(F.to_string(index=False))
    print("\n-- stage x source (donor counts) --")
    print(pd.crosstab(F["stage"].map(SHORT).reindex(F.index), F["source"]).reindex([SHORT[s] for s in STAGE_ORDER if s in F["stage"].unique()]))
    print("\n-- per-stage medians (donor-level) --")
    g = F.groupby(F["stage"].map(SHORT))[["med_nCountRNA","med_nFeat","med_mt","stress_umi_mean"]].median()
    print(g.reindex([SHORT[s] for s in STAGE_ORDER if s in F["stage"].unique()]).to_string())
    print("\nwrote rawA_*.csv, rawF_qc_source.csv to", OUTD)

if __name__ == "__main__":
    main()
