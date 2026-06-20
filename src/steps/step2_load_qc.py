"""Step 2 — load Paper 1 hepatocytes + donor + libsize + QC sanity (Artefact A2).

Reference implementation already exists in src/pipeline.py:load; this module is the
modular scaffold.
"""
from __future__ import annotations


def load_qc(paper1_dir, donor_cols=("Patient.ID", "patient", "donor", "orig.ident", "sample")):
    """Load the Paper 1 hepatocyte count matrix, metadata, donor IDs and library sizes.

    Inputs
      paper1_dir : data/processed/paper1/ (counts.mtx, genes.txt, barcodes.txt,
                   cell_metadata.csv, metadata_all_cells.csv). See config.PAPER1.
      donor_cols : candidate column names for the donor/patient ID (first hit wins).
    Outputs
      M (genes x cells sparse), genes[], barcodes[], stage[], donor[], libsize[].
    Artefact ID
      A2 — per-stage and per-donor cell-count table (results/tables/qc_counts.csv).
    Algorithm
      1. scipy.io.mmread counts.mtx -> CSC; read genes/barcodes.
      2. Join cell_metadata.csv on barcodes -> stage per cell.
      3. From metadata_all_cells.csv, find the donor column (donor_cols) -> donor per cell.
      4. libsize = column sums of M.
      5. Tabulate cells per stage and per donor; write A2.
    Acceptance check
      Donor IDs are present and non-null (needed by Step 6); ~47 donors, ~69k cells.
    Stats notes
      QC from the source object is INHERITED — treat it as sanity-only and RE-NORMALIZE
      from raw counts downstream (log1p CP10k). Do NOT re-filter cells here; just record
      counts. Donor IDs MUST survive to Step 6 (unit of inference = donor).
    """
    raise NotImplementedError(
        "Step 2 scaffold. Reference: src/pipeline.py:load. Fill in QC-count tabulation "
        "(A2) and donor-ID resolution, returning M, genes, barcodes, stage, donor, libsize."
    )
