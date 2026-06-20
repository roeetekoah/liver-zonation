"""Step 4b — zone classifier + per-cell entropy de-zonation read-out (Artefact A4b).

Reference implementation already exists in src/classifier.py; this module is the
modular scaffold.
"""
from __future__ import annotations


def classify_entropy(Xp2, y_zone, Xp1, p1_stage, p1_barcodes, classes=(0, 1, 2)):
    """Train a zone classifier on Paper 2, score Paper 1, output per-cell zone entropy.

    Inputs
      Xp2, y_zone : Paper 2 hepatocyte features + zone labels (paper2_train.npz).
      Xp1         : Paper 1 hepatocyte features in the SAME shared-gene order (Step 3).
      p1_stage, p1_barcodes : per-cell stage and IDs for the output table.
    Outputs
      zone_probs : Paper 1 per-cell predict_proba over zones.
      entropy[]  : H = −Σ p log p per Paper 1 cell (low = zonated, high = de-zonated).
      eval       : held-out Paper 2 confusion matrix + accuracy.
    Artefact ID
      A4b — classifier_entropy.csv + Paper 2 confusion matrix.
    Algorithm
      1. Split Paper 2 into train/test; fit a CALIBRATED multinomial logistic regression.
      2. Evaluate on the Paper 2 held-out split (confusion matrix) FIRST.
      3. Apply the Paper-2-fitted scaler+model to Paper 1 -> predict_proba.
      4. entropy = −Σ p log p per cell; assemble {cell_id, stage, entropy, p_zone*}.
    Acceptance check
      Paper 2 held-out accuracy clearly beats chance; healthy Paper 1 entropy is LOW.
    Stats notes
      PREFER a calibrated multinomial logistic model over a random forest — better-
      calibrated probabilities make the entropy read-out trustworthy. Use the Paper 2
      scaler on Paper 1 (no leakage). Aggregate entropy per donor for Step 6, not per cell.
    """
    raise NotImplementedError(
        "Step 4b scaffold. Reference: src/classifier.py. Fit calibrated multinomial "
        "logistic on Paper 2, report held-out confusion matrix, emit Paper 1 entropy (A4b)."
    )
