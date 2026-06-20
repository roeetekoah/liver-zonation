"""Step 5 — healthy positive-control validation GATE (Artefact A5).

Reference implementation already exists in src/pipeline.py:validate; this module is
the modular scaffold.
"""
from __future__ import annotations


def validate(coord, col, stage, entropy=None,
             pc_markers=("GLUL", "CYP2E1"), pp_markers=("ASS1", "HAL")):
    """Confirm the coordinate recovers known zonation in HEALTHY cells before proceeding.

    Inputs
      coord[] : zonation coordinate (Step 4).
      col{}   : gene -> per-cell z vector (for marker correlations).
      stage[] : per-cell disease stage (healthy subset is the positive control).
      entropy[]: optional classifier entropy (Step 4b) for the low-entropy check.
    Outputs
      report : {marker: (rho, expected_sign, pass)} + overall PASS/FAIL boolean.
    Artefact ID
      A5 — validation table (results/tables/validation.csv).
    Algorithm
      1. Restrict to healthy cells.
      2. Spearman(coord, marker): expect rho>0 for GLUL/CYP2E1 (pericentral),
         rho<0 for ASS1/HAL (periportal).
      3. If entropy given, check healthy mean entropy is LOW (well-zonated baseline).
    Acceptance check / GATE
      ALL marker signs correct AND healthy entropy low. This is a hard GATE — Step 6
      must NOT run if validation fails (fix the signature/scoring first).
    Stats notes
      Positive control only; uses cell-level correlations within healthy donors purely
      as a sanity check, NOT as a disease inference.
    """
    raise NotImplementedError(
        "Step 5 scaffold. Reference: src/pipeline.py:validate. Return per-marker Spearman "
        "with expected signs and an overall PASS that GATES Step 6."
    )
