#!/usr/bin/env python3
"""Generate the "Biology Findings" PDF for the liver-zonation MASLD study.

This report is written for a reviewer who insisted on REAL BIOLOGY (not summary statistics),
on controlled confounders, and — crucially — that EVERY claim citing a figure must SHOW that
figure with the key region CIRCLED/ARROWED so the eye lands exactly where it should.

No LaTeX is used: the document is rendered with matplotlib's PdfPages via a small top-to-bottom
flow-layout engine (mirrors src/reports/make_methods_explainer.py), so it builds anywhere
matplotlib is installed.  Real result figures are embedded with plt.imread + ax.imshow and then
annotated in axes-fraction coordinates with a red Ellipse + FancyArrowPatch + short label.

Output: results/reports/Zonation_Biology_Findings.pdf

Run:  python src/reports/make_biology_findings.py
"""
from __future__ import annotations
import os, sys, textwrap
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Ellipse
from matplotlib.backends.backend_pdf import PdfPages
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# ---- palette ----
INK     = "#1a1a1a"
TEAL    = "#1b6e78"      # headings / pericentral
RUST    = "#c05621"      # accents / periportal
MUTED   = "#5a5a5a"
RULE    = "#cdd6d8"
BOXBG   = "#f3f7f8"
BOXEDGE = "#bcd0d3"
CAUTBG  = "#fdf4ec"
CAUTEDGE = "#e7c4a3"
RED     = "#d11e1e"      # annotation colour (must read clearly on any figure)

# ---- page geometry (A4 portrait), all in inches, origin top-left ----
PW, PH = 8.27, 11.69
ML, MR, MT, MB = 0.92, 0.92, 0.92, 0.85
TEXTW = PW - ML - MR


class Doc:
    """Minimal top-to-bottom flow layout over matplotlib pages. Cursor self.y is inches-from-top."""
    def __init__(self, path, title_running="", png_dir=None):
        self.pdf = PdfPages(path)
        self.title_running = title_running
        self.png_dir = png_dir
        if png_dir:
            os.makedirs(png_dir, exist_ok=True)
        self.fig = None
        self.page = 0
        self._new_page(first=True)

    # -- page lifecycle --
    def _flush(self):
        self._chrome()
        self.pdf.savefig(self.fig, dpi=200)
        if self.png_dir:
            self.fig.savefig(os.path.join(self.png_dir, f"page_{self.page:02d}.png"), dpi=200)
        plt.close(self.fig)

    def _new_page(self, first=False):
        if self.fig is not None:
            self._flush()
        self.page += 1
        self.fig = plt.figure(figsize=(PW, PH))
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, PW); self.ax.set_ylim(0, PH)
        self.ax.invert_yaxis(); self.ax.axis("off")
        self.y = MT

    def _chrome(self):
        if self.page == 1:
            return
        self.ax.plot([ML, PW - MR], [PH - MB + 0.18] * 2, color=RULE, lw=0.6)
        self.ax.text(ML, PH - MB + 0.30, self.title_running, fontsize=7.0, color=MUTED, va="top")
        self.ax.text(PW - MR, PH - MB + 0.30, f"p. {self.page}", fontsize=7.0,
                     color=MUTED, va="top", ha="right")

    def _room(self, need):
        if self.y + need > PH - MB:
            self._new_page()

    # -- primitives --
    def space(self, dy=0.10):
        self.y += dy

    def _wrap(self, txt, fs):
        cpl = max(10, int(TEXTW * 72.0 / (0.57 * fs)))
        return textwrap.wrap(txt, cpl) or [""]

    def para(self, txt, fs=9.3, color=INK, gap=0.07, indent=0.0, lh=None):
        lh = lh or fs / 72.0 * 1.42
        lines = []
        for chunk in txt.split("\n"):
            lines += self._wrap(chunk, fs) if chunk.strip() else [""]
        self._room(lh)
        for ln in lines:
            self._room(lh)
            self.ax.text(ML + indent, self.y, ln, fontsize=fs, color=color, va="top",
                         family="serif")
            self.y += lh
        self.y += gap

    def bullet(self, txt, fs=9.3, color=INK, marker="•", mcolor=None, indent=0.0):
        lh = fs / 72.0 * 1.42
        hang = 0.20 + indent
        cpl = max(10, int((TEXTW - hang) * 72.0 / (0.57 * fs)))
        lines = textwrap.wrap(txt, cpl) or [""]
        self._room(lh)
        self.ax.text(ML + indent + 0.02, self.y, marker, fontsize=fs, color=mcolor or TEAL,
                     va="top", family="serif", fontweight="bold")
        for ln in lines:
            self._room(lh)
            self.ax.text(ML + hang, self.y, ln, fontsize=fs, color=color, va="top", family="serif")
            self.y += lh
        self.y += 0.02

    def h1(self, txt, fs=15.5):
        self.space(0.16)
        self._room(0.55)
        self.ax.text(ML, self.y, txt, fontsize=fs, color=TEAL, va="top", family="serif",
                     fontweight="bold")
        self.y += fs / 72.0 + 0.07
        self.ax.plot([ML, PW - MR], [self.y, self.y], color=TEAL, lw=1.3)
        self.y += 0.12

    def h2(self, txt, fs=11.2):
        self.space(0.12)
        self._room(0.40)
        self.ax.text(ML, self.y, txt, fontsize=fs, color=INK, va="top", family="serif",
                     fontweight="bold")
        self.y += fs / 72.0 + 0.10

    def callout(self, title, body, fs=9.1, accent=TEAL, facecolor=BOXBG, edgecolor=BOXEDGE):
        lh = fs / 72.0 * 1.42
        pad = 0.12
        cpl = max(10, int((TEXTW - 2 * pad - 0.1) * 72.0 / (0.57 * fs)))
        lines = []
        for chunk in body.split("\n"):
            lines += textwrap.wrap(chunk, cpl) if chunk.strip() else [""]
        boxh = pad * 2 + (fs / 72.0 * 1.5) + len(lines) * lh + 0.06
        self._room(boxh + 0.10)
        box = FancyBboxPatch((ML, self.y), TEXTW, boxh,
                             boxstyle="round,pad=0.02,rounding_size=0.06",
                             linewidth=1.0, edgecolor=edgecolor, facecolor=facecolor, mutation_aspect=1)
        self.ax.add_patch(box)
        self.ax.add_patch(Rectangle((ML, self.y), 0.06, boxh, color=accent, lw=0))
        yy = self.y + pad
        self.ax.text(ML + pad + 0.06, yy, title, fontsize=fs + 0.6, color=accent, va="top",
                     family="serif", fontweight="bold")
        yy += fs / 72.0 * 1.5
        for ln in lines:
            self.ax.text(ML + pad + 0.06, yy, ln, fontsize=fs, color=INK, va="top", family="serif")
            yy += lh
        self.y += boxh + 0.14

    # -- embed a real figure PNG and annotate it (the heart of this report) --
    def embed_figure(self, path, height, annotations=(), caption=None, capfs=8.4,
                     width_frac=1.0):
        """Place a result-figure PNG at the cursor and overlay annotations.

        annotations: iterable of dicts in AXES-FRACTION coords (origin bottom-left of the
        image axes, x/y in [0,1]). Each may contain:
            ellipse   = (cx, cy, w, h[, angle])   red hollow ellipse around the key region
            arrow     = ((x0,y0),(x1,y1))         red arrow from x0,y0 -> x1,y1 (the head)
            label     = "text"                    short red caption
            label_xy  = (x, y)                    where the label sits (defaults near ellipse)
            label_ha  = 'left'|'center'|'right'
        Missing files are skipped gracefully with a small placeholder note.
        """
        if not os.path.exists(path):
            self._room(0.4)
            self.ax.text(ML, self.y, f"[figure not found: {os.path.basename(path)} — skipped]",
                         fontsize=8.5, color=MUTED, va="top", family="serif", style="italic")
            self.y += 0.28
            return

        try:
            img = plt.imread(path)
        except Exception as exc:  # pragma: no cover - defensive
            self._room(0.4)
            self.ax.text(ML, self.y, f"[could not read {os.path.basename(path)}: {exc}]",
                         fontsize=8.5, color=MUTED, va="top", family="serif", style="italic")
            self.y += 0.28
            return

        ih, iw = img.shape[0], img.shape[1]
        aspect = iw / ih
        draw_w = TEXTW * width_frac
        # if the natural height for the chosen width is taller than `height`, shrink width to fit
        nat_h = draw_w / aspect
        if nat_h > height:
            draw_w = height * aspect
            nat_h = height
        cap_h = 0.0
        if caption:
            cap_h = len(self._wrap(caption, capfs)) * (capfs / 72.0 * 1.4) + 0.06
        self._room(nat_h + cap_h + 0.14)

        left = (ML + (TEXTW - draw_w) / 2.0) / PW          # centre the image in the column
        bottom = 1 - (self.y + nat_h) / PH
        ax = self.fig.add_axes([left, bottom, draw_w / PW, nat_h / PH])
        ax.imshow(img)
        ax.set_xlim(0, iw); ax.set_ylim(ih, 0)            # image coords, y inverted (top=0)
        ax.axis("off")

        tx = ax.transAxes
        for a in annotations:
            if "ellipse" in a:
                e = a["ellipse"]
                cx, cy, w, h = e[0], e[1], e[2], e[3]
                ang = e[4] if len(e) > 4 else 0.0
                ax.add_patch(Ellipse((cx, cy), w, h, angle=ang, transform=tx,
                                     facecolor="none", edgecolor=RED, lw=2.5, zorder=10))
            if "arrow" in a:
                (x0, y0), (x1, y1) = a["arrow"]
                ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), transform=tx,
                                             arrowstyle="-|>", mutation_scale=16,
                                             color=RED, lw=2.0, zorder=11))
            if "label" in a:
                if "label_xy" in a:
                    lx, ly = a["label_xy"]
                else:
                    e = a.get("ellipse")
                    lx = e[0] if e else 0.5
                    ly = (e[1] + e[3] / 2 + 0.06) if e else 0.9
                ax.text(lx, ly, a["label"], transform=tx, color=RED, fontsize=8.6,
                        family="serif", fontweight="bold",
                        ha=a.get("label_ha", "center"), va="center", zorder=12,
                        bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                                  edgecolor=RED, lw=1.0, alpha=0.92))

        self.y += nat_h + 0.06
        if caption:
            for ln in self._wrap(caption, capfs):
                self.ax.text(ML, self.y, ln, fontsize=capfs, color=MUTED, va="top",
                             family="serif", style="italic")
                self.y += capfs / 72.0 * 1.4
            self.y += 0.06
        self.y += 0.06

    def close(self):
        self._flush()
        self.pdf.close()


# ============================ a small schematic for the cover ============================
def fig_lobule(ax):
    ax.add_patch(Rectangle((0, 0), 1, 1, color=TEAL, alpha=0.05, lw=0))
    n = 240
    xs = np.linspace(0.10, 0.90, n)
    for i, x in enumerate(xs):
        t = i / (n - 1)
        c = (TEAL if t < 0.5 else RUST)
        ax.plot([x, x], [0.34, 0.64], color=c, alpha=0.16 + 0.5 * abs(0.5 - t) * 2, lw=2)
    ax.scatter([0.10], [0.49], s=300, color=TEAL, zorder=5)
    ax.scatter([0.90], [0.49], s=300, color=RUST, zorder=5)
    ax.text(0.10, 0.24, "central vein\n(pericentral)", ha="center", va="top", fontsize=8.5,
            color=TEAL, family="serif")
    ax.text(0.90, 0.24, "portal triad\n(periportal)", ha="center", va="top", fontsize=8.5,
            color=RUST, family="serif")
    ax.annotate("", xy=(0.88, 0.76), xytext=(0.12, 0.76),
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.4))
    ax.text(0.5, 0.88, "zonation coordinate  (one number per hepatocyte)",
            ha="center", va="top", fontsize=9.3, color=INK, family="serif")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)


# ============================ figure paths ============================
F_A1   = config.FIG_H1 / "a1_pcpp_representatives_stage.png"
F_B1L  = config.FIG_H2 / "b1_heatmap_level_stage.png"
F_B1P  = config.FIG_H2 / "b1_heatmap_pattern_stage.png"
F_B4   = config.FIG_H2 / "b4_set_expression_by_stage.png"
F_C3   = config.FIG_CONF / "c3_level_vs_slope.png"
F_C2   = config.FIG_CONF / "c2_depth_paired.png"
F_C2C  = config.FIG_CONF / "c2_multimetric_survival.png"
F_C4   = config.FIG_CONF / "c4_endstage_umi_scatter.png"
F_D    = config.FIG_STAGING / "d_zonation_vs_fibrosis.png"
F_PCA  = config.FIG_STAGING / "e_pca_pc12_map.png"
F_LOAD = config.FIG_STAGING / "e_pca_loadings.png"


def build(path, png_dir=None):
    d = Doc(path, title_running="Spatial Hepatocyte Zonation in MASLD — Biology Findings",
            png_dir=png_dir)

    # ============================== COVER ==============================
    d.y = 1.35
    d.ax.text(ML, d.y, "Spatial Hepatocyte Zonation", fontsize=26, color=TEAL, va="top",
              family="serif", fontweight="bold"); d.y += 0.50
    d.ax.text(ML, d.y, "in MASLD Progression", fontsize=26, color=TEAL, va="top",
              family="serif", fontweight="bold"); d.y += 0.58
    d.ax.text(ML, d.y, "what changes, what doesn’t, and how sure we are", fontsize=14.5,
              color=INK, va="top", family="serif", style="italic"); d.y += 0.42
    d.ax.text(ML, d.y, "A confounder-controlled, mechanism-resolved analysis.", fontsize=11,
              color=MUTED, va="top", family="serif"); d.y += 0.40
    # cover schematic
    cov_h = 1.9
    d._room(cov_h + 0.2)
    left = ML / PW; bottom = 1 - (d.y + cov_h) / PH
    cax = d.fig.add_axes([left, bottom, TEXTW / PW, cov_h / PH]); cax.axis("off")
    fig_lobule(cax); d.y += cov_h + 0.18

    d.para("The healthy liver is zonated: hepatocytes near the central vein (pericentral) and near the "
           "portal triad (periportal) run opposite metabolic programs along a single porto-central axis. "
           "We built TWO co-primary rulers to read that axis — a curated gene-set ruler and a "
           "label-free PCA axis — validated both on healthy tissue, then transferred them unchanged "
           "to disease. Every readout in this report uses the donor as the unit of inference "
           "(47 donors, ~69,426 hepatocytes; ruler = expanded_curated unless noted).")
    d.callout("Methods caveat, stated up front",
              "The scored matrix is the SCT-corrected assay (depth-regularized; per-cell totals "
              "~3–5.7k), so sequencing depth is already largely controlled at the source, before any "
              "of the confounder analyses below. Section 4 shows the result survives explicit depth "
              "equalization on top of this.",
              accent=RUST, facecolor=CAUTBG, edgecolor=CAUTEDGE)

    # ====================== 1. THE RULER IS REAL BIOLOGY ======================
    d._new_page()
    d.h1("1.  The ruler is real biology")
    d.para("Before trusting an unsupervised axis, we must show it is zonation and not a technical "
           "artifact. The dominant axis of variation (PC1) IS the zonation axis: it correlates "
           "|r| = 0.76 with the curated zonation coordinate and |r| = 0.54 with the canonical "
           "8-marker axis, and it carries 5.8% of total variance — about twice the next component. "
           "Sequencing depth and quality load on PC2, NOT on PC1.")
    d.embed_figure(
        str(F_PCA), height=2.55,
        annotations=[
            # left panel (a): zonation gradient runs left->right along PC1 (colour = curated coord)
            {"ellipse": (0.24, 0.50, 0.40, 0.62, 0.0),
             "arrow": ((0.24, 0.14), (0.24, 0.30)),
             "label": "(a) colour grades along PC1 = zonation",
             "label_xy": (0.245, 0.06), "label_ha": "center"},
            # right panel (b): depth is diffuse, not aligned to PC1
            {"ellipse": (0.74, 0.50, 0.40, 0.62, 0.0),
             "label": "(b) depth is diffuse, not on PC1",
             "label_xy": (0.745, 0.06), "label_ha": "center"},
        ],
        caption="e_pca_pc12_map: PC1 vs PC2 coloured by the curated zonation coordinate (left) and by "
                "sequencing depth (right). The smooth left→right colour gradient in (a) means PC1 IS "
                "the zonation axis; in (b) depth is scattered with no PC1 alignment.")
    d.para("The loadings read as genuine biology, not noise. The periportal pole is led by acute-phase "
           "and fibrinogen-like genes (CRP, SAA1, SAA2, FGL1); the pericentral pole is led by "
           "bile-acid / alcohol metabolism genes (ADH4, AKR1D1). These are exactly the textbook "
           "zonal programs.")
    d.embed_figure(
        str(F_LOAD), height=3.85,
        annotations=[
            # pericentral (+) pole near top: ADH4*/AKR1D1 (purple bars, right side)
            {"ellipse": (0.66, 0.74, 0.40, 0.13, 0.0),
             "arrow": ((0.50, 0.66), (0.58, 0.72)),
             "label": "pericentral pole: ADH4*, AKR1D1",
             "label_xy": (0.50, 0.61), "label_ha": "center"},
            # periportal (-) pole: CRP/SAA1/SAA2/FGL1 (orange bars, just below centre, left side)
            {"ellipse": (0.40, 0.46, 0.46, 0.16, 0.0),
             "arrow": ((0.62, 0.40), (0.52, 0.45)),
             "label": "periportal pole: CRP, SAA1, SAA2, FGL1",
             "label_xy": (0.64, 0.36), "label_ha": "center"},
        ],
        caption="e_pca_loadings: top genes on the learned PC1 axis. Purple = pericentral (+) pole, "
                "orange = periportal (−) pole; * marks a canonical marker. The poles recover known "
                "zonal biology.")

    # ============== 2. HEALTHY IS CLEAR, DISEASE COLLAPSES ==============
    d._new_page()
    d.h1("2.  Healthy zonation is clear — and collapses with disease")
    d.para("With a validated ruler in hand, the first disease question is whether the pericentral and "
           "periportal programs stay anti-correlated within a donor (as they must if zonation is "
           "intact). Per-donor PC-vs-PP scatters answer it directly. In Healthy tissue the cloud is a "
           "tight anti-diagonal (well-powered donor 30, r = −0.48), and it stays anti-correlated "
           "through NAFLD/NASH (r = −0.53, −0.41). By Cirrhosis and End-stage the anti-diagonal "
           "is gone — the cloud becomes a positive blob (r = +0.26, +0.22): the two programs now rise "
           "and fall together, the signature of a collapsed axis.")
    d.embed_figure(
        str(F_A1), height=2.05,
        annotations=[
            # leftmost (Healthy) panel: tight anti-diagonal
            {"ellipse": (0.105, 0.50, 0.15, 0.78, 0.0),
             "label": "Healthy: tight anti-diagonal",
             "label_xy": (0.105, 0.985), "label_ha": "center"},
            # rightmost (End-stage) panel: round positive blob
            {"ellipse": (0.90, 0.50, 0.15, 0.78, 0.0),
             "label": "End-stage: positive blob",
             "label_xy": (0.90, 0.985), "label_ha": "center"},
        ],
        caption="a1_pcpp_representatives_stage: per-donor pericentral vs periportal program scores, one "
                "representative donor per stage (Healthy→End-stage). The within-donor anti-diagonal "
                "(left) gives way to a positive blob (right).")

    # ============== 3. THE MECHANISM IS ASYMMETRIC ==============
    d._new_page()
    d.h1("3.  The mechanism is asymmetric and specific")
    d.para("A collapsed axis could happen two ways: the spatial GRADIENT could flatten (de-zonation), "
           "or one program could simply switch OFF (turn-off). These have different biology, so we "
           "separate them. The answer is clear: pericentral TURN-OFF dominates. Pericentral program "
           "expression LEVEL drops ~34–37% by End-stage, and every gene set agrees on the direction.")
    d.embed_figure(
        str(F_B4), height=2.05,
        annotations=[
            # left panel = Pericentral arm, lines drop at End-stage (far right of left panel)
            {"ellipse": (0.40, 0.55, 0.16, 0.55, 0.0),
             "arrow": ((0.30, 0.86), (0.40, 0.72)),
             "label": "pericentral drops at End-stage",
             "label_xy": (0.27, 0.93), "label_ha": "center"},
            # right panel = Periportal arm, holds across stages
            {"ellipse": (0.88, 0.45, 0.16, 0.55, 0.0),
             "label": "periportal holds",
             "label_xy": (0.86, 0.93), "label_ha": "center"},
        ],
        caption="b4_set_expression_by_stage: mean per-donor program level by stage for every signature "
                "set. Left (pericentral) arms fall at End-stage; right (periportal) arms stay flat — "
                "the loss is asymmetric.")
    d.para("Gene by gene, 14/26 pericentral genes lose BOTH level and gradient (the turn-off quadrant; "
           "e.g. CYP2E1 dLevel −1.21, ADH4 −0.93), while 22/23 periportal genes hold their level "
           "(stable). The level-vs-slope map makes the asymmetry visible: pericentral (teal) genes "
           "cluster in the bottom-left turn-off quadrant.")
    d.embed_figure(
        str(F_C3), height=2.45, width_frac=0.66,
        annotations=[
            # left panel only matters; we embed at reduced width so left panel ~ fills.
            # In full image, bottom-left turn-off quadrant of the LEFT panel.
            {"ellipse": (0.30, 0.28, 0.34, 0.34, 0.0),
             "arrow": ((0.16, 0.10), (0.24, 0.22)),
             "label": "TURN-OFF quadrant:\npericentral (teal) cluster",
             "label_xy": (0.40, 0.09), "label_ha": "center"},
        ],
        caption="c3_level_vs_slope (stage panel): each point is one signature gene; x = change in LEVEL, "
                "y = change in gradient |slope|, Healthy→End-stage. Pericentral genes (teal) pile into "
                "the bottom-left TURN-OFF quadrant (lost level AND slope).")
    d.para("Now the key dissociation. The pericentral heatmap ROWS fade in the LEVEL view (genes "
           "turning off), but in the PATTERN view — where each gene is z-scored within its own panel, "
           "removing level — the diagonal banding largely PERSISTS to Cirrhosis. So pure gradient loss "
           "(de-zonation) is the WEAKER, secondary effect; turn-off is primary. The bipolar-axis "
           "collapse seen in Section 2 is most likely downstream of pericentral silencing.")
    d.embed_figure(
        str(F_B1L), height=3.25,
        annotations=[
            # top (pericentral) rows fade left->right (Healthy ... End-stage).
            # y-fraction is bottom-origin: top CYP3A4/CYP2E1 rows sit high (~0.80).
            {"ellipse": (0.55, 0.79, 0.80, 0.15, 0.0),
             "arrow": ((0.93, 0.93), (0.88, 0.84)),
             "label": "top (pericentral) rows fade Healthy→End-stage = turn-off",
             "label_xy": (0.50, 0.985), "label_ha": "center"},
        ],
        caption="b1_heatmap_level_stage: raw mean expression on a shared colour scale across stages "
                "(left=Healthy → right=End-stage). The top pericentral rows (CYP3A4/CYP2E1...) fade "
                "rightward — the genes turn off.")
    d.embed_figure(
        str(F_B1P), height=2.55,
        annotations=[
            # diagonal banding persists through Cirrhosis (4th panel from left)
            {"ellipse": (0.715, 0.50, 0.165, 0.84, 0.0),
             "arrow": ((0.60, 0.07), (0.66, 0.18)),
             "label": "banding PERSISTS to Cirrhosis = pattern survives",
             "label_xy": (0.55, 0.02), "label_ha": "center"},
        ],
        caption="b1_heatmap_pattern_stage: each gene z-scored WITHIN its own panel (level removed). The "
                "diagonal banding — the spatial gradient — largely survives into Cirrhosis, so "
                "de-zonation is the weaker effect.")

    # ============== 4. IT IS ROBUST ==============
    d._new_page()
    d.h1("4.  It is robust — confounders controlled")
    d.para("A reviewer’s first worry is that the collapse is a sampling or depth artifact. It is not. "
           "The headline trend — Spearman(zonation strength, stage) = −0.612 — is essentially "
           "unmoved by equalizing cell count across donors (common-N = 200 → −0.586) and by thinning "
           "EVERY cell to a common depth and re-scoring (−0.617).")
    d.embed_figure(
        str(F_C2), height=2.75, width_frac=0.92,
        annotations=[
            # the H1-trend numbers box, bottom-right of the plot
            {"ellipse": (0.62, 0.14, 0.52, 0.13, 0.0),
             "arrow": ((0.40, 0.04), (0.50, 0.11)),
             "label": "trend survives depth equalization: −0.612 → −0.617",
             "label_xy": (0.40, 0.005), "label_ha": "center"},
        ],
        caption="c2_depth_paired: per-donor anti-correlation at original depth vs thinned to a common "
                "2000 SCT-counts. Deep, strongly-zonated donors weaken toward 0 when thinned, but the "
                "STAGE trend (boxed) is unchanged: −0.612 → −0.617.")
    d.para("And this is not specific to the anti-correlation readout. We repeated the depth-equalization "
           "test for EVERY zonation metric — coordinate spread (SD), inter-quartile range, and 5–95% "
           "range — and all four keep a significant collapsing trend at common depth (strength −0.62, "
           "spread −0.44, IQR −0.40, range −0.39; all p < 0.05). The collapse is a property of the data, "
           "not of one metric or of sequencing depth.")
    d.embed_figure(
        str(F_C2C), height=2.5, width_frac=0.82,
        annotations=[
            {"ellipse": (0.5, 0.5, 0.98, 0.92, 0.0),
             "label": "every metric stays negative after depth equalization",
             "label_xy": (0.5, 0.96), "label_ha": "center"},
        ],
        caption="c2_multimetric_survival: Spearman(metric, stage) at original depth (teal) vs common "
                "depth (rust) for four independent zonation readouts. All stay negative (collapsing) and "
                "significant — the depth control is not anti-correlation-specific.")
    d.para("Depth DOES causally degrade the measurement — a deep, zonated donor weakens from "
           "r = −0.55 to −0.33 when thinned — but depth does not track disease stage, so it cannot "
           "manufacture the trend. The End-stage positive blob is likewise NOT a depth artifact: among "
           "End-stage cells, the BEST-sequenced ones are if anything MORE positive (high-depth tercile "
           "+0.33 vs low-depth tercile +0.24), the opposite of what a depth artifact would predict.")
    d.embed_figure(
        str(F_C4), height=3.0, width_frac=0.80,
        annotations=[
            # the numbers box (bottom-centre): all = +0.277, top tercile MORE positive
            {"ellipse": (0.50, 0.18, 0.66, 0.16, 0.0),
             "arrow": ((0.74, 0.06), (0.62, 0.13)),
             "label": "best-sequenced cells are MORE positive, not less",
             "label_xy": (0.50, 0.025), "label_ha": "center"},
        ],
        caption="c4_endstage_umi_scatter: End-stage cells coloured by depth. The anti-correlation is "
                "positive overall (+0.277) and the high-depth tercile is MORE positive than the low — "
                "so high-depth cells are not more anti-correlated. The collapse is not explained by depth.")

    # ============== 5. IT TRACKS FIBROSIS ==============
    d._new_page()
    d.h1("5.  It tracks fibrosis specifically")
    d.para("Finally, the de-zonation signal is not generic disease severity — it is tied to FIBROSIS. "
           "Zonation strength declines monotonically across the fibrosis stages F0→F4 "
           "(Spearman rho = −0.49, p = 4.4e−4, n = 47). And it is fibrosis-SPECIFIC: the partial "
           "correlation controlling for the NAS activity score holds at rho = −0.40, whereas the "
           "reverse — strength vs NAS controlling for fibrosis — collapses to −0.12.")
    d.embed_figure(
        str(F_D), height=2.35,
        annotations=[
            # leftmost panel "Zonation strength": the F3->F4 drop at the far right
            {"ellipse": (0.275, 0.62, 0.10, 0.55, 0.0),
             "arrow": ((0.245, 0.18), (0.27, 0.40)),
             "label": "F0→F4 decline in zonation strength",
             "label_xy": (0.245, 0.07), "label_ha": "center"},
        ],
        caption="d_zonation_vs_fibrosis: donor-level zonation readouts vs Fibrosis (F0–F4); point size "
                "~ n_cells. The leftmost panel (zonation strength) declines from F0/F1 to F4 "
                "(rho = −0.49).")

    # ============== 6. HONEST CAVEATS ==============
    d._new_page()
    d.h1("6.  Honest caveats")
    d.para("These limitations are stated plainly so the strength of each claim is not over-read.")
    d.bullet("Only 4 healthy-control donors anchor the “healthy” end, and 2 of them are low-depth "
             "and weakly zonated — the healthy baseline is thinly powered.", mcolor=RUST)
    d.bullet("De-zonation (pure gradient loss) is the WEAKER effect; the dominant, primary mechanism "
             "is pericentral turn-off. The two should not be conflated.", mcolor=RUST)
    d.bullet("Within “NASH-without-cirrhosis” the F1→F3 grading is essentially flat: the fibrosis "
             "signal is the F0/F1-vs-F4 contrast, not fine intermediate grading.", mcolor=RUST)
    d.bullet("The depth control operates on the SCT-corrected scale, not raw UMI counts — it removes "
             "residual depth effects on top of SCT, not raw-count depth from scratch.", mcolor=RUST)
    d.bullet("This is a cross-sectional human cohort. We therefore establish a confounder-ROBUST "
             "ASSOCIATION between fibrosis and de-zonation — NOT disease→de-zonation causality.",
             mcolor=RUST)
    d.callout("What the evidence does and does not support",
              "Supported: (i) PC1 is genuine zonation biology; (ii) the bipolar axis collapses with "
              "disease; (iii) the mechanism is asymmetric pericentral turn-off, with de-zonation "
              "secondary; (iv) the trend is robust to cell-count and depth equalization; (v) it tracks "
              "fibrosis specifically.  Not supported: a causal claim, fine within-NASH grading, or a "
              "strong healthy baseline.",
              accent=RUST, facecolor=CAUTBG, edgecolor=CAUTEDGE)

    # ============== 7. METHODS RECAP ==============
    d.h1("7.  Methods recap")
    d.para("Rulers (co-primary). (1) Curated signature-mean coordinate: mean_z(pericentral) − "
           "mean_z(periportal) over per-gene z-scores. (2) A label-free PCA axis (PC1) learned without "
           "any gene list. Both must pass an 8-marker healthy validation gate before transfer to "
           "disease. Readouts span four figure families: A (axis collapse), B (mechanism: level vs "
           "pattern), C (confounder controls: cell count, depth, End-stage depth), D (fibrosis/NAS "
           "staging), and E (ruler interpretation: PCA map and loadings) — ~25 figures in all. All "
           "inference is donor-level across ~47 donors (~69,426 hepatocytes), with the donor as the "
           "unit throughout.")

    d.close()


def main():
    out = os.path.join(str(config.REPORTS), "Zonation_Biology_Findings.pdf")
    os.makedirs(str(config.REPORTS), exist_ok=True)
    png_dir = os.environ.get("BIOFINDINGS_PNG_DIR")  # set to dump per-page PNGs for self-check
    build(out, png_dir=png_dir)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
