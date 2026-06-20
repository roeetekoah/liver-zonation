"""Step 5b — "ruler" diagnostics: is the coordinate a trustworthy measuring stick? (A5b)

NOT yet implemented in src/pipeline.py — this is a real stub to be written.
"""
from __future__ import annotations


def ruler_diagnostics(coord, pc, pp, col, stage, donor, pc_genes, pp_genes):
    """Per-stage diagnostics distinguishing a degraded RULER from real biology.

    Inputs
      coord, pc, pp : Step 4 outputs.    col{} : gene -> z vector.
      stage, donor  : per-cell labels.
      pc_genes, pp_genes : the signatures used to build the coordinate.
    Outputs
      diag_df : per-stage rows with
        internal_coherence       : mean pairwise corr WITHIN each program (PC; PP).
        cross_program_anticorr   : corr(pc, pp) (expect strongly negative when healthy).
        split_half_repro         : corr of coord from two random halves of each program.
        program_off_vs_restr_lost: mean program level vs spread (is the gene OFF, or is
                                    its spatial RESTRICTION lost while level is intact?).
    Artefact ID
      A5b — ruler diagnostics table (results/tables/ruler_diagnostics.csv).
    Algorithm
      1. For each stage: compute within-program coherence, cross-program anti-correlation.
      2. Split each program's genes in half, rebuild two sub-coordinates, correlate.
      3. Compare mean expression ("program off") vs coordinate spread ("restriction lost").
    Acceptance check
      In healthy: high coherence, strong anti-correlation, high split-half reproducibility.
    Stats notes
      Separates "the signature genes turned off" from "the zonation axis dissolved" — the
      collapse claim needs the latter, so report both. Stage-level summaries, not per cell.
    """
    raise NotImplementedError(
        "Step 5b scaffold (no reference in pipeline.py). Implement per-stage coherence, "
        "anti-correlation, split-half reproducibility, and program-off vs restriction-lost (A5b)."
    )
