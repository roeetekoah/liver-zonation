"""Deterministic binomial thinning shared by the count-based analyses.

Each gene receives an independent, stable pseudo-random stream derived from the
analysis seed and gene name. Results therefore do not depend on Python hash
randomization, set iteration order, or which other genes a script requests.
"""
from hashlib import sha256

import numpy as np


def _gene_seed(base_seed: int, gene: str) -> int:
    digest = sha256(f"liver-zonation:{base_seed}:{gene}".encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "little")


def thin_genes(frame, genes, probabilities, base_seed: int = 0, fillna: bool = False):
    """Return deterministic binomial-thinned arrays for the requested genes."""
    output = {}
    for gene in sorted(set(genes)):
        values = frame[gene]
        if fillna:
            values = values.fillna(0)
        rng = np.random.RandomState(_gene_seed(base_seed, gene))
        output[gene] = rng.binomial(values.to_numpy(dtype=int), probabilities)
    return output
