"""Step 6 — DONOR-LEVEL zonation collapse across disease stages (Artefact A6, H1).

Reference implementation already exists in src/pipeline.py:collapse; this module is
the modular scaffold.
"""
from __future__ import annotations


def collapse(coord, pc, pp, stage, donor, entropy=None, min_cells=30, n_boot=2000):
    """Test whether zonation structure collapses with disease — one value PER DONOR.

    Inputs
      coord, pc, pp : Step 4 outputs.   entropy : optional Step 4b per-cell entropy.
      stage, donor  : per-cell labels.  min_cells : min cells to keep a donor.
    Outputs
      per_donor_df : {donor, stage, stage_rank, n, spread, anticorr, mean_entropy}.
      trend        : per-metric {rho, p, boot_CI, perm_p} of metric vs stage_rank.
    Artefact ID
      A6 — collapse_per_donor.csv + headline trend stats (H1).
    Algorithm
      1. For each donor with >= min_cells: compute ONE value per metric —
         coordinate spread = std(coord); PC–PP anti-correlation = corr(pc, pp);
         mean entropy (if given).
      2. Map donors to stage_rank (ordered: Healthy<NAFLD<NASH<Cirrhosis<End-stage).
      3. Ordered-trend test across the ~47 donor values (Spearman or Jonckheere).
      4. Donor bootstrap CI on the trend statistic.
      5. Donor-LABEL-shuffle permutation null (negative control) -> perm p-value.
    Acceptance check
      spread DOWN, anti-correlation toward 0, mean entropy UP across stages, with
      perm_p small and bootstrap CI excluding 0.
    Stats notes
      UNIT OF INFERENCE = DONOR, never cell. Cell-level p-values are pseudoreplication
      and invalid. Aggregate first, THEN test the trend on the donor-level values.
    """
    raise NotImplementedError(
        "Step 6 scaffold. Reference: src/pipeline.py:collapse. Compute one metric per "
        "donor, ordered-trend test + donor bootstrap CI + donor-label-shuffle null (A6/H1)."
    )
