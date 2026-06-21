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

T = str(config.TABLES); FIG = str(config.FIGURES); RES = str(config.RESULTS)


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
            ("recommended_role", "role")]
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
    prog = rd("paper2_full/h2_program_summary.csv")
    axiseval = rd("unsupervised_axis_eval.csv")
    tw = rd("expanded_curated/h2_transcriptome_wide_summary.csv")
    tw_n = tw_frac = tw_sig = "n/a"
    if tw is not None and len(tw):
        r = tw.iloc[0]; tw_n = str(int(r["n_tested"])); tw_frac = f"{r['frac_weakening']*100:.0f}"
        tw_sig = str(int(r["n_q05_weakening"]))

    lm_s, lm_p = h1("paper2_landmark"); un_s, un_p = h1("unsupervised")
    ex_s, ex_p = h1("expanded_curated"); fl_s, fl_p = h1("paper2_full")

    prog_tex = ""
    if prog is not None:
        prog = prog.sort_values("median_trend_rho")
        prog_tex = "\\begin{tabular}{l r r}\n\\hline\nprogram & median slope-trend $\\rho$ & \\% weaken \\\\\n\\hline\n"
        for _, r in prog.iterrows():
            prog_tex += f"{str(r['program']).replace('_', chr(92)+'_')} & {r['median_trend_rho']:+.2f} & {r['frac_weakening']*100:.0f}\\% \\\\\n"
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
using the test cohort to choose the instrument would be leakage. The frozen primary is the
top-ranked \emph{published-signature} set; learned rulers are shown for comparison but do not compete
in the auto-selection. We keep the whole spectrum (curated, data-ranked, learned PCA, regularized,
supervised) because agreement of \emph{independent construction mechanisms} is the robustness
evidence --- not because any one is cherry-picked.

%(summary_table)s

\subsection{Which ruler we selected, and why it is not the strongest-on-disease one}
By healthy-ruler quality the selected primary set is %(selected)s. Notably this is \emph{not} the
set with the strongest disease trend (the small curated %(core_name)s set has a steeper collapse) ---
choosing that would be cherry-picking. Selection used healthy metrics only; the disease result is
the independent confirmation.

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
\textbf{H2a (global):} most zonated genes lose their donor-level zonal slope with disease
(held-out split; e.g.\ 96/100 genes weaken for the unsupervised ruler). \textbf{H2b (differential
vulnerability):} grouping genes into programs reveals a clear order --- pericentral Wnt/identity
genes de-zonate first, then nitrogen/urea and xenobiotic metabolism, whereas acute-phase/secreted
and bile-acid programs are spared or even strengthen:

%(prog_table)s

Biologically this is coherent: loss of the pericentral Wnt identity is the earliest and strongest
de-zonation, while acute-phase genes change with disease \emph{globally} (not zonally), so their
zonal slope does not collapse. Note H2 (loss of spatial restriction) is distinct from classic DE
(change in level); the cross-table \texttt{h2\_slopeloss\_vs\_DE.csv} reports both per gene.

\paragraph{H2c --- transcriptome-wide (every gene, donor-level).} Taking H2 forward: assign every
cell the frozen ruler coordinate and test \emph{all} %(tw_n)s genes' donor-level zonal slope.
%(tw_frac)s\,\% weaken directionally, but only %(tw_sig)s survive BH-FDR at $q<0.05$ (all non-ruler
genes). So the collapse is \emph{broad and diffuse} --- most genes lose a little zonation rather than
a few master genes losing a lot --- which is why the powered read-outs are the program-level (H2b)
and held-out ruler-gene tests, not per-gene FDR at $n=47$ donors.

\subsection{H3 --- de-zonation couples weakly to plasticity}
Within donors, de-zonation correlates positively with plasticity-marker expression
(KRT7/KRT19/SOX9/SOX4/KRT23/NCAM1) in $\sim$70\% of donors (landmark sign-test $p=0.008$), but the
effect is small (mean $\rho\approx0.02$). This is the weakest of the three hypotheses: directionally
consistent with Paper~1's transdifferentiation theme, but not a strong donor-level effect here.

\begin{center}\includegraphics[width=\textwidth]{figures/ruler_panel.png}\end{center}

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
        "selected": tt(_selected()), "core_name": tt("core_curated"),
        "lm_name": tt("paper2_landmark"), "ex_name": tt("expanded_curated"),
        "top250": tt("paper2_top250"), "full": tt("paper2_full"),
        "lm_s": lm_s, "lm_p": lm_p, "ex_s": ex_s, "ex_p": ex_p,
        "un_s": un_s, "un_p": un_p, "fl_s": fl_s,
        "agree": agree or "the unsupervised and signature rulers agree",
        "prog_table": prog_tex, "tw_n": tw_n, "tw_frac": tw_frac, "tw_sig": tw_sig,
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


def _selected():
    p = os.path.join(T, "selected_set_decision.txt")
    if os.path.exists(p):
        for line in open(p):
            if line.startswith("SELECTED set:"):
                return line.split(":", 1)[1].strip()
    return "expanded_curated"


if __name__ == "__main__":
    main()
