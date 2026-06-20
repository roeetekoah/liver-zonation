"""Step 7 — pseudobulk donor×zone differential expression across stages (A7, H2).

Reference implementation already exists in src/pipeline.py:de; this module is the
modular scaffold.
"""
from __future__ import annotations


def de(M, genes, libsize, coord, stage, donor, sig_genes, min_donor_cells=20, min_frac=0.10):
    """Find genes whose zonal restriction changes with disease — pseudobulk, FDR, guarded.

    Inputs
      M, genes, libsize : Paper 1 counts + library sizes.
      coord, stage, donor: zonation coordinate + per-cell labels.
      sig_genes         : signature genes to EXCLUDE / flag (circularity guard).
    Outputs
      de_df per zone (portal, central): {gene, effect_vs_stage, p, q, is_signature}.
    Artefact ID
      A7 — de_portal.csv / de_central.csv (H2 drivers).
    Algorithm
      1. Bin coord into zones (terciles): portal / mid / central.
      2. PSEUDOBULK: per (donor, zone) mean log1p CP10k for donors with >= min_donor_cells.
      3. Keep genes detected in >= min_frac of donor pseudobulks.
      4. Test each gene's pseudobulk vs donor stage_rank (Spearman / linear); BH-FDR.
      5. Circularity guards: exclude signature genes from the driver list; use a RANDOM
         held-out gene split (build coord on one half, test the disjoint half) REPEATED
         K~20-50 times, reporting the distribution across splits (median effect + fraction
         significant) — meaningful with the full ~1,640-gene set, not 20 landmarks;
         optionally fit interaction expr ~ coord + stage + coord×stage.
    Acceptance check
      A meaningful set of NON-signature genes is significant (q<0.05) after FDR.
    Stats notes
      Pseudobulk per donor×zone is the unit (avoids cell pseudoreplication). The
      coord×stage interaction term tests whether the zonal GRADIENT (not just the level)
      changes with disease. Never test the genes that built the coordinate.
    """
    raise NotImplementedError(
        "Step 7 scaffold. Reference: src/pipeline.py:de. Build donor×zone pseudobulk, "
        "BH-FDR test vs stage, with signature-exclusion / held-out / interaction guards (A7/H2)."
    )
