#!/usr/bin/env python3
"""The Zonation Story — a clean, arc-driven report for the professor.

Design lessons from the previous (rejected) report:
  * ONE readable figure per full page (complex multi-panel figures are unreadable when shrunk).
  * NO auto-placed annotation circles (they were consistently offset/wrong). Tell the eye where to
    look in the CAPTION instead.
  * Tell the ARC: we moved from weak INDICATORS (coordinate spread / IQR / anti-correlation) to the
    actual in-depth BIOLOGY (pericentral programs turning OFF, gene by gene).
  * Show the FULL 47-donor panels, not just representatives.
  * Be honest: turn-off is strong and robust; DE-ZONATION is weak and partly a z-scoring artifact.
  * Include the fibrosis re-staging (D) and the learned-ruler interpretation (E).
  * NO confounder-control section (parked — see CONFOUNDERS_PLAN.md).

No LaTeX: matplotlib PdfPages. Output: results/reports/Zonation_Story.pdf
Run:  python src/reports/make_zonation_story.py
"""
from __future__ import annotations
import os, sys, textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

INK, TEAL, RUST, MUTED, RULE = "#1a1a1a", "#1b6e78", "#c05621", "#5a5a5a", "#cdd6d8"
PW, PH = 8.27, 11.69
ML, MR, MT, MB = 0.92, 0.92, 0.92, 0.85
TEXTW = PW - ML - MR


class Report:
    def __init__(self, path):
        self.pdf = PdfPages(path)
        self.page = 0

    def _newfig(self):
        fig = plt.figure(figsize=(PW, PH))
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, PW); ax.set_ylim(0, PH); ax.invert_yaxis(); ax.axis("off")
        return fig, ax

    def _wrap(self, txt, fs):
        cpl = max(10, int(TEXTW * 72.0 / (0.55 * fs)))
        out = []
        for chunk in txt.split("\n"):
            out += textwrap.wrap(chunk, cpl) if chunk.strip() else [""]
        return out

    def _footer(self, ax):
        if self.page > 1:
            ax.plot([ML, PW - MR], [PH - MB + 0.18] * 2, color=RULE, lw=0.6)
            ax.text(ML, PH - MB + 0.30, "Hepatocyte zonation in MASLD — the story",
                    fontsize=7, color=MUTED, va="top")
            ax.text(PW - MR, PH - MB + 0.30, f"p. {self.page}", fontsize=7,
                    color=MUTED, va="top", ha="right")

    def _save(self, fig, ax):
        self._footer(ax)
        self.pdf.savefig(fig, dpi=200)
        plt.close(fig)

    def text_page(self, title, blocks, big=False, subtitle=None):
        self.page += 1
        fig, ax = self._newfig()
        y = 1.9 if big else MT
        ax.text(ML, y, title, fontsize=25 if big else 16, color=TEAL, va="top",
                family="serif", fontweight="bold")
        y += (25 if big else 16) / 72.0 + 0.14
        if subtitle:
            for ln in self._wrap(subtitle, 12.5):
                ax.text(ML, y, ln, fontsize=12.5, color=INK, va="top", family="serif")
                y += 12.5 / 72.0 * 1.4
            y += 0.12
        if not big:
            ax.plot([ML, PW - MR], [y, y], color=TEAL, lw=1.3)
            y += 0.16
        for b in blocks:
            if b.startswith("## "):
                y += 0.06
                ax.text(ML, y, b[3:], fontsize=12, color=INK, va="top", family="serif",
                        fontweight="bold")
                y += 12 / 72.0 + 0.10
                continue
            for ln in self._wrap(b, 10):
                ax.text(ML, y, ln, fontsize=10, color=INK, va="top", family="serif")
                y += 10 / 72.0 * 1.46
            y += 0.13
        self._save(fig, ax)

    def figure_page(self, heading, intro, fig_path, caption, fig_h_max=8.4):
        self.page += 1
        fig, ax = self._newfig()
        y = MT
        ax.text(ML, y, heading, fontsize=15, color=TEAL, va="top", family="serif", fontweight="bold")
        y += 15 / 72.0 + 0.06
        ax.plot([ML, PW - MR], [y, y], color=TEAL, lw=1.2)
        y += 0.12
        if intro:
            for ln in self._wrap(intro, 9.8):
                ax.text(ML, y, ln, fontsize=9.8, color=INK, va="top", family="serif")
                y += 9.8 / 72.0 * 1.44
            y += 0.10
        cap_lines = self._wrap(caption, 8.6) if caption else []
        cap_h = len(cap_lines) * (8.6 / 72.0 * 1.42) + 0.10
        avail_top = y
        avail_bottom = PH - MB - cap_h - 0.10
        avail_h = max(1.0, avail_bottom - avail_top)
        if os.path.exists(fig_path):
            img = plt.imread(fig_path)
            aspect = img.shape[0] / img.shape[1]
            w = TEXTW; h = w * aspect
            if h > min(avail_h, fig_h_max):
                h = min(avail_h, fig_h_max); w = h / aspect
            left = ML + (TEXTW - w) / 2.0
            iax = fig.add_axes([left / PW, 1 - (avail_top + h) / PH, w / PW, h / PH])
            iax.imshow(img); iax.axis("off")
            y = avail_top + h + 0.12
        else:
            ax.text(ML, y, f"[missing figure: {os.path.basename(fig_path)}]", fontsize=9,
                    color=MUTED, va="top", family="serif", style="italic")
            y += 0.3
        for ln in cap_lines:
            ax.text(ML, y, ln, fontsize=8.6, color=MUTED, va="top", family="serif", style="italic")
            y += 8.6 / 72.0 * 1.42
        self._save(fig, ax)

    def close(self):
        self.pdf.close()


def build(path):
    H1 = str(config.FIG_H1); H2 = str(config.FIG_H2)
    CONF = str(config.FIG_CONF); STG = str(config.FIG_STAGING)
    r = Report(path)

    # ---------- title ----------
    r.text_page(
        "Hepatocyte Zonation\nin MASLD Progression", big=True,
        subtitle="From weak indicators to the molecular event: the pericentral program turns OFF.",
        blocks=[
            "Healthy liver is spatially zonated — pericentral and periportal hepatocytes run opposite "
            "metabolic programs. We assigned every hepatocyte a pericentral↔periportal coordinate using "
            "two independent rulers (a curated gene-set and a label-free PCA axis), then transferred "
            "them to a 47-donor MASLD cohort (~69,000 hepatocytes). Every readout uses the DONOR as the "
            "unit of inference.",
            "Methods note: the scored matrix is the SCT-corrected assay, so per-cell sequencing depth is "
            "already largely equalized (~4–5k counts). Confounder controls are parked for now "
            "(CONFOUNDERS_PLAN.md); this report is the biology.",
        ])

    # ---------- the arc ----------
    r.text_page(
        "The argument, in one page",
        ["## The question",
         "Healthy hepatocytes are zonated. Does that zonation break down in MASLD — and if so, HOW? "
         "Is it (a) the genes switching OFF (turn-off), or (b) the genes staying on but losing their "
         "spatial gradient (de-zonation)? These are different biology.",
         "## Why summary statistics did not settle it",
         "The first instinct is to summarise each donor with one number — the spread of its cells "
         "along the zonation axis, the inter-quartile range, the pericentral–periportal anti-"
         "correlation. These are INDICATORS, and they are weak: the per-donor coordinate distribution "
         "is a broad single hump whose width changes only modestly and non-monotonically with disease. "
         "You cannot read the mechanism off them.",
         "## So we went into the biology, gene by gene",
         "Instead of summarising, we looked at the actual expression — per zone, per gene, per stage "
         "and per fibrosis grade. The answer is clear and consistent across every view:",
         "   •  The PERICENTRAL program TURNS OFF — its genes are silenced, expression level drops "
         "~34–37% by end-stage / fibrosis F4. This is the dominant, robust signal.",
         "   •  The PERIPORTAL program largely HOLDS its level.",
         "   •  True DE-ZONATION (gradient flattening with expression retained) is WEAK — and the one "
         "view that seemed to show it is partly a z-scoring artifact (explained inside).",
         "   •  The apparent 'loss of zonation' (anti-correlation collapse) is mostly a DOWNSTREAM "
         "consequence of the turn-off: silence the pericentral genes and the coordinate becomes noise.",
         "   •  The effect TRACKS FIBROSIS specifically, and the label-free ruler is genuine biology.",
        ])

    # ---------- Part 1: the weak indicators ----------
    r.figure_page(
        "1.  The weak indicators",
        "Per representative patient at each stage: the distribution of cells along the zonation axis "
        "(top row) and the PC-vs-PP scatter (bottom). This is what 'coordinate spread' actually measures.",
        os.path.join(H1, "a2_zonation_distribution_by_patient_expanded_curated.png"),
        "Look at the top row: every patient's coordinate distribution is a single broad hump, and its "
        "width (SD / IQR, printed under each) changes only modestly and NON-monotonically across stages "
        "(NAFLD is actually the widest). A summary like 'spread falls with disease' is an indicator, "
        "not a result — which is why we go to the gene-level biology below.")

    # ---------- Part 2: the geometry ----------
    r.figure_page(
        "2.  The bipolar geometry dissolves",
        "PC-vs-PP scatter for the best-powered representative donor at each stage. In health the two "
        "programs trade off (anti-diagonal cloud); with disease that structure is lost.",
        os.path.join(H1, "a1_pcpp_representatives_stage.png"),
        "Healthy (donor 30, r=−0.48) and NAFLD/NASH show a tight anti-diagonal — cells are either "
        "pericentral-high/periportal-low or vice versa. By Cirrhosis (+0.26) and End-stage (+0.22) the "
        "cloud is a round/positive blob: the programs no longer trade off. (This anti-correlation "
        "collapse is largely downstream of the pericentral turn-off shown in Part 3.)")
    r.figure_page(
        "2b.  The same, for ALL 47 donors (nothing cherry-picked)",
        "Every donor's PC-vs-PP scatter, grouped into blocks by disease stage. Representatives above "
        "are not hand-picked — here is the full cohort.",
        os.path.join(H1, "a1_pcpp_contact_sheet_stage.png"),
        "Read top (Healthy) to bottom (End-stage). The anti-diagonal is clearest in the early blocks "
        "and degrades downward, but it is donor-variable — note that two of the four healthy controls "
        "are low-depth and already weak. The per-donor anti-correlation r is printed on each panel.")

    # ---------- Part 3: TURN-OFF (the headline) ----------
    r.figure_page(
        "3.  The headline: the pericentral program turns OFF",
        "Gene × zone-ordered-cells heatmap, RAW expression level, shared colour scale across stages "
        "(bright = high, dark = low). Genes ordered by their healthy zonal slope (pericentral-rising "
        "at top, periportal-rising at bottom).",
        os.path.join(H2, "b1_heatmap_level_stage.png"),
        "Look at the TOP (pericentral) rows — CYP3A4, CYP2E1, CYP1A2, GLUL: they are bright in Healthy "
        "(left) and FADE to dark by End-stage (right). The bottom (periportal) rows stay comparatively "
        "bright. This is turn-off, and it is pericentral-biased.")
    r.figure_page(
        "3b.  Program level drops — every gene set agrees",
        "Mean per-donor raw expression of the pericentral arm (left) and periportal arm (right) across "
        "stages, one line per candidate signature set (a robustness panel).",
        os.path.join(H2, "b4_set_expression_by_stage.png"),
        "Left panel: the pericentral lines all DROP at End-stage (−34 to −37%). Right panel: the "
        "periportal lines stay flat. The loss is asymmetric and set-independent.")
    r.figure_page(
        "3c.  …and it happens IN the pericentral zone",
        "Cells split into three zones (pericentral / mid / periportal by coordinate terciles); boxplots "
        "across donors of each program's level in each zone, per stage.",
        os.path.join(H2, "b2_zone_program_boxplots_stage.png"),
        "Teal = pericentral program. In Healthy it is high in the pericentral zone (~1.25) and low in "
        "the periportal zone. Follow the pericentral-zone teal box across stages: it collapses to ~0.74 "
        "by End-stage. The periportal program (rust) holds its level. (Boxes widen at End-stage = real "
        "donor heterogeneity + small n, not measurement noise.)")
    r.figure_page(
        "3d.  Gene by gene: turn-off, not de-zonation",
        "For each signature gene, the change in expression LEVEL (x) vs the change in zonal SLOPE "
        "magnitude (y), Healthy→End-stage. Bottom-left quadrant = lost both = turn-off.",
        os.path.join(CONF, "c3_level_vs_slope.png"),
        "Pericentral genes (teal) cluster in the turn-off quadrant: 14/26 lose BOTH level and gradient "
        "(e.g. CYP2E1 dLevel −1.21, ADH4 −0.93). Periportal genes (rust): 22/23 hold their level. The "
        "mechanism is turn-off, gene by gene — not a spurious level drop misread as de-zonation.")
    r.figure_page(
        "3e.  The marker genes confirm it",
        "Mean raw expression of canonical markers vs the zonation coordinate, one line per stage.",
        os.path.join(H1, "a3_marker_profiles_stage.png"),
        "Pericentral markers (CYP1A2, CYP2E1, SLCO1B3, GLUL) keep their gradient through mid-disease "
        "then collapse in level at End-stage (turn-off). Periportal markers (ASS1, ALDOB, ARG1) hold "
        "their level and mostly flatten only mildly.")

    # ---------- Part 4: de-zonation is WEAK ----------
    r.figure_page(
        "4.  Is there de-zonation? Honestly, weakly — and here is the trap",
        "Same heatmap, but each gene z-scored WITHIN its own stage panel (the 'pattern' view, intended "
        "to show the gradient independent of level).",
        os.path.join(H2, "b1_heatmap_pattern_stage.png"),
        "The diagonal banding largely PERSISTS through Cirrhosis — so the spatial pattern does not "
        "obviously collapse. CRITICAL CAVEAT: in the End-stage panel the top (pericentral) rows show "
        "speckled purple/orange. That is NOT a gradient — those genes have turned OFF, so z-scoring "
        "their near-zero signal WITHIN the panel amplifies pure noise into fake colour. Read silenced "
        "genes from the LEVEL view (Part 3), not here. Net: we do not have strong evidence for de-"
        "zonation; the robust event is turn-off.")
    r.figure_page(
        "4b.  Program gradients flatten only modestly",
        "Pericentral (left) and periportal (right) program expression vs the zonation coordinate, one "
        "line per stage; the per-stage slope is the steepness of zonation.",
        os.path.join(H2, "b3_program_vs_coord_stage.png"),
        "The pericentral slope flattens only modestly (≈ +0.126 → +0.102); the periportal slope barely "
        "changes. What moves decisively is the LEVEL (the pericentral curve drops). So de-zonation "
        "(pure gradient loss) is the weaker, secondary effect — turn-off dominates.")

    # ---------- Part 5: fibrosis re-staging (D) ----------
    r.figure_page(
        "5.  Re-staged by FIBROSIS (not just the coarse 5 stages)",
        "The cohort re-binned by fibrosis grade F0→F4 (available in the metadata). Zonation strength, "
        "pericentral program level, and coordinate spread vs fibrosis; per-donor points + per-grade "
        "median + Spearman trend.",
        os.path.join(STG, "d_zonation_vs_fibrosis.png"),
        "All three decline with fibrosis (strength ρ=−0.49, p=4.4e−4; pericentral level ρ=−0.45). The "
        "graded fibrosis axis is a stronger biological readout than the coarse stages. (Low-n grades "
        "are faded / flagged on the figure — F0 has 5 donors.)")
    r.figure_page(
        "5b.  …and it is FIBROSIS-specific, not generic activity",
        "Zonation strength vs fibrosis (left) and vs NAS activity score (right), with partial "
        "correlations.",
        os.path.join(STG, "d_fibrosis_vs_nas.png"),
        "Strength tracks fibrosis (ρ=−0.49) far better than NAS (ρ=−0.25, n.s.). Partial correlations "
        "settle it: controlling for NAS, the fibrosis association holds (−0.40); controlling for "
        "fibrosis, the NAS association collapses (−0.12). The signal is tied to FIBROSIS.")

    # ---------- Part 6: the ruler is real biology (E) ----------
    r.figure_page(
        "6.  The label-free ruler is genuine biology",
        "We also built the zonation axis with NO marker genes — PCA on healthy hepatocytes. Cells in "
        "PC1–PC2 space, coloured by the curated coordinate (a) and by sequencing depth (b).",
        os.path.join(STG, "e_pca_pc12_map.png"),
        "PC1 IS zonation: the curated coordinate runs cleanly along it (|corr|=0.76; |corr|=0.54 with "
        "the canonical marker axis; 5.8% of variance, ~2× the next PC). Sequencing depth (panel b) is "
        "diffuse and loads on PC2 — NOT on the zonation axis. So the learned ruler is biology, not a "
        "technical artifact.")
    r.figure_page(
        "6b.  The learned axis's top genes are real zonation genes",
        "Top positive- and negative-loading genes on the zonation principal component.",
        os.path.join(STG, "e_pca_loadings.png"),
        "The periportal pole is dominated by acute-phase/periportal genes (CRP, SAA1, SAA2, fibrinogen-"
        "like FGL1); the pericentral pole carries bile-acid/pericentral enzymes (ADH4, AKR1D1). These "
        "are textbook zonation markers the PCA found on its own.")

    # ---------- caveats ----------
    r.text_page(
        "Honest caveats",
        ["## What is strong",
         "Pericentral turn-off is the dominant, robust signal — seen consistently in the level heatmap, "
         "the per-set program levels, the zone boxplots, the gene-by-gene level/slope map, and the "
         "marker profiles. It tracks fibrosis specifically.",
         "## What is weak / unresolved",
         "• DE-ZONATION (gradient flattening with expression retained) is NOT convincingly demonstrated. "
         "The program slopes flatten only modestly, and the heatmap 'pattern' view's apparent end-stage "
         "signal in pericentral rows is largely z-scoring noise from silenced genes.",
         "• Only 4 healthy-control donors, two of them low-depth and weakly zonated — the healthy "
         "baseline is thin.",
         "• The scored matrix is SCT-corrected (depth pre-equalized), so this is not built on raw-depth-"
         "confounded data; a true raw-depth check would need the RNA assay.",
         "• Confounder controls are intentionally PARKED (they had been validating the secondary "
         "indicators, not the turn-off) — see CONFOUNDERS_PLAN.md for the recentered plan and stronger "
         "checks (negative-control genes, purity, covariate regression).",
         "• This is a cross-sectional human cohort: we establish a robust ASSOCIATION between disease/"
         "fibrosis and pericentral turn-off, not proof that disease causes it.",
        ])

    r.close()
    return path


if __name__ == "__main__":
    out = os.path.join(str(config.REPORTS), "Zonation_Story.pdf")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    build(out)
    print("wrote", out)
