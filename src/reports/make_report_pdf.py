#!/usr/bin/env python3
"""Assemble a PDF report of the signature-set battery + H1/H2/H3 transfer results.
Reads results/tables/* and results/figures/* ; writes results/Signature_Battery_Report.pdf.
Run:  python src/make_report_pdf.py
"""
import os, sys, datetime
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # src/
import config

T = config.TABLES; FIG = config.FIGURES
OUT_PDF = os.path.join(str(config.RESULTS), "Signature_Battery_Report.pdf")


def _text_page(pdf, title, lines, fontsize=10):
    fig = plt.figure(figsize=(11, 8.5)); fig.text(0.06, 0.95, title, fontsize=16, weight="bold")
    fig.text(0.06, 0.90, "\n".join(lines), fontsize=fontsize, va="top", family="monospace")
    pdf.savefig(fig); plt.close(fig)


def _table_page(pdf, title, df, cols, fontsize=7):
    fig, ax = plt.subplots(figsize=(11, 8.5)); ax.axis("off")
    ax.set_title(title, fontsize=14, weight="bold", loc="left")
    d = df[cols].copy()
    for c in d.columns:
        if d[c].dtype.kind == "f": d[c] = d[c].map(lambda x: "" if pd.isna(x) else f"{x:.3g}")
    tbl = ax.table(cellText=d.values, colLabels=d.columns, loc="upper left", cellLoc="center")
    tbl.auto_set_font_size(False); tbl.set_fontsize(fontsize); tbl.scale(1, 1.4)
    pdf.savefig(fig); plt.close(fig)


def _img_page(pdf, title, img_path):
    if not os.path.exists(img_path): return
    fig = plt.figure(figsize=(11, 8.5)); fig.suptitle(title, fontsize=14, weight="bold")
    ax = fig.add_axes([0.03, 0.03, 0.94, 0.9]); ax.axis("off")
    ax.imshow(plt.imread(img_path)); pdf.savefig(fig); plt.close(fig)


def main():
    summ = pd.read_csv(os.path.join(T, "signature_battery_summary.csv")) if os.path.exists(
        os.path.join(T, "signature_battery_summary.csv")) else pd.DataFrame()
    decision = ""
    dp = os.path.join(T, "selected_set_decision.txt")
    if os.path.exists(dp): decision = open(dp).read()

    with PdfPages(OUT_PDF) as pdf:
        # 1. title / overview
        _text_page(pdf, "Spatial Degradation of Hepatocyte Zonation — Signature-Set Battery", [
            f"Generated: {datetime.date.today().isoformat()}",
            "",
            "Paper 1 (disease): Gribben/Vallier 2024, snRNA-seq, 47 donors, ~69k hepatocytes (GSE202379).",
            "Paper 2 (healthy ruler): Yakubovsky/Itzkovitz 2026 spatial atlas; eta = sumPP/(sumPP+sumPC).",
            "",
            "METHOD: build candidate PC/PP gene sets; score each as coord = mean_z(PC) - mean_z(PP);",
            "judge RULER QUALITY on HEALTHY metrics only (validation signs, PC-PP anticorrelation,",
            "split-half reproducibility). Disease H1/H2/H3 are TRANSFER results, never used to pick a set.",
            "",
            "H1 = donor-level collapse of zonation across stage (spread down, PC-PP anticorr -> 0).",
            "H2 = zonal-slope loss of zonation genes (held-out, donor-level).",
            "H3 = de-zonation <-> plasticity coupling (donor-level).",
            "",
            "See: candidate_set_build_report.csv, signature_battery_summary.csv, selected_set_decision.txt.",
        ])
        # 2. battery summary table (healthy ruler quality + role)
        if len(summ):
            _table_page(pdf, "Signature battery — ruler quality (HEALTHY) + recommended role", summ,
                        ["set_name", "n_pc", "n_pp", "validation_pass", "healthy_pc_pp_anticorr",
                         "healthy_splithalf_rho_mean", "recommended_role"])
            # 3. disease transfer table (clearly labelled)
            _table_page(pdf, "Disease TRANSFER results (H1/H2) — NOT used for set selection", summ,
                        ["set_name", "h1_coord_spread_rho_vs_stage", "h1_coord_spread_perm_p",
                         "h1_pc_pp_anticorr_rho_vs_stage", "h2_frac_weakening", "h2_median_trend_rho",
                         "recommended_role"])
        # 4. combined panel
        _img_page(pdf, "Four rulers x H1/H2/H3 (donor-level)", os.path.join(str(FIG), "ruler_panel.png"))
        # 4b. H2b program-level differential vulnerability (gene-rich full set)
        pp = os.path.join(T, "paper2_full", "h2_program_summary.csv")
        if os.path.exists(pp):
            _table_page(pdf, "H2b — program-level zonal-slope loss (paper2_full; more negative = faster)",
                        pd.read_csv(pp), ["program", "n_genes", "median_trend_rho",
                                          "frac_weakening", "n_q05_weakening"], fontsize=9)
        # 5. decision + agreement
        agree = ""
        ap = os.path.join(T, "unsupervised_axis_eval.csv")
        if os.path.exists(ap):
            a = pd.read_csv(ap).iloc[0]
            agree = (f"Unsupervised(PCA) vs landmark-signature agreement: rho(axis,coord)="
                     f"{a['rho_axis_coord']:+.3f}, rho(axis,pc)={a['rho_axis_pc']:+.3f}, "
                     f"rho(axis,pp)={a['rho_axis_pp']:+.3f}.")
        _text_page(pdf, "Selected set decision + unsupervised agreement",
                   (decision.splitlines() or ["(no decision file)"]) + ["", agree])
    print("wrote", OUT_PDF)


if __name__ == "__main__":
    main()
