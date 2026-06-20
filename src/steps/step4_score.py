"""Step 4 — signature scoring: zonation coordinate + plasticity score (Artefact A4).

Reference implementation already exists in src/pipeline.py:score; this module is the
modular scaffold.
"""
from __future__ import annotations


def score(M, genes, libsize, pc_genes, pp_genes, plast_genes):
    """Compute the per-cell zonation coordinate and a plasticity score.

    Inputs
      M, genes, libsize : Paper 1 counts (genes x cells), gene symbols, library sizes.
      pc_genes, pp_genes: pericentral / periportal signatures (core | expanded | sensitivity).
      plast_genes       : ductal/progenitor plasticity markers (KRT7/19, SOX9/4, ...).
    Outputs
      coord[]  : zonation coordinate = mean_z(PC) − mean_z(PP) per cell.
      pc[], pp[]: the two module z-score means (kept for Step 6 anti-correlation).
      plast[]  : mean_z(plast_genes) per cell.
      col{}    : gene -> per-cell z-scored vector (reused by validation).
    Artefact ID
      A4 — coordinates table (results/tables/coordinates.csv) with coord/pc/pp/plasticity.
    Algorithm
      1. For each signature gene: v = log1p(counts/libsize*1e4); z = (v−mean)/sd.
      2. pc = mean z over PC genes present; pp = mean z over PP genes present.
      3. coord = pc − pp.   plast = mean z over plasticity markers present.
    Acceptance check
      coord spans both signs; pc and pp are anti-correlated in healthy cells.
    Stats notes
      Run with the CORE signatures for the primary coordinate, then re-run with EXPANDED
      (robustness) and periportal SENSITIVITY (HAMP removed) to show the result is not an
      acute-phase artefact. Never mix tiers within one coordinate.
    """
    raise NotImplementedError(
        "Step 4 scaffold. Reference: src/pipeline.py:score. Return coord, pc, pp, plast, col "
        "for the chosen signature tier (core/expanded/sensitivity)."
    )
