"""Step 4 — signature scoring: zonation coordinate + plasticity score (Artefact A4)."""
from __future__ import annotations
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # src/
import config
from steps.common import log, PLAST, VAL


def load_signature_set(which=config.DEFAULT_SET):
    """Return (PC_genes, PP_genes) lists for a named signature set (config.SIGNATURE_SETS)."""
    pc_path, pp_path = config.signature_files(which)
    PC = [g.strip() for g in open(str(pc_path)) if g.strip()]
    PP = [g.strip() for g in open(str(pp_path)) if g.strip()]
    return PC, PP


def zrows(M, genes, libsize, wanted):
    """gene -> per-cell z-scored log1p-CP10k vector, for each requested gene present in `genes`.
    Slices all requested rows once and converts to CSR (fast row access) — far faster than a
    per-gene getrow() on a CSC matrix when `wanted` is large (e.g. the full transcriptome)."""
    gi = {g: i for i, g in enumerate(genes)}
    keep = [g for g in wanted if g in gi]
    if not keep:
        return {}
    sub = M[[gi[g] for g in keep]].tocsr()          # one slice, row-format
    lib = np.asarray(libsize, float)
    out = {}
    for j, g in enumerate(keep):
        v = np.log1p(np.asarray(sub.getrow(j).todense()).ravel().astype(float) / lib * 1e4)
        sd = v.std(); out[g] = (v - v.mean()) / sd if sd > 0 else v * 0
    return out


def score(M, genes, libsize, pc_genes, pp_genes, plast_genes=tuple(PLAST), which=""):
    """Compute the per-cell zonation coordinate (mean_z(PC) - mean_z(PP)) and a plasticity score.

    Inputs
      M, genes, libsize : Paper 1 counts (genes x cells), gene symbols, library sizes.
      pc_genes, pp_genes: pericentral / periportal signature lists (from load_signature_set).
      plast_genes       : ductal/progenitor plasticity markers.
    Outputs
      coord[], pc[], pp[], plast[], col{gene -> z-vector}.
    Notes
      Per-arm standardization equalises the two arms despite the PC/PP gene-count imbalance
      (e.g. full = 1273 PC vs 364 PP): each arm is a mean, but the smaller arm is noisier, so
      unit-variance scaling each side before subtracting fixes that.
    """
    log(f"Steps 3-4a: signature scoring [set={which}] ...")
    want = set(list(pc_genes) + list(pp_genes) + list(plast_genes)
               + VAL["pericentral"] + VAL["periportal"])
    col = zrows(M, genes, libsize, want)
    pc = np.mean([col[g] for g in pc_genes if g in col], axis=0)
    pp = np.mean([col[g] for g in pp_genes if g in col], axis=0)
    pc = (pc - pc.mean()) / (pc.std() + 1e-9)
    pp = (pp - pp.mean()) / (pp.std() + 1e-9)
    coord = pc - pp
    plast = (np.mean([col[g] for g in plast_genes if g in col], axis=0)
             if any(g in col for g in plast_genes) else np.zeros_like(coord))
    return coord, pc, pp, plast, col
