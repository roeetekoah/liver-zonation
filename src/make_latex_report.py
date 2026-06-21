#!/usr/bin/env python3
"""Generate a clean, ORDERED LaTeX report of every inspected ruler: per-set explanation +
derivation + validation (8-marker gate) + controls (ruler diagnostics) + H1/H2/H3 transfer
results + the collapse figure. Sets are ordered by HEALTHY-ruler quality (NOT disease strength,
to avoid cherry-picking). Writes results/Zonation_Ruler_Report.tex and compiles with pdflatex.

Run:  python src/make_latex_report.py
"""
import os, sys, subprocess, datetime
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # src/
import config

T = str(config.TABLES); FIG = str(config.FIGURES); RES = str(config.RESULTS)
SUMM = os.path.join(T, "signature_battery_summary.csv")

DESC = {
    "paper2_landmark": "Paper 2's exact 20+20 hepatocyte landmark genes (Hepatocyte-\\{PC,PP\\}-LM.csv), "
        "the genes Paper 2 itself uses to assign per-cell snRNA zonation (eta method).",
    "core_curated": "13+8 hand-curated, highly interpretable canonical anchors (GLUL, CYP2E1, ASS1, HAL, ...).",
    "expanded_curated": "paper2\\_landmark plus curated extra anchors (26+23), de-duplicated.",
    "paper2_top50": "Top 50+50 genes by |center-of-mass| among q<0.05 zonated genes (supplementary table 8).",
    "paper2_top100": "Top 100+100 zonated genes by |center-of-mass|.",
    "paper2_top250": "Top 250+250 zonated genes by |center-of-mass|.",
    "paper2_full": "All significant zonated hepatocyte genes (q<0.05, max-expr>1e-4), split by COM sign (1624+447).",
    "selected_frozen": "The auto-frozen primary ruler (a copy of the best signature set by healthy metrics).",
    "full": "Legacy transcriptome-wide unweighted signature mean (main pipeline).",
    "supervised": "Whole-transcriptome multinomial logistic regression trained on Paper 2 zone labels (landmarks excluded).",
    "unsupervised": "Label-free PCA porto-central axis learned on Paper 1 HEALTHY cells (sensitivity version).",
    "unsupervised_top50": "The 50+50 strongest +/- loading genes of the unsupervised PCA axis, scored as a signature.",
    "unsupervised_top100": "The 100+100 strongest +/- loading genes of the unsupervised PCA axis.",
    "unsupervised_lasso": "Lasso (L1) sparse ruler distilling the Paper-2-trained PCA axis (clean/external training).",
    "unsupervised_elasticnet": "Elastic-net (L1+L2) sparse ruler distilling the Paper-2-trained PCA axis (clean).",
}


def esc(s):
    """Escape LaTeX specials in plain tokens (set names / roles). No backslashes occur in these."""
    s = str(s)
    for a, b in [("_", r"\_"), ("&", r"\&"), ("%", r"\%"), ("#", r"\#")]:
        s = s.replace(a, b)
    return s


def rd(p):
    return pd.read_csv(p) if os.path.exists(p) else None


def fnum(x, f="{:+.3f}"):
    try:
        return f.format(float(x)) if pd.notna(x) else "n/a"
    except Exception:
        return "n/a"


def quality_score(r):
    if not r["validation_pass"]:
        return -99
    ac = r["healthy_pc_pp_anticorr"]; sh = r["healthy_splithalf_rho_mean"]
    ac = 0 if pd.isna(ac) else ac; sh = 0 if pd.isna(sh) else sh
    return (sh) + max(0.0, -ac)        # reward reproducibility + bipolar (negative) anticorr


def section(s, srow):
    sd = os.path.join(T, s)
    L = [f"\\section*{{{esc(s)} \\hfill {esc(srow['recommended_role'])}}}"]
    desc = DESC.get(s, "Candidate zonation ruler.")
    L.append(desc + f" \\textbf{{Genes:}} {int(srow['n_pc'])} PC + {int(srow['n_pp'])} PP.")
    # validation + controls
    val = rd(os.path.join(sd, "validation.csv")); rul = rd(os.path.join(sd, "ruler_diagnostics.csv"))
    nv = f"{int(srow['n_validation_correct'])}/{int(srow['n_validation_present'])}" if val is not None else "n/a"
    L.append("\\paragraph{Validation (8-marker healthy gate) \\& controls.} "
             f"Markers correct: {nv} ({'PASS' if srow['validation_pass'] else 'FAIL'}). "
             f"Healthy PC--PP anticorrelation = {fnum(srow['healthy_pc_pp_anticorr'])} "
             f"(want strongly negative); split-half reproducibility = "
             f"{fnum(srow['healthy_splithalf_rho_mean'])}; coherence PC/PP = "
             f"{fnum(srow['healthy_coherence_pc'])}/{fnum(srow['healthy_coherence_pp'])}.")
    # H1
    L.append("\\paragraph{H1 (donor-level collapse, TRANSFER).} "
             f"coord-spread vs stage rho = {fnum(srow['h1_coord_spread_rho_vs_stage'])} "
             f"(perm p = {fnum(srow['h1_coord_spread_perm_p'], '{:.2g}')}); "
             f"PC--PP anticorr trend rho = {fnum(srow['h1_pc_pp_anticorr_rho_vs_stage'])} "
             f"(perm p = {fnum(srow['h1_pc_pp_anticorr_perm_p'], '{:.2g}')}).")
    # H2
    if pd.notna(srow.get("h2_n_genes_tested", np.nan)):
        L.append("\\paragraph{H2 (zonal slope-loss, held-out).} "
                 f"{int(srow['h2_n_genes_tested'])} genes tested; "
                 f"{srow['h2_frac_weakening']*100:.0f}\\% weaken; median trend rho = "
                 f"{fnum(srow['h2_median_trend_rho'])}.")
    # H3
    pl = rd(os.path.join(sd, "per_donor_plasticity.csv"))
    if pl is not None and len(pl):
        rs = pl["rho_dez_plast"].values; npos = int((rs > 0).sum()); n = len(rs)
        try:
            from scipy.stats import binomtest; p = binomtest(npos, n, 0.5).pvalue
        except Exception:
            p = np.nan
        L.append("\\paragraph{H3 (de-zonation $\\leftrightarrow$ plasticity, donor-level).} "
                 f"mean rho = {fnum(np.nanmean(rs))}; {npos}/{n} donors $>$0; sign-test p = "
                 f"{fnum(p, '{:.2g}')}.")
    # figure
    figp = os.path.join(FIG, f"collapse_{s}.png")
    if os.path.exists(figp):
        L.append("\\begin{center}\\includegraphics[width=0.92\\textwidth]"
                 f"{{figures/collapse_{s}.png}}\\end{{center}}")
    return "\n".join(L) + "\n\\clearpage\n"


def main():
    summ = pd.read_csv(SUMM)
    summ["q"] = summ.apply(quality_score, axis=1)
    summ = summ.sort_values("q", ascending=False).reset_index(drop=True)
    decision = open(os.path.join(T, "selected_set_decision.txt")).read() if os.path.exists(
        os.path.join(T, "selected_set_decision.txt")) else ""

    head = r"""\documentclass[10pt]{article}
\usepackage[margin=1in]{geometry}\usepackage{graphicx}\usepackage{parskip}
\usepackage{hyperref}\setlength{\parindent}{0pt}
\title{Spatial Degradation of Hepatocyte Zonation\\ Ruler Battery --- Per-Set Report}
\author{Auto-generated}\date{%s}
\begin{document}\maketitle
\section*{Method (read first)}
Candidate zonation rulers were built, each scored as a per-cell coordinate
(coord $=$ mean\_z(PC) $-$ mean\_z(PP), or a learned projection). \textbf{Ruler quality is judged
ONLY on Paper 2 / healthy-atlas criteria} (8-marker validation gate, healthy PC--PP
anticorrelation, split-half reproducibility). The best healthy ruler is frozen, then transferred
to the Paper 1 disease cohort, where H1/H2/H3 are TEST results --- never used for selection.
Sections below are ordered by healthy-ruler quality (split-half $+\,\max(0,-$anticorr$)$).
H1 = donor-level zonation collapse; H2 = zonal-slope loss; H3 = de-zonation/plasticity coupling.

\paragraph{Selection decision.}\begin{verbatim}
%s
\end{verbatim}
\clearpage
""" % (datetime.date.today().isoformat(), decision.strip())

    body = "".join(section(r["set_name"], r) for _, r in summ.iterrows())
    tex = head + body + "\\end{document}\n"
    texp = os.path.join(RES, "Zonation_Ruler_Report.tex")
    open(texp, "w", encoding="utf-8").write(tex)
    print("wrote", texp)
    # compile (twice for refs); pdflatex must be on PATH
    ok = True
    for _ in range(2):
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                            "Zonation_Ruler_Report.tex"], cwd=RES, capture_output=True, text=True)
        if r.returncode != 0:
            ok = False
            print("pdflatex error tail:\n", r.stdout[-1500:])
            break
    print("compiled OK ->", os.path.join(RES, "Zonation_Ruler_Report.pdf") if ok else "FAILED")


if __name__ == "__main__":
    main()
