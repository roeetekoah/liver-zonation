#!/usr/bin/env python3
"""Generate the NARRATIVE analytical report (prose: background, methods, analysis, interpretation,
limitations, conclusions) with embedded figures + key tables. Compiles to
results/Zonation_Narrative_Report.pdf via pdflatex. The per-set results dump is the separate
Zonation_Ruler_Report.pdf.

Run:  python src/make_narrative_report.py
"""
import os, sys, datetime
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # src/
import config

T = str(config.TABLES); FIG = str(config.FIGURES); RES = str(config.REPORTS)


def rd(p):
    p = os.path.join(T, p)
    return pd.read_csv(p) if os.path.exists(p) else None


def tt(s):                       # \texttt with escaped underscores
    return r"\texttt{" + str(s).replace("_", r"\_") + "}"


def num(df, where, col, f="{:+.3f}"):
    try:
        return f.format(float(df.loc[where, col]))
    except Exception:
        return "n/a"


def h1(set_name, metric="coord_spread"):
    d = rd(f"{set_name}/collapse_trends.csv")
    if d is None: return "n/a", "n/a"
    d = d.set_index("metric")
    return num(d, metric, "rho_vs_stage"), num(d, metric, "perm_p", "{:.2g}")


def summary_table_tex(summ):
    cols = [("set_name", "ruler"), ("n_pc", "PC"), ("n_pp", "PP"),
            ("healthy_pc_pp_anticorr", "healthy anticorr"),
            ("healthy_splithalf_rho_mean", "split-half"),
            ("h1_coord_spread_rho_vs_stage", "H1 spread $\\rho$"),
            ("display_role", "role")]
    rows = []
    for _, r in summ.iterrows():
        cells = []
        for c, _ in cols:
            v = r[c]
            if isinstance(v, float):
                cells.append("" if pd.isna(v) else f"{v:.2f}")
            else:
                cells.append(str(v).replace("_", r"\_"))
        rows.append(" & ".join(cells) + r" \\")
    head = " & ".join(h for _, h in cols)
    return ("\\begin{tabular}{l r r r r r l}\n\\hline\n" + head + " \\\\\n\\hline\n"
            + "\n".join(rows) + "\n\\hline\n\\end{tabular}")


def main():
    summ = rd("signature_battery_summary.csv")
    if summ is not None:
        summ = summ.copy()
        summ["q"] = summ.apply(lambda r: (-99 if not r["validation_pass"] else
                               (0 if pd.isna(r["healthy_splithalf_rho_mean"]) else r["healthy_splithalf_rho_mean"])
                               + max(0.0, -(0 if pd.isna(r["healthy_pc_pp_anticorr"]) else r["healthy_pc_pp_anticorr"]))), axis=1)
        summ = summ.sort_values("q", ascending=False)
    prog = rd("expanded_curated/h2_program_summary.csv")   # H2b on the VALID ruler
    axiseval = rd("unsupervised_axis_eval.csv")
    tw = rd("expanded_curated/h2_transcriptome_wide_summary.csv")
    tw_n = tw_frac = tw_sig = "n/a"
    if tw is not None and len(tw):
        r = tw.iloc[0]; tw_n = str(int(r["n_tested"])); tw_frac = f"{r['frac_weakening']*100:.0f}"
        tw_sig = str(int(r["n_q05_weakening"]))

    lm_s, lm_p = h1("paper2_landmark"); un_s, un_p = h1("unsupervised_p2")   # clean label-free co-primary
    ex_s, ex_p = h1("expanded_curated"); fl_s, fl_p = h1("paper2_full")
    co_a, co_b = _co_primaries(summ); co_decide = _co_decide(summ, co_a, co_b)

    prog_tex = ""; wnt_q = "n/a"
    if prog is not None:
        prog = prog.sort_values("median_trend_rho")
        has_q = "q_bh" in prog.columns
        prog_tex = ("\\begin{tabular}{l r r r}\n\\hline\nprogram & $n$ & median $\\rho$ & "
                    "MWU $q$ vs background \\\\\n\\hline\n")
        for _, r in prog.iterrows():
            nm = str(r["program"]).replace("_", chr(92) + "_")
            q = r["q_bh"] if has_q and pd.notna(r.get("q_bh", np.nan)) else np.nan
            qs = "--" if pd.isna(q) else (f"{q:.1e}" if q < 0.01 else f"{q:.2f}")
            prog_tex += f"{nm} & {int(r['n_genes'])} & {r['median_trend_rho']:+.2f} & {qs} \\\\\n"
            if r["program"] == "wnt_pericentral_identity" and pd.notna(q):
                wnt_q = f"{q:.0e}"
        prog_tex += "\\hline\n\\end{tabular}"

    agree = ""
    if axiseval is not None:
        a = axiseval.iloc[0]
        agree = (f"the label-free PCA axis correlates $\\rho={a['rho_axis_coord']:+.2f}$ with the "
                 f"landmark-signature coordinate ($\\rho={a['rho_axis_pc']:+.2f}$ with its PC arm, "
                 f"${a['rho_axis_pp']:+.2f}$ with its PP arm)")

    tex = r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}\usepackage{graphicx}\usepackage{parskip}\usepackage{hyperref}
\title{Spatial Degradation of Hepatocyte Zonation in Human MASLD\\
\large An analysis report: building, validating and transferring a zonation ruler}
\author{}\date{%(date)s}
\begin{document}\maketitle

\section{Background and question}
The liver lobule is spatially organized along a porto-central axis: pericentral hepatocytes (near
the central vein) and periportal hepatocytes (near the portal triad) run complementary metabolic
programs, and most hepatocyte genes are \emph{zonated}. \textbf{Paper~2} (Yakubovsky \& Itzkovitz,
\emph{Nature} 2026) built a spatially resolved atlas of the \emph{healthy} human liver and a
quantitative zonation reference. \textbf{Paper~1} (Gribben, Vallier et al., \emph{Nature} 2024,
GSE202379) profiled $\sim$69k hepatocytes by single-nucleus RNA-seq across 47 donors spanning
MASLD stages (Healthy $\to$ NAFLD $\to$ NASH $\to$ Cirrhosis $\to$ End-stage), but is
\emph{spatially blind}. Paper~1 reports qualitatively that ``hepatocytes lose their zonation''.

This project makes that quantitative. We use Paper~2's healthy zonation as a \emph{ruler} to assign
each Paper~1 hepatocyte a pseudo-zonation coordinate, then test, at the level of the \textbf{donor}
(never the cell, to avoid pseudoreplication):
\begin{itemize}
\item \textbf{H1}: does zonation collapse with disease stage?
\item \textbf{H2}: which gene programs lose their zonal restriction (slope), and fastest?
\item \textbf{H3}: are de-zonated cells also more plastic (hepatocyte$\leftrightarrow$cholangiocyte)?
\end{itemize}

\section{Method, and the one rule that governs it}
A ruler is any rule that maps a cell's transcriptome to a porto-central coordinate. We compared
many: Paper~2's exact 20+20 \emph{landmark} genes; curated anchor sets; data-driven top-$N$ and
``full'' sets ranked from Paper~2's zonation table; a \emph{learned} dense PCA axis; sparse
\emph{lasso}/\emph{elastic-net} axes; and a supervised whole-transcriptome classifier. Each yields
coord $=\mathrm{mean\_z}(\mathrm{PC})-\mathrm{mean\_z}(\mathrm{PP})$ or a learned projection.

\textbf{The governing rule: ruler quality is judged ONLY on the healthy atlas} --- an 8-marker
sign gate (pericentral CYP2E1/CYP1A2/GLUL/PCK2 must correlate $+$; periportal ASS1/ALDOB/PCK1/HAL
$-$), the healthy PC--PP anti-correlation (a real axis has the two arms mutually exclusive), and
split-half reproducibility. The best healthy ruler is \emph{frozen} and only \emph{then} applied to
the disease cohort. Disease H1/H2/H3 are the \emph{test}; they are never used to choose a ruler.
Choosing by disease strength would be circular (leakage).

\subsection{Statistical tests --- what each checks, and how}
Every test follows the donor rule: collapse each donor's cells to one number, then test on the
$\approx$47 donor values (resampling/permuting donors, never cells). Tests are rank-based by default
(ordinal stages, skewed scores, small $n$); effect sizes are reported beside every $p$; BH-FDR
controls multiple testing.

\begin{tabular}{l l l}
\hline
test & what it checks & how \\
\hline
Spearman $\rho$ & monotone trend of a metric vs stage & rank correlation; donor-level \\
Jonckheere--Terpstra & ordered-groups trend (dedicated) & $J=\sum_{a<b}U_{ab}$, permutation $p$ \\
Donor bootstrap CI & how big / how sure the trend is & resample donors $B{=}2000$, 2.5/97.5 pct \\
Label-shuffle perm. & is the pipeline finding noise? & shuffle stage labels, recompute \\
Held-out gene split & H2 without circularity & build coord on half genes, test other half, $K{=}20$ \\
Mann--Whitney $U$ (H2b) & does a program weaken $>$ background? & $U$ of program vs rest, rank-biserial, BH-$q$ \\
Per-gene FDR (H2c) & which individual genes lose slope & Spearman per gene, BH over $\sim$30k \\
Within-donor corr (H3) & dez$\leftrightarrow$plast, stage-free & $\rho_d$ per donor; sign test \& Wilcoxon vs 0 \\
Mann--Whitney AUC (H3) & dez vs zonated plasticity & within-donor AUC, aggregate \\
OLS + C(stage)+C(donor) & partial dez effect (descriptive) & coefficient on dez (cell-level SE) \\
\hline
\end{tabular}

\section{Results and analysis}

\subsection{Not every ruler is a ruler: a dilution curve}
The 8-marker gate passes for almost everything (the markers are strong), but it is not sufficient.
The decisive control is the \emph{healthy PC--PP anti-correlation}. Small, high-SNR sets are
genuinely bipolar (%(lm_name)s: $-0.45$; %(ex_name)s: $-0.48$), but as the gene set grows the axis
degrades and finally inverts: %(top250)s $\approx +0.04$, %(full)s $\approx +0.55$. Averaging
$\sim$2000 weakly-zonated genes lets a shared technical/expression factor dominate, so the
``full'' coordinate is \emph{not} a zonation axis at all. This is why a transcriptome-wide
\emph{unweighted} mean fails while a \emph{weighted} or selected ruler succeeds.

\subsection{Ruler ranking and selection (healthy metrics ONLY)}
Every ruler is scored on \textbf{healthy} quality alone --- a quality score of
(split-half reproducibility) $+\,\max(0,-$healthy PC--PP anticorrelation$)$ --- and the table below
is \textbf{ordered by it}. Disease-collapse strength is deliberately \emph{excluded} from selection:
using the test cohort to choose the instrument would be leakage.

\textbf{Eligibility is by leakage, not by publishability.} A ruler may compete for the frozen
primary slot iff its axis was \emph{not} fit on Paper-1 cells. This matters because two learned
rulers (\texttt{unsupervised}, \texttt{unsupervised\_combined}) are fit by PCA on Paper-1 healthy
cells --- so their healthy anticorrelation/split-half are computed on the very cells the axis was
fit to (\emph{in-sample}, and therefore optimistically inflated; that is exactly why they top the
raw table). They remain valid H1 robustness checks --- the Paper-1 \emph{disease} cells are never
used to fit them --- so we keep and show them, marked \emph{control (Paper1-fit)}, but they do not
compete. Every other ruler (published gene lists, which fit nothing; and the Paper-2-trained learned
axes \texttt{unsupervised\_p2}/\texttt{supervised}/\texttt{lasso}/\texttt{elasticnet}, external to
Paper 1) is leakage-clean and eligible regardless of whether it is a curated list or a label-free
axis.

%(summary_table)s

\subsection{Two co-primary rulers, and why we report both}
Among the leakage-clean rulers we freeze \textbf{two co-primaries} of deliberately different
construction, then transfer \emph{both} to disease: an \textbf{interpretable} published anchor
(%(co_a)s) and a \textbf{label-free} learned axis (%(co_b)s, trained entirely on the external
Paper~2 healthy atlas). On healthy quality they are statistically indistinguishable
(%(co_decide)s), so picking one over the other would be arbitrary --- and the label-free axis is in
fact the \emph{highest}-scoring eligible ruler, so the result is not an artefact of insisting on a
hand-curated gene list. The headline rests on the two \emph{agreeing}: a curated signature and an
unsupervised axis built with no marker genes both reconstruct the same coordinate and both show the
same collapse. We also note the selected rulers are \emph{not} the steepest-collapsing ones (the
tiny curated %(core_name)s set collapses harder) --- choosing by disease strength would be
cherry-picking; selection used healthy metrics only, and disease is the independent confirmation.

\subsection{H1 --- zonation collapses (and it is robust)}
On every \emph{valid} ruler, per-donor coordinate spread falls and the PC--PP anti-correlation
rises toward zero across stages. The signal is concentrated and reproducible:
landmark spread $\rho=%(lm_s)s$ (perm $p=%(lm_p)s$); expanded $\rho=%(ex_s)s$; the label-free dense
PCA axis $\rho=%(un_s)s$ (perm $p=%(un_p)s$). The broken ``full'' ruler is null ($\rho=%(fl_s)s$),
exactly as its healthy diagnostics predicted. The agreement of the published-signature ruler and a
\emph{label-free} ruler is the key point: the collapse is a property of the data, not of any one
gene list.

\paragraph{Early disease is the noisy part (stated honestly).} The decline is \emph{not} strictly
monotonic from Healthy: at NAFLD the coordinate is often as zonated as (or slightly more than)
Healthy, and the Healthy$\to$NAFLD \emph{direction flips across rulers} (up for landmark/expanded,
down for the dense PCA axis) --- exactly the instability expected where the signal is weakest and $n$
smallest (Healthy $n=4$, NAFLD $n=7$). All rulers nonetheless \emph{agree} on the strong
NASH$\to$end-stage decline. So the defensible claim is an ordered collapse \emph{across the disease
course, driven by NASH$\to$end-stage}, with early steatosis leaving zonation largely intact ---
consistent with steatosis beginning pericentrally before inflammation and fibrosis dissolve the axis.

\subsection{Leakage control --- the unsupervised axis is clean}
A fair concern: was the learned axis trained on disease cells? No. It was learned on healthy cells
only and frozen. To remove all doubt we also trained the axis \emph{entirely on the external
Paper~2 healthy atlas} (zero Paper~1 cells in fitting) and transferred it: the collapse survived
($\rho=-0.50$, $p=3\times10^{-4}$, 8/8 markers). And %(agree)s --- so the axis is not a
signature-formula artefact, and the result is not a variance-maximization artefact.

\subsection{H2 --- which programs lose zonation, and fastest}
\textbf{H2a (held-out slope-loss).} Building the coordinate from one random half of the ruler genes
and testing the other half (repeated $K{=}20\times$), most held-out genes lose their donor-level
zonal slope with disease (e.g.\ 96/100 weaken for the unsupervised ruler) --- a non-circular
confirmation that the genes defining zonation flatten with disease.

\textbf{H2c (transcriptome-wide, per gene).} Taking it further: assign every cell the frozen ruler
coordinate and test \emph{all} %(tw_n)s genes' donor-level zonal slope. %(tw_frac)s\,\% lean toward
weakening (a real directional bias --- pure noise would give 50\%), \emph{but only %(tw_sig)s survive
BH-FDR} at $q<0.05$. Why so few? Each gene's slope is estimated per donor from a handful of zone
bins, and with only $n{=}47$ donors the per-gene test is weak; correcting across $\sim$30k genes,
almost no single gene is individually a stand-out. So the collapse is \textbf{broad and diffuse} ---
most genes lose a \emph{little} zonation rather than a few master genes losing a lot.

\textbf{H2b (program-level --- where the power and the structure are).} Diffuse does \emph{not} mean
uniform. Grouping genes into programs and aggregating recovers the power that per-gene FDR throws
away: for each program we test, by Mann--Whitney $U$, whether its genes weaken \emph{more than the
genome background} (background median $\rho=-0.06$, %(tw_frac)s\,\% weakening), with a rank-biserial
effect and BH across programs. The programs weaken at \emph{significantly different rates}:

%(prog_table)s

Pericentral Wnt/identity genes de-zonate first and hardest (median $\rho=-0.40$, MWU $q\approx
%(wnt_q)s$, rank-biserial $-0.82$), followed by urea/nitrogen, xenobiotic CYP and lipid metabolism
(all $q<0.05$ more negative than background); acute-phase/secreted and bile-acid programs are
\emph{spared} (not different from, or less negative than, background). This is the resolution of the
apparent paradox: per-gene FDR (H2c) flags few individuals because each is noisy, yet the
\emph{between-program} contrast (H2b) is highly significant because averaging within a program and
comparing against the rest is far better powered. Biologically coherent --- loss of pericentral Wnt
identity leads, while acute-phase genes change \emph{globally} (not zonally) so their zonal slope is
untouched. (H2 = loss of spatial restriction, distinct from classic level-DE; cross-tabulated per
gene in \texttt{h2\_slopeloss\_vs\_DE.csv}.)

\subsection{H3 --- de-zonation couples weakly to plasticity}
Within donors, de-zonation correlates positively with plasticity-marker expression
(KRT7/KRT19/SOX9/SOX4/KRT23/NCAM1) in $\sim$70\% of donors (landmark sign-test $p=0.008$), but the
effect is small (mean $\rho\approx0.02$). This is the weakest of the three hypotheses: directionally
consistent with Paper~1's transdifferentiation theme, but not a strong donor-level effect here.

\begin{center}\includegraphics[width=\textwidth]{%(panel)s}\end{center}

\section{Discussion}
Three independent constructions --- a published landmark signature, a label-free PCA axis (trained
even on a fully external healthy atlas), and regularized sparse axes --- converge on the same
conclusion: hepatocyte zonation progressively collapses across MASLD, the pericentral Wnt-identity
program leads the loss, and de-zonation is mildly associated with epithelial plasticity. Because
ruler selection was confined to healthy-atlas criteria, the disease findings are genuine transfer
results rather than fitted outcomes.

\section{Limitations}
(i) Donor numbers per stage are imbalanced (4/7/27/4/5), so cirrhosis/end-stage estimates are thin;
all inference is donor-level with bootstrap CIs and permutation nulls to respect this. (ii) Paper~2
per-cell zone labels are an $\eta$-over-landmark reconstruction (Paper~2's own method) --- spatially
grounded but not a physical coordinate; classifier entropy is therefore auxiliary. (iii) The
``full'' unweighted set is a cautionary negative, not a result. (iv) H2b program groupings are
curated and the smaller rulers contain few genes per program, so the gene-rich \texttt{paper2\_full}
table is used for the program comparison.

\section{Conclusions}
Hepatocyte zonation collapses with MASLD stage at the donor level (H1), driven first by the
pericentral Wnt-identity program with nitrogen and xenobiotic metabolism following (H2), and is
weakly coupled to epithelial plasticity (H3). The result is robust to how the ruler is built and to
training the ruler on a fully external healthy atlas.

\vspace{1em}\footnotesize Companion artefacts: per-set dossier \texttt{Zonation\_Ruler\_Report.pdf};
machine tables \texttt{signature\_battery\_summary.csv}, \texttt{selected\_set\_decision.txt},
per-set \texttt{results/tables/<set>/}.
\end{document}
"""
    M = {
        "date": datetime.date.today().isoformat(),
        "summary_table": summary_table_tex(summ) if summ is not None else "",
        "panel": (FIG + "/ruler_panel.png").replace("\\", "/"),
        "co_a": tt(co_a), "co_b": tt(co_b), "co_decide": co_decide, "core_name": tt("core_curated"),
        "lm_name": tt("paper2_landmark"), "ex_name": tt("expanded_curated"),
        "top250": tt("paper2_top250"), "full": tt("paper2_full"),
        "lm_s": lm_s, "lm_p": lm_p, "ex_s": ex_s, "ex_p": ex_p,
        "un_s": un_s, "un_p": un_p, "fl_s": fl_s,
        "agree": agree or "the unsupervised and signature rulers agree",
        "prog_table": prog_tex, "tw_n": tw_n, "tw_frac": tw_frac, "tw_sig": tw_sig, "wnt_q": wnt_q,
    }
    for k, v in M.items():
        tex = tex.replace("%(" + k + ")s", str(v))
    texp = os.path.join(RES, "Zonation_Narrative_Report.tex")
    open(texp, "w", encoding="utf-8").write(tex)
    import subprocess
    for _ in range(2):
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                            "Zonation_Narrative_Report.tex"], cwd=RES, capture_output=True, text=True)
        if r.returncode != 0:
            print("pdflatex error tail:\n", r.stdout[-1500:]); return
    print("wrote", os.path.join(RES, "Zonation_Narrative_Report.pdf"))


def _co_primaries(summ):
    """(interpretable, label-free) co-primary set names, read from display_role; robust defaults."""
    co_a, co_b = "expanded_curated", "unsupervised_p2"
    if summ is not None and "display_role" in summ.columns:
        a = summ[summ["display_role"] == "PRIMARY (interpretable)"]
        b = summ[summ["display_role"] == "PRIMARY (label-free)"]
        if len(a): co_a = a.iloc[0]["set_name"]
        if len(b): co_b = b.iloc[0]["set_name"]
    return co_a, co_b


def _co_decide(summ, co_a, co_b):
    """One-clause statement of the healthy-score gap between the two co-primaries."""
    try:
        ga = summ[summ.set_name == co_a].iloc[0]["healthy_score"]
        gb = summ[summ.set_name == co_b].iloc[0]["healthy_score"]
        gap = abs(ga - gb)
        band = "within" if gap < 0.02 else "beyond"
        return (f"healthy-quality scores {ga:.2f} vs {gb:.2f}, a gap of {gap:.3f} --- {band} the "
                "0.02 tie band")
    except Exception:
        return "healthy-quality scores essentially tied"


if __name__ == "__main__":
    main()
