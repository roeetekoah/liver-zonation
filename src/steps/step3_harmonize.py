"""Step 3 — gene-ID harmonization across Paper1 ∩ Paper2 ∩ signatures (Artefact A3).

NOT yet implemented in src/pipeline.py — this is a real stub to be written.
"""
from __future__ import annotations


def harmonize(p1_genes, p2_genes, signature_genes, M=None, libsize=None):
    """Reconcile gene identifiers across datasets and build the shared feature matrix.

    Inputs
      p1_genes        : Paper 1 gene symbols (data/processed/paper1/genes.txt).
      p2_genes        : Paper 2 gene symbols (from the .mat / paper2_train.npz).
      signature_genes : union of PC/PP signature genes (signatures/*_core.txt etc).
      M, libsize      : optional Paper 1 counts + libsizes to produce z/rank features.
    Outputs
      shared_genes[]  : symbols present in all three (or in P1 ∩ P2 ∩ requested sigs).
      mapping_report  : DataFrame {gene, in_p1, in_p2, in_sig, kept} + overall rate.
      features        : per-cell z-scored (or rank-transformed) matrix on shared_genes.
    Artefact ID
      A3 — gene-mapping report (results/tables/gene_mapping.csv) + mapping rate logged.
    Algorithm
      1. Normalize symbol casing / known aliases (synonym table) on each list.
      2. shared = intersection; record per-list membership and the mapping rate.
      3. For each shared gene compute log1p CP10k, then z-score (or rankdata) per gene.
      4. Return shared_genes, mapping_report, features (cells x shared_genes).
    Acceptance check
      Mapping rate for signature genes is high (>~80%); flag any core anchor that drops.
    Stats notes
      Harmonize ONCE and reuse the same feature space for scoring and the classifier so
      Paper 1 and Paper 2 features are directly comparable.
    """
    raise NotImplementedError(
        "Step 3 scaffold (no reference in pipeline.py). Implement symbol harmonization, "
        "mapping-rate report (A3) and z/rank feature construction on the shared gene set."
    )
