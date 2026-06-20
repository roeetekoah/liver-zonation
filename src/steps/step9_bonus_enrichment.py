"""Step 9 (BONUS, optional) — overlap of collapse drivers with Paper 3 risk genes (A9-bonus).

NOT yet implemented in src/pipeline.py — this is a real, strictly-optional stub.
Gene-list-only and lightweight: no heavy data, just set overlap statistics.
"""
from __future__ import annotations


def bonus_enrichment(driver_genes, risk_target_genes, background_genes,
                     expr_for_matching=None):
    """Test whether Step-7 collapse-driver genes are enriched for Paper 3 risk targets.

    Inputs
      driver_genes      : significant non-signature genes from Step 7 (A7).
      risk_target_genes : Paper 3 risk-variant target genes (gene list).
      background_genes   : all tested/expressed genes (the universe).
      expr_for_matching : optional per-gene mean expression, to build an EXPRESSION-MATCHED
                          background (drivers skew highly expressed -> control for it).
    Outputs
      result : {overlap, expected, fold_enrichment, p_hypergeom_or_fisher, q_bh}.
    Artefact ID
      A9-bonus — driver↔risk-gene enrichment table.
    Algorithm
      1. Restrict all sets to the background universe.
      2. If expr_for_matching given, sample a background matched by expression bins.
      3. Hypergeometric (or Fisher exact 2x2) test of driver ∩ risk overlap.
      4. BH-correct across any zone/stage variants tested.
    Acceptance check
      Overlap exceeds the matched-background expectation with q<0.05 (if pursued).
    Stats notes
      STRICTLY OPTIONAL / stretch (Paper 3). Use an expression-MATCHED background so the
      signal is not just "both lists are highly expressed genes." Gene-list-only; light.
    """
    raise NotImplementedError(
        "Step 9 BONUS scaffold (no reference in pipeline.py). Implement hypergeometric/"
        "Fisher overlap of drivers vs Paper 3 risk genes against a matched background (A9)."
    )
