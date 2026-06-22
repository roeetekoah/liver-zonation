#!/usr/bin/env python3
"""Generate a stand-alone METHODS COMPANION PDF that explains, from first principles, how the
zonation ruler is built, normalized, and validated:

  * per-gene normalization (log1p-CP10k -> per-gene z-score) and what "by the healthy atlas" means
  * combining genes into one coordinate: signature-mean scoring
  * PCA in depth: it maximizes the variance of WHAT, exactly
  * the 8-marker healthy validation gate
  * the healthy quality score (anti-correlation + split-half) and how selection uses it

No LaTeX needed: the document is rendered with matplotlib's PdfPages (a tiny flow-layout engine
below), so it builds anywhere matplotlib is installed. Output: results/Zonation_Methods_Explainer.pdf

Run:  python src/make_methods_explainer.py
"""
from __future__ import annotations
import os, sys, textwrap
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib.backends.backend_pdf import PdfPages
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

# ---- palette ----
INK     = "#1a1a1a"
TEAL    = "#1b6e78"      # headings / pericentral
RUST    = "#c05621"      # accents / periportal
MUTED   = "#5a5a5a"
RULE    = "#cdd6d8"
BOXBG   = "#f3f7f8"
BOXEDGE = "#bcd0d3"
CODEBG  = "#f0f1ee"

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
        self.pdf.savefig(self.fig)
        if self.png_dir:
            self.fig.savefig(os.path.join(self.png_dir, f"page_{self.page:02d}.png"), dpi=110)
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
        # conservative char width for DejaVu Serif: ~ 0.50*fs points wide per char
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
        lines = self._wrap(txt, fs)
        # shrink wrap width slightly for hanging indent
        cpl = max(10, int((TEXTW - hang) * 72.0 / (0.57 * fs)))
        lines = textwrap.wrap(txt, cpl) or [""]
        self._room(lh)
        self.ax.text(ML + indent + 0.02, self.y, marker, fontsize=fs, color=mcolor or TEAL,
                     va="top", family="serif", fontweight="bold")
        for i, ln in enumerate(lines):
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

    def eq(self, tex, fs=12.5, gap=0.12):
        h = fs / 72.0 * 2.0 + gap
        self._room(h)
        self.ax.text(PW / 2.0, self.y + 0.06, tex, fontsize=fs, color=INK, va="top",
                     ha="center", family="serif")
        self.y += h

    def callout(self, title, body, fs=9.1, accent=TEAL):
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
                             linewidth=1.0, edgecolor=BOXEDGE, facecolor=BOXBG, mutation_aspect=1)
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

    def figure(self, draw_fn, height, caption=None, capfs=8.4):
        cap_h = 0.0
        if caption:
            cap_lines = self._wrap(caption, capfs)
            cap_h = len(cap_lines) * (capfs / 72.0 * 1.4) + 0.06
        self._room(height + cap_h + 0.12)
        left = ML / PW
        bottom = 1 - (self.y + height) / PH
        ax = self.fig.add_axes([left, bottom, TEXTW / PW, height / PH])
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
        draw_fn(ax)
        self.y += height + 0.06
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


# ============================ schematic figures ============================
def fig_title(ax):
    ax.add_patch(Rectangle((0, 0), 1, 1, color=TEAL, alpha=0.06, lw=0))
    # a stylized lobule: central vein (teal) -> portal triad (rust), a gradient bar
    n = 240
    xs = np.linspace(0.08, 0.92, n)
    for i, x in enumerate(xs):
        t = i / (n - 1)
        c = (TEAL if t < 0.5 else RUST)
        ax.plot([x, x], [0.30, 0.62], color=c, alpha=0.18 + 0.5 * abs(0.5 - t) * 2, lw=2)
    ax.scatter([0.08], [0.46], s=320, color=TEAL, zorder=5)
    ax.scatter([0.92], [0.46], s=320, color=RUST, zorder=5)
    ax.text(0.08, 0.20, "central vein\n(pericentral)", ha="center", va="top", fontsize=8.5,
            color=TEAL, family="serif")
    ax.text(0.92, 0.20, "portal triad\n(periportal)", ha="center", va="top", fontsize=8.5,
            color=RUST, family="serif")
    ax.annotate("", xy=(0.90, 0.74), xytext=(0.10, 0.74),
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.4))
    ax.text(0.5, 0.84, "zonation coordinate  (one number per hepatocyte)",
            ha="center", va="top", fontsize=9.5, color=INK, family="serif")


def fig_zscore(ax):
    rng = np.random.RandomState(3)
    raw = rng.lognormal(mean=0.6, sigma=0.9, size=4000)
    z = (np.log1p(raw) - np.log1p(raw).mean()) / np.log1p(raw).std()
    a1 = ax.inset_axes([0.04, 0.12, 0.40, 0.78])
    a2 = ax.inset_axes([0.56, 0.12, 0.40, 0.78])
    a1.hist(raw, bins=40, color=RUST, alpha=0.85)
    a1.set_title("raw counts (one gene)", fontsize=8.5, family="serif", color=INK)
    a1.set_yticks([]); a1.tick_params(labelsize=7)
    a2.hist(z, bins=40, color=TEAL, alpha=0.85)
    a2.axvline(0, color=INK, lw=1)
    a2.set_title("log1p-CP10k, then per-gene z-score", fontsize=8.5, family="serif", color=INK)
    a2.set_yticks([]); a2.tick_params(labelsize=7)
    for a in (a1, a2):
        for s in a.spines.values():
            s.set_color(RULE)
    ax.annotate("", xy=(0.55, 0.5), xytext=(0.45, 0.5),
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.6))


def fig_pca(ax):
    # left: cells x genes z matrix schematic ; right: cell cloud + principal axis
    a1 = ax.inset_axes([0.02, 0.10, 0.36, 0.82])
    rng = np.random.RandomState(7)
    Z = rng.randn(14, 10)
    # impose a zonation gradient: cells (rows) ordered by a latent coord; two gene blocks anti-correlate
    coord = np.linspace(-1.6, 1.6, 14)
    Z[:, :5] += coord[:, None] * 0.9     # pericentral block up with coord
    Z[:, 5:] -= coord[:, None] * 0.9     # periportal block down with coord
    a1.imshow(Z, aspect="auto", cmap="PuOr", vmin=-2.4, vmax=2.4)
    a1.set_xlabel("genes  (features)", fontsize=8, family="serif")
    a1.set_ylabel("cells  (hepatocytes)", fontsize=8, family="serif")
    a1.set_xticks([]); a1.set_yticks([])
    a1.set_title("z-scored matrix", fontsize=8.6, family="serif", color=INK)

    a2 = ax.inset_axes([0.50, 0.10, 0.48, 0.82])
    g1 = coord * 1.0 + rng.randn(14) * 0.35      # a pericentral gene
    g2 = -coord * 1.0 + rng.randn(14) * 0.35     # a periportal gene
    a2.scatter(g1, g2, s=46, color=TEAL, edgecolor="white", zorder=4)
    # principal axis line (direction of max spread)
    pts = np.vstack([g1, g2]).T
    pts = pts - pts.mean(0)
    u, s, vt = np.linalg.svd(pts, full_matrices=False)
    d = vt[0]
    t = np.linspace(-2.3, 2.3, 2)
    a2.plot(d[0] * t, d[1] * t, color=RUST, lw=2.2, zorder=3)
    a2.annotate("PC1: axis of\nmax variance\nacross cells", xy=(d[0]*2.0, d[1]*2.0),
                xytext=(0.2, 2.0), fontsize=8.0, color=RUST, family="serif",
                arrowprops=dict(arrowstyle="-|>", color=RUST, lw=1.2))
    a2.set_xlabel("pericentral gene (z)", fontsize=8, family="serif", color=TEAL)
    a2.set_ylabel("periportal gene (z)", fontsize=8, family="serif", color=RUST)
    a2.axhline(0, color=RULE, lw=0.8); a2.axvline(0, color=RULE, lw=0.8)
    a2.set_xticks([]); a2.set_yticks([])
    a2.set_title("each cell is a point in gene-space", fontsize=8.6, family="serif", color=INK)
    for s_ in a2.spines.values():
        s_.set_color(RULE)


def fig_validation(ax):
    pc = [("CYP2E1", "+"), ("CYP1A2", "+"), ("GLUL", "+"), ("PCK2", "+")]
    pp = [("ASS1", "−"), ("ALDOB", "−"), ("PCK1", "−"), ("HAL", "−")]
    ax.text(0.25, 0.96, "pericentral markers", ha="center", va="top", fontsize=9,
            color=TEAL, family="serif", fontweight="bold")
    ax.text(0.75, 0.96, "periportal markers", ha="center", va="top", fontsize=9,
            color=RUST, family="serif", fontweight="bold")
    ax.text(0.25, 0.86, "expect  corr(coord, gene) > 0", ha="center", va="top", fontsize=7.6,
            color=MUTED, family="serif")
    ax.text(0.75, 0.86, "expect  corr(coord, gene) < 0", ha="center", va="top", fontsize=7.6,
            color=MUTED, family="serif")
    y0 = 0.74
    for i, (g, s) in enumerate(pc):
        yy = y0 - i * 0.165
        ax.text(0.10, yy, g, ha="left", va="center", fontsize=8.8, family="monospace", color=INK)
        ax.text(0.40, yy, s, ha="center", va="center", fontsize=11, color=TEAL, fontweight="bold")
        ax.text(0.455, yy, "✓", ha="center", va="center", fontsize=10, color="#2e7d32")
    for i, (g, s) in enumerate(pp):
        yy = y0 - i * 0.165
        ax.text(0.60, yy, g, ha="left", va="center", fontsize=8.8, family="monospace", color=INK)
        ax.text(0.90, yy, s, ha="center", va="center", fontsize=11, color=RUST, fontweight="bold")
        ax.text(0.955, yy, "✓", ha="center", va="center", fontsize=10, color="#2e7d32")
    ax.axvline(0.5, color=RULE, lw=0.8)
    ax.text(0.5, 0.045, "GATE: ≥4 of 8 present  AND  a majority on the correct side  →  PASS",
            ha="center", va="bottom", fontsize=8.2, color=INK, family="serif")


def fig_quality(ax):
    rng = np.random.RandomState(11)
    a1 = ax.inset_axes([0.05, 0.14, 0.40, 0.74])
    pc = rng.randn(300); pp = -0.78 * pc + rng.randn(300) * 0.6
    a1.scatter(pc, pp, s=8, color=TEAL, alpha=0.5)
    a1.set_xlabel("PC-arm score", fontsize=8, family="serif")
    a1.set_ylabel("PP-arm score", fontsize=8, family="serif")
    a1.set_title("(i) anti-correlation\n(healthy: strongly negative)", fontsize=8.2, family="serif")
    a1.set_xticks([]); a1.set_yticks([])
    for s in a1.spines.values():
        s.set_color(RULE)

    a2 = ax.inset_axes([0.57, 0.14, 0.40, 0.74])
    base = rng.randn(300)
    h1 = base + rng.randn(300) * 0.55
    h2 = base + rng.randn(300) * 0.55
    a2.scatter(h1, h2, s=8, color=RUST, alpha=0.5)
    a2.set_xlabel("coordinate, gene-half A", fontsize=8, family="serif")
    a2.set_ylabel("coordinate, gene-half B", fontsize=8, family="serif")
    a2.set_title("(ii) split-half\n(reproducible: positive)", fontsize=8.2, family="serif")
    a2.set_xticks([]); a2.set_yticks([])
    for s in a2.spines.values():
        s.set_color(RULE)


def fig_coherence(ax):
    # within-program coherence: PC genes co-vary (left); a fragmented program (right)
    rng = np.random.RandomState(5)
    for k, (title, lat, col, sub) in enumerate([
            ("coherent program", 1.0, TEAL, "genes move together → high coherence"),
            ("fragmented program", 0.15, RUST, "genes decoupled → low coherence")]):
        a = ax.inset_axes([0.04 + k * 0.52, 0.16, 0.42, 0.72])
        base = rng.randn(60)
        for _ in range(6):
            g = lat * base + (1 - lat) * rng.randn(60) * 1.0 + rng.randn(60) * 0.25
            a.plot(np.sort(rng.permutation(60))[:0] if False else np.arange(60),
                   g + _ * 3.2, color=col, lw=0.9, alpha=0.8)
        a.set_title(title, fontsize=8.4, family="serif", color=INK)
        a.set_xlabel(sub, fontsize=7.3, family="serif", color=MUTED)
        a.set_xticks([]); a.set_yticks([])
        for s in a.spines.values():
            s.set_color(RULE)


def fig_spread_iqr(ax):
    rng = np.random.RandomState(2)
    a1 = ax.inset_axes([0.05, 0.20, 0.40, 0.70])
    a2 = ax.inset_axes([0.57, 0.20, 0.40, 0.70])
    healthy = rng.uniform(-2.4, 2.4, 1400) + rng.randn(1400) * 0.25
    diseased = rng.randn(1400) * 0.55
    for a, data, title, col in [(a1, healthy, "healthy donor", TEAL),
                                (a2, diseased, "de-zonated donor", RUST)]:
        a.hist(data, bins=34, range=(-3, 3), color=col, alpha=0.5, orientation="vertical")
        sd = np.std(data); q1, q3 = np.percentile(data, [25, 75]); mu = np.mean(data)
        ytop = a.get_ylim()[1]
        a.add_patch(Rectangle((q1, 0), q3 - q1, ytop, color=col, alpha=0.16, lw=0))
        a.annotate("", xy=(mu + sd, ytop * 0.86), xytext=(mu - sd, ytop * 0.86),
                   arrowprops=dict(arrowstyle="<->", color=INK, lw=1.1))
        a.text(mu, ytop * 0.93, "±1 SD (spread)", ha="center", fontsize=7.0, family="serif")
        a.text(q3, ytop * 0.5, " IQR", ha="left", fontsize=7.0, color=col, family="serif")
        a.set_title(title, fontsize=8.4, family="serif", color=INK)
        a.set_xlabel("zonation coordinate", fontsize=7.6, family="serif")
        a.set_yticks([]); a.set_xticks([])
        for s in a.spines.values():
            s.set_color(RULE)


def fig_slopeloss(ax):
    a1 = ax.inset_axes([0.05, 0.18, 0.40, 0.70])
    a2 = ax.inset_axes([0.57, 0.18, 0.40, 0.70])
    bins = np.arange(5)
    rng = np.random.RandomState(8)
    steep = 2.2 - 0.85 * bins
    flat = 1.0 - 0.06 * bins
    for a, y, title, col in [(a1, steep, "healthy: steep zonal slope", TEAL),
                             (a2, flat, "diseased: slope lost (flat)", RUST)]:
        yj = y + rng.randn(5) * 0.05
        a.plot(bins, yj, "o-", color=col, lw=2, ms=6)
        # slope guide line
        m, b = np.polyfit(bins, yj, 1)
        a.plot(bins, m * bins + b, "--", color=INK, lw=1, alpha=0.6)
        a.text(0.5, 0.08, f"slope ≈ {m:+.2f}", transform=a.transAxes, fontsize=8,
               family="serif", color=INK)
        a.set_title(title, fontsize=8.4, family="serif", color=INK)
        a.set_xlabel("coordinate bin  (PC → PP)", fontsize=7.6, family="serif")
        a.set_ylabel("gene expression", fontsize=7.6, family="serif")
        a.set_ylim(-0.2, 2.6); a.set_xticks(bins); a.set_yticks([])
        a.tick_params(labelsize=7)
        for s in a.spines.values():
            s.set_color(RULE)


def fig_pipeline(ax):
    steps = [
        ("genes\n(list or\nPCA)", TEAL),
        ("normalize\nz-score\n(Sec. 2)", "#3a7d52"),
        ("combine\nsig-mean or\nPCA axis", RUST),
        ("validate\n8-marker\ngate", "#8a6d3b"),
        ("score\nhealthy\nquality Q", TEAL),
        ("freeze 2\nco-primaries", INK),
    ]
    n = len(steps)
    x0, usable = 0.006, 0.988
    w = 0.140
    gap = (usable - n * w) / (n - 1)
    yc = 0.5
    for i, (label, c) in enumerate(steps):
        x = x0 + i * (w + gap)
        box = FancyBboxPatch((x, yc - 0.23), w, 0.46,
                             boxstyle="round,pad=0.004,rounding_size=0.02",
                             linewidth=1.2, edgecolor=c, facecolor="white")
        ax.add_patch(box)
        ax.text(x + w / 2, yc, label, ha="center", va="center", fontsize=7.0,
                family="serif", color=INK)
        if i < n - 1:
            ax.add_patch(FancyArrowPatch((x + w, yc), (x + w + gap, yc),
                         arrowstyle="-|>", mutation_scale=9, color=MUTED, lw=1.1))
    ax.text(0.5, 0.04, "selection uses HEALTHY metrics only; disease H1/H2/H3 are the test",
            ha="center", va="bottom", fontsize=7.8, color=MUTED, family="serif", style="italic")


# ============================ content ============================
def build(path, png_dir=None):
    d = Doc(path, title_running="Zonation Ruler — Methods Companion", png_dir=png_dir)

    # ---------- title ----------
    d.y = 1.5
    d.ax.text(ML, d.y, "The Zonation Ruler", fontsize=27, color=TEAL, va="top",
              family="serif", fontweight="bold"); d.y += 0.52
    d.ax.text(ML, d.y, "How it is built, normalized, and validated", fontsize=14.5,
              color=INK, va="top", family="serif"); d.y += 0.40
    d.ax.text(ML, d.y, "A methods companion — written to answer four questions precisely:",
              fontsize=10, color=MUTED, va="top", family="serif"); d.y += 0.34
    for q in ["1.  The PCA maximizes the variance of WHAT, exactly?",
              "2.  How is a per-gene z-score computed — and what does “by the healthy atlas” mean?",
              "3.  What is the 8-marker validation, step by step?",
              "4.  How is the healthy quality score calculated?"]:
        d.ax.text(ML + 0.1, d.y, q, fontsize=10, color=INK, va="top", family="serif"); d.y += 0.30
    d.y += 0.12
    d.figure(fig_title, 2.0)
    d.para("Every claim here is traced to the actual code: src/steps/step4_score.py (signature "
           "scoring), step4c_learned_coords.py (PCA rulers), step4b_classifier.py (Paper-2 loader), "
           "step5_validate.py (the gate), step5b_ruler_diagnostics.py (quality metrics), and "
           "summarize_signature_battery.py (selection). Page references are to functions, not lines.",
           fs=8.6, color=MUTED)

    # ---------- 1. orientation ----------
    d._new_page()
    d.h1("1.  Orientation: what a “ruler” is")
    d.para("The healthy liver lobule is spatially organized along a porto-central axis. Hepatocytes "
           "near the central vein (pericentral) and near the portal triad (periportal) run opposite "
           "metabolic programs. This spatial gradient is called zonation.")
    d.para("Our disease data (Paper 1: 47 donors, ~69,000 hepatocyte nuclei across five MASLD stages) "
           "is single-nucleus RNA-seq — it has no spatial coordinates. A ruler is a rule that reads "
           "a cell’s gene expression and returns one number: a pseudo-zonation coordinate placing that "
           "cell on the pericentral↔periportal axis. We learn the rule on a healthy reference "
           "(Paper 2: a spatial atlas that defines the zonation program), freeze it, then apply it to "
           "the disease cells and ask whether zonation degrades with disease.")
    d.callout("Two families of ruler — same output",
              "SIGNATURE-MEAN rulers use two published gene lists (a pericentral set and a periportal "
              "set) and average them.  LEARNED rulers use PCA to discover the axis from the data with no "
              "gene list at all.  Both end in exactly one coordinate per cell, and both are judged by "
              "the same healthy-quality criteria before they are trusted on disease.")
    d.para("The rest of this document walks the common machinery bottom-up: first how a single gene’s "
           "value is normalized (Sec. 2), then the two ways genes are combined into a coordinate "
           "(Secs. 3–4), then the two healthy checks every ruler must pass — the validation gate "
           "(Sec. 5) and the quality score (Sec. 6).")

    # ---------- 2. normalization ----------
    d.h1("2.  Per-gene normalization: the z-score")
    d.para("A raw count matrix cannot be compared cell-to-cell or gene-to-gene directly: cells differ "
           "in sequencing depth, and genes differ by orders of magnitude in baseline expression. Two "
           "steps fix this.")
    d.h2("Step A — depth normalization + log (per cell)")
    d.para("For each cell c, divide each gene’s count by that cell’s total counts (its library size), "
           "scale to a fixed 10,000, and take log1p. This is “log1p-CP10k”:")
    d.eq(r"$x_{gc} \;=\; \log\!\left(1 + 10^{4}\cdot \frac{c_{gc}}{\sum_{g'} c_{g'c}}\right)$")
    d.para("Now a value reflects relative abundance within the cell, not how deeply that cell was "
           "sequenced. (In code: np.log1p(counts / libsize * 1e4), in zrows() and _z_dense_p1().)")
    d.h2("Step B — standardization (per gene, across cells)")
    d.para("For each gene g, subtract that gene’s mean and divide by its standard deviation, where the "
           "mean and SD are taken over cells:")
    d.eq(r"$z_{gc} \;=\; \frac{x_{gc} - \mu_g}{\sigma_g}, \qquad "
         r"\mu_g = \frac{1}{N}\sum_{c} x_{gc}, \quad "
         r"\sigma_g^2 = \frac{1}{N}\sum_{c}(x_{gc}-\mu_g)^2$")
    d.figure(fig_zscore, 1.7,
             caption="A single gene before and after. The z-score recenters every gene to mean 0, SD 1, "
                     "so a highly-expressed housekeeping gene and a rare marker contribute on equal "
                     "footing to the coordinate.")
    d.para("After this, z = +2 means “two SDs above this gene’s typical level” — a unit that is "
           "comparable across genes. Without it, a few high-abundance genes would dominate any average.")
    d.callout("What “z-scored by the healthy atlas” means (your Q2)",
              "The mean and SD in Step B are computed over a specific set of cells, and which set matters. "
              "For the clean label-free ruler (unsupervised_p2), μ_g and σ_g — and the PCA below — are "
              "computed entirely on the Paper-2 HEALTHY ATLAS hepatocytes (the matrix mat_norm in the "
              "atlas file, already depth-normalized by its authors, so Step A is not repeated). The "
              "resulting standardization is then applied to the Paper-1 disease cells. Because the "
              "statistics come from healthy external tissue, the ruler never ‘sees’ the disease cells "
              "while being defined — this is what keeps it leakage-free.", accent=RUST)

    # ---------- 3. signature-mean ----------
    d.h1("3.  Combining genes into one coordinate: signature-mean")
    d.para("The simplest ruler takes a published pericentral gene set (PC) and periportal set (PP). "
           "For a cell, average the z-scores over each set to get two arm scores, restandardize each "
           "arm to unit variance, and subtract:")
    d.eq(r"$\bar z^{\,\mathrm{PC}}_{c} = \frac{1}{|\mathrm{PC}|}\sum_{g\in \mathrm{PC}} z_{gc},"
         r"\qquad \mathrm{coord}_{c} = \tilde z^{\,\mathrm{PC}}_{c} - \tilde z^{\,\mathrm{PP}}_{c}$")
    d.para("The subtraction makes the coordinate bipolar: a cell scores high only if it is "
           "simultaneously high on the pericentral program AND low on the periportal program. "
           "Re-standardizing each arm before subtracting (the tilde) equalizes the two sides even when "
           "the gene sets are very different sizes (e.g. 26 PC vs 23 PP for the expanded set). "
           "(In code: score() in step4_score.py.)")

    # ---------- 4. PCA ----------
    d.h1("4.  The PCA ruler: variance of WHAT, exactly")
    d.para("The learned ruler uses no gene list. It builds the z-scored matrix Z with one row per cell "
           "and one column per feature gene (genes expressed in ≥5% of hepatocytes and present in the "
           "atlas), then runs PCA on it. Here is the crux of your question.")
    d.figure(fig_pca, 2.3,
             caption="Left: the input is a cells×genes matrix of z-scores. Right: PCA treats each CELL "
                     "as a point in gene-space and finds the straight axis along which the cloud of cells "
                     "is most stretched out.")
    d.h2("What is being maximized")
    d.para("PCA looks for a direction in gene-space — a vector of per-gene weights w (the loadings) — "
           "such that the per-cell score formed by that direction has the largest possible variance "
           "ACROSS CELLS:")
    d.eq(r"$s_{c} = \mathbf{w}^{\top}\mathbf{z}_{c} = \sum_{g} w_{g}\,z_{gc}, "
         r"\qquad \mathrm{PC1} = \max_{\|\mathbf{w}\|=1}\ \mathrm{Var}_{c}(s_{c})$")
    d.callout("Say it in words",
              "PCA does NOT maximize the variance of a gene, and not the variance across genes. It "
              "maximizes the variance, across hepatocytes, of a single weighted-sum-of-genes score. "
              "Equivalently: of all the ways to collapse a cell’s ~thousands of gene values into one "
              "number by a weighted sum, PC1 is the weighting that spreads the cells out the most. "
              "Geometrically, it is the long axis of the cell cloud.")
    d.para("Why does that axis turn out to be zonation? Among healthy hepatocytes — which are otherwise "
           "a fairly uniform cell type — spatial position along the porto-central axis is the single "
           "largest structured source of expression differences. So the direction of maximum cell-to-"
           "cell variance is, empirically, the porto-central axis. The genes with large positive "
           "loadings form one pole (pericentral) and those with large negative loadings the other "
           "(periportal); that the two poles are anti-correlated across cells is exactly what makes the "
           "axis a usable bipolar ruler.")
    d.h2("We do not blindly take PC1")
    d.para("PCA returns several components. We compute, for each of the top components, the rank "
           "correlation between its per-cell score and a small marker axis (mean of pericentral-marker "
           "z minus mean of periportal-marker z), pick the component with the largest absolute "
           "correlation, and flip its sign so that pericentral is the high end. This guarantees the "
           "learned axis is oriented to biology, not to an arbitrary technical factor. (In code: the "
           "argmax over corrs in unsupervised()/unsupervised_p2().)")
    d.h2("Three PCA variants — the difference is which cells the variance is taken over")
    d.bullet("unsupervised_p2 — variance maximized over the Paper-2 healthy ATLAS cells (external to "
             "Paper 1). Leakage-free; this is the label-free co-primary ruler.", mcolor=TEAL)
    d.bullet("unsupervised — variance maximized over Paper-1 HEALTHY cells. Because its healthy quality "
             "metrics are then measured on those same cells, they are in-sample (optimistic).",
             mcolor=RUST)
    d.bullet("unsupervised_combined — variance maximized over the pool of Paper-1 healthy + Paper-2 "
             "atlas cells. Same in-sample caveat as above.", mcolor=RUST)
    d.para("This is why eligibility for the frozen-primary slot is leakage-clean (axis not fit on "
           "Paper-1 cells), not publishability — see Sec. 6.")

    # ---------- 5. validation ----------
    d.h1("5.  The 8-marker validation gate")
    d.para("Before any ruler is trusted, it must recover textbook zonation in HEALTHY cells. This is a "
           "positive control: if the coordinate cannot reproduce what is already known in healthy "
           "tissue, nothing it says about disease is credible. The check uses a fixed panel of eight "
           "canonical markers — the same panel for every ruler:")
    d.bullet("Pericentral (expect to rise with the coordinate): CYP2E1, CYP1A2 (xenobiotic P450s), "
             "GLUL (glutamine synthetase — the canonical pericentral Wnt-target), PCK2.", mcolor=TEAL)
    d.bullet("Periportal (expect to fall with the coordinate): ASS1 (urea cycle), ALDOB, PCK1 "
             "(gluconeogenesis), HAL (histidine catabolism).", mcolor=RUST)
    d.figure(fig_validation, 2.05,
             caption="For each present marker we take the Spearman correlation between the coordinate and "
                     "the marker’s z-vector, restricted to healthy cells, and check its sign.")
    d.h2("The rule")
    d.para("In healthy cells only, for each marker compute corr(coord, marker). A pericentral marker "
           "passes if the correlation is positive; a periportal marker passes if it is negative. The "
           "ruler clears the gate when at least four of the eight markers are present AND a majority of "
           "the present markers have the correct sign. The majority rule (rather than all-eight) keeps "
           "one noisy or dropout-prone marker from sinking an otherwise sound ruler. A ruler that fails "
           "is dropped before any disease analysis runs. (In code: validate() in step5_validate.py; "
           "the panel is VAL in common.py.)")
    d.callout("Why this is a fair test",
              "The eight markers are a fixed canonical panel, identical across all rulers, so it does not "
              "favour any particular gene list. For the label-free PCA rulers the markers are wholly "
              "independent of how the axis was built. The gate is about sign (direction), not magnitude — "
              "it asks only ‘does the ruler point the right way in healthy tissue?’")

    # ---------- 6. quality score ----------
    d.h1("6.  The healthy quality score")
    d.para("Passing the gate makes a ruler admissible; the quality score ranks the admissible ones. It "
           "combines two healthy-cell properties, each measuring something the gate does not.")
    d.h2("(i) PC–PP anti-correlation")
    d.para("Across healthy cells, the Spearman correlation between the pericentral arm score and the "
           "periportal arm score. A genuine bipolar axis is strongly NEGATIVE: cells high on one "
           "program are low on the other. A value near zero (or positive) means the two arms are not "
           "really opposite — not a true zonation axis.")
    d.h2("(ii) Split-half reproducibility")
    d.para("This asks: is the coordinate a property of the whole gene program, or an accident of a few "
           "influential genes? If the program is real, any random half of it should reconstruct almost "
           "the same coordinate as the other half. The procedure, run in healthy cells:")
    d.bullet("Randomly split the PC genes into two disjoint halves (A and B); do the same for the PP "
             "genes.")
    d.bullet("Build two independent coordinates: coord_A = arm(PC_A) − arm(PP_A) and coord_B from the "
             "B halves. Each is a complete little ruler made from half the genes.")
    d.bullet("Take the Spearman correlation between coord_A and coord_B across cells.")
    d.bullet("Repeat 20 times with fresh random splits and average; report the mean (and a 2.5–97.5% "
             "interval).")
    d.para("A high value (close to 1) means the two halves agree — the coordinate is reproducible and "
           "internally consistent, i.e. it is a reliable measurement, not noise. A low value means the "
           "ruler hangs on a handful of genes and should not be trusted. (In code: _coord_from_halves() "
           "and the n_splits loop in step5b_ruler_diagnostics.py.)")
    d.figure(fig_quality, 1.95,
             caption="The two score ingredients, both measured in healthy cells. Left: a good ruler’s two "
                     "arms are strongly anti-correlated. Right: two coordinates built from disjoint random "
                     "gene-halves land almost on top of each other (high split-half).")
    d.h2("The combined score")
    d.para("Both ingredients are ‘higher = better’, so the score adds them, rewarding a negative "
           "anti-correlation by flipping its sign:")
    d.eq(r"$Q \;=\; \rho_{\mathrm{split}} \;+\; \max(0,\; -\rho_{\mathrm{PC,PP}})$")
    d.para("Worked example (expanded_curated): split-half ρ = 0.670 and PC–PP anti-correlation "
           "= −0.479, so Q = 0.670 + 0.479 = 1.149. The label-free co-primary unsupervised_p2 scores "
           "Q = 0.691 + 0.471 = 1.162. (In code: the metrics are columns in ruler_diagnostics.csv "
           "from step5b; the score is healthy_splithalf_rho_mean − healthy_pc_pp_anticorr in "
           "summarize_signature_battery.py.)")
    d.callout("What the score deliberately ignores — and the in-sample caveat (your Q1–4 tie-in)",
              "Disease-collapse strength is NOT in the score: using the test cohort to choose the "
              "instrument would be circular. Selection uses healthy metrics only. One subtlety follows "
              "directly from Sec. 4: a PCA axis fit on Paper-1 healthy cells is then scored on those "
              "same cells, so its anti-correlation and split-half are optimistically inflated (in-"
              "sample). That is why such rulers (unsupervised, unsupervised_combined) are marked "
              "‘control (Paper1-fit)’ and excluded from the competition, while leakage-clean rulers "
              "— published lists and Paper-2-trained axes — compete on equal footing.", accent=RUST)
    d.h2("(iii) A third diagnostic: within-program coherence")
    d.para("Coherence is reported alongside the score (and tracked into disease) but is not part of Q. "
           "It is the mean pairwise correlation among the genes of ONE program — every pericentral gene "
           "against every other pericentral gene (and likewise for periportal) — using their per-cell "
           "z-vectors within a stage. It asks a different question from the two above: not ‘are the two "
           "programs opposite?’ (anti-correlation, which is BETWEEN programs) and not ‘is the whole "
           "coordinate reproducible?’ (split-half), but ‘are the genes inside one program still moving "
           "together as a coordinated unit?’")
    d.figure(fig_coherence, 1.7,
             caption="Each line is one gene’s profile across cells. Left: a coherent program — the genes "
                     "rise and fall together (high mean pairwise correlation). Right: a fragmented program "
                     "— the genes have decoupled (low coherence).")
    d.para("Why it earns its own readout: it separates ‘the program’s genes switched off’ from ‘the "
           "program lost its internal coordination.’ Tracking coherence across disease stages helps tell "
           "a genuine loss of spatial organization from a mere change in average expression level. (In "
           "code: coherence_pc / coherence_pp via _mean_pairwise_corr() in step5b.)")

    # ---------- 7. statistics vocabulary ----------
    d.h1("7.  Reading the disease results: the statistics vocabulary")
    d.para("The healthy checks above decide which ruler to trust. The disease tests (H1/H2/H3) then run "
           "on the 47 donors. A few recurring terms in those results deserve precise definitions.")
    d.h2("Spearman’s ρ (rho)")
    d.para("ρ is a rank correlation: replace each variable’s values by their ranks (1st, 2nd, 3rd, …) "
           "and take the ordinary correlation of those ranks. It ranges from −1 to +1 and measures "
           "whether two quantities move together monotonically, without assuming the relationship is a "
           "straight line. We use it by default because single-nucleus counts and per-donor summaries are "
           "heavy-tailed and not linear, and ranks are robust to outliers. Example: ‘per-donor spread "
           "vs stage ρ = −0.43’ means that across the 47 donors, higher disease stage goes with smaller "
           "coordinate spread, fairly consistently. ρ is an effect size — we always report it next to a "
           "p-value, because a tiny ρ can be ‘significant’ yet biologically trivial.")
    d.h2("Permutation p-value (perm p)")
    d.para("A p-value answers: if there were truly no association, how often would chance alone produce "
           "an effect at least this large? Instead of trusting a textbook formula (which assumes "
           "normality and independence we do not have with 47 tied, non-normal donors), we compute it by "
           "SHUFFLING. We randomly permute the stage labels across donors, recompute the statistic, and "
           "repeat ~2,000 times to build a null distribution; the perm p is the fraction of shuffles "
           "whose effect is as extreme as the observed one. It assumes almost nothing about the data’s "
           "shape, which is exactly what a small, messy cohort needs. (In code: perm_p in step6; "
           "jonckheere_terpstra(n_perm=2000) in common.py.)")
    d.h2("Coordinate spread (SD) vs IQR — two ways to measure de-zonation")
    d.para("For one donor, collect all that donor’s cells’ coordinates into a distribution. A healthy "
           "donor’s cells span the whole porto-central axis (a wide distribution); a de-zonated donor’s "
           "cells bunch toward the middle (a narrow one). H1 measures that width two ways:")
    d.bullet("Spread = the standard deviation of the donor’s coordinates — the average distance of cells "
             "from the donor mean. Sensitive to the tails: a few extreme cells move it.")
    d.bullet("IQR (inter-quartile range) = the 75th percentile minus the 25th percentile — the width of "
             "the middle 50% of cells. It ignores the tails, so it is robust to a handful of outlier "
             "cells or doublets.")
    d.figure(fig_spread_iqr, 1.85,
             caption="One donor’s coordinate distribution. The double arrow is ±1 SD (the spread); the "
                     "shaded band is the IQR. Healthy (left): wide. De-zonated (right): both shrink.")
    d.para("We report both precisely because they have different failure modes: if only one fell with "
           "disease, the collapse could be an artefact of that choice (e.g. SD driven by outliers). They "
           "fall together (spread ρ ≈ −0.43, IQR ρ ≈ −0.47 on the expanded ruler), so the collapse is "
           "real, not a metric artefact. (In code: coord_spread_std = np.nanstd, coord_iqr = p75 − p25 "
           "in step5b/step6.)")
    d.h2("Zonal slope, and ‘slope-loss, held-out’ (the H2 primary test)")
    d.para("A gene’s zonal slope captures how steeply it is zonated in a given donor. Bin that donor’s "
           "cells into quantiles of the coordinate (five bins running pericentral→periportal), form a "
           "pseudobulk expression value per bin, and fit the slope of expression against bin index. A "
           "strongly zonated gene has a steep slope; a gene that has lost its spatial restriction has a "
           "flat one. Slope-LOSS is that slope flattening as disease advances — tested across donors "
           "after aligning each gene by its known direction so that ‘more negative trend’ means "
           "‘weakening’ for both poles.")
    d.figure(fig_slopeloss, 1.75,
             caption="One gene across coordinate bins. Healthy (left): a steep slope — high pericentrally, "
                     "low periportally. Diseased (right): the slope has flattened — the gene no longer "
                     "tracks position. H2 asks whether this flattening trends with disease stage.")
    d.callout("Why ‘held-out’ — avoiding a circular test",
              "There is a trap: if we bin cells using a coordinate that was itself built from gene X, "
              "then test gene X’s slope along that coordinate, X correlates with its own coordinate by "
              "construction — circular. The held-out design breaks this: the coordinate used for binning "
              "is built from a RANDOM HALF of the signature genes, and slope-loss is measured only on the "
              "OTHER half. No gene is ever tested against a coordinate it helped define. This is repeated "
              "over 20 random splits and averaged, so the H2 result is non-circular by construction. (In "
              "code: h2_slope_loss() with the held-out split, step7_de.py.)")

    # ---------- 8. recap ----------
    d.h1("8.  How the pieces fit together")
    d.figure(fig_pipeline, 1.5)
    d.para("Reading left to right: choose genes (a published list, or let PCA find them); normalize "
           "each gene to a z-score (Sec. 2); combine into one coordinate per cell, either by the "
           "signature mean (Sec. 3) or the PCA axis (Sec. 4); require the coordinate to pass the "
           "8-marker healthy gate (Sec. 5); rank the survivors by the healthy quality score (Sec. 6); "
           "freeze the best two leakage-clean rulers — one interpretable, one label-free — and only "
           "then transfer them to the disease cohort, where collapse (H1), program slope-loss (H2), and "
           "plasticity coupling (H3) are genuine out-of-sample tests.")
    d.callout("One-line answers",
              "Q1  PCA maximizes the variance, across hepatocytes, of a weighted-sum-of-genes score — "
              "the long axis of the cell cloud in gene-space, which is zonation.\n"
              "Q2  z = (log1p-CP10k expression − gene mean) / gene SD; ‘by the healthy atlas’ = those "
              "mean/SD (and the PCA) come from Paper-2 healthy cells, then applied to Paper 1.\n"
              "Q3  In healthy cells, check that 8 canonical markers correlate with the coordinate in the "
              "expected direction; pass if ≥4 present and a majority are correct.\n"
              "Q4  Q = split-half reproducibility + the size of the (negative) PC–PP anti-correlation, "
              "both measured in healthy cells; disease is never used to select.")

    d.close()
    return path


if __name__ == "__main__":
    out = os.path.join(str(config.REPORTS), "Zonation_Methods_Explainer.pdf")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    build(out)
    print("wrote", out)
