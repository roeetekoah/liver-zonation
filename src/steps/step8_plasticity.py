"""Step 8 — de-zonation ↔ plasticity coupling, WITHIN donor/stage (A8, H3).

Reference implementation already exists in src/pipeline.py:plasticity; this module is
the modular scaffold.
"""
from __future__ import annotations


def plasticity(coord, plast, stage, donor, min_cells=30):
    """Test whether more de-zonated cells/donors are more plastic — without stage confound.

    Inputs
      coord[] : zonation coordinate (Step 4).
      plast[] : plasticity score (ductal/progenitor markers, Step 4).
      stage, donor : per-cell labels.
    Outputs
      per_donor_rho : within-donor Spearman(de-zonation, plasticity) per donor + summary.
      ols_fit       : plast ~ dez + C(stage) + C(donor) coefficient and p for `dez`.
    Artefact ID
      A8 — plasticity coupling stats (H3).
    Algorithm
      1. de-zonation proxy: distance of coord from its center (|z(coord)|, sign-flipped),
         so mid-axis cells = more de-zonated.
      2. Per donor (>= min_cells): Spearman(dez, plast); summarize mean rho & % positive.
      3. Pooled OLS plast ~ dez + C(stage) + C(donor) to regress OUT stage & donor.
    Acceptance check
      Mean within-donor rho > 0 and the OLS `dez` coefficient is positive & significant.
    Stats notes
      NEVER pool raw cells across donors/stages — disease stage confounds both de-zonation
      and plasticity, manufacturing a spurious correlation. Test WITHIN donor/stage, or
      explicitly include C(stage)+C(donor) as covariates.
    """
    raise NotImplementedError(
        "Step 8 scaffold. Reference: src/pipeline.py:plasticity. Compute within-donor "
        "de-zonation↔plasticity correlation + OLS with stage/donor covariates (A8/H3)."
    )
