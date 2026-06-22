#!/usr/bin/env python3
"""H2b — program-level differential vulnerability, done rigorously.

Input is the TRANSCRIPTOME-WIDE per-gene slope-trend table (h2_transcriptome_wide.csv), which is
computed on a VALID, frozen ruler coordinate (default expanded_curated) over ALL ~30k genes. We
group genes into curated programs and, for each program, formally test whether its genes' zonal
slopes weaken MORE than the genome background (Mann-Whitney U, one-sided 'more negative', with a
rank-biserial effect size), BH-corrected across programs. This is what makes the "Wnt de-zonates
first" claim a test, not just a median; and it explains why H2b finds structure even though
per-gene FDR (H2c) flags few individual genes: aggregation within a program + contrast against
background recovers the power that per-gene testing throws away.

Run:  python src/h2_program_analysis.py [ruler]   (default expanded_curated)
"""
import os, sys
import numpy as np, pandas as pd
from scipy.stats import mannwhitneyu
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # src/
import config
from steps.common import log, bh, OUT

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


def main(ruler="expanded_curated"):
    twp = os.path.join(OUT, ruler, "h2_transcriptome_wide.csv")
    if not os.path.exists(twp):
        print(f"need {twp} — run h2_transcriptome_wide.py {ruler} first"); return
    df = pd.read_csv(twp).dropna(subset=["slope_trend_rho"])
    df["program"] = df["gene"].map(lambda g: GENE2PROG.get(g, "other"))
    bg = df["slope_trend_rho"].values                       # genome background

    rows = []
    for prog in list(PROGRAMS) + ["other"]:
        gg = df[df["program"] == prog]
        tr = gg["slope_trend_rho"].values
        if len(tr) == 0:
            continue
        p = rbis = np.nan
        if prog != "other" and len(tr) >= 3:
            other = df[df["program"] != prog]["slope_trend_rho"].values
            u = mannwhitneyu(tr, other, alternative="less")     # program MORE negative than rest?
            p = float(u.pvalue); auc = u.statistic / (len(tr) * len(other)); rbis = 2 * auc - 1
        rows.append({"signature_set": ruler, "program": prog, "n_genes": int(len(tr)),
                     "median_trend_rho": float(np.nanmedian(tr)), "frac_weakening": float(np.mean(tr < 0)),
                     "mwu_p_more_negative_than_background": p, "rank_biserial_vs_background": rbis})
    out = pd.DataFrame(rows)
    prog_mask = out["program"] != "other"
    out.loc[prog_mask, "q_bh"] = bh(out.loc[prog_mask, "mwu_p_more_negative_than_background"].values)
    out = out.sort_values("median_trend_rho")
    out.to_csv(os.path.join(OUT, ruler, "h2_program_summary.csv"), index=False)

    log(f"H2b program-level vulnerability [coordinate = valid '{ruler}' ruler; background median "
        f"rho={np.nanmedian(bg):+.3f}, {np.mean(bg<0)*100:.0f}% of all genes weaken]:")
    for _, r in out.iterrows():
        extra = "" if r["program"] == "other" else (f"  MWU vs bg p={r['mwu_p_more_negative_than_background']:.2g}"
                                                    f" q={r.get('q_bh', np.nan):.2g} rbis={r['rank_biserial_vs_background']:+.2f}")
        log(f"  {r['program']:24s} n={int(r['n_genes']):4d} median={r['median_trend_rho']:+.3f} "
            f"weak={r['frac_weakening']*100:3.0f}%{extra}")
    log(f"  wrote {os.path.join(OUT, ruler, 'h2_program_summary.csv')}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "expanded_curated")
