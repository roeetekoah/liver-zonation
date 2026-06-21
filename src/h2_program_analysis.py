#!/usr/bin/env python3
"""H2b — program-level differential vulnerability: which biological programs lose their zonal
restriction fastest? Groups the H2 slope-loss genes into curated programs and compares the
distribution of donor-level slope-trend rho (more negative = weakens faster). Also emits a
ranked outlier table and (if available) a classic-DE cross (does the gene also change level?).

Run:  python src/h2_program_analysis.py [set_name]   (default: unsupervised)
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # src/
import config

T = config.TABLES

PROGRAMS = {
    "cyp_xenobiotic": "CYP2E1 CYP1A2 CYP3A4 CYP2C8 CYP2C18 CYP2C19 CYP2C9 CYP27A1 CYP2A6 CYP2A7 "
                      "CYP3A5 AOX1 FMO3 FMO5 GSTA1 GSTA2 UGT2B4 UGT1A1 UGT2B7 ADH1A ADH1B ADH1C "
                      "ADH4 ADH6 AKR1D1 AKR1C1 AMACR DCXR ALDH1L1 ALDH6A1",
    "bile_acid_transport": "SLCO1B3 SLCO1B1 SLC10A1 ABCB11 ABCC2 ABCB4 BAAT SLC51A SLC51B CYP7A1 CYP8B1",
    "wnt_pericentral_identity": "GLUL LGR5 AXIN2 TBX3 NKD1 RNF43 ZNRF3 NOTUM TCF7L2 RHBG CTNNB1",
    "urea_nitrogen": "ASS1 ASL ARG1 CPS1 OTC NAGS GLS2 GLUD1 SLC38A4 TAT HAL SDS GLDC AGXT",
    "lipid_metabolism": "FASN MLXIPL SCD ELOVL5 ELOVL6 ACSL5 ACSL1 GPAM APOA5 ACACA ACACB FABP1 "
                        "APOB APOA2 APOC1 APOH PLIN2 HSD17B13 DGAT2 SREBF1",
    "acute_phase_secreted": "SERPINA1 APOA1 ALB CRP SAA1 SAA2 SAA4 HP HPX TF FGA FGB FGG C7 C8G C9 "
                            "A2M ORM1 ORM2 AGT HAMP LBP SERPINA3 SERPING1 APOF",
    "cholangiocyte_plasticity": "KRT7 KRT19 SOX9 SOX4 KRT23 NCAM1 KLF6 CFTR EPCAM SPP1 TNFRSF12A ANXA4 DCDC2",
}
GENE2PROG = {}
for prog, s in PROGRAMS.items():
    for g in s.split():
        GENE2PROG.setdefault(g, prog)


def main(which="unsupervised"):
    sd = os.path.join(T, which)
    h2p = os.path.join(sd, "h2_slope_loss.csv")
    if not os.path.exists(h2p):
        print(f"no {h2p} — run the battery/pipeline for '{which}' first"); return
    df = pd.read_csv(h2p)
    df["program"] = df["gene"].map(lambda g: GENE2PROG.get(g, "other"))

    # ---- program-level summary (H2b) ----
    rows = []
    for prog, gg in df.groupby("program"):
        tr = gg["mean_slope_trend_rho"].values
        rows.append({"signature_set": which, "program": prog, "n_genes": len(gg),
                     "median_trend_rho": float(np.nanmedian(tr)),
                     "frac_weakening": float(np.mean(tr < 0)),
                     "n_q05_weakening": int(((gg.get("q_trend", 1) < 0.05) & (tr < 0)).sum())})
    prog_df = pd.DataFrame(rows).sort_values("median_trend_rho")
    prog_df.to_csv(os.path.join(sd, "h2_program_summary.csv"), index=False)

    # ---- ranked outliers ----
    s = df.sort_values("mean_slope_trend_rho")
    out = pd.concat([s.head(15).assign(group="strongest_weakening"),
                     s.tail(15).assign(group="weakest_or_strengthening")])
    out[["signature_set" if "signature_set" in out else "gene"]] if False else None
    out = out[["gene", "direction", "program", "mean_slope_trend_rho",
               "frac_splits_weakening", "q_trend", "group"]]
    out.insert(0, "signature_set", which)
    out.to_csv(os.path.join(sd, "h2_outliers.csv"), index=False)

    # ---- classic-DE cross (does a de-zonating gene also change level?) ----
    de_note = "no DE table found"
    de_pieces = []
    for z in ("central", "portal"):
        dep = os.path.join(T, "paper2_full", f"de_{z}.csv")
        if os.path.exists(dep):
            d = pd.read_csv(dep)[["gene", "rho_vs_stage", "q"]].rename(
                columns={"rho_vs_stage": f"level_rho_{z}", "q": f"level_q_{z}"})
            de_pieces.append(d)
    if de_pieces:
        merged = df[["gene", "program", "mean_slope_trend_rho", "q_trend"]].copy()
        for d in de_pieces:
            merged = merged.merge(d, on="gene", how="left")
        merged.insert(0, "signature_set", which)
        merged.to_csv(os.path.join(sd, "h2_slopeloss_vs_DE.csv"), index=False)
        de_note = "wrote h2_slopeloss_vs_DE.csv (slope-loss x classic level-DE)"

    print(f"[{which}] program-level slope-trend (most negative = weakens fastest):")
    print(prog_df.to_string(index=False))
    print(f"\nwrote {sd}/h2_program_summary.csv, h2_outliers.csv  ({de_note})")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "unsupervised")
